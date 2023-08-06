# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
pstore-lib -- Python Protected Password Store (Library)
Copyright (C) 2013  Walter Doekes <wdoekes>, OSSO B.V.

    This library is free software; you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation; either version 3 of the License, or (at
    your option) any later version.

    This library is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,
    USA.
"""
try:
    from pgpdump import AsciiData, BinaryData
except ImportError:
    from pstorelib.pgpdump_tiny import AsciiData, BinaryData


__all__ = ('get_pubkey_id_from_ascii', 'get_pubkey_id_from_binary')


def get_pubkey_id_from_ascii(data):
    generator = AsciiData(data)
    for packet in generator.packets():
        if packet.raw == 6:
            return packet.key_id


def get_pubkey_id_from_binary(data):
    generator = BinaryData(data)
    for packet in generator.packets():
        if packet.raw == 6:
            return packet.key_id


if __name__ == '__main__':
    # FIXME: proper tests..
    from base64 import b64decode
    import sys
    data = b64decode(open(sys.argv[1], 'r').read().replace('\n', ''))
    print get_pubkey_id_from_binary(data)
