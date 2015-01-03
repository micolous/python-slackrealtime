``python-slackrealtime``
========================

Python library for the `Slack Real-Time Messaging API`_.  Requires Twisted and Autobahn.

Currently a work in progress, not all of the protocol is implemented, and the behaviour of this library is not fully documented.

The project aims to provide a light wrapping around Slack's API in order to make objects of some of it's constructs, and provide some convenience functionality (such as converting timestamps to fully-fledged ``datetime`` objects).  As such, the API will adapt (to a degree) to Slack RTM API changes.

It also includes a very thin wrapper around Slack's `REST API`_ (``slackrealtime.api``), for the purposes of setting up the initial connection.

It is designed primarily to allow writing bots that interact with the Slack API.

LGPLv3+ license.

There **also** exists a Python library written by Slack themselves which doesn't use Twisted, `python-slackclient`_.

.. _Slack Real-Time Messaging API: https://api.slack.com/rtm
.. _REST API: https://api.slack.com/
.. _python-slackclient: https://github.com/slackhq/python-slackclient

Installing the dev version
--------------------------

In order to install the development version from the git repository::

  $ pip install 'git+git://github.com/micolous/python-slackrealtime.git#egg=slackrealtime'

This can also be included in a ``requirements.txt`` file like this::

  git+git://github.com/micolous/python-slackrealtime.git#egg=slackrealtime

Getting an API token
--------------------

There are two ways to get an API token for this library:

* Use the `Slack Web API`_ page to create a token for your user.
* Add a Bots integration to your team (which issues an ``xoxb`` token, which has some additional restrictions).

.. _Slack Web API: https://api.slack.com/web

This library does not presently support OAuth or other such authentication mechanisms, only static API tokens.

