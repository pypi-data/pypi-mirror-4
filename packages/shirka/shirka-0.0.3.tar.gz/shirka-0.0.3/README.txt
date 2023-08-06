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

.. code-block:: python

    python tests.py # run all tests
    python -m unittest responders.xkcd # run one test

Usage
=====

- start.py

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

- Configuration file

.. code-block:: yaml

    parameters:
        consumers: [test]
        bot.name: nono
        bot.email: no-reply@shirka.com

        remote.users: [XXX]
        remote.servers: 
            # paramiko option - http://www.lag.net/paramiko/docs/paramiko.SSHClient-class.html
            nono: {host: XXXX, username: XXXX, look_for_keys: false, password: XXXX }

        # configure flow parameterstest
        flowdock.test.organisation: shirka
        flowdock.test.flow.name:    FLOW_NAME
        flowdock.test.flow.token:   FLOW_TOKEN
        flowdock.test.user.name:    rande
        flowdock.test.user.token:   USER_TOKEN


    services:

        # Configure the bot
        bot:
            class: shirka.consumers.Bot
            arguments: [ '%bot.name%', '%bot.email%']

        # Configure shared responders
        responders.math:        { class: shirka.responders.MathResponder }
        responders.xkcd:        { class: shirka.responders.XkcdResponder }
        responders.big_bro:     { class: shirka.responders.BigbroResponder }
        responders.reminder:    { class: shirka.responders.ReminderResponder }
        responders.status:      { class: shirka.responders.StatusResponder }
        responders.rage_face:   { class: shirka.responders.RagefaceResponder }
        responders.wat:         { class: shirka.responders.WatResponder }
        responders.9gag:        { class: shirka.responders.NineGagResponder }

        responders.remote:
            class: shirka.responders.RemoteResponder
            arguments: 
                - '%remote.servers%'
                - '%remote.users%'


        # Configure flowdock push API
        flowdock.test:
            class: flowdock.FlowDock
            kwargs: 
                api_key:  '%flowdock.test.flow.token%'
                app_name: '%bot.name%'
                project:  Project test

        consumer.test.flowdock.logger:
            class: logging.getLogger
            arguments:
                - 'flowdock.%flowdock.test.flow.name%'
                
        # Configure Stream API Consumer with valid responders
        consumer.test.flowdock:
            class: shirka.consumers.FlowDockConsumer
            arguments: 
                - '@bot'
                - "%flowdock.test.flow.token%"
                - 
                    - '@responders.rage_face' 
                    - '@responders.test.whois'
                    - '@responders.math' 
                    - '@responders.big_bro'
                    - '@responders.reminder'
                    - '@responders.remote'
                    - '@responders.status'
                    - '@responders.test.help'
                    - '@responders.test.whois'
                    
                - '@flowdock.test'
            kwargs:
                logger: '@consumer.test.flowdock.logger'

        responders.test.whois:
            class: shirka.responders.FlowdockWhoisResponder
            arguments:
                - '%flowdock.test.organisation%'
                - '%flowdock.test.flow.name%'
                - '%flowdock.test.user.token%'

        responders.test.help:
            class: shirka.responders.HelpResponder
