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
import bcd
import math
import StringIO

version = 0.1

def str7bit(s):
    return "".join([chr(ord(c) & 127) for c in s])

class FileLockedException(Exception):
    pass

class FileNotFoundException(Exception):
    pass

class DiscFullException(Exception):
    pass

class dfs_file(object):
    """
    Class to represent a DFS file
    """
    _dfs = None
    _dir = ""
    _name = ""
    _load_addr = 0
    _exec_addr = 0
    _length = 0
    _start_sector = 0
    _locked = False

    def __init__(
        self,
        dfs,
        directory = "\0",
        name = "",
        load_addr = 0,
        exec_addr = 0,
        length = 0,
        start_sector = 0,
        locked = False):
        """
        Initialise the file entry with passed (or sensible default) values
        """
        self._dfs = dfs
        self._dir = directory
        self._name = name
        self._load_addr = load_addr
        self._exec_addr = exec_addr
        self._length = length
        self._start_sector = start_sector
        self._locked = locked

    def parse(self, data1, data2):
        """
        Given two 8 byte blocks from the catalogue on disc, populate the
        file parameters
        """
        info1 = struct.unpack("<7sc", data1)
        info2 = struct.unpack("<HHHBB", data2)
        self._dir = chr(ord(info1[1]) & 127)
        self._name = str7bit(info1[0].strip())
        self._load_addr = info2[0] + (((info2[3] >> 2) & 3) << 16)
        self._exec_addr = info2[1] + (((info2[3] >> 6) & 3) << 16)
        self._length = info2[2] + (((info2[3] >> 4) & 3) << 16)
        self._start_sector = info2[4] + ((info2[3] & 3) << 8)
        self._locked = (ord(info1[1]) & 128) == 128

    def unparse(self):
        """
        Construct two 8 byte blocks from the file parameters to be written
        to disc
        """
        if len(self._name) > 0:
            fd1 = str7bit(self.name_padded)
            if self._locked:
                fd1 = fd1 + chr((ord(self._dir) & 127) + 128)
            else:
                fd1 = fd1 + chr(ord(self._dir) & 127)
            fd2 = struct.pack("<HHHBB",
                self._load_addr & 0xFFFF,
                self._exec_addr & 0xFFFF,
                self._length & 0xFFFF,
                (((self._load_addr >> 16) & 3) << 2) +
                (((self._length >> 16) & 3) << 4) +
                (((self._exec_addr >> 16) & 3) << 6) +
                ((self._start_sector >> 8) & 3),
                self._start_sector & 0xFF
            )
        else:
            fd1 = struct.pack("<Q", 0)
            fd2 = struct.pack("<Q", 0)
        return [fd1, fd2]

    @property
    def dir(self):
        """
        Return the directory this file is in
        """
        return self._dir

    @dir.setter
    def dir(self, directory):
        """
        Set the directory this file is in
        """
        self._dir = directory

    @property
    def fullname(self):
        """
        Return <dir>.<name>
        """
        return "%s.%s" % (self._dir, self._name,)

    @property
    def name(self):
        """
        Return the name of this file
        """
        return self._name

    @property
    def name_padded(self):
        """
        Return the name of this file padded out to 7 characters with spaces
        """
        return (self._name + "        ")[:7]

    @name.setter
    def name(self, name):
        """
        Set the name of this file. The string is trimmed of trailing spaces and nulls
        """
        while len(name) > 0 and (name[-1] == "\0" or name[-1] == " "):
            name = name[:-1]
        self._name = name

    @property
    def load_addr(self):
        """
        Return the load address of this file
        """
        return self._load_addr

    @load_addr.setter
    def load_addr(self, load_addr):
        """
        Set the load address of this file
        """
        self._load_addr = load_addr

    @property
    def exec_addr(self):
        """
        Return the execution address of this file
        """
        return self._exec_addr

    @exec_addr.setter
    def exec_addr(self, exec_addr):
        """
        Set the execution address of this file
        """
        self._exec_addr = exec_addr

    @property
    def length(self):
        """
        Return the length of the file data
        """
        return self._length

    @length.setter
    def length(self, length):
        """
        Set the length of the file data
        """
        # TODO: Must resize file here, including moving data if there isn't room where it is
        self._length = length

    @property
    def start_sector(self):
        """
        Return the start sector of this file
        """
        return self._start_sector

    @start_sector.setter
    def start_sector(self, start_sector):
        """
        Set the start sector of this file
        """
        # TODO: Must move the file data here, first verifying there is room
        self._start_sector = start_sector

    @property
    def locked(self):
        """
        Return the locked flag of this file
        """
        return self._locked

    @locked.setter
    def locked(self, locked):
        """
        Set the start sector of this file
        """
        self._locked = locked

    def read(self):
        """
        Given a filedata structure, read the contents of the file (It's ok,
        they are all tiny by modern standards!)
        """
        self._dfs.file.seek(self._dfs.ofs + (self._start_sector * 256))
        return self._dfs.file.read(self._length)

    def __repr__(self):
        """
        Return a nice representation of this object
        """
        if self._locked:
            lck = "R/O"
        else:
            lck = "R/W"
        return "<%s %s.%s Load: &%06x Exec: &%06x Length: %d Sector: &%04x %s>" % (
            self.__class__.__name__,
            self._dir, self._name,
            self._load_addr,
            self._exec_addr,
            self._length,
            self._start_sector,
            lck)

