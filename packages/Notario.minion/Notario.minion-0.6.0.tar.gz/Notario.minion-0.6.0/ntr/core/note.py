# from sarge import shell_format
from subprocess import call
from path import path

import glob
import os
# import sys

"""
!!! TODO: What to do if we try to edit a note
that is not there?
"""


class Note:

    def list(self):
        """
        List should display the name of all Notes.
        !!! TODO: We should return (optionally ?) as a list.
        """
        notes = ''
        os.chdir(self.path)
        for note in glob.glob("*" + self.ext):
            #we are removing the extension.
            notes += "%s\n" % note[:- self.lxt]

        #We remove trailing newline.
        return notes[:-1]

    def open(self, name, editor=None):
        """
        Opens the Note specified by name on the
        given editor.
        """
        if not editor:
            editor = self.editor

        note = self.path + name + self.ext
        note = path(note).abspath()
        call([editor, note])
        # call([editor, shell_format(note)])
        # print shell_format(note)

    def edit(self, name, content):
        """
        Edits a Note, and if it does not exist
        it will make a new note with the content.
        """
        note = self._note(name, True)

        if not content:
            content = ""

        if note.exists() is False:
            note.touch()
        else:
            content = "\n%s" % content

        note.write_text(content, None, 'strict', os.linesep, True)
        #TODO: Handle case not true(?)
        return True

    def new(self, name, content=""):
        return self.edit(name, content)

    def exists(self, name):
        return self._note(name, True).exists()

    #Get should give you an object, File?
    def get(self, name):
        """
        Returns the contents of the name Note.
        """
        if not self.exists(name):
            return None

        note = self._note(name, True)
        lines = note.lines(None, 'strict', False)
        return "\n".join(lines)

    def delete(self, name):
        """
        Deletes a Note.
        """
        if self.exists(name):
            self._note(name, True).remove()

    def _note(self, name, asFile=False):
        self._ensure_dir_exists()

        if asFile:
            return path(self.path + name + self.ext)
        else:
            return self.path + name + self.ext

    def _ensure_dir_exists(self):
        notes = path(self.path)
        if notes.exists() is False:
            notes.makedirs()
        return notes

    def __init__(self, dir, ext, edt, **rst):
        """
        Keyword arguments:
        dir -- path to the target directory.
        ext -- extension for the note files.
        edt -- editor used to open notes.
        rst -- rest of parameters, used so we can expan config
        """

        #We should prob do real sanity check ;)
        if not dir.endswith('/'):
            dir += '/'

        self.path = dir

        self._ensure_dir_exists()

        self.editor = edt
        self.ext = ext
        self.lxt = ext.__len__()
