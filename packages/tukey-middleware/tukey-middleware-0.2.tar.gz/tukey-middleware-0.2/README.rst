=============================
Tukey Middleware
=============================

Tukey is a console for managing cloud resources particularly IaaS clouds.
Tukey is built on the OpenStack Dashboard, Horizon, and provides the
additional functionality of interacting with ec2 compatible clouds and
authentication via Shibboleth and OpenID.

Tukey Middleware provides access to multiple cloud resources using the 
a subset of the OpenStack Identity and Compute JSON APIs. Clouds currently
supported are Eucalyptus and OpenStack.

For info go to:

 * http://opensciencedatacloud.org

Dependencies
============

For Ubuntu use apt to install::

    $ sudo apt-get install python-virtualenv postgresql-9.1 postgresql-server-dev-9.1 swig build-essential memcached
    $ sudo apt-get build-dep python-psycopg2
    

Getting Started
===============

For local development, first create a virtualenv for the project.
In the ``tools`` directory there is a script to create one for you::

  $ python tools/install_venv.py


There are three main proxies you will need to start: the authentication
service the nova proxy and the glance proxy
Run the start up scripts for each service::

  $ ./auth.sh
  $ ./nova.sh
  $ ./glance.sh
