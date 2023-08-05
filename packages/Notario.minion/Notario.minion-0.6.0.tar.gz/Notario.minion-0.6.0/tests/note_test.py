import unittest
import os
import shutil

#parentdir = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(file_dir)
lib_dir = parent_dir + '/lib'
#print parentdir
os.sys.path.append(lib_dir)

from note import Note


class NoteTest(unittest.TestCase):

    def setUp(self):
        self.path = file_dir + '/tmp'
        self.ext = '.txt'
        self.editor = 'subl'
        self.note = Note(self.path, self.ext, self.editor)

    def tearDown(self):
        #if os.path.isdir(self.path): If its not there, something went wrong!
        shutil.rmtree(self.path)
        self.note = None

    def test_empty_list(self):
        """
        New Note, we don't have entries.
        """
        self.failIf(self.note.list())

    def test_new(self):
        """
        Create a new Note.
        """
        self.failUnless(self.note.new("TestNote", "LoremIpsumNote"))

    def test_edit(self):
        self.note.edit("TestNote", "LoremIpsumNote")
        self.note.edit("TestNote", "MoreLoreMore")

    def test_list(self):
        self.failIf(self.note.list())
        self.note.new("TestNote", "LoremIpsumNote")
        self.failUnless(self.note.list() == "TestNote")

    def test_exists(self):
        self.note.list()
        self.note.new("TestNote", "LoremIpsumNote")
        self.failUnless(self.note.exists("TestNote"))
        self.failIf(self.note.exists("DoesNotExist"))

    def test_get_existing(self):
        self.note.new("TestNote", "LoremIpsumNote")
        self.failUnless(self.note.get("TestNote") == "LoremIpsumNote")

    def test_get_non_existing(self):
        self.failIf(self.note.get("NoneNote"))

    def test_delete(self):
        self.note.new("TestNote", "LoremIpsumNote")
        self.failUnless(self.note.exists("TestNote"))
        self.note.delete("TestNote")
        self.failIf(self.note.exists("TestNote"))
        #It should not crap out if the note does not exist.
        self.note.delete("TestNote")


    # def test_edit(self):
    #   pass

    # def test_open(self):
    #   pass

    # def test_show(self):
    #   pass

    # def test_delete(self):
    #   pass

    # def test_copy(self):
    #   pass


def main():
    unittest.main()

if __name__ == '__main__':
    main()
