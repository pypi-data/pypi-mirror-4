#!/usr/bin/env python2
# -*- encoding:utf-8 -*-
import os,stat
import sys
import re
import shutil
import random
import string
from werkzeug import script
from flaskext.actions import utils

def preprocess_file(path, **values):
    f = open(path, 'r')
    text = f.read()
    f.close()

    # Save configuration file back
    f = open(path, 'w')
    f.write(text % values)
    f.close()

def startproject(proj_name=''):
    """
    Start new flask project
    """
    if not proj_name:
        sys.stderr.write("proj_name required.\n")
        sys.exit(1)
    if not re.search(r'^[a-zA-Z][a-zA-Z0-9\-]*$', proj_name):
        # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[a-zA-Z]', proj_name):
          message = 'make sure the name begins with a letter'
        else:
          message = 'use only numbers, letters and dashes'
        sys.stderr.write("%r is not a valid project name. Please %s.\n" %
                         (proj_name, message))
        sys.exit(1)
    if os.path.exists(proj_name):
        sys.stderr.write('Folder with name "%s" already exists' % proj_name)
        sys.exit(1)
    from flaskext import actions
    source = os.path.join(actions.__path__[0], 'project_template')
    shutil.copytree(source, proj_name)
    path_join = lambda path: os.path.join(proj_name, path)

    # Rename .py_tmpl to .py
    for fn in os.listdir(proj_name):
        if fn.endswith('.py_tmpl'):
            os.rename(path_join(fn), path_join(fn.replace('_tmpl', '')))

    # Update configuration file
    key = utils.generate_secret_key()
    preprocess_file(path_join('manage.py'), project=proj_name)
    preprocess_file(path_join('__init__.py'), project=proj_name)
    preprocess_file(path_join('settings.py'), project=proj_name,secretkey=key)
    sub_proj_dir = path_join(proj_name)
    os.mkdir(sub_proj_dir)
    shutil.move(path_join('__init__.py'),sub_proj_dir)
    shutil.move(path_join('views'),sub_proj_dir)
    shutil.move(path_join('static'),sub_proj_dir)
    shutil.move(path_join('templates'),sub_proj_dir)
    os.chmod(path_join('manage.py'),
             os.stat(path_join('manage.py')).st_mode |
             stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


script.run(dict(
        startproject = startproject,
        ), '', sys.argv[1:])
