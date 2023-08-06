#!/usr/bin/python

# Copyright (C) 2012-2013 Cyrille Defranoux
#
# This file is part of Pyknx.
#
# Pyknx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyknx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyknx. If not, see <http://www.gnu.org/licenses/>.
#
# For any question, feature requests or bug reports, feel free to contact me at:
# knx at aminate dot net

import socket

class Socket:
    def __init__(self):
        self._socket = socket.socket()
        self._socket.settimeout(5)
        # self._socket.setblocking(1)

    def bind(self, address):
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(address)
        self._socket.listen(5)

    def connect(self, address):
        self._socket.connect(address)

    def close(self):
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def waitForData(self, endChar = chr(4)):
        # Wait for a connection.
        try:
            conn, address = self._socket.accept()
        except socket.timeout:
            return (None, None)

        # Read incoming data.
        data = ''
        while True:
            try:
                chunk = conn.recv(4)
                endCharIx = chunk.find(endChar)
                isLastChunk = endCharIx != -1
                if isLastChunk:
                    chunk = chunk[:endCharIx]
                data += chunk
                if isLastChunk:
                    break
            except:
                logger.reportException('Exception when waiting for incoming data.')
                try:
                    if not conn is None: conn.close()
                except:
                    logger.reportException('Could not close connection. Connection is discarded and process continues.')
                    pass
                return None, None
        return (data, conn)

    def sendData(self, data, endChar = chr(4)):
        self._socket.sendall(data + endChar)
        answer = ''
        self._socket.settimeout(60)
        while True:
            chunk = self._socket.recv(4096)
            answer += chunk
            if not chunk or chunk[len(chunk)-1] == endChar:
                break
        return answer
