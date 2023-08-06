========================
NutJob Nutcracker Client
========================

The NutJob client is an alternate Redis client based on
``redis.StrictRedis``.  It is meant for use with Turnstile, in
conjunction with the Redis proxy nutcracker, aka twemproxy.  Certain
functionality which is unsupported by nutcracker is overridden in
NutJob, either to disable it (such as Turnstile's ``PUBLISH`` to
report errors) or to replace it with equivalent functionality (such as
the ``register_script()`` call used by the Turnstile compactor
daemon).

NutJob is really only intended for use with Turnstile; it is not meant
as a general-purpose Redis/nutcracker client.

How to Use
==========

To use NutJob, add the following configuration settings to the
appropriate sections of your Turnstile configuration::

    [redis]
    redis_client = nutjob
    server_version = <see text>
    host = <nutcracker IP>

    [control]
    redis_client = redis
    server_version =
    host = <Redis server IP>

Note the overrides in the ``[control]`` section, particularly the
explicitly empty value of ``server_version``: the Turnstile control
daemon MUST be configured to use the standard Redis client and to
connect to an actual Redis server; the control daemon relies on
functionality that nutcracker does not support.

As for the ``server_version`` value in the ``[redis]`` section: this
value is optional, but if set, it should be the minimum server version
of the Redis servers connected behind the nutcracker proxy.  This
information is used by the Turnstile compactor daemon to enable an
optimization; normally, the compactor daemon determines whether to use
this optimization based on the server version reported by the Redis
server itself, but nutcracker does not support this version retrieval,
and so NutJob provides this ``server_version`` side channel to allow
its use.
