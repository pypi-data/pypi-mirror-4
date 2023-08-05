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

def fromBCD(bcd):
    """
    Convert a BCD byte to a decimal integer
    """
    return ((bcd >> 4) * 10) + (bcd & 15)

def toBCD(decimal):
    """
    Convert a decimal integer to a BCD byte
    """
    return (int(decimal / 10) << 4) + (decimal % 10)

if __name__ == '__main__':
    for integer in [1, 10, 15, 25, 28, 50, 99]:
        bcd = toBCD(integer)
        decimal = fromBCD(bcd)
        print "%d = BCD[%d] or BCD[0x%x] which converts back to %d" % (integer, bcd, bcd, decimal)
        if integer != decimal:
            raise Exception("Conversion error!")
