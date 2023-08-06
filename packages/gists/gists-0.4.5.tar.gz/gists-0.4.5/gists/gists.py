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
from actions import (list_gists, show, get, post, delete, update, authorize,
                     fork, star, unstar)
from handlers import (handle_list, handle_show, handle_update,
                      handle_authorize, handle_get, handle_post, handle_delete,
                      handle_fork, handle_star)
from formatters import (format_list, format_post, format_update,
                        format_get, format_show, format_delete,
                        format_authorize, format_star)
from version import VERSION


USER_MSG = ("github username. Use this user instead of the defined one in "
            "the configuration file. If action demands authentication, a "
            "password request will be prompt")
GIST_ID_MSG = ("identifier of the Gist. Execute 'gists list' to know Gists "
               "identifiers")


def run(*args, **kwargs):

    # Initialize argument's parser
    description = 'Manage Github gists from CLI'
    parser = argparse.ArgumentParser(description=description,
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
    __add_fork_parser(subparsers)
    __add_star_parser(subparsers)
    __add_unstar_parser(subparsers)

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
    parser_list = subparsers.add_parser("list", help="list a user's Gists")
    parser_list.add_argument("-u", "--user", help=USER_MSG)
    group1 = parser_list.add_mutually_exclusive_group()
    group1.add_argument("-p", "--private", help="""return the private gists
                        besides the public ones. Needs authentication""",
                        action="store_true")
    group1.add_argument("-s", "--starred", help="""return ONLY the starred
                        gists. Needs authentication""", action="store_true")
    parser_list.set_defaults(handle_args=handle_list,
                             func=list_gists, formatter=format_list)


def __add_show_parser(subparsers):
    """ Define the subparser to handle with the 'show' functionallity.

    :param subparsers: the subparser entity
    """
    # Add the subparser to handle the 'show' action
    parser_show = subparsers.add_parser("show", help="""show a Gist. Shows
                                        Gist metadata by default.
                                        With '-f' (--filename) option, shows
                                        the content of one of the Gist files
                                        """)
    parser_show.add_argument("gist_id", help=GIST_ID_MSG)
    parser_show.add_argument("-f", "--filename", help="gist file to show")
    parser_show.set_defaults(handle_args=handle_show, func=show,
                             formatter=format_show)


def __add_get_parser(subparsers):
    """ Define the subparser to handle the 'get' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'get' action
    parser_get = subparsers.add_parser("get", help="""download a single gist
                                       file. If the gist has just a single
                                       file, argument '-f' (--filename) is not
                                       needed""")
    parser_get.add_argument("gist_id", help=GIST_ID_MSG)
    parser_get.add_argument("-f", "--filename", help="file to download")
    parser_get.add_argument("-o", "--output_dir", help="destination directory",
                            default=".")
    parser_get.set_defaults(handle_args=handle_get, func=get,
                            formatter=format_get)


def __add_create_parser(subparsers):
    """ Define the subparser to handle the 'create' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'create' action
    parser_post = subparsers.add_parser("create", help="""create a new gist.
                                        Needs authentication""")
    parser_post.add_argument("-u", "--user", help=USER_MSG)
    parser_post.add_argument("-f", "--filenames", nargs='+', help="""specify
                             files to upload with Gist creation""",
                             required=True)
    parser_post.add_argument("-p", "--private", help="""private Gist? ('false'
                             by default)""", action="store_true")
    parser_post.add_argument("-i", "--input_dir", help="""input directory where
                             the source files are""")
    parser_post.add_argument("-d", "--description", help="""description for
                             the Gist to create""")
    parser_post.set_defaults(handle_args=handle_post, func=post,
                             formatter=format_post)


def __add_update_parser(subparsers):
    """ Define the subparser to handle the 'update' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'update' action
    parser_update = subparsers.add_parser("update", help="""update a gist.
                                          Needs authentication""")
    parser_update.add_argument("gist_id", help=GIST_ID_MSG)
    parser_update.add_argument("-u", "--user", help=USER_MSG)

    group1 = parser_update.add_argument_group("file options",
                                              "update Gist files")
    group1.add_argument("-f", "--filenames", nargs='+',
                        help="Gist files to update")
    group11 = group1.add_mutually_exclusive_group()
    group11.add_argument("-n", "--new", action="store_true", help="""files
                         supplied are new for the Gist. '-f' (--filenames)
                         argument needed""",
                         default=False)
    group11.add_argument("-r", "--remove", action="store_true",
                         help="""files supplied will be removed from the Gist.
                         '-f' (--filenames) argument needed""", default=False)
    group1.add_argument("-i", "--input_dir", help="""directory where the files
                        are. Current directory by default""")
    group2 = parser_update.add_argument_group('metadata options',
                                              "update Gist metadata")
    group2.add_argument("-d", "--description", help="update Gist description")
    parser_update.set_defaults(handle_args=handle_update, func=update,
                               formatter=format_update)


def __add_delete_parser(subparsers):
    """ Define the subparser to handle the 'delete' functionality.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'delete' action
    parser_delete = subparsers.add_parser("delete", help="""delete a Gist.
                                          Needs authentication""")
    parser_delete.add_argument("gist_id", help=GIST_ID_MSG)
    parser_delete.add_argument("-u", "--user", help=USER_MSG)
    parser_delete.set_defaults(handle_args=handle_delete, func=delete,
                               formatter=format_delete)


def __add_authorize_parser(subparsers):
    """ Define the subparser to handle the 'authorize' functionallity.

    :param subparsers: the subparser entity
    """

    # Add the subparser to handle the 'authorize' action.
    parser_authorize = subparsers.add_parser("authorize", help="""authorize
                                             this project in github""")
    parser_authorize.add_argument("-u", "--user", help="""your github user
                                  . Needed to generate the auth token. """,
                                  required=True)
    parser_authorize.set_defaults(handle_args=handle_authorize, func=authorize,
                                  formatter=format_authorize)


def __add_version_parser(subparsers):
    """ Define the subparser to handle 'version' functionallity.

    :param subparsers: the subparser entity
    """

    parser_version = subparsers.add_parser("version", help="""print the version
                                           of the release""")
    parser_version.set_defaults(handle_args=lambda x: (None,),
                                func=lambda x: None,
                                formatter=lambda x: VERSION)


def __add_fork_parser(subparsers):
    """ Define the subparser to handle 'fork' functionallity.

    :param subparsers: the subparser entity
    """

    parser_fork = subparsers.add_parser("fork", help="""fork another users'
                                        Gists""")
    parser_fork.add_argument("gist_id", help=GIST_ID_MSG)
    parser_fork.add_argument("-u", "--user", help=USER_MSG)
    parser_fork.set_defaults(handle_args=handle_fork, func=fork,
                             formatter=format_post)


def __add_star_parser(subparsers):
    """ Define the subparser to handle 'star' functionallity.

    :param subparsers: the subparser entity
    """

    parser_star = subparsers.add_parser("star", help="star a Gist")
    parser_star.add_argument("gist_id", help=GIST_ID_MSG)
    parser_star.add_argument("-u", "--user", help=USER_MSG)
    parser_star.set_defaults(handle_args=handle_star, func=star,
                             formatter=format_star)


def __add_unstar_parser(subparsers):
    """ Define the subparser to handle 'unstar' functionallity.

    :param subparsers: the subparser entity
    """

    parser_unstar = subparsers.add_parser("unstar", help="unstar a Gist")
    parser_unstar.add_argument("gist_id", help=GIST_ID_MSG)
    parser_unstar.add_argument("-u", "--user", help=USER_MSG)
    parser_unstar.set_defaults(handle_args=handle_star, func=unstar,
                               formatter=format_star)
