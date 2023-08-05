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

import os
import model
from clint.textui import colored

"""

gists.formatters
~~~~~~~~~~~~~~~~

'formatters' is the last step of the execution workflow. All the methods
receive an instance of the :class: `Result <Result>` and use them to format
the output legible, clear and pretty (using the usefull 'clint' package)


"""


def format_show(result):
    """ Formats the output of the 'show' action.

    :param result: Result instance
    """

    if result.success:
        resultdata = result.data

        # If the data is an instance of the 'GistFile' data model,
        # parse the file, otherwise, parse the 'Gist' metadata
        if isinstance(resultdata, model.GistFile):
            return __format_file(resultdata)
        else:
            return __format_gist(resultdata)
    else:
        # Format the error string message
        return __format_error(result.data)


def format_post(result):
    """ Formats the output of the 'create' action.

    :param result: Result instance
    """

    if result.success:
        # Format the 'Gist' metadata object
        return __format_gist(result.data)
    else:
        # Format the error string message
        return __format_error(result.data)


def format_get(result):
    """ Formats the output of the 'get/download' action.

    :param result: Result instance
    """

    if result.success:
        # The result is just a string informing the success
        return result.data
    else:
        # Format the error string message
        return __format_error(result.data)


def format_delete(result):
    """ Formats the output of the 'delete' action.

    :param result: Result instance
    """

    if result.success:
        # The result is just a string informing the success
        return result.data
    else:
        # Format the error string message
        return __format_error(result.data)


def format_update(result):
    """ Formats the output of the 'delete' action.

    :param result: Result instance
    """

    if result.success:
        # Format the 'Gist' metadata object
        return __format_gist(result.data)
    else:
        # Format the error string message
        return __format_error(result.data)


def format_list(result):
    """ Formats the output of the 'list' action.

    :param result: Result instance
    """
    if result.success:

        # Get the list of Gists from the data
        list_of_gists = result.data

        # Calculate the number of columns of the current terminal window
        rows, columns = os.popen('stty size', 'r').read().split()

        # Set the header
        gists_string = colored.cyan('-' * int(columns)) + "\n"
        gists_string += colored.cyan("List of gists\n")
        gists_string += colored.cyan('-' * int(columns)) + "\n"

        # Set the contents for each Gist listed
        for gist in list_of_gists:
            gists_string += colored.green(gist.identifier + ": ")
            description = "(no desc)"
            if gist.description and gist.description != "":
                description = gist.description
            gists_string += description
            gist_names = [gistfile.filename for
                    gistfile in gist.files]
            stringfiles = " [" + ", ".join(gist_names) + "]"
            gists_string += colored.red(stringfiles)
            if not gist.public:
                gists_string += " (Private) "
            gists_string += '\n'

        # Set the footer
        gists_string += colored.cyan('-' * int(columns)) + "\n"

        # Return the formatted String
        return gists_string
    else:
        # Format the error string message
        return __format_error(result.data)


def format_authorize(result):
    """ This is enough for this method. """
    if result.success:
        return "Authentication token written in '~/.gistsrc'"
    else:
        # Format the error string message
        return __format_error(result.data)


def __format_gist(gist):
    """ Formats the output for a Gist metadata object.

    :param gist: :class: `Gist <Gist>` instance.
    """

    # Calculate the number of columns of the current terminal window
    rows, columns = os.popen('stty size', 'r').read().split()

    # Prepare the Header
    gists_string = colored.cyan('-' * int(columns)) + "\n"
    gists_string += colored.cyan("Gist [" + gist.identifier + "]") + '\n'
    gists_string += colored.cyan('-' * int(columns)) + "\n"

    # Format Gist data
    gists_string += colored.green('Description:\t')
    if gist.description:
        gists_string += gist.description + '\n'
    gists_string += colored.green('Url:\t\t')
    gists_string += gist.url + '\n'
    gists_string += colored.green('Html Url:\t')
    gists_string += gist.html_url + '\n'
    gists_string += colored.green('Private:\t')
    gists_string += str(not gist.public) + '\n'

    gists_string += colored.green('Files:\t\t')
    gist_names = [gistfile.filename for
                    gistfile in gist.files]
    stringfiles = "[" + ", ".join(gist_names) + "]"
    gists_string += colored.red(stringfiles) + '\n'

    # Prepare the Footer
    gists_string += colored.cyan('-' * int(columns)) + "\n"
    return gists_string


def __format_error(data):
    """ Print the string output error. """
    return colored.red("Error: ") + data


def __format_file(file_gist):
    """ Formats the output for a GistFile object.

    :param gist: :class: `GistFile <GistFile>` instance.
    """

    # Calculate the number of columns of the current terminal window
    rows, columns = os.popen('stty size', 'r').read().split()

    # Prepare the Header
    gist_string = colored.cyan('-' * int(columns)) + "\n"
    gist_string += colored.cyan("File [" + file_gist.filename + "]\n")
    gist_string += colored.cyan('-' * int(columns)) + "\n"

    # Format Gist data
    gist_string += (colored.green("Language:") + " " +
            colored.red(file_gist.language) + "\n")
    gist_string += (colored.green("Size:") + " " +
         colored.red(file_gist.size) + "\n")
    gist_string += (colored.green("Raw Url:") + " " +
            colored.red(file_gist.raw_url + "\n"))
    gist_string += (colored.green("Content:\n\n")
            + file_gist.content + "\n\n")

    # Prepare the Footer
    gist_string += colored.cyan('-' * int(columns)) + "\n"

    return gist_string
