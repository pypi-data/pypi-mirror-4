"""
Flask-Actions
-------------

custom actions for flask

Links
`````

* `documentation <http://packages.python.org/Flask-Actions>`_
* `development version
  <http://bitbucket.org/youngking/flask-actions/get/tip.gz#egg=Flask-Actions-dev>`_


"""
from setuptools import setup
import os


def read_file(*path):
    base_dir = os.path.dirname(__file__)
    file_path = (base_dir, ) + tuple(path)
    return file(os.path.join(*file_path)).read()

setup(
    name='Flask-Actions',
    version='0.6.6',
    url='http://blog.flyzen.com',
    license='BSD',
    author='Young King',
    author_email='yanckin@gmail.com',
    description='custom actions for flask to help manage your application',
    long_description=(
        read_file("README.rst") + "\n\n" +
        "Change History\n" +
        "==============\n\n" +
        read_file("CHANGES.rst")),
    packages=['flaskext', 'flaskext.actions'],
    include_package_data = True,
    package_data={'flask-actions': ['flaskext/actions/project_template/*']},
    namespace_packages=['flaskext'],
    test_suite='nose.collector',
    tests_require=['Nose'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Werkzeug'
    ],
    scripts=['flaskext/actions/flask_admin.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
