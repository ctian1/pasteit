#!/usr/bin/python3.4
import glob
import os
import random
import string
import re
import hashlib

class PastesRepo:
    """ A repository for all the registerted pastes """

    def __init__(self):
        self.pastes = {} # Create the pastes' dict
        self.scan() # Scan for available pastes

    def scan(self):
        """ Scan for available pastes """
        pastes = glob.glob('pastes/'+'?'*10) # Find all pastes files
        # Create a representation for each paste
        for paste in pastes:
            self.pastes[paste[-10:]] = Paste(paste)

    def create(self, author, content, password):
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
        paste = Paste()
        paste.id = id
        paste.author = author
        paste.content = content
        if password:
            paste.password = hashlib.sha1(password.encode('utf-8')).hexdigest() # Hash with sha1
        else:
            paste.password = False
        paste.save()
        self.pastes[id] = paste
        return id

    def exists(self, id):
        """ Check if a paste exists """
        return os.path.exists('pastes/'+id)

    def get(self, id):
        """ Get a paste by id """
        return self.pastes[id]

    def __repr__(self):
        return '<Pastes repository>'

class Paste:
    """ Paste representation """

    def __init__(self, filename=None):
        self.loaded = False
        # If a file is provided, load the paste from it
        if filename:
            self.loadFromFile(filename)
        else:
            self.id = None
            self.author = None
            self.content = None
            self.password = None
        self.loaded = True

    def loadFromFile(self, filename):
        """ Load the paste from a file """
        if not self.loaded:
            if os.path.exists(filename):
                # Read the file content
                with open(filename, 'r') as f:
                    raw = f.read()
                headers, content = raw.split('\n', 1) # Split headers and content
                flags = headers.split('|')
                # Pastes files alwayls starts with pastes
                if flags[0] != 'pastes':
                    raise RuntimeError('Invalid pastes file: '+filename)
                # Load file
                self.id = filename[-10:]
                self.author = flags[1]
                self.content = content
                if flags[2] == '!':
                    self.password = False
                else:
                    self.password = flags[2]
            else:
                raise FileNotFoundError('Paste not found: '+filename)
        else:
            raise RuntimeError('Paste already loaded')

    def save(self):
        """ Save the paste """
        raw = 'pastes|'+self.author+'|'+(self.password if self.password else '!')+'\n'+self.content
        with open('pastes/'+self.id, 'w') as f:
            f.write(raw)

    def delete(self):
        """ Delete the paste """
        os.remove('pastes/'+self.id)

    def __str__(self):
        return self.content

    def __repr__(self):
        return '<Paste \''+self.id+'\'>'
