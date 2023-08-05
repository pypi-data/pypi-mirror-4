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

gists.literals
~~~~~~~~~~~

All the return literals here.

"""

APP_NAME = "Gists CLI"

APP_URL = "https://github.com/jdevesa/gists"

LISTS_ERROR = "Can not return the list of gists. Github reason: '%s'"

DOWNLOAD_OK = "File '%s' downloaded successfully!"

DOWNLOAD_MORE_FILES = ("Gist has more than one file. "
   "Specify file by '-f' option. Available values are [%s]")

FILE_NOT_FOUND = ("File not found in gist. Available values are [%s])")

DOWNLOAD_ERROR = "Can not download gist file. Github reason: '%s'"

SHOW_ERROR = "Can not show gist file. Github reason: '%s'"

UNHANDLED_EXCEPTION = "Unhandled exception"

DELETE_CONFIRMATION = "Are you sure you want to delete gist %s [yN]"

DELETE_OK = "Gist '%s' deleted succesfully"

DELETE_NOK = "Can not delete the gist. Github reason: '%s'"

DELETE_ABORTED = "Delete aborted."

UPDATE_NOK = "Can not update the gist. Github reason: '%s'"

UPDATE_RM_NF = "Can not remove a file that actually does not exist in gist. "

UPDATE_NF = ("Filename not found in gist. Use the '-n' (--new) argument "
   "to attach a new file in the gist.")

UPDATE_NEW_DUP = ("File already exists in Gist. Remove the "
   "'n' (--new) argument if you want to update the existent file. Change the "
   "file name if you actually want to update a new file in the gist. ")

CONFIG_FILE_NOT_FOUND = "Configuration file not found or not valid"

DOWNLOADING = "Downloading: %s\nTo: %s\nBytes: %s"

USER_NOT_FOUND = ("Can not load GitHub user name neither from '--user (-u)' "
    "parameter nor from the configuration file. ")

CREDENTIAL_NOT_FOUND = ("Credential should be informed via configuration "
    "file or '-s' argument")

AUTHORIZE_NOK = "Could not get an authorization token. Github reason: '%s'"
