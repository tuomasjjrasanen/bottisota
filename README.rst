===========
 Bottisota
===========

Bottisota is a programming game where players program battle bot
AIs. All bots are identical, it's the AI which makes all the
difference.

Similar projects:
 - TclBots
 - Realtime battle

Objects
=======

- Bots

Bot
---

A mobile programmable weapon platform.

Attributes
~~~~~~~~~~

- x coordinate: integer
- y coordinate: integer
- heading: integer
- speed: integer

Bot Control Protocol
~~~~~~~~~~~~~~~~~~~~

+-----------------------+---------------------------+
|Call message           |Return message             |
+=======================+===========================+
|``POS?``               |``POS= x y speed heading`` |
+-----------------------+---------------------------+
|``CLK?``               |``CLK= tick``              |
+-----------------------+---------------------------+
|``DRV? speed heading`` |``DRV= status``            |
+-----------------------+---------------------------+

Build and install
=================

Simply just run::
    python3 setup.py build
    python3 setup.py install --user
