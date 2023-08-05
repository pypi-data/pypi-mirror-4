#!/usr/bin/python
#===============================================================================
# Copyright (C) 2012 Adrian Hungate
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#===============================================================================
"""
This file is part of PyMMB - The crossplatform MMB library and toolset
If you don't use MMC Flash cards in a BBC Microcomputer, this is unlikely
to be a lot of use to you!
"""

import struct
import dfs

version = 0.1
MAXDISCS = 511

class DiscNotFoundException(Exception):
    pass

class InvalidDiscException(Exception):
    pass

class ParameterError(Exception):
    pass

class disc(dfs.dfs):
    """
    Class to represent a single disc in an MMB file
    """
    _mmb = None
    _id = -1
    _title = ""
    _exists = True
    _formatted = False
    _locked = True

    ENTRY_RO = 0x00
    ENTRY_RW = 0x0F
    ENTRY_EMPTY = 0xF0
    ENTRY_INVALID = 0xFF

    def __init__(self, did, mmb, title = "", status = 0xFF):
        """
        Initialise the disc entry with passed (or sensible default) values
        """
        dfs.dfs.__init__(self)
        self._mmb = mmb
        self._id = did
        self.title = title
        self.status = status

    def from_mmb(self, _file, ofs):
        """
        Initialize DFS from MMB file
        """
        self.file = _file
        self.ofs = ofs
        self.read_catalog()

    @property
    def id(self):
        """
        Return the ID (Read only)
        """
        return self._id

    @property
    def status(self):
        """
        Get the disc's status byte from the status flags
        """
        if not self._exists:
            return self.ENTRY_INVALID
        elif not self._formatted:
            return self.ENTRY_EMPTY
        elif not self._locked:
            return self.ENTRY_RW
        return self.ENTRY_RO

    @status.setter
    def status(self, status):
        """
        Set the status flags from an encoded byte
        """
        self._exists = (status & self.ENTRY_INVALID) != self.ENTRY_INVALID
        self._formatted = ((status & self.ENTRY_EMPTY) != self.ENTRY_EMPTY) & self._exists
        self._locked = ((status & self.ENTRY_RW) != self.ENTRY_RW) | (not self._exists)

    @property
    def exists(self):
        """
        Get status flag - Does this disc exist in the MMB?
        """
        return self._exists

    @exists.setter
    def exists(self, exists):
        """
        Set status flag - Does this disc exist in the MMB?
        """
        self._exists = exists

    @property
    def formatted(self):
        """
        Get status flag - Is this disc formatted?
        """
        return self._formatted

    @formatted.setter
    def formatted(self, formatted):
        """
        Set status flag - Is this disc formatted?
        """
        if not self.exists:
            raise InvalidDiscException("Illegal attempt to format nonexistant disc %s" % (self.id,))
        self._formatted = formatted

    @property
    def locked(self):
        """
        Get status flag - Is this disc locked (Read Only)?
        """
        return self._locked

    @locked.setter
    def locked(self, locked):
        """
        Set status flag - Is this disc locked (Read Only)?
        """
        if not self.exists:
            raise InvalidDiscException("Illegal attempt to lock nonexistant disc %s" % (self.id,))
        if not self.formatted:
            raise InvalidDiscException("Illegal attempt to lock unformatted disc %s" % (self.id,))
        self._locked = locked

    def read_from(self, filename):
        """
        Load an SSD image into this slot in the MMB
        """
        if not self.exists:
            raise InvalidDiscException("Illegal attempt to overwrite nonexistant disc %s" % (self.id,))
        if self.formatted and self.locked:
            raise InvalidDiscException("Illegal attempt to overwrite locked disc %s" % (self.id,))
        disc = dfs.dfs(filename)
        disc.write_to_file(self._mmb.file, 8192 + (204800 * self.id))
        self.from_mmb(self._mmb.file, 8192 + (204800 * self.id))
        self.formatted = True
        self.write_catalog()
        self._mmb.write_catalog()

    def format(self, title = "NONAME"):
        """
        Format the DFS disc pointed to by this structure
        """
        if not self.exists:
            raise InvalidDiscException("Illegal attempt to format nonexistant disc %s" % (self.id,))
        if self.formatted and self.locked:
            raise InvalidDiscException("Illegal attempt to format locked disc %s" % (self.id,))
        disc = dfs.dfs()
        disc.title = title
        disc.write_to_file(self._mmb.file, 8192 + (204800 * self.id))
        self.from_mmb(self._mmb.file, 8192 + (204800 * self.id))
        self.formatted = True
        self.write_catalog()
        self._mmb.write_catalog()

    def unformat(self):
        """
        Mark disc as unformatted, remove title from MMB catalogue
        """
        if not self.exists:
            raise InvalidDiscException("Illegal attempt to format nonexistant disc %s" % (self.id,))
        if self.formatted and self.locked:
            raise InvalidDiscException("Illegal attempt to unformat locked disc %s" % (self.id,))
        self.title = "UnFormatted"
        self.formatted = False
        self.write_catalog()
        self._mmb.write_catalog()

    def __repr__(self):
        if self.formatted:
            fmt = " FORMATTED"
            if self.locked:
                lck = " R/O"
            else:
                lck = " R/W"
        elif self.exists:
            fmt = " EMPTY"
            lck = ""
        else:
            fmt = " NON-EXISTENT"
            lck = ""
        return "<%s: %d: %s%s%s>" % (
            self.__class__.__name__,
            self._id,
            self._title,
            fmt,
            lck,)

