``python-slackrealtime``
========================

Python library for the `Slack Real-Time Messaging API`_.  Requires Twisted and Autobahn.

Currently a work in progress, not all of the protocol is implemented, and the behaviour of this library is not fully documented.

The project aims to provide a light wrapping around Slack's API in order to make objects of some of it's constructs, and provide some convenience functionality (such as converting timestamps to fully-fledged ``datetime`` objects).  As such, the API will adapt (to a degree) to Slack RTM API changes.

It also includes a very thin wrapper around Slack's `REST API`_ (``slackrealtime.api``), for the purposes of setting up the initial connection.

It is designed primarily to allow writing bots that interact with the Slack API.  I have a `repository with examples available`_.

LGPLv3+ license.

There **also** exists a Python library written by Slack themselves which doesn't use Twisted, `python-slackclient`_.

.. _Slack Real-Time Messaging API: https://api.slack.com/rtm
.. _REST API: https://api.slack.com/
.. _repository with examples available: https://github.com/micolous/slackbots
.. _python-slackclient: https://github.com/slackhq/python-slackclient


Installing the dev version
--------------------------

You'll need to install non-Python dependencies::

  # apt-get install libffi-dev python-dev build-essential

In order to install the development version from the git repository::

  $ pip install 'git+https://github.com/micolous/python-slackrealtime.git#egg=slackrealtime'

This can also be included in a ``requirements.txt`` file like this::

  git+https://github.com/micolous/python-slackrealtime.git#egg=slackrealtime

Getting an API token
--------------------

There are three ways to get an API token for this library:

* ``xoxb``: Add a Bots integration to your team, which has some `additional restrictions`_.
* ``xoxp``: Use the `Legacy Token Generator`_ to create a token for your user, or implement OAuth2 (batteries not included).
* ``xoxs``: Scrape the Slack Web UI for a variable called ``boot_data.api_token``, which additionally allows you access to the ``users.admin`` family of undocumented methods.

.. _Legacy Token Generator: https://api.slack.com/custom-integrations/legacy-tokens
.. _additional restrictions: https://api.slack.com/bot-users

This library does not presently support OAuth or other such authentication mechanisms, only static API tokens.

