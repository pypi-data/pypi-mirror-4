Heka Configuration
--------------------

To assist with getting a working Heka set up, heka-py provides a
:doc:`api/config` module which will take declarative configuration info in
either ini file or python dictionary format and use it to configure a
HekaClient instance. Even if you choose not to use these configuration
helpers, this document provides a good overview of the configurable options
provided by default by the :doc:`api/client` client class.

The config module will accept configuration data either in ini format (as a
text value or a stream input) or as a Python dictionary value. This document
will first describe the supported ini file format, followed by the
corresponding dictionary format to which the ini format is ultimately
converted behind the scenes.

ini format
==========

The primary `HekaClient` configuration should be provided in a `heka`
section of the provided ini file text. (Note that the actual name of the
section is passed in to the config parsing function, so it can be any legal ini
file section name, but for illustration purposes these documents will assume
that the section name is `heka`.) A sample `heka` section might look like
this::

  [heka]
  logger = myapp
  severity = 4
  disabled_timers = foo
                    bar
  sender_class = heka.senders.zmq.ZmqPubSender
  sender_bindstrs = tcp://127.0.0.1:5565
  sender_queue_length = 5000
  global_disabled_decorators = incr_count

Of all of these settings, only `sender_class` is strictly required. A detailed
description of each option follows:

logger
  Each heka message that goes out contains a `logger` value, which is simply
  a string token meant to identify the source of the message, usually the
  name of the application that is running. This can be specified separately for
  each message that is sent, but the client supports a default value which will
  be used for all messages that don't explicitly override. The `logger` config
  option specifies this default value. This value isn't strictly required, but
  if it is omitted '' (i.e. the empty string) will be used, so it is strongly
  suggested that a value be set.

severity
  Similarly, each heka message specifies a `severity` value corresponding to
  the integer severity values defined by `RFC 3164
  <https://www.ietf.org/rfc/rfc3164.txt>`_. And, again, while each message can
  set its own severity value, if one is omitted the client's default value will
  be used. If no default is specified here, the default default (how meta!)
  will be 6, "Informational".

disabled_timers
  Heka natively supports "timer" behavior, which will calculate the amount of
  elapsed time taken by an operation and send that data along as a message to
  the back end. Each timer has a string token identifier. Because the act of
  calculating code performance actually impacts code performance, it is
  sometimes desirable to be able to activate and deactivate timers on a case by
  case basis. The `disabled_timers` value specifies a set of timer ids for
  which the client should NOT actually generate messages. Heka will attempt
  to minimize the run-time impact of disabled timers, so the price paid for
  having deactivated timers will be very small. Note that the various timer ids
  should be newline separated.

sender_class
  This should be a Python dotted notation reference to a class (or factory
  function) for a Heka "sender" object. A sender needs to provide a
  `send_message(msg)` method, which is responsible for serializing the message
  and passing it along to the router / back end / output mechanism /
  etc. heka-py provides some development senders, but the main one it
  provides for intended production use makes use of ZeroMQ (using the pub/sub
  pattern) to broadcast the messages to any configured listeners.

sender_*
  As you might guess, different types of senders can require different
  configuration values. Any config options other than `sender_class` that start
  with `sender_` will be passed to the sender factory as keyword arguments,
  where the argument name is the option name minus the `sender_` component and
  the value is the specified value. In the example above, the ZeroMQ bind
  string and the queue length will be passed to the ZmqPubSender constructor.

global_*
  Any configuration value prefaced with `global_` represents an option that is
  global to all Heka clients process-wide and not just the client being
  configured presently.

In addition to the main `heka` section, any other config sections that start
with `heka_` (or whatever section name is specified) will be considered to be
related to the heka installation. Only specific variations of these are
supported, however. The first of these is configuration for HekaClient
:doc:`api/filters`. Here is an example of such a configuration::

  [heka_filter_sev_max]
  provider = heka.filters.severity_max_provider
  severity = 4

  [heka_filter_type_whitelist]
  provider = heka.filters.type_whitelist_provider
  types = timer
          oldstyle

Each `heka_filter_*` section must contain a `provider` entry, which is a
dotted name specifying a filter provider function. The rest of the options in
that section will be converted into configuration parameters. The provider
function will be called and passed the configuration parameters, returning a
filter function that will be added to the client's filters. The filters will be
applied in the order they are specified. In this case a "severity max" filter
will be applied, so that only messages with a severity of 4 (i.e. "warning") or
lower will actually be passed in to the sender. Additionally a "type whitelist"
will be applied, so that only messages of type "timer" and "oldstyle" will be
delivered.


plugins
=======

Heka allows you to bind new extensions onto the client through a plugin
mechanism.

Each plugin must have a configuration section name with a prefix of
`heka_plugin_`.  Configuration is parsed into a dictionary, passed into a
configurator and then the resulting plugin method is bound to the client.

Each configuration section for a plugin must contain at least one option with
the name `provider`. This is a dotted name for a function which will be used to
configure a plugin.  The return value for the provider is a configured method
which will then be bound into the Heka client.

Each plugin extension method has a canonical name that is bound to the
heka client as a method name. The suffix that follows the
`heka_plugin_` prefix is used only to distinguish logical sections
for each plugin within the configuration file.

An example best demonstrates what can be expected.  To load the dummy plugin,
you need a `heka_plugin_dummy` section as well as some configuration
parameters. Here's an example ::

    [heka_plugin_dummysection]
    provider=heka.tests.plugin.config_plugin
    port=8080
    host=localhost

Once you obtain a reference to a client, you can access the new method. ::

    from heka.holder import CLIENT_HOLDER
    client = CLIENT_HOLDER.get_client('your_app_name')
    client.dummy('some', 'ignored', 'arguments', 42)


dictionary format
=================

When using the `client_from_text_config` or `client_from_stream_config`
functions of the config module to parse an ini format configuration, heka-py
simply converts these values to a dictionary which is then passed to
`client_from_dict_config`. If you choose to not use the specified ini format,
you can parse configuration yourself and call `client_from_dict_config`
directly. The configuration specified in the "ini format" section above would
be converted to the following dictionary::

  {'logger': 'myapp',
   'severity': 4,
   'disabled_timers': ['foo', 'bar'],
   'sender': {'class': 'heka.senders.zmq.ZmqPubSender',
              'bindstrs': 'tcp://127.0.0.1:5565',
              'queue_length': 5000,
    },
   'global': {'disabled_decorators': ['incr_count']},
   'filters': [('heka.filters.severity_max',
                {'severity': 4},
                ),
               ('heka.filters.type_whitelist',
                {'types': ['timer', 'oldstyle']},
                ),
   ],
   }

To manually load a Heka client with plugins, the `client_from_dict_config`
function allows you to pass in a list of plugin configurations using the
`plugins` dict key, used in the same fashion as `filters` in the example
directly above.

The configuration specified in the "plugins" section above would be converted
into the following dictionary, where the key will be the name of the method
bound to the client::

    {'dummy': ('heka.tests.plugin:config_plugin',
               {'port': 8080,
                'host': 'localhost'
                },
    )
    }


Debugging your configuration
============================

You may find yourself with a heka client which is not behaving
in a manner that you expect.  Heka provides a deepcopy of the
configuration that was used when the client was instantiated for
debugging purposes.

The following code shows how you can verify that the configuration
used is actually what you expect it to be ::

    cfg = {'logger': 'addons-marketplace-dev',
           'sender': {'class': 'heka.senders.UdpSender',
           'host': ['logstash1', 'logstash2'],
           'port': '5566'}}
    client = client_from_dict_config(cfg)
    assert client._config == json.dumps(cfg)
