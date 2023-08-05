from cement.core import controller
import os
from ntr import VERSION
from ntr.core.note import Note

BANNER = """
=====================================
  _   _       _             _
 | \ | | ___ | |_ __ _ _ __(_) ___
 |  \| |/ _ \| __/ _` | '__| |/ _ \.
 | |\  | (_) | || (_| | |  | | (_) |
 |_| \_|\___/ \__\__,_|_|  |_|\___/

============ (c) 2012 goliatone =====
v%s
-------------------------------------
 """ % VERSION


class NotarioBaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = 'Notario, a simple command line utility to manage notes.'

        config_defaults = dict(
            note='Note',
            e='subl',
            debug=True
        )
        arguments = [
            (['-n', '--note'], dict(action='store',
                                    help="The note's name.")),
            (['-c', '--content'], dict(action='store',
                                        help='Create a new note.')),
            (['-cp', '--copy'], dict(action='store_true',
                                    help='Copy note to clipboard')),
            (['-pt', '--paste'], dict(action='store_true',
                                    help='Copy note from clipboard')),
            (['-e'], dict(action='store_const', const='subl',
                                    help='Opens Note in users default editor.')),
            (['-editor'], dict(action='store',
                                    help='Opens Note in given editor.')),
            (['-v', '--version'], dict(action='version', version=BANNER))
        ]

    def _setup(self, base_app):
        super(NotarioBaseController, self)._setup(base_app)

        # expand config so we can send it to the note.
        options = dict(self.config.items('notario'))

        # TODO: We want to use $EDITOR, how to get that value?
        self.note = Note(**options)

    @controller.expose(hide=True, aliases=['run'])
    def default(self):
        #short
        args = self.pargs

        # default action
        action = 'list'

        # we are just unboxing all the args
        (namespace, n, c, cp, pt, e, editor, p) = vars(args)
        c = 'empty' if not c else c
        # self.log.info('Content: ' + c)

        # Let's figure out the action based on the
        # arguments we got:
        if args.note:
            if not self._exists():
                action = 'new'
            else:
                action = 'show'

            if args.content:
                action = 'edit'

        # we want the content of the note in the
        # clipboard
        if args.copy:
            self.copy()

        # we have the actual content of the note
        # in the clipboard. Get it!
        if args.paste:
            args.content = self._get_clip()
            action = 'edit'

        if args.editor:
            self.editor = args.editor
        else:
            self.editor = None

        # self.log.info("We are executing action: " + action)

        # dinamically access the required method:
        action = getattr(self, action)
        action()

        # do we want to edit our note?
        if(args.e or args.editor):
            self.note.open(args.note, self.editor)

        # Send a simple growl message with mostly default values
        #gntp.notifier.mini("Here's a quick message", callback="http://github.com/")
        #self.log.info("Received option foo with value '%s'"% o)

    @controller.expose(aliases=['ls'], help="List all the notes.")
    def list(self):
        o = self.note.list()

        if not o:
            print "No notes found."
        else:
            #print "Listing all Notes:"
            print o

    @controller.expose(help="Shows the Note with the given name.")
    def show(self):
        note = self.note.get(self.pargs.note)

        if not note:
            print "The note %s is empty." % self.pargs.note
        else:
            print note

    @controller.expose(help="Opens the Note in a new editor window.")
    def open(self, editor="subl"):
        note = self.pargs.note
        self.note.open(note)

    @controller.expose(help="Create a new Note.")
    def new(self):
        name = self.pargs.note
        content = self.pargs.content
        # We create a new file for the note.
        self._save(content, name)

        # if we created a new note, but did
        # not provide content, we assume we
        # want to create + edit in IDE
        if not content:
            self.open()

    @controller.expose(help="Add content to a note. Optionally opens editor.")
    def edit(self):
        name = self.pargs.note
        content = "%s" % self.pargs.content
        self._save(content, name)

    @controller.expose(help="Delete Note.")
    def delete(self):
        name = self.pargs.note
        self.note.delete(name)

        print "Note %s deleted." % name

    @controller.expose(aliases=['cp'], help="Puts the content of a note into the clipboard.")
    def copy(self):
        """
        Puts the content of a note into the clipboard.
        """
        note = self.pargs.note
        content = self.note.get(note)
        self._set_clip(content)

    @controller.expose(help="Use the clipboard's content.")
    def clip(self):
        name = self.pargs.note
        content = self._get_clip()
        self._save(content, name)

    @controller.expose(hide=True)
    def _save(self, content, name):
        """
        After we edit a note, we put it's content
        in the clipboard
        """
        if self.note.edit(name, content):
            if content:
                self._set_clip(content)

    @controller.expose(hide=True)
    def _get_clip(self):
        outf = os.popen('pbpaste', 'r')
        content = outf.read()
        outf.close()
        return content

    @controller.expose(hide=True)
    def _set_clip(self, content):
        outf = os.popen('pbpaste', 'w')
        outf.write(content)
        outf.close()

    @controller.expose(hide=True)
    def _exists(self):
        return self.note.exists(self.pargs.note)
