# Copyright 2013 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import redis


class NutJobStrictRedis(redis.StrictRedis):
    """
    A replacement for ``redis.StrictRedis`` which allows Turnstile to
    communicate properly with the nutcracker Redis proxy.  Turnstile's
    use of ``PUBLISH`` for error reporting is ignored, rather than
    being passed on to the proxy.  The Turnstile compactor daemon's
    use of LUA scripts is also enabled by redefining the
    ``redis.client.Script`` class to not attempt to use ``SCRIPT
    LOAD``, which is unsupported by nutcracker.

    Note that the Turnstile control daemon CANNOT use this client; you
    must set ``control.redis.redis_client`` to "redis" and set
    ``control.redis.server_version`` to nothing.  This also, of
    course, means that the control daemon CANNOT connect to
    nutcracker; it must connect directly to a Redis database.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ``NutJobStrictRedis`` client.  Takes only
        keyword arguments; positional arguments are not recognized.
        Also adds one optional keyword argument, ``server_version``,
        which provides the minimum version of the Redis servers behind
        the nutcracker proxy; this defaults to "2.4" if not provided.
        """

        # Save the redis version, if one is provided
        self.redis_version = kwargs.pop('server_version', '2.4')

        super(NutJobStrictRedis, self).__init__(**kwargs)

    def info(self):
        """
        Returns a dictionary containing information about the Redis
        server.  Since nutcracker does not support ``INFO`` (it
        doesn't know which server to pass the request on to), this
        implementation returns a dictionary of one
        key--"redis_version"--and bases the value of the key on the
        value passed in to the constructor (if any).
        """

        return {'redis_version': self.redis_version}

    def publish(self, channel, message):
        """
        Publish ``message`` on ``channel``.  Returns the number of
        subscribers the message was delivered to.  This variant does
        not call out to Redis, since nutcracker does not support
        ``PUBLISH``.
        """

        return 0

    def register_script(self, script):
        """
        Register a LUA ``script`` specifying the ``keys`` it will
        touch.  Returns a Script object that is callable and hides the
        complexity of deal with scripts, keys, and shas. This is the
        preferred way to work with LUA scripts.
        """

        return NutJobScript(self, script)


class NutJobScript(object):
    """
    The nutcracker proxy supports ``EVAL`` and ``EVALSHA``, but oddly
    not ``SCRIPT LOAD``, which is an integral component of
    ``redis.StrictRedis``'s support for LUA scripts.  This variant of
    ``redis.client.Script`` avoids the use of ``SCRIPT LOAD`` and
    calls ``EVAL`` directly; this is less efficient, but allows the
    scripting feature of recent Redis to be used.
    """

    def __init__(self, registered_client, script):
        """
        Initialize a ``NutJobScript`` object.

        :param registered_client: The client the script is associated
                                  with.
        :param script: The text of the script.
        """

        self.registered_client = registered_client
        self.script = script

    def __call__(self, keys=[], args=[], client=None):
        """
        Call the script with the provided keys and arguments.

        :param keys: A list of the keys the script is to act upon.
        :param args: A list of arguments (besides keys) to pass to the
                     script.
        :param client: An alternate client to use for executing the
                       script.

        :returns: The results of calling the script on the server.
        """

        client = client or self.registered_client
        args = tuple(keys) + tuple(args)

        # Call the script
        return client.eval(self.script, len(keys), *args)
