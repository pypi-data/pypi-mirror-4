Gists
=====

CLI interface for managing GitHub gists

Install it
----------

Two ways of installation:

* [Download](https://github.com/jdevesa/gists/zipball/master) the source code, extract it, and execute `python setup.py install`
* `pip install gists`

Configure it
------------

First time you run 'gists', execute the command

<!-- language: bash -->

    $ gists authorize -u your_github_user -s your_github_password


And the file ~/.gistsrc (which stores the 'gists' configuration) will be written
with your GitHub api authentication token.

Anytime you can revoke your authentication token in your [applications page](https://github.com/settings/applications) on GitHub.

Use it!
-------

### Set up credentials ###

Gists uses the file '~/.gistsrc' to obtain your GitHub authentication token. First thing you need to do is set up your
credentials to perform actions that needs authentication. Method is just:

<!-- language: bash -->

    $ gists authorize -u your_github_user -s your_github_password

<!-- language: lang-none -->

You can perform this actions many times you wish to override the values.

If you don't want to authorize the app, you can always use the **-u** and **-s** parameters to provide the
credentials in each command.


### List of Gists ###

#### Basic Usage ####

Return a list of gists. Basic usage is:

<!-- language: bash -->

    $ gists list

<!-- language: lang-none -->

This will return a list of Gists from field __user__ from [credentials] section in your (~/.gistsrc) file. 

#### More arguments: ####

* __-u__ (--user) specifies from whom user you want to retrieve his/her gists.
* __-p__ (--private) retrieves the private gists from the user besides the public ones. (Needs authentication)


### Show a Gist ###


Shows the detail of a Gist. There are two modes here: without the __-f__ argument, that will show the Gist metadata (url, description, name of the files...) and with the __-f__ argument, that shows the content of one of the files of the Gist. Identifier of the Gist, (obtained via `gists list`) is mandatory as first argument.

Example without __-f__ argument:

<!-- language:bash -->

    $ gists show e110cc498a31dc442fc3

<!-- language: lang-none -->

Example with __-f__ argument:

<!-- language: bash -->

    $ gists show e110cc498a31dc442fc3 -f examplegist.txt

<!-- language: lang-none -->


### Download a Gist ###

Download a file from a Gist using the 'get' action. While in the 'show' action the parameter __-f__ is optional depending on the kind of data you want to show, here is mandatory. So, a basic usage is:

<!-- language: bash -->

    $ gists get e110cc498a31dc442fc3 -f examplegist.txt

<!-- language: lang-none -->

The name of the target file in your OS will be the same of the argument provided by __-f__. There is no way to change this.

#### More arguments ####

* __-o__ (--output\_dir) destination directory where you want to save the gist


### Create a Gist ###

Creates a Gist. Needs a file to be uploaded. So, authentication and __-f__ arguments are required. Basic usage is:

<!-- language: bash -->

    $ gists create -f examplegist.txt

<!-- language: lang-none -->

The name of the file in the OS will be the same of the name of the file in the Gist. No way to change this.

#### More arguments ####

* __-p__ (--private) whenever you want the Gist to be private.
* __-d__ (--description) Set the description of the Gist.
* __-i__ (--input\_dir) Specify the input directory where the file is.


### Update a Gist ###

Update an existent Gist. Several examples:

#### Modify just the description ####

To modify the description, use the __-d__ (--description) argument:

<!-- language: bash -->

    $ gists update e110cc498a31dc442fc3 -d "New gist description"

<!-- language: lang-none -->

#### Modify the contents of a file ####

Modify the contents of a File that already exists in the Gist:

<!-- language: bash -->

    $ gists update e110cc498a31dc442fc3 -f examplegist.txt

<!-- language: lang-none -->

#### Add a new file to a Gist ####

Modify a Gist adding a new file, using the __-n__ (--new) argument:

<!-- language: bash -->

    $ gists update e110cc498a31dc442fc3 -f new_file_to_gist.py -n

<!-- language: lang-none -->

#### Remove a file from a Gist ####

Modify a Gist removing one of its files, using the __-r__ (--remove) argument:

<!-- language: bash -->

    $ gists update e110cc498a31dc442fc3 -f no_longer_needed_file.py -r

<!-- language: lang-none -->

#### More arguments ####

* __-i__ (--input\_dir) Specify the input directory where the file is.
