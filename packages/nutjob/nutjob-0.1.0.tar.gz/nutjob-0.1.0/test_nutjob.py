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

import mock
import redis
import unittest2

import nutjob


class TestNutJobStrictRedis(unittest2.TestCase):
    @mock.patch.object(redis.StrictRedis, '__init__')
    def test_init_noversion(self, mock_init):
        nj = nutjob.NutJobStrictRedis(a=1, b=2, c=3)

        self.assertEqual(nj.redis_version, '2.4')
        mock_init.assert_called_once_with(a=1, b=2, c=3)

    @mock.patch.object(redis.StrictRedis, '__init__')
    def test_init_withversion(self, mock_init):
        nj = nutjob.NutJobStrictRedis(a=1, b=2, c=3, server_version='2.6')

        self.assertEqual(nj.redis_version, '2.6')
        mock_init.assert_called_once_with(a=1, b=2, c=3)

    @mock.patch.object(redis.StrictRedis, '__init__')
    @mock.patch.object(redis.StrictRedis, 'execute_command')
    def test_info(self, mock_execute_command, mock_init):
        nj = nutjob.NutJobStrictRedis(server_version='2.6')

        result = nj.info()

        self.assertEqual(result, {'redis_version': '2.6'})
        self.assertFalse(mock_execute_command.called)

    @mock.patch.object(redis.StrictRedis, '__init__')
    @mock.patch.object(redis.StrictRedis, 'execute_command')
    def test_publish(self, mock_execute_command, mock_init):
        nj = nutjob.NutJobStrictRedis()

        result = nj.publish('channel', 'message')

        self.assertEqual(result, 0)
        self.assertFalse(mock_execute_command.called)

    @mock.patch.object(redis.StrictRedis, '__init__')
    @mock.patch.object(redis.StrictRedis, 'execute_command')
    @mock.patch.object(nutjob, 'NutJobScript', return_value='script obj')
    def test_register_script(self, mock_NutJobScript,
                             mock_execute_command, mock_init):
        nj = nutjob.NutJobStrictRedis()

        result = nj.register_script("this is a script")

        self.assertEqual(result, 'script obj')
        self.assertFalse(mock_execute_command.called)
        mock_NutJobScript.assert_called_once_with(nj, "this is a script")


class TestNutJobScript(unittest2.TestCase):
    def test_init(self):
        client = mock.Mock()

        script = nutjob.NutJobScript(client, "this is a script")

        self.assertEqual(script.registered_client, client)
        self.assertEqual(script.script, "this is a script")
        self.assertEqual(client.mock_calls, [])

    def test_call(self):
        client = mock.Mock(**{'eval.return_value': 'script result'})
        script = nutjob.NutJobScript(client, "this is a script")

        result = script(['key1', 'key2'], ['arg1', 'arg2'])

        self.assertEqual(result, 'script result')
        client.eval.assert_called_once_with(
            "this is a script", 2, 'key1', 'key2', 'arg1', 'arg2')

    def test_call_altclient(self):
        client = mock.Mock(**{'eval.return_value': 'normal client'})
        altcli = mock.Mock(**{'eval.return_value': 'alternate client'})
        script = nutjob.NutJobScript(client, "this is a script")

        result = script(client=altcli)

        self.assertEqual(result, 'alternate client')
        self.assertEqual(client.mock_calls, [])
        altcli.eval.assert_called_once_with("this is a script", 0)
