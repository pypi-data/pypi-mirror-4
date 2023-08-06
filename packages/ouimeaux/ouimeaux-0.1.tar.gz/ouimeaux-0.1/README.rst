========
ouimeaux
========

ouimeaux is a Python interface to `Belkin WeMo`_ devices. It uses gevent_
for async I/O and requests_ for communication with the devices. It also
provides a minimal command-line interface for discovery and switch toggling.

.. contents::
   :depth: 3

Python API
~~~~~~~~~~

Environment
-----------
The main interface is presented by an ``Environment``, which optionally accepts
functions called when a Switch or Motion device is identified::

    >>> from ouimeaux.environment import Environment
    >>>
    >>> def on_switch(switch):
    ...     print "Switch found!", switch.name
    ...
    >>> def on_motion(motion):
    ...     print "Motion found!", switch.motion
    ...
    >>> env = Environment(on_switch, on_motion)

Discovery of all WeMo devices in an environment is then straightforward; simply
pass the length of time (in seconds) you want discovery to run::

    >>> env.discover(seconds=3)
    Switch found! Living Room

During that time, the ``Environment`` will continually broadcast search requests
and parse responses. At any point, you can see the names of discovered devices::

    >>> env.list_switches()
    ['Living Room', 'TV Room', 'Front Closet']
    >>> env.list_motions()
    ['Front Hallway']

Devices can be retrieved by using ``get_switch`` and ``get_motion`` methods::

    >>> switch = env.get_switch('TV Room')
    >>> switch
    <WeMo Switch "TV Room">

Devices
-------
All devices have an ``explain()`` method, which will print out a list of all
available services, as well as the actions and arguments to those actions
on each service::

    >>> switch.explain()

    basicevent
    ----------
      SetSmartDevInfo(SmartDevURL)
      SetServerEnvironment(ServerEnvironmentType, TurnServerEnvironment, ServerEnvironment)
      GetDeviceId()
      GetRuleOverrideStatus(RuleOverrideStatus)
      GetIconURL(URL)
      SetBinaryState(BinaryState)
    ...

Services and actions are available via simple attribute access. Calling actions
returns a dictionary of return values::

    >>> switch.basicevent.SetBinaryState(BinaryState=0)
    {'BinaryState': 0}

Switches
--------
Switches have three shortcut methods defined: ``get_state``, ``on`` and ``off``.

Motions
-------
Motions currently don't have any shortcut methods defined.


.. _gevent: http://www.gevent.org/
.. _requests: http://docs.python-requests.org/en/latest/
.. _Belkin WeMo: http://www.belkin.com/us/wemo


Command Line
~~~~~~~~~~~~
The ``wemo`` script will discover devices in your environment and turn
switches on and off. To list devices::

    $ wemo list

Default is to search for 5 seconds; you can pass ``--timeout`` to change that.

To turn a switch on and off, you first have to know the name. Then::

    $ wemo switch "TV Room" on
    $ wemo switch "TV Room" off

