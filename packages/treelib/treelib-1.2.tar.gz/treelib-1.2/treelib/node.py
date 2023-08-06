# treelib - Simple to use for you.
# Python 2/3 Tree Implementation
#
# Copyright (C) 2011    Brett Alistair Kromkamp - brettkromkamp@gmail.com
# Copyright (C) 2012,2013   Xiaming Chen - chenxm35@gmail.com
# Copyright (C) 2013    Holger Bast - holgerbast@gmx.de
# All rights reserved.
#
# This file is part of project treelib.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Neither the name of the copyright holder nor the names of the contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import unittest
import uuid

def sanitize_id(id):
	return id.strip().replace(" ", "_")

# Module constants
(_ADD, _DELETE, _INSERT) = range(3)

class Node(object):
	"""Class for basic node functionality."""

	def __init__(self, name, identifier=None, expanded=True):
		self.__identifier = (str(uuid.uuid1()) if identifier is None else
				sanitize_id(str(identifier)))
		self.name = name
		self.expanded = expanded
		self.__bpointer = None		# identifier
		self.__fpointer = []		# identifier

	@property
	def identifier(self):
		return self.__identifier

	@property
	def bpointer(self):
		return self.__bpointer

	@bpointer.setter
	def bpointer(self, value):
		if value is not None:
			self.__bpointer = sanitize_id(value)

	@property
	def fpointer(self):
		return self.__fpointer

	@fpointer.setter
	def fpointer(self, value):
		if value is not None and isinstance(value, list):
			self.__fpointer = value

	def update_fpointer(self, identifier, mode=_ADD):
		if mode is _ADD:
			self.__fpointer.append(sanitize_id(identifier))
		elif mode is _DELETE:
			self.__fpointer.remove(sanitize_id(identifier))
		elif mode is _INSERT:
			self.__fpointer = [sanitize_id(identifier)]

#--------------------------------------------------------------------------------

# Test suite

class TestNode(unittest.TestCase):
	def setUp(self):
		self.node1 = Node("Test One", "ide ntifier 1 ")

	def test_initialization(self):
		self.assertEqual(self.node1.name, "Test One")
		self.assertEqual(self.node1.identifier, "ide_ntifier_1")
		self.assertEqual(self.node1.expanded, True)

	def test_set_fpointer(self):
		self.node1.update_fpointer(" identi fier 2")
		self.assertEqual(self.node1.fpointer, ['identi_fier_2'])

	def test_set_bpointer(self):
		self.node1.bpointer = " identi fier  1"
		self.assertEqual(self.node1.bpointer, 'identi_fier__1')
		
	def test_set_data(self):
		self.node1.data = {1:'hello', "two":'world'}
		self.assertEqual(self.node1.data, {1:'hello', "two":'world'})

	def tearDown(self):
		pass

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
	unittest.main()
