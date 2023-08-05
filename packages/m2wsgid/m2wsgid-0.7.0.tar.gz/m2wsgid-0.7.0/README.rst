WSGId = WSGI Daemon
===================

Description
===========

Wsgid is a mongrel2 (http://mongrel2.org) adapter for WSGI applications. With wsgid you will be able to run your WSGI app as a true unix daemon.

Install
=======

To install just clone this repo and run: (pip package coming soon)
   
   sudo python setup.py install

Use example
===========


Before youcan use wsgid, you will need to initialize your wsgid app folder. This folder is where you app will live. To do so, just run

   wsgid init --app-path=/path/to/my/wsgid-app-folder


From now on, all command you type must have ``--app-path=/path/to/my/wsgid-app-folder`` parameter.
   

What this command does is create some well known folders, eg: ``pid/, pid/master, pid/worker, app, logs``.

All of you application code will be places inside the ``${WSGID_APP_FOLDER}/app`` folder. So to deploy a django app, just copy your project folder to ``${WSGID_APP_FOLDER}/app``.


To start an application just call wsgid like this.

   wsgid --app-path=/path/to/the/app --recv=tcp://127.0.0.1:8889 --send=tcp://127.0.0.1:8890


This will load the app located at ``/path/to/the/app`` and be ready to process requests. wsgid automatically detects what kind of application it will load.


You don't have to type all this every time. You can use the ``init`` command to create a config file, like this:

   wsgid config --app-path=/path/to/the/app --recv=tcp://127.0.0.1:8889 --send=tcp://127.0.0.1:8890


This will create a ``wsgid.json`` file inside your wsgid app folder. So the next time you start you app you8 can type just:


   wsgid --app-path=/path/to/the/app


If wsgid is not able do detect the aplication WSGI framework you can use the --wsgi-app option. 
   wsgid --app-path=/path/to/the/app --recv=tcp://127.0.0.1:8889 --send=tcp://127.0.0.1:8890 --wsgi-app=my.package.application


``--wsgi-app`` is the full qualified name of the WSGI application object, this way wsgid can find the app's entry point, as defined by pep-333.

See more at: http://wsgid.com


Plugable Appication Loaders
===========================

wsgid has a plugable Application Loader subsystem, this way you can write your own AppLoader.  To do this just write an class that extends the wsgid.core.Plugin class and implements the IAppLoader interface. See the PyRoutesLoader (wsgid/loaders/__init__.py) for an actual example. To make wsgid use your loader just pass na aditional option: *--loader-dir*. This must point to the path where yout loader is located. More about this, read the docs on the site: http://wsgid.com

License
=======

wsgid is Licensed under *New BSD*, see LICENSE for details.

Know more
=========

Know more about the wsgid project at the official website: http://wsgid.com and at the docs: http://wsgid.com/docs


https://github.com/daltonmatos/wsgid

2010-2011 | Dalton Barreto
