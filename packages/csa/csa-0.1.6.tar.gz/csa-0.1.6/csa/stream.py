#
#  This file is part of the Connection-Set Algebra (CSA).
#  Copyright (C) 2010,2011 Mikael Djurfeldt
#
#  CSA is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  CSA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class Stream:
    def __init__ (self, c):
        self.g = c.__iter__ ()
        self.next ()

    def __eq__ (self, other):
        return (self.j, self.i) == other.head ()

    def __lt__ (self, other):
        return (self.j, self.i) < (other.j, other.i)

    def empty (self):
        return not self.g

    def head (self):
        return self.i, self.j

    def next (self):
        try:
            self.e = self.g.next ()
            self.i = self.e[0]
            self.j = self.e[1]
        except StopIteration:
            self.g = False