class dfs(object):
    """
    Class to represent a DFS disc
    """
    OPTS = [
        'NONE',
        'LOAD',
        'RUN',
        'EXEC',
    ]
    filename = None
    file = None
    _title = ""
    cycle = 0
    opt = 0
    ofs = 0
    fileCount = 0
    sectors = 800
    _files = []

    def __init__(self, filename = None, tracks = 80):
        """
        Construct dfs object
        """
        self._files = [dfs_file(self) for i in range(31)]
        if filename != None:
            self.open_file(filename)
        elif tracks == 40 or tracks == 80:
            self.sectors = tracks * 10
        else:
            raise Exception("Invalid track count %s, should be 40 or 80" % tracks)

    def __del__(self):
        """
        Finalize this object (Just a sugary cleanup)
        """
        self.close();

    @classmethod
    def new(cls, filename, title = "NONAME", tracks = 80):
        """
        Create a new DFS disc, with an empty catalog, then re-open it
        """
        obj = cls(tracks = tracks)
        obj.title = title
        obj.write_to(filename)
        return cls(filename)

    def close(self):
        """
        Close this disc, including the file (if we opened it) and blow away
        all data to break any references
        """
        if self.ofs == 0 and self.file != None:
            self.file.close()
        self.filename = None
        self.file = None
        self._title = ""
        self.cycle = None
        self.opt = None
        self.ofs = None
        self.fileCount = None
        self.sectors = None
        if self._files:
            for item in self._files:
                item._dfs = None
        self._files = None

    @property
    def files(self):
        """
        Return only file entries for files which exist
        """
        return self._files[:self.fileCount]

    @property
    def title(self):
        """
        Return the trimmed title suitable for matching and displaying
        """
        return self._title

    @property
    def fullname(self):
        """
        For compatibility with dfs.dfs_file, return the disc title
        """
        return self.title

    @property
    def title_padded(self):
        """
        Return the padded title suitable from writing to disc
        """
        return (self._title + "             ")[:12]

    @title.setter
    def title(self, title):
        """
        Set the title. The string is trimmed of trailing spaces and nulls
        """
        while len(title) > 0 and (title[-1] == "\0" or title[-1] == " "):
            title = title[:-1]
        self._title = title

    def open_file(self, filename):
        """
        Open the given file (It must already exist!)
        """
        self.ofs = 0
        self.filename = filename
        self.file = open(filename, "r+b", 0)  # Open the disc for updating with no buffer
        self.read_catalog()

    def write_to(self, filename):
        """
        Open a new file (or overwrite an existing one) and copy the entire disc.
        """
        _file = open(filename, "w+b")
        self.write_to_file(_file, 0)
        _file.close()

    def write_to_file(self, _file, ofs):
        """
        Given an existing file, and an offset, copy the entire disc.
        """
        # Now copy self.sectors - 2 of data, or write empty disc with zeros
        _file.seek(ofs)
        if self.file is not None:
            self.file.seek(self.ofs)
            for sect in range(0, self.sectors):
                _file.write(self.file.read(256))
        else:
            sector = "\0" * 256
            for sect in range(0, self.sectors):
                _file.write(sector)
            _file.seek(ofs)
            # Do catalog sector 0
            t = str(self.title_padded)
            _file.write(t[:8])
            # Do catalog sector 1
            _file.seek(ofs + 256)
            cycle = bcd.toBCD(self.cycle)
            count = self.fileCount << 3
            opt = ((self.opt & 3) << 4) + ((self.sectors >> 8) & 3)
            _file.write(struct.pack("<4sBBBB", t[8:12], cycle, count, opt, self.sectors & 255))

    def read_catalog(self):
        """
        The DFS catalog starts with 16 bytes of volume data (8 bytes in each
        of the first two 256 byte sectors). Then there are 31 catalog entries
        in a standard DFS catalog which we number from 0 to 30 (incl).
        """
        self.file.seek(self.ofs)
        data = self.file.read(512)
        info1 = struct.unpack("<8s", data[0:8])
        info2 = struct.unpack("<4sBBBB", data[256:264])
        self.title = str7bit(info1[0] + info2[0])
        self.cycle = bcd.fromBCD(info2[1])
        self.fileCount = info2[2] / 8
        self.opt = (info2[3] >> 4) & 3
        self.sectors = info2[4] + ((info2[3] & 3) << 8)
        for fid in range(0, 31):
            ofs1 = (fid + 1) * 8
            ofs2 = 256 + ((fid + 1) * 8)
            self._files[fid].parse(data[ofs1:ofs1 + 8], data[ofs2:ofs2 + 8])

    def write_catalog(self):
        """
        Write the volume data then a catalogue (2 sectors) to the specified
        position in the file
        """
        self.file.seek(self.ofs)
        # Do catalog sector 0
        t = self.title_padded
        self.file.write(t[:8])
        # Do catalog sector 1
        self.file.seek(self.ofs + 256)
        self.cycle = self.cycle + 1
        cycle = bcd.toBCD(self.cycle)
        count = self.fileCount << 3
        opt = ((self.opt & 3) << 4) + ((self.sectors >> 8) & 3)
        self.file.write(struct.pack("<4sBBBB", t[8:12], cycle, count, opt, self.sectors & 255))
        # Now write out the file entries
        fid = 0
        for file_entry in self._files:
            data1, data2 = file_entry.unparse()
            ofs1 = (fid + 1) * 8
            ofs2 = 256 + ((fid + 1) * 8)
            self.file.seek(self.ofs + ofs1)
            self.file.write(data1)
            self.file.seek(self.ofs + ofs2)
            self.file.write(data2)
            fid = fid + 1
        self.file.flush()

    def catalog(self):
        """
        Return a standard (looking) BBC DFS catalog (*CAT)
        """

        def prt_file(file_entry):
            if file_entry.locked:
                lck = "L"
            else:
                lck = " "
            if file_entry.dir == '$':
                _dir = "  "
            else:
                _dir = file_entry.dir + "."
            return "  %2s%-8s %1s      " % (_dir, file_entry.name, lck,)

        def catalog_sort(a, b):
            if a.name[0] == '!' and b.name[0] != '!':
                return -1
            elif b.name[0] == '!' and a.name[0] != '!':
                return 1
            return cmp(a.name.upper(), b.name.upper())

        dirs = {}
        for file_entry in self._files[0:self.fileCount]:
            if not dirs.has_key(file_entry.dir):
                dirs[file_entry.dir] = []
            dirs[file_entry.dir].append(file_entry)
        retval = "%s (%d)\nFiles %-2d            Option %d (%s)\nSects. %-10d   Dir. :0.$\n\n" % (
            self.title,
            self.cycle,
            self.fileCount,
            self.opt,
            self.OPTS[self.opt],
            self.sectors,
        )
        even = False
        if dirs.has_key('$'):
            dollar = dirs['$']
            del dirs['$']
            dollar.sort(catalog_sort)
            for file_entry in dollar:
                retval = retval + prt_file(file_entry)
                even = not even
                if not even:
                    retval = retval + "\n"
            if even:
                retval = retval + "\n"
            retval = retval + "\n"
        keys = dirs.keys()
        keys.sort()
        even = False
        for _dir in keys:
            dirs[_dir].sort(catalog_sort)
            for file_entry in dirs[_dir]:
                retval = retval + prt_file(file_entry)
                even = not even
                if not even:
                    retval = retval + "\n"
        if even:
            retval = retval + "\n"
        return retval

    def info(self, directory = None, filename = None):
        """
        Print detailed info on given file or all files
        """
        retstr = "%-9s %-6s  %-6s  %-6s  %s\n" % ("Name", "Load", "Exec", "Len", "Sect")
        for file_entry in self._files[0:self.fileCount]:
            if directory != None and filename != None and (file_entry.dir.upper() != directory.upper() or file_entry.name.upper() != filename.upper()):
                continue
            retstr = retstr + "%s.%-7s &%06x &%06x &%06x %d\n" % (
                file_entry.dir,
                file_entry.name,
                file_entry.load_addr,
                file_entry.exec_addr,
                file_entry.length,
                file_entry.start_sector,
            )
        return retstr

    def find_file(self, directory, filename):
        """
        Find a file matching the directory and filename. Return the filedata structure
        """
        for file_entry in self.files:
            if file_entry.dir.upper() == directory.upper() and file_entry.name.upper() == filename.upper():
                return file_entry
        raise FileNotFoundException("File Not Found: %s.%s", (directory, filename))

    def create_file(self, directory, filename, data, load_addr = 0, exec_addr = 0):
        """
        Create/overwrite a the file <directory>.<filename> with <data>
        """
        new_file = False
        try:
            file_entry = self.find_file(directory, filename)
            if file_entry.locked:
                raise FileLockedException("File '%s.%s' is locked against modification" % (directory, filename))
        except FileNotFoundException:
            if self.fileCount == 31:
                raise DiscFullException("No catalog entries available to add new file")
            file_entry = self._files[self.fileCount]
            file_entry.dir = directory
            file_entry.name = filename
            file_entry.load_addr = load_addr
            file_entry.exec_addr = exec_addr
            file_entry.start_sector = 0
            file_entry.length = -1
            file_entry.locked = False
            new_file = True
        # Add the file etc
        if new_file:
            self.fileCount = self.fileCount + 1
        # Is the current file big enough?
        if file_entry.length < len(data):
            # No, ok let's find the end of the data on the disc
            if self.fileCount == 0:
                # Empty disc - Start at sector 2
                end = 2
            elif not new_file and self._files[0] == file_entry:
                # Overwrite existing file at end of disc
                end = file_entry.start_sector
            else:
                # Move file to end of disc
                end = 2
                for tmp in self.files:
                    tmp_end = tmp.start_sector + math.ceil(tmp.length / 256)
                    if tmp_end > end:
                        end = tmp_end
            if ((self.sectors - end) * 256) < len(data):
                raise DiscFullException("Not enough space to write file of length %d" % (len(data,)))
            file_entry.start_sector = int(end)
        file_entry.length = len(data)
        # Sort the catalogue by start sector descending
        self._files.sort(lambda a, b: cmp(b.start_sector, a.start_sector))
        # Seek and write the file data
        self.file.seek(self.ofs + (file_entry.start_sector * 256))
        self.file.write(data)
        # Finally, flush the change out to the image file
        self.write_catalog()

    def delete_file(self, directory, filename):
        """
        Delete a file from disc
        """
        file_entry = self.find_file(directory, filename)
        if file_entry.locked:
            raise FileLockedException("File '%s.%s' is locked against modification" % (directory, filename))
        # Forget about the file
        file_entry.load_addr = 0
        file_entry.exec_addr = 0
        file_entry.length = 0
        file_entry.start_sector = 0
        self.fileCount = self.fileCount - 1
        # Sort the catalogue by start sector descending
        self._files.sort(lambda a, b: cmp(b.start_sector, a.start_sector))
        # Finally, flush the change out to the image file
        self.write_catalog()

    def compact(self):
        """
        Compact this disc, re-ordering file entries and moving free space to the end.
        Open new temporary file as disc.
        Repeat:
          Read file from this disc.
          Write file to temp disc.
        Copy data from temp disc to this disc
        """
        def sortfiles(a, b):
            d = cmp(a.dir.upper(), b.dir.upper())
            n = cmp(a.name.upper(), b.name.upper())
            if (d != 0):
                if (a.dir == "$"):
                    print "%s $ first" % (a.fullname)
                    return -1
                elif (b.dir == "$"):
                    print "%s $ first" % (b.fullname)
                    return 1
                print "Different dirs"
                return d
            elif (n != 0):
                if (a.name[1].upper() == b.name[1].upper()):
                    return n
                elif (a.name[0] == "!"):
                    print "%s ! first" % (a.fullname)
                    return -1
                elif (b.name[0] == "!"):
                    print "%s ! first" % (b.fullname)
                    return 1
                return n
            print "All the same"
            return 0
        tmpfile = StringIO.StringIO()
        tmpfile.seek(self.sectors * 256)
        tmpdisc = dfs()
        tmpdisc.file = tmpfile
        tmpdisc.ofs = 0
        tmpdisc.write_catalog()
        tmpdisc.read_catalog()
        tmpdisc.cycle = self.cycle
        print tmpdisc.catalog()
        files = self.files[:]
        files.sort(sortfiles)
        for dfsfile in files:
            tmpdisc.create_file(dfsfile.dir, dfsfile.name, dfsfile.read(), dfsfile.load_addr, dfsfile.exec_addr)
        tmpdisc.write_to_file(self.file, self.ofs)
        self.read_catalog()

if __name__ == '__main__':
    DFS = dfs('/tmp/DISC.SSD')
    #DFS.write_to('/tmp/DISC2.SSD')
    #DFS = dfs('/tmp/DISC2.SSD')
    #print DFS.info()
    #DFS.compact()
    print DFS.info()
    #print DFS.find_file("$", "!BooT").read()
    #DFS = dfs()
    #DFS.opt = 3
    #DFS.title = "FRED"
    #DFS.cycle = 7
    #DFS.write_to("/tmp/empty.ssd")
    #print DFS.catalog()
