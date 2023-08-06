======
Shirka
======

This a bot based on twisted, mostly a python learning project

Consumers
=========

* flowdock: read message from flow dock stream API

Responders
==========

* face
* whois
* math
* wat
* xkcd
* ascii
* 9gag

Installation
============

Install dependencies::

    pip install twisted
    pip install twistedhttpstream
    pip install requests
    pip install sympy
    pip install mocker
    pip install pyopenssl
    pip install python-flowdock
    pip install markdown
    pip install paramiko
    pip install pyyaml
    pip install ioc

Running Tests
=============

    python tests.py # run all tests
    python -m unittest responders.xkcd # run one test

Usage
=====

.. code-block:: python

    # vim: set fileencoding=utf-8 :

    import twistedhttpstream, yaml, sys, logging
    from twisted.internet import reactor
    import ioc

    logging.basicConfig(level=logging.DEBUG)

    container = ioc.build([
        'config.yml',
    ])

    if __name__ == "__main__":

        for flow in container.parameters['consumers']:
            twistedhttpstream.stream(
                reactor, 
                "https://stream.flowdock.com/flows/%s/%s" % (container.parameters["flowdock.%s.organisation" % flow], flow), 
                container.get("consumer.%s.flowdock" % flow), 
                username=container.parameters["flowdock.%s.user.token" % flow], 
                password=""
            )
        

        reactor.run()
