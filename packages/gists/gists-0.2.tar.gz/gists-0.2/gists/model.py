# Copyright (c) 2012 <Jaume Devesa (jaumedevesa@gmail.com)>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""

gists.model
~~~~~~~~~~~

Model defines the two classes that extend of builtin python 'dicts'. They represent
a Gist object and a Gist File. Used to make the code of other modules clearer.


"""

class Gist(dict):
    """ :class: `Gist <Gist>` Simple Gist object. """

    def __init__(self, parsed_gist={}):
        """ Initialize gist object variables. """

        super(Gist, self).__init__(parsed_gist)

    @property
    def url(self):
        return self['url']

    @property
    def html_url(self):
        return self['html_url']

    @property
    def description(self):
        return self['description']

    @description.setter
    def description(self, description):
        self['description'] = description

    @property
    def identifier(self):
        return self['id']

    @property
    def user(self):
        return self['user']['login']

    @property
    def public(self):
        return self['public']

    @public.setter
    def public(self, public):
        self['public'] = public

    @property
    def files(self):
        """ Parse the 'self['files']' into GistFile objects. """
        if not 'files' in self:
            self['files'] = {}
            return self['files']
        return [GistFile(self['files'][gistfile])
                for gistfile in self['files'] if self['files'][gistfile] != 'null']

    def getFile(self, requested_filename):
        candidates = [gistfile for gistfile in self.files
                if gistfile.filename == requested_filename]
        if len(candidates) == 0:
            return None
        return candidates[0]

    def setFile(self, filename, gist_file):
        self['files'][filename] = gist_file

    def addFile(self, gistfile):
        if not 'files' in self:
            self['files'] = {}
        self['files'][gistfile.filename] = gistfile


class GistFile(dict):
    """ :class: `GistFile <GistFile>` File that belongs to a Gist. """

    def __init__(self, parsed_file={}):
        super(GistFile, self).__init__(parsed_file)

    @property
    def raw_url(self):
        return self['raw_url']

    @property
    def language(self):
        return self['language']

    @property
    def filename(self):
        return self['filename']

    @filename.setter
    def filename(self, filename):
        self['filename'] = filename

    @property
    def content(self):
        return self['content']

    @content.setter
    def content(self, content):
        self['content'] = content

    @property
    def mimetype(self):
        return self['type']

    @property
    def size(self):
        return self['size']


class Authorization(dict):
    """ :class: `Authorization <Authorization>` authorization object. """

    def __init__(self, parsed_auth={}):
        super(Authorization, self).__init__(parsed_auth)

    @property
    def id(self):
        return self['id']

    @property
    def url(self):
        return self['url']

    @property
    def app(self):
        return self['app']['name']

    @property
    def app_url(self):
        return self['app']['url']

    @property
    def created(self):
        return self['created_at']

    @property
    def updated(self):
        return self['updated_at']

    @property
    def token(self):
        return self['token']

    @property
    def note(self):
        return self['note']

    @note.setter
    def note(self, note):
        self['note'] = note

    @property
    def note_url(self):
        return self['note_url']

    @note_url.setter
    def note_url(self, note_url):
        self['note_url'] = note_url

    @property
    def scopes(self):
        return self['scopes']

    @scopes.setter
    def scopes(self, scopes):
        self['scopes'] = scopes
