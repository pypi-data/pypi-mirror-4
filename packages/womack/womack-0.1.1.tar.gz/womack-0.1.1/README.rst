======
Womack
======

Womack is a service that you can use to push realtime events between
your regular, plain-old, non-websockety web application and
clients. It is built on top of `gevent-socketio`_ and `redis`_.

Why Womack?
-----------

You want to write an application, like a game or shared calendar or
group chat or some kind of game that involves chatting about calendars
in a group. You want the convenience of writing most of your
application in the regular, stateless, blocking way you are used to
writing web applications, and access to all of the nice tools that you
have over in that box. But you also want your calendar game UI to be
snappy and realtime and not rely on polling or keeping track of game
state in two places. So you put a service like Womack in the
middle and use it to push real-time events to clients as your
blocking application receives input and does its thing in the
database or S3 or wherever.


Quickstart:
-----------

1. Install and start `redis`_

2. Clone this repository.

3. Make a `virtualenv`_, then install dependencies with ``make server``

   .. note ::

      On Windows you may need to install gevent manually.

4. Install Womack: ``python setup.py develop``

5. Start womack server: ``womack``

7. In a browser, load http://localhost:8111/test.html

8. In a python shell, enter::

     >>> import womack.publish
     >>> wm = womack.publish.Publisher()
     >>> wm.publish('hello', {'hello': 'world'})

   You should see the message *"hello world"* appear immediately in
   the browser.


Similar projects
----------------

Womack was heavily inspired by and includes some client-side code
derived from the excellent nodejs project `juggernaut`_ and the
`python client`_ for juggernaut.

Womack has slightly different internal message routing from
juggernaut, making it (in our opinion at least) more appropriate for
multi-tenant applications. And it is also easier for python
programmers to customize, since it is written in python.

About the name
--------------

`You don't know what you'll do until you're put under pressure`_ ...


.. _redis : http://redis.io/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _gevent-socketio: https://github.com/abourget/gevent-socketio
.. _juggernaut: https://github.com/maccman/juggernaut
.. _python client: https://github.com/mitsuhiko/python-juggernaut
.. _You don't know what you'll do until you're put under pressure: http://en.wikipedia.org/wiki/Across_110th_Street#Soundtrack
