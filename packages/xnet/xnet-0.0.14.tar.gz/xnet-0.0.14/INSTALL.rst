
============================================
Xnet install instructions
============================================

Debian 6
========

Development packages are needed to build a newer gevent
than what debian ships with.

    $ sudo apt-get install gcc
    $ sudo apt-get install libevent-dev
    $ sudo apt-get install python-dev
    $ sudo apt-get install python-pip

Optional if you want to contain xnet in a local directory
instead of making a system installation.

    $ sudo apt-get install python-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

Now install gevent and finally xnet.

    $ pip install gevent==0.13.8
    $ pip install xnet


OSX
===

For some reason, gevent 0.13.8 misbehaves under OSX, but the development
release 1.0rc2 works quite OK. This must be compiled so Xcode is a requirement.
The list below is probably incomplete. I'm developing on OSX Lion but I don't
remember all the prerequisites. Drop me a mail and tell me what's missing:

Optional if you want to contain xnet in a local directory
instead of making a system installation.

    $ sudo port install py-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

And then gevent.

    $ pip install cython -e git://github.com/surfly/gevent.git@1.0rc2#egg=gevent

