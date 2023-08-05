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

gists.gists
~~~~~~~~~~~

This single-function module defines the input parameters and the subparsers,
and coordinates the 'handlers'->'actions'->'formatters' execution workflow

"""

import argparse
from actions import list_gists, show, get, post, delete, update, authorize
from handlers import handle_list, handle_show, handle_update, handle_authorize
from handlers import handle_get, handle_post, handle_delete
from formatters import format_list, format_post, format_update
from formatters import format_get, format_show, format_delete, format_authorize
from version import VERSION


def run(*args, **kwargs):

    # Initialize argument's parser
    parser = argparse.ArgumentParser(
            description='Manage Github gists from CLI',
            epilog="Happy Gisting!")

    # Define subparsers to handle each action
    subparsers = parser.add_subparsers(help="Available commands.")

    # Add the subparsers
    __add_list_parser(subparsers)
    __add_show_parser(subparsers)
    __add_get_parser(subparsers)
    __add_create_parser(subparsers)
    __add_update_parser(subparsers)
    __add_delete_parser(subparsers)
    __add_authorize_parser(subparsers)
    __add_version_parser(subparsers)

    # Parse the arguments
    args = parser.parse_args()

    # Calling the handle_args function defined, parsing the args and return
    # and object with the needed values to execute the function
    parameters = args.handle_args(args)

    # Passing the 'parameters' object as array of parameters
    result = args.func(*parameters)

    # Parsing the 'result' object to be output formatted.
    # (that must be a single object)
    result_formatted = args.formatter(result)

    # Print the formatted output
    print result_formatted


def __add_list_parser(subparsers):
    """ Define the subparser to handle the 'list' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the list of gists
    parser_list = subparsers.add_parser("list", help="List gists")
    parser_list.add_argument("-u", "--user",
            help="""Github user. Overrides the default 'user' property
            in configuration file""")
    parser_list.add_argument("-s", "--secret",
            help="""Github password. Overrides the default 'token' property
            in configuration file""")
    parser_list.add_argument("-p", "--private",
            help="""Return the private gists besides the public ones.
            Password needed (by arguments or in configuration file)""",
            action="store_true")
    parser_list.set_defaults(handle_args=handle_list,
            func=list_gists, formatter=format_list)


def __add_show_parser(subparsers):
    """ Define the subparser to handle with the 'show' functionallity.

    :param subparsers: the subparser entity
    """
    # Add the subparser to handle the 'show' action
    parser_show = subparsers.add_parser("show",
            help="""Show a gist. Shows the general gist data by default.
            With '-f' (--filename) option, shows the content of one of the
            gist files""")
    parser_show.add_argument("gist_id",
            help="Identifier of the gist to retrieve")
    parser_show.add_argument("-f", "--filename",
            help="Gist file to show.")
    parser_show.set_defaults(handle_args=handle_show, func=show,
            formatter=format_show)


def __add_get_parser(subparsers):
    """ Define the subparser to handle the 'get' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'get' action
    parser_get = subparsers.add_parser("get",
            help="""Download a single gist file. If the gist only
            have a single file, argument '-f' (--filename) is not needed""")
    parser_get.add_argument("gist_id",
            help="Identifier of the gist to retrieve")
    parser_get.add_argument("-f", "--filename",
            help="Gist file to download.")
    parser_get.add_argument("-o", "--output_dir",
            help="Destination directory",
            default=".")
    parser_get.set_defaults(handle_args=handle_get, func=get,
            formatter=format_get)


def __add_create_parser(subparsers):
    """ Define the subparser to handle the 'create' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'create' action
    parser_post = subparsers.add_parser("create",
            help="Create a new gist")
    parser_post.add_argument("-u", "--user",
            help="""Github user. Overrides the default 'user' property
            in configuration file""")
    parser_post.add_argument("-s", "--secret",
            help="""Github password. Overrides the default 'token' property
            in configuration file""")
    parser_post.add_argument("-f", "--filename",
            help="Specify gist file to upload.", required=True)
    parser_post.add_argument("-p", "--private",
            help="""Private gist. (public by default)""",
            action="store_true")
    parser_post.add_argument("-i", "--input_dir",
            help="Input directory where the source file is")
    parser_post.add_argument("-d", "--description",
            help="escription for the gist to create")
    parser_post.set_defaults(handle_args=handle_post, func=post,
            formatter=format_post)


def __add_update_parser(subparsers):
    """ Define the subparser to handle the 'update' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'update' action
    parser_update = subparsers.add_parser("update",
            help="Update a gist")
    parser_update.add_argument("gist_id",
            help="Identifier of the gist to update")
    parser_update.add_argument("-u", "--user",
            help="""Github user. Overrides the default 'user' property
            in configuration file""")
    parser_update.add_argument("-s", "--secret",
            help="""Github password. Overrides the default 'token' property
            in configuration file""")
    group1 = parser_update.add_argument_group("File options",
            "Update Gist files")
    group1.add_argument("-f", "--filename",
             help="Gist file to update.")
    group11 = group1.add_mutually_exclusive_group()
    group11.add_argument("-n", "--new", action="store_true",
            help="New file for the gist. '-f' (--filename) argument needed",
            default=False)
    group11.add_argument("-r", "--remove", action="store_true",
            help="Delete file for the gist. '-f' (--filename) argument needed",
            default=False)
    group11.add_argument("-i", "--input_dir",
            help="Input directory where the source file is")
    group2 = parser_update.add_argument_group('Metadata options',
            "Update Gist General Data")
    group2.add_argument("-d", "--description",
            help="Update gist description")
    parser_update.set_defaults(handle_args=handle_update, func=update,
            formatter=format_update)


def __add_delete_parser(subparsers):
    """ Define the subparser to handle the 'delete' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'delete' action
    parser_delete = subparsers.add_parser("delete", help="Delete a gist")
    parser_delete.add_argument("gist_id",
            help="Identifier of the Gist to delete")
    parser_delete.add_argument("-u", "--user",
            help="""Github user. Overrides the default 'user' property
            in configuration file""")
    parser_delete.add_argument("-s", "--secret",
            help="""Github password. Overrides the default 'token' property
            in configuration file""")
    parser_delete.set_defaults(handle_args=handle_delete, func=delete,
            formatter=format_delete)


def __add_authorize_parser(subparsers):
    """ Define the subparser to handle the 'authorize' functionallity.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'authorize' action.
    parser_authorize = subparsers.add_parser("authorize",
            help="Authorize the 'gists' module")
    parser_authorize.add_argument("-u", "--user",
            help="""Your GitHub user used to generate the auth token. """,
            required=True)
    parser_authorize.add_argument("-s", "--secret",
            help="""Your Github password used to generate the auth token.""",
            required=True)
    parser_authorize.set_defaults(handle_args=handle_authorize, func=authorize,
            formatter=format_authorize)


def __add_version_parser(subparsers):
    """ Define the subparser to handle 'version' functionallity.

    :param subparsers: the subparser entity
    """

    parser_version = subparsers.add_parser("version",
            help="Print the version of the release")
    parser_version.set_defaults(handle_args=lambda x: (None,),
            func=lambda x: None, formatter=lambda x: VERSION)
