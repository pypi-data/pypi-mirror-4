Flask-Actions
=========================================

.. module:: Flask-Actions

The **Flask-Actions** extension provides support for writing external actions in Flask. This includes running a development server, a customized Python shell,a fastcgi server like django . 


Install
-------------------------

Install with **easy_install**::

    easy_install Flask-Actions

Install with **pip**::

    pip install Flask-Actions

Start a new project
----------------------
**Flask-Actions** even has an auto code generator for creating a new flask project,let's look at it's usage::

    usage: flask_admin.py <action> [<options>]
           flask_admin.py --help

    actions:
      startproject:
        Start new flask project

        --proj-name                   string  

now we create a new project::

    flask_admin.py startproject helloproject

let's look at what we created::

    helloproject/
    ├── helloproject
    │   ├── __init__.py
    │   ├── static
    │   │   └── style.css
    │   ├── templates
    │   │   └── layout.html
    │   └── views
    │       ├── frontend.py
    │       ├── frontend.pyc
    │       ├── __init__.py
    │       └── __init__.pyc
    ├── manage.py
    └── settings.py


Action Usage
--------------------------

A normal startup scripts is like this::

    # manage.py
    # -*- encoding:utf-8 -*-

    from flask import Flask
    from flaskext.actions import Manager
    import settings
    from helloproject import app

    app.config.from_object(settings)
    manager = Manager(app)

    if __name__ == "__main__":
        manager.run()


And you can run 'python manage.py --help' to see more ::


    usage: manage.py <action> [<options>]
           manage.py --help

    actions:
      bshell:
        run shell use bpython

      clean:
        Clean the specify filename extention files from the directory.
        :param pretend: Instead  of  actually performing the clean,just print it

        -d, --directory               string    .
        -e, --extention               string    .pyc
        --no-pretend
        --no-verbose

      compile_pyc:
        Compile all python files in the directory into bytecode files.
                

        -d, --directory               string    .
        --no-verbose

      generate_secret_key:
          creates a new secret key

              -l, --length                  integer   32

      runserver:
        Start a new development server.

        -h, --hostname                string    0.0.0.0
        -p, --port                    integer   7777
        --no-reloader
        --no-debugger
        --no-evalex
        --no-threaded
        --processes                   integer   1

      shell:
        Start a new interactive python session.

        --no-ipython

      show_urls:
        Displays all of the url matching routes for the project.


less commands
`````````````````
you can change the manage.py and modify the line::

  manager = Manager(app)

to the line ::

  manager = Manager(app,default_help_actions=False)

This will avoid load the default help actions.


more commands
````````````````
you can change the manage.py and modify the line::

  manager = Manager(app)

to the line ::

  manager = Manager(app,default_server_actions=True)

This will load the default server actions.

currently,flask-actions has supported the following servers:

- appengine
- flup
- paste
- cherrypy
- twisted
- gevent
- eventlet
- gunicorn
- tornado
- fapws
- diesel
- meinheld
- eurasia
- rocket



Add Custom action
-----------------------
**Flask-Actions** uses werkzeug management script utilities,you'd rather dive into it's documentation :`Werkzeug Documentation - Management Script Utilities <http://werkzeug.pocoo.org/documentation/dev/script.html#writing-actions>`_

here is an simple example::

    def hello(app):
        def action(user=('u','world')):
            """
            test command
            """
            print "hello %s!"%user
        return action
    manager.add_action('hello',hello)

or you can use the `manager.register` decorator instead::

    @manager.register('hello')
    def hello(app):
        def action(user=('u','world')):
            """
            test command
            """
            print "hello %s!"%user
        return action

then your can run the **hello** command::

   python manage.py hello -u honey

You will see::

   hello honey!


Deploy use fastcgi
------------------------
To start your server,run the `runfcgi` command (to do this,you must enable the `default_sever_actions`)::

    ./manage.py runfcgi [options]

Select your preferred protocol by using the ``protocol=<protocol_name>`` option
with ``./manage.py runfcgi`` -- where ``<protocol_name>`` may be one of: ``scgi`` (the default),
``fcgi`` or ``ajp``. 

Running a threaded server on a TCP port::

    ./manage.py runfcgi --method=threaded --host=127.0.0.1 --port=3033

    or 

    ./manage.py runfcgi --method=threaded -h localhost -p 3001

Running a preforked server on a Unix domain socket::

    ./manage.py runfcgi --method=prefork --socket=/home/user/mysite.sock --pidfile=flask.pid

Run without daemonizing (backgrounding) the process (good for debugging)::

    ./manage.py runfcgi --daemonize=false --socket=/tmp/mysite.sock --maxrequests=1

Stopping the FastCGI daemon
`````````````````````````````

If you have the process running in the foreground, it's easy enough to stop it:
Simply hitting ``Ctrl-C`` will stop and quit the FastCGI server. However, when
you're dealing with background processes, you'll need to resort to the Unix
``kill`` command.

If you specify the ``pidfile`` option to `runfcgi`, you can kill the
running FastCGI daemon like this::

    kill `cat $PIDFILE`

...where ``$PIDFILE`` is the ``pidfile`` you specified.

Setup Nginx
``````````````````````````````
Run the application using fastcgi daemonize mode ,like this::

    python manage.py runfcgi --protocol=fcgi -p 7777  --daemonize --pidfile=/var/run/flaskapp.pid

but you would rather use an init.d scripts to execute above commands ,
then you can configure the nginx like this ::

      upstream flaskapp {
         server 127.0.0.1:7777;
         }

      server {
      listen 8080;
      server_name  127.0.0.0;


      location / {
        fastcgi_pass  flaskapp;
        fastcgi_param REQUEST_METHOD    $request_method;
        fastcgi_param QUERY_STRING      $query_string;
        fastcgi_param CONTENT_TYPE      $content_type;
        fastcgi_param CONTENT_LENGTH    $content_length;
        fastcgi_param SERVER_ADDR       $server_addr;
        fastcgi_param SERVER_PORT       $server_port;
        fastcgi_param SERVER_NAME       $server_name;
        fastcgi_param SERVER_PROTOCOL   $server_protocol;
        fastcgi_param PATH_INFO         $fastcgi_script_name;
        fastcgi_param REMOTE_ADDR       $remote_addr;
        fastcgi_param REMOTE_PORT       $remote_port;
        fastcgi_pass_header Authorization;
        fastcgi_intercept_errors off;
      }

.. _api:

API
---

.. module:: flaskext.actions

.. autoclass:: Manager
   :members: register,add_actions,add_action