class mmb(object):
    """
    Class to represent an MMB file
    """
    # The name of the MMB
    filename = None
    # The filehandle of the MMB
    file = None
    # The drive mappings
    drives = [None, None, None, None]
    # The MMB catalogue
    discs = []

    def __init__(self, filename = None):
        """
        Construct mmb object
        """
        self.drives = [0, 1, 2, 3]
        self.discs = [disc(did, self) for did in range(MAXDISCS)]
        if filename != None:
            self.open_file(filename)

    @classmethod
    def create(cls, filename, entries = None, size = None):
        """
        Create an empty MMB container and return it
        """
        if (entries is None and size is None) or (entries is not None and size is not None):
            raise ParameterError("Must specify one of 'entries' or 'size'")
        if size is not None:
            entries = int((size - 8192) / 204800)
        if entries < 1 or entries > MAXDISCS:
            raise ParameterError("Number of entries must be between 1 and 511 inclusive")
        MMB = cls()
        for did in range(entries):
            MMB.discs[did].exists = True
            # MMB.discs[did].formatted = False
        MMB.filename = filename
        MMB.file = open(filename, "w+b", 0)
        MMB.write_catalog()
        for did in range(entries):
            MMB.discs[did].file = None
            MMB.discs[did].ofs = None
            MMB.discs[did].write_to_file(MMB.file, 8192 + (204800 * did))
        MMB.close()
        return cls(filename)

    def open_file(self, filename):
        """
        Open the given file (It must already exist!)
        """
        self.filename = filename
        self.file = open(self.filename, "r+b", 0)  # Open the MMB for updating with no buffer
        self.read_catalog()

    def close(self):
        """
        Close and deactivate this MMB image
        """
        if self.file:
            self.file.close()
        for did in range(MAXDISCS):
            self.discs[did].close()
            self.discs[did] = None
        self.discs = None
        self.drives = [0, 1, 2, 3]
        self.file = None
        self.filename = None

    def find_empty_disc(self):
        """
        Find the first existent, unformatted, disc slot
        """
        for did in range(MAXDISCS):
            if self.discs[did].exists:
                if not self.discs[did].formatted:
                    return self.get_disc(did)
        return dfs.DiscFullException("There are no available disc slots")

    def read_catalog(self):
        """
        The MMB file starts with 16 bytes of settings, followed by 511 * 16byte
        catalog entries.
        """
        self.file.seek(0)
        data = self.file.read(8)
        drv = struct.unpack(">BBBBBBBB", data)
        for i in range(4):
            self.drives[i] = drv[i] + (drv[i + 4] << 8)
        self.file.seek(16)
        data = self.file.read(16 * MAXDISCS)
        for did in range(MAXDISCS):
            info = struct.unpack(">12sxxxB", data[did * 16:(did + 1) * 16])
            self.discs[did].title = info[0]
            self.discs[did].status = info[1]
            self.discs[did].dirty = False
            if self.discs[did].exists:
                self.discs[did].from_mmb(self.file, 8192 + (204800 * did))

    def write_catalog(self):
        """
        Write the catalogue back to the MMB file.
        """
        self.file.seek(0)
        self.file.write(struct.pack("BBBBBBBBQ",
            self.drives[0] & 0xFF,
            self.drives[1] & 0xFF,
            self.drives[2] & 0xFF,
            self.drives[3] & 0xFF,
            (self.drives[0] >> 8) & 1,
            (self.drives[1] >> 8) & 1,
            (self.drives[2] >> 8) & 1,
            (self.drives[3] >> 8) & 1,
            0
        ))
        for did in range(MAXDISCS):
            self.file.write(
                struct.pack(">12sBBBB",
                    self.discs[did].title_padded,
                    0,
                    0,
                    0,
                    self.discs[did].status
                ))
        self.file.flush()

    def get_startup_disc(self, drive):
        """
        Get the disc currently mapped to the given drive
        """
        if drive < 0 or drive > 3:
            raise InvalidDiscException("Drive ID %s is out of range 0 <= ID <= 3" % (drive,))
        return self.drives[drive]

    def set_startup_disc(self, drive, did):
        """
        Map a disc to one of four drives (0 - 3)
        """
        if drive < 0 or drive > 3:
            raise InvalidDiscException("Drive ID %s is out of range 0 <= ID <= 3" % (drive,))
        if did < 0 or did > 510:
            raise InvalidDiscException("Disc ID %s is out of range 0 <= ID <= 510" % (did,))
        self.drives[drive] = did

    def find_disc(self, name):
        """
        Return a DFS object for the (first) disc named "name"
        """
        name = name.upper()
        for disc in self.discs:
            # We use fullname here to allow overrides to manipulate the name
            if disc.formatted and name == disc.fullname.upper():
                return disc
        raise DiscNotFoundException("There is no disc named '%s'" % (name,))

    def get_disc(self, did):
        """
        Return a DFS object for the disc in slot "did"
        """
        if did < 0 or did > 510:
            raise InvalidDiscException("Disc ID %s is out of range 0 <= ID <= 510" % (did,))
        if not self.discs[did].exists:
            raise InvalidDiscException("Disc ID %s does not exist in this MMB" % (did,))
        return self.discs[did]

    def catalog(self, show_unformatted = False):
        """
        Return a listing of all formatted discs, marking locked discs.
        """
        retval = ""
        pos = 0
        for disc in self.discs:
            if disc.exists:
                if disc.formatted:
                    if disc.locked:
                        lck = "L"
                    else:
                        lck = " "
                    retval = retval + "%03d: %-12s %s " % (disc.id, disc.title, lck)
                    pos = pos + 1
                else:
                    if show_unformatted:
                        retval = retval + "%03d: %-14s " % (disc.id, "Unformatted")
                        pos = pos + 1
                if pos == 4:
                    retval = retval + "\n"
                    pos = 0
        return retval

if __name__ == '__main__':
    MMB = mmb('BEEB.MMB')
    #MMB.get_disc(310).locked = True
    #MMB.get_disc(300).write_to("/tmp/utils.ssd")
    #MMB.get_disc(312).read_from("/tmp/utils.ssd")
    #MMB.get_disc(312).title = "MORE_UTILS_2"
    #MMB.get_disc(312).write_catalog()
    #MMB.get_disc(312).locked = False
    #MMB.get_disc(312).unformat()
    #MMB.write_catalog()
    #print print MMB.catalog()
    #print MMB.get_disc(300).catalog()
    #print MMB.get_disc(312).catalog()
    #print MMB.get_disc(300)
    #print MMB.find_disc("X-X-X").catalogue()
    #print MMB.catalog()
    #print MMB.get_disc(300).find_file("$", "COPY").read()
    #print MMB.get_disc(6)
    #MMB.get_disc(6).unformat()
    #print MMB.get_disc(6)
