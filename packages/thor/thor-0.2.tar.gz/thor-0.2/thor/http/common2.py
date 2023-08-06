#!/usr/bin/env python

"""
Thor HTTP Parser

This module contains utility functions and a base class
for the parsing portions of the HTTP client and server.
"""

__author__ = "Mark Nottingham <mnot@mnot.net>"
__copyright__ = """\
Copyright (c) 2005-2011 Mark Nottingham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


class HttpParser:
    """
    This is a base class for something that has to parse HTTP/1.x messages, 
    request or response.

    It expects you to override input_start, input_body and input_end, and call
    handle_input when you get bytes from the network.
    """

    inspecting = False  # if True, don't fail on errors, but preserve them

    def __init__(self):
        self.input_header_length = 0
        self.input_transfer_length = 0
        self._input_buffer = ""
        self._input_state = WAITING
        self._input_delimit = None
        self._input_body_left = 0
        self._output_state = WAITING
        self._output_delimit = None

    def input_start(self, top_line, hdr_tuples, conn_tokens,
                     transfer_codes, content_length):
        """
        Take the top set of headers from the input stream, parse them
        and queue the request to be processed by the application.

        Returns boolean allows_body to indicate whether the message allows a
        body.

        Can raise ValueError to indicate that there's a problem and parsing
        cannot continue.
        """
        raise NotImplementedError

    def input_body(self, chunk):
        "Process a body chunk from the wire."
        raise NotImplementedError

    def input_end(self, trailers):
        """
        Indicate that the response body is complete. Optionally can contain
        trailers.
        """
        raise NotImplementedError

    def input_error(self, err):
        "Indicate an unrecoverable parsing problem with the input stream."
        raise NotImplementedError

    def handle_input(self, chunk):
        """
        Given a chunk of input, figure out what state we're in and handle it,
        making the appropriate calls.
        """
        if self._input_buffer != "":
            chunk = self._input_buffer + chunk
            self._input_buffer = ""

        if self._input_state == WAITING:
            if hdr_end.search(chunk): # found one
                rest = self._parse_headers(chunk)
                try:
                    self.handle_input(rest)
                except RuntimeError:
                    self.input_error(error.TooManyMsgsError)
                    # we can't recover from this, so we bail.
            else: # partial headers; store it and wait for more
                self._input_buffer = chunk
        elif self._input_state == HEADERS_DONE:
            try:
                handler = getattr(self, '_handle_%s' % self._input_delimit)
            except AttributeError:
                raise Exception, "Unknown input delimiter %s" % \
                                 self._input_delimit
            handler(chunk)
        elif self._input_state == ERROR:
            pass # I'm silently ignoring input that I don't understand.
        else:
            raise Exception, "Unknown state %s" % self._input_state

    def _handle_nobody(self, chunk):
        "Handle input that shouldn't have a body."
        self.input_end([])
        self._input_state = WAITING
        self.handle_input(chunk)

    def _handle_close(self, chunk):
        "Handle input where the body is delimited by the connection closing."
        self.input_transfer_length += len(chunk)
        self.input_body(chunk)

    def _handle_chunked(self, chunk):
        "Handle input where the body is delimited by chunked encoding."
        while chunk:
            if self._input_body_left < 0: # new chunk
                chunk = self._handle_chunk_new(chunk)
            elif self._input_body_left > 0:
                # we're in the middle of reading a chunk
                chunk = self._handle_chunk_body(chunk)
            elif self._input_body_left == 0: # body is done
                chunk = self._handle_chunk_done(chunk)

    def _handle_chunk_new(self, chunk):
        try:
            # they really need to use CRLF
            chunk_size, rest = chunk.split(linesep, 1)
        except ValueError:
            # don't have the whole chunk_size yet... wait a bit
            if len(chunk) > 512:
                # OK, this is absurd...
                self.input_error(error.ChunkError(chunk))
                # TODO: need testing around this; catching the right thing?
            else:
                self._input_buffer += chunk
            return
        # TODO: do we need to ignore blank lines?
        if ";" in chunk_size: # ignore chunk extensions
            chunk_size = chunk_size.split(";", 1)[0]
        try:
            self._input_body_left = int(chunk_size, 16)
        except ValueError:
            self.input_error(error.ChunkError(chunk_size))
            return
        self.input_transfer_length += len(chunk) - len(rest)
        return rest

    def _handle_chunk_body(self, chunk):
        got = len(chunk)
        if self._input_body_left + 2 < got: # got more than the chunk
            this_chunk = self._input_body_left
            self.input_body(chunk[:this_chunk])
            self.input_transfer_length += this_chunk + 2
            self._input_body_left = -1
            return chunk[this_chunk + 2:] # +2 consumes the trailing CRLF
        elif self._input_body_left + 2 == got:
            # got the whole chunk exactly (including CRLF)
            self.input_body(chunk[:-2])
            self.input_transfer_length += self._input_body_left + 2
            self._input_body_left = -1
        elif self._input_body_left == got: # corner case
            self._input_buffer += chunk  
        else: # got partial chunk
            self.input_body(chunk)
            self.input_transfer_length += got
            self._input_body_left -= got

    def _handle_chunk_done(self, chunk):
        if len(chunk) >= 2 and chunk[:2] == linesep:
            self._input_state = WAITING
            self.input_end([])
            self.handle_input(chunk[2:]) # 2 consumes the CRLF
        elif hdr_end.search(chunk): # trailers
            self._input_state = WAITING
            trailer_block, rest = hdr_end.split(chunk, 1)
            trailers = self._parse_fields(trailer_block.splitlines())
            if trailers == None: # found a problem
                self._input_state = ERROR # TODO: need an explicit error 
                return
            else:
                self.input_end(trailers)
                self.handle_input(rest)
        else: # don't have full trailers yet
            self._input_buffer = chunk

    def _handle_counted(self, chunk):
        "Handle input where the body is delimited by the Content-Length."
        if self._input_body_left <= len(chunk): # got it all (and more?)
            self.input_transfer_length += self._input_body_left
            self.input_body(chunk[:self._input_body_left])
            self.input_end([])
            self._input_state = WAITING
            if chunk[self._input_body_left:]:
                self.handle_input(chunk[self._input_body_left:])
        else: # got some of it
            self.input_body(chunk)
            self.input_transfer_length += len(chunk)
            self._input_body_left -= len(chunk)

    def _parse_fields(self, header_lines, gather_conn_info=False):
        """
        Given a list of raw header lines (without the top line,
        and without the trailing CRLFCRLF), return its header tuples.
        """

        hdr_tuples = []
        conn_tokens = []
        transfer_codes = []
        content_length = None

        for line in header_lines:
            if line[:1] in [" ", "\t"]: # Fold LWS
                if len(hdr_tuples):
                    hdr_tuples[-1] = (
                        hdr_tuples[-1][0], 
                        "%s %s" % (hdr_tuples[-1][1], line.lstrip())
                    )
                    continue
                else: # top header starts with whitespace
                    self.input_error(error.TopLineSpaceError(line))
                    if not self.inspecting:
                        return
            try:
                fn, fv = line.split(":", 1)
            except ValueError:
                if self.inspecting:
                    hdr_tuples.append(line)
                else:
                    continue # TODO: error on unparseable field?
            if fn[-1] in [" ", "\t"]:
                self.input_error(error.HeaderSpaceError(fn))
                if not self.inspecting:
                    return
            hdr_tuples.append((fn, fv))

            if gather_conn_info:
                f_name = fn.strip().lower()
                f_val = fv.strip()

                # parse connection-related headers
                if f_name == "connection":
                    conn_tokens += [
                        v.strip().lower() for v in f_val.split(',')
                    ]
                elif f_name == "transfer-encoding": # TODO: parameters? no...
                    transfer_codes += [v.strip().lower() for \
                                       v in f_val.split(',')]
                elif f_name == "content-length":
                    if content_length != None:
                        try:
                            if int(f_val) == content_length:
                                # we have a duplicate, non-conflicting c-l.
                                continue
                        except ValueError:
                            pass
                        self.input_error(error.DuplicateCLError())
                        if not self.inspecting:
                            return
                    try:
                        content_length = int(f_val)
                        assert content_length >= 0
                    except (ValueError, AssertionError):
                        self.input_error(error.MalformedCLError(f_val))
                        if not self.inspecting:
                            return
            
        # yes, this is a horrible hack.     
        if gather_conn_info:
            return hdr_tuples, conn_tokens, transfer_codes, content_length
        else:
            return hdr_tuples

    def _parse_headers(self, chunk):
        """
        Given a string that we knows starts with a header block (possibly
        more), parse the headers out and return the rest. Calls
        self.input_start to kick off processing.
        """
        top, rest = hdr_end.split(chunk, 1)
        self.input_header_length = len(top)
        header_lines = top.splitlines()

        # chop off the top line
        while True: # TODO: limit?
            try:
                top_line = header_lines.pop(0)
                if top_line.strip() != "":
                    break
            except IndexError: # empty
                return rest
        
        try:
            hdr_tuples, conn_tokens, transfer_codes, content_length \
            = self._parse_fields(header_lines, True)
        except TypeError: # returned None because there was an error
            if not self.inspecting:
                return "" # throw away the rest
            
        # ignore content-length if transfer-encoding is present
        if transfer_codes != [] and content_length != None:
            content_length = None

        try:
            allows_body = self.input_start(top_line, hdr_tuples,
                        conn_tokens, transfer_codes, content_length)
        except ValueError: # parsing error of some kind; abort.
            if not self.inspecting:
                return "" # throw away the rest
            allows_body = True

        self._input_state = HEADERS_DONE
        if not allows_body:
            self._input_delimit = NOBODY
        elif len(transfer_codes) > 0:
            if transfer_codes[-1] == 'chunked':
                self._input_delimit = CHUNKED
                self._input_body_left = -1 # flag that we don't know
            else:
                self._input_delimit = CLOSE
        elif content_length != None:
            self._input_delimit = COUNTED
            self._input_body_left = content_length
        else:
            self._input_delimit = CLOSE
        return rest
