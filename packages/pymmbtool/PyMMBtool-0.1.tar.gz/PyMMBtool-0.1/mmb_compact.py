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

import PyMMB
import sys
import math

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Syntax: %s <BEEB.MMB> (<disc_name> | <disc_id>)" % sys.argv[0]
        sys.exit()
    MMB = PyMMB.mmb.mmb(sys.argv[1])
    try:
        DFS = MMB.get_disc(int(sys.argv[2]))
    except:
        DFS = MMB.find_disc(sys.argv[2])
    DFS.compact()
    end = 2
    for dfsfile in DFS.files:
        this_end = dfsfile.start_sector + math.ceil(dfsfile.length / 256)
        if this_end > end:
            end = this_end
    print "This disc has %s bytes free" % ((DFS.sectors - end) * 256)
