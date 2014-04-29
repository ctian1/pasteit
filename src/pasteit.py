#!/usr/bin/python3.4
# Pastes, a simple Python3 pastes application
# Copyright (C) 2014 Pietro Albini <pietro@pietroalbini.io>
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
import os.path
import cherrypy
import hashlib
import tools
import repo
import json

pastes_repo = repo.PastesRepo()

class PasteIt:
    """ Root of PasteIt """

    favicon_ico = None # Disable favicon

    @cherrypy.expose
    @tools.template('see.html')
    def default(self, id):
        # Try to find the id
        try:
            paste = pastes_repo.get(id)
        except KeyError:
            raise cherrypy.NotFound()
        else:
            # If a password is set check if the password was already inserted
            if paste.password:
                try:
                    # If true show the paste
                    if id in cherrypy.session['password_pastes']:
                        return {'paste': paste}
                except KeyError:
                    pass
                # Else redirect to the password form
                raise cherrypy.HTTPRedirect('/password/'+id)
            else:
                return {'paste': paste}

    @cherrypy.expose
    @tools.template('index.html')
    def index(self, author=None, content=None, password=None, language=None):
        # If he hasn't inserted the password redirect him to the login form
        if cherrypy.tree.apps[''].config['pasteit']['password'] and 'password_inserted' not in cherrypy.session:
            raise cherrypy.HTTPRedirect('/password')
        else:
            result = {}
            result['error'] = None
            # Obtain the languages list
            with open('languages.json', 'r') as f:
                result['languages'] = json.load(f)
            # If the method is POST, suppose that the user want to save the paste
            if cherrypy.request.method == 'POST':
                # Author and content are required!
                if not author or not content:
                    result['error'] = 'Something is missing'
                else:
                    # If the password wasn't provided, suppose the user don't want it
                    if not password:
                        password = False
                    # Try to create the paste
                    # If it was create, go to it
                    try:
                        id = pastes_repo.create(author, content, password, language)
                    except ValueError as e:
                        result['error'] = str(e)
                    else:
                        # If a password was set, automatically allow you to see the paste
                        if password:
                            # Boot the password_pastes key
                            if 'password_pastes' not in cherrypy.session:
                                cherrypy.session['password_pastes'] = []
                            # Append the id to allowed pastes
                            cherrypy.session['password_pastes'].append(id)
                        raise cherrypy.HTTPRedirect('/'+id)
            return result

    @cherrypy.expose
    def raw(self, id):
        try:
            paste = pastes_repo.get(id)
        except KeyError:
            raise cherrypy.NotFound()
        else:
            # If a password is set check if the password was already inserted
            if paste.password:
                try:
                    # If true show the paste
                    if id in cherrypy.session['password_pastes']:
                        return paste.content
                except KeyError:
                    pass
                # Else redirect to the password form
                raise cherrypy.HTTPRedirect('/password/'+id+'?next=/raw/'+id)
            else:
                return paste.content

    @cherrypy.expose
    @tools.template('password.html')
    def password(self, id=None, password=None, next=None):
        result = {'error': None, 'paste_id': None, 'next': None}
        redirect = False
        # If the password was provided, check if it's correct
        if password != None:
            # If an ID is provided, then the password is the one of that ID
            if id:
                # Get the paste
                try:
                    paste = pastes_repo.get(id)
                except KeyError:
                    raise cherrypy.NotFound()
                else:
                    # If a password is set, the valid one is that, else raise a not found
                    if paste.password:
                        valid = paste.password
                        password = hashlib.sha1(password.encode('utf-8')).hexdigest() # sha1-ize the password
                    else:
                        raise cherrypy.NotFound()
            # Else check for the global one
            else:
                valid = cherrypy.tree.apps[''].config['pasteit']['password']
            if password == valid:
                # If an id was provided, redirect to the correct paste
                if id:
                    # Boot the password_pastes key
                    if 'password_pastes' not in cherrypy.session:
                        cherrypy.session['password_pastes'] = []
                    # Append the id to allowed pastes
                    cherrypy.session['password_pastes'].append(id)
                    if next:
                        raise cherrypy.HTTPRedirect(next)
                    else:
                        raise cherrypy.HTTPRedirect('/'+id)
                # Else redirect to the home page
                else:
                    cherrypy.session['password_inserted'] = True
                    if next:
                        raise cherrypy.HTTPRedirect(next)
                    else:
                        raise cherrypy.HTTPRedirect('/')
            else:
                result['error'] = 'Invalid password!'
        # Set up some defaults
        if id:
            result['paste_id'] = id
        if next:
            result['next'] = next
        return result

if __name__ == "__main__":
    cherrypy.tree.mount( PasteIt(), '', 'pasteit.conf' ) # Mount the PasteIt object

    # Update jinja2 env with the configuration
    tools.jinja_env.globals['config'] = cherrypy.tree.apps[''].config['pasteit']

    # Start cherrypy
    cherrypy.engine.start()
    cherrypy.engine.block()
