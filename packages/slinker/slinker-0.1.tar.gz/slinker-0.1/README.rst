Slinker
=======

Slinker provide a single one to one event, we call it a ``link``.

A ``link`` can only have a single sender and a single reciver.


The source code is locate at `github <https://github.com/youngking/slinker>`_ .

.. image:: https://travis-ci.org/youngking/slinker.png?branch=master
   :alt: Build Status


Introduction
------------------

Link receiver can subscribe to specific link. A reciver function required
a sender argument, and a keyworld argument which is optional.

  >>> from slinker import Namespace
  >>> links = Namespace()
  >>> started = links.link('round-started')
  >>> def each(round):
  ...     print "Round %s!" % round
  ...
  >>> started.connect(each)
  >>> for round in range(1, 4):
  ...     started.send(round)
  ...
  Round 1!
  Round 2!
  Round 3!

Here provide a decorator ``receiver`` which can be used for connect. Because a
link can only have one reciever. If you want to connect to another receiver, 
you must disconnect the formly receiver.

  >>> started.disconnect(each)
  >>> from slinker import receiver
  >>> @receiver(started)
      def test(sender, **kwargs):
  ...     return sender
  >>> func, result = started.send('hello')
  >>> func == test
  ... True
  >>> result == 'hello'
  ...  True


More examples
----------------

see the ``tests`` directory.
