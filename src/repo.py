#!/usr/bin/python3.4
import glob
import os
import random
import string
import re
import hashlib
import time
import pygments.lexers
import tools
from threading import Timer
from db import DB

db = DB()

schema = "id text PRIMARY KEY, content text, author text, language text, password text, temporary boolean, created text"

class PastesRepo:
    """ A repository for all the registered pastes """

    def __init__(self):
        db.add_table('pastes', db.tables['pastes'][1])
        
        self.pastes = {} # Create the pastes' dict
        self.scan() # Scan for available pastes

    def scan(self):
        """ Scan for available pastes """
        pastes = db.get_all_data('pastes') # Find all pastes rows
        # Create a representation for each paste
        for paste in pastes:
            self.pastes[paste[0]] = Paste(self, paste[0]) #TODO: NOTE: THIS IS WHAT Paste() SHOULD ACCEPT

    def create(self, content, password, author, language, temporary=False):
        """ Create a new paste """
        # Generate the paste identifier
        pattern = string.ascii_lowercase+string.ascii_uppercase+string.digits # Alphanumeric pattern
        while 1:
            id = ''.join( random.sample(pattern, 10) ) # Generate the id
            # If the id does not exist yet break the while
            if not self.exists(id):
                break
        # Validate author
        if not re.match(r"^([A-Za-z0-9 \.'àèéìòùÀÈÉÌÒÙ]+)$", author):
            raise ValueError('Invalid author')
        # Create the paste
        paste = Paste(self)
        paste.id = id
        paste.author = author
        paste.content = content
        paste.language = language
        paste.temporary = temporary
        if paste.temporary:
            paste.timer = Timer(10800, lambda p: print(str(p.delete()) + " delete"), [paste])
            paste.timer.start()
            print("Created paste '{0}' with a timer.".format(paste.id))
        if password:
            paste.password = hashlib.sha1(password.encode('utf-8')).hexdigest() # Hash with sha1
        else:
            paste.password = ""
        paste.save()
        self.pastes[id] = paste
        return id

    def exists(self, id):
        """ Check if a paste exists """
        if db.get_data('pastes', 'id', id):
            return True
        else:
            return False

    def get(self, id):
        """ Get a paste by id """
        return self.pastes[id]

    def __repr__(self):
        return '<Pastes repository>'

class Paste:
    """ Paste representation """

    def __init__(self, repo, id=None):
        self.loaded = False
        self.repo = repo
        # If an id is provided, load the paste from it
        if id:
            self.load(id)
        else:
            self.id = None
            self.author = ""
            self.content = None
            self.password = None
            self.language = None
            self.temporary = False
            self.created = time.strftime("%m/%d/%y at %H:%M:%S")
        self.loaded = True

    def load(self, id):
        """ Load the paste from the DB """
        if not self.loaded:
            if db.check_table('pastes'):
                # Read the file content
                data = db.get_data('pastes', 'id', id)[0]
                if not data:
                    raise FileNotFoundError('Paste not found: '+id)
                else:
                    self.id = data[0]
                    self.content = data[1]
                    self.author = data[2]
                    self.language = data[3]
                    self.password = data[4]
                    self.temporary = data[5]
                    self.created = data[6]
                    
                    if self.temporary:
                        if time.mktime(time.localtime()) - 10800 > self.createdAt(formatted=False):
                            print("Cleaned up paste '{0}'.".format(self.id))
                            self.delete()
                        else:
                            self.timer = Timer(10800, lambda p: print(str(p.delete()) + " delete"), [self])
                            self.timer.start()
                            print("Loaded paste '{0}' with a timer.".format(self.id))
                    else:
                        print("Loaded paste '{0}'.".format(self.id))
            else:
                raise FileNotFoundError('Paste not found: '+id)
        else:
            raise RuntimeError('Paste already loaded')

    def save(self):
        """ Save the paste """
        data = {'id': self.id,
            'content': self.content,
            'author': self.author,
            'language': self.language,
            'password': self.password,
            'temporary': self.temporary,
            'created': self.created}
        
        if db.get_data('pastes', 'id', self.id):
            db.delete_data('pastes', 'id', self.id)
        db.add_data('pastes', data)

    def delete(self):
        """ Delete the paste """
        print("Deleting paste '{0}'.".format(self.id))
        if self.id in self.repo.pastes:
            self.repo.pastes.pop(self.id)
        db.delete_data('pastes', 'id', self.id)

    def createdAt(self, formatted=True):
        """ Get the creation date """
        if formatted:
            if self.temporary == True:
                n = "T"
            else:
                n = "P"
            return self.created + " <b>[" + n + "]</b>"
        else:
            return time.mktime(time.strptime(self.created, "%m/%d/%y at %H:%M:%S"))

    def formattedContent(self):
        """ Return the formatted paste content """
        # Detect which lexer use
        if self.language == "guess":
            try:
                lexer = pygments.lexers.guess_lexer(self.content)
            except Exception:
                lexer = pygments.lexers.get_lexer_by_name("text")
        else:
            lexer = pygments.lexers.get_lexer_by_name(self.language)
        # Return the formatted output
        return tools.highlight(self.content, lexer)

    def __str__(self):
        return self.formattedContent()

    def __repr__(self):
        return '<Paste \''+self.id+'\'>'
