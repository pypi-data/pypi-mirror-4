=================
Tom's Best Friend
=================

Tom's Best Friend is a `TOML <https://github.com/mojombo/toml>`_ parser for
people with deadlines. No, sorry. For humans. No, dammit, all the good taglines
are taken.

.. code-block:: python

    >>> from pprint import pprint
    >>> from tomsbestfriend import loads

    >>> pprint(
    ...     loads(
    ...     """
    ...     [cartoons]
    ...     characters = ["filbert", "heffer"]
    ...     hilarious = true
    ...
    ...     [cartoons.info]
    ...     episodes = 52
    ...     """
    ...     )
    ... )
    {'cartoons': {'characters': [u'filbert', u'heffer'],
                  'hilarious': True,
                  'info': {'episodes': 52}}}


Contributing
------------

I'm Julian Berman.

``TomsBestFriend`` is on `GitHub <http://github.com/Julian/TomsBestFriend>`_.

Get in touch, via GitHub or otherwise, if you've got something to contribute,
it'd be most welcome!

You can also generally find me on Freenode (nick: ``tos9``) in various
channels, including ``#python``.
