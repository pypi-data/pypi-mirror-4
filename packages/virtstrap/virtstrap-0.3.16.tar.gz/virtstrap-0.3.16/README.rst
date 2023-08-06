virtstrap
=========

A simple script that allows you to setup a repeatable project using a
variety of tools. The project came out of a need to use some things
from buildout and some things from pip and virtualenv. However,
eventually buildout support was abandoned as pip and virtualenv
were powerful enough for the job - they just needed better tools.

Main Goals
----------
    
- Create repeatable projects between other developers and environments
- Provide a simple and easy to use interface
- Create Gemfile/Gemfile.lock like system
- Set custom environment variables in the virtualenv
- Setup multi python virtualenvs
- Create a plugin system similar that is both flexible and simple
- Allow for local caching of compiled python modules so new virtstrap
  environments don't continually go online to find a module.
- A configuration file that is portable to more than just virtstrap. This
  allows for programs that aren't virtstrap to take advantage of the 
  the configuration file.

Current Features
----------------

- Provides a standard location for virtualenv
- Provide a quick and simple way to activate the current environment
- Generate a requirements file much like a Gemfile.lock
- Provide a simple plugin system
- Allows for arbitrary environment variables to be set

Is this yet another build tool?
-------------------------------

Yes and no. Virtstrap is meant as a layer above virtualenv+pip to give
the user buildout like capabilities without all the buildout overhead (I hope).

Why not virtualenv-wrapper?
---------------------------

I looked into using it but it did not fit my particular needs. It's a great
tool but I originally wanted to create a tool that didn't have to be installed 
system wide to see use. Now, however, I see that as a horrible oversight and 
an unnecessary limitation. Although I still feel there is something elegant 
about keeping the package out of the global system, it now seems unreasonable
to me. As a consequence, this question seems even more relevant. However,
after having built the initial versions of virtstrap, I realized 
that virtstrap could make virtualenv-wrapper even simpler. It could also be 
shared between developers, build systems, and any number of scenarios. So,
here's my crack at making something truly useful for python development.

virtstrap Quick Start
---------------------

The easiest way to get started with virtstrap is to install it
on your local machine by simply doing the following::

    pip install virtstrap

Note: If you don't want to install it into your system. Look below for
an alternative installation.

To add virtstrap to your project. The most basic usage is::

    cd path_to_your_project_path
    vstrap init

This will add a directory named ``.vs.env`` and a file called 
``quickactivate`` to your directory.

Configuration Files
-------------------

As of 0.3.x configuration files won't be required. Granted, virtstrap isn't
very useful without it, but, if you really want to start a virtstrapped 
environment without doing anything, it's as simple as ``vstrap init``.

To get more out of virtstrap you should define a ``VEfile``. This stands for
virtual environment file. This is a general purpose file to be used for 
defining your virtual environment.

The configuration file will be expected in the root directory of your project.
Any other location can be specified, but that is extremely discouraged. 

At the moment the file is a YAML file. Eventually I hope to move away from
yaml as its syntax can get in the way of defining requirements and
the general environment.

Links
-----

* Website Coming Soon!
* `Documentation <http://readthedocs.org/docs/virtstrap/en/latest/>`_
