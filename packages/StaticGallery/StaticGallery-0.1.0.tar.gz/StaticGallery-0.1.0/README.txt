==============
Static Gallery
==============

Static Web Gallery Generator using Jinja2 And PIL.

In the context of the application, a gallery is a directory with photos, the source is the parent directory
of the galleries. The destiny is the directory where the galleries will be copied and the html files generated.


Installation
------------

You will need to install PIL and Jinja2 first:

    $ pip install jinja2
    $ pip install PIL

You can install it in a virtualenv, otherwise you will need to install it
as root if you don't change the root of the python package installation.

Use
---

It's really easy to change the design/styles of the gallery, you can create a jinja template for the menu
and a different one for the gallery, add them in the templates directory and later select them from the command-line
with the `--template-gallery` and `--template-menu` options.

You can run the server with `--server` if you want to check easily template changes (or whatever you want).

This is the command line help:

    usage: staticgallery [-h] [--template-gallery TEMPLATE_GALLERY]
                        [--template-menu TEMPLATE_MENU] [--src SRC] [--dst DST]
                        [--server] [--port PORT] [--reload]

    Static Gallery Generator Options.

    optional arguments:
      -h, --help            show this help message and exit
      --template-gallery TEMPLATE_GALLERY
                        Choose the name of the template for the gallery
      --template-menu TEMPLATE_MENU
                        Choose the template for the menu
      --src SRC             Source directory for the galleries
      --dst DST             Destiny where the web galleries will be generated
      --server              Executes a server
      --port PORT           Choose the port for the server, by default 8000
      --reload              Reload all galleries, even if they exist in the
                            destiny


Configuration
-------------

You can change the configuration easily just editing the file in $HOME/.staticgallery/config.cfg
too. By default you will need to configure the source of your image directory, the destiny is by default
`~/.staticgallery/site`, but you can move it wherever you want.

Once you have your gallery generated you can see it using `staticgallery --server --port 8080` and
redirecting your browser to `http://localhost:8080`.

Have fun! :-D
