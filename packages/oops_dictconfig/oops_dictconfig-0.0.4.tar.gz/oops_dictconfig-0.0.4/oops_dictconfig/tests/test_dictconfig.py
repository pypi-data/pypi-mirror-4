# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

from testtools import TestCase

import oops
import oops_amqp
from oops_datedir_repo import DateDirRepo

from oops_dictconfig.dictconfig import config_from_dict


class ConfigFromDictTests(TestCase):

    def get_config_from_dict(self, publishers):
        dict_config = dict(publishers=publishers)
        return config_from_dict(dict_config)

    def test_empty_dict_gets_config_instance(self):
        config = config_from_dict({})
        self.assertIsInstance(config, oops.Config)

    def test_empty_dict_gets_no_publishers(self):
        config = config_from_dict({})
        self.assertEqual(0, len(config.publishers))

    def test_empty_publishers_list_gives_no_publishers(self):
        config = self.get_config_from_dict([])
        self.assertEqual(0, len(config.publishers))

    def test_missing_publisher_type_gives_exception(self):
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [dict()])
        self.assertEqual('Missing publisher type: {}', e.message)

    def test_unknown_publisher_type_gives_exception(self):
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [dict(type='unknown')])
        self.assertEqual('Unknown publisher type: unknown', e.message)

    def test_datedir_missing_error_dir_gives_exception(self):
        publisher_defn = dict(type='datedir')
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing error_dir key: %s' % str(publisher_defn),
                e.message)

    def test_datedir_gives_datedir_publisher(self):
        publisher_defn = dict(type='datedir', error_dir=self.getUniqueString())
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(1, len(config.publishers))
        self.assertIsInstance(config.publishers[0].im_self, DateDirRepo)

    def test_datedir_sets_error_dir_on_repo(self):
        error_dir = self.getUniqueString()
        publisher_defn = dict(type='datedir', error_dir=error_dir)
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(error_dir, config.publishers[0].im_self.root)

    def test_datedir_sets_inherit_id_on_repo(self):
        inherit_id = True
        publisher_defn = dict(type='datedir', error_dir=self.getUniqueString(),
                inherit_id=inherit_id)
        config = self.get_config_from_dict([publisher_defn])
        self.assertEquals(inherit_id, config.publishers[0].im_self.inherit_id)

    def test_datedir_sets_stash_path_on_repo(self):
        stash_path = True
        publisher_defn = dict(type='datedir', error_dir=self.getUniqueString(),
                stash_path=stash_path)
        config = self.get_config_from_dict([publisher_defn])
        self.assertEquals(stash_path, config.publishers[0].im_self.stash_path)

    def test_datedir_wraps_if_new_only(self):
        """If new_only is set in the definition then the publisher method is wrapped."""
        publisher_defn = dict(type='datedir', error_dir=self.getUniqueString(),
                new_only=True)
        config = self.get_config_from_dict([publisher_defn])
        # FIXME: brittle test, dependent on implementation details of
        #   oops.publish_new_only. Find a better way of testing that the
        #   publish method was wrapped by oops.publish_new_only
        self.assertEquals('result', config.publishers[0].func_name)

    def test_datedir_doesnt_wrap_if_new_only_is_False(self):
        publisher_defn = dict(type='datedir', error_dir=self.getUniqueString(),
                new_only=False)
        config = self.get_config_from_dict([publisher_defn])
        # FIXME: brittle test, dependent on implementation details of
        #   oops.publish_new_only. Find a better way of testing that the
        #   publish method was not wrapped by oops.publish_new_only
        self.assertEquals('publish', config.publishers[0].func_name)

    def test_amqp_missing_exchange_name_gives_error(self):
        publisher_defn = dict(type='amqp')
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing exchange_name key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_missing_routing_key_gives_error(self):
        publisher_defn = dict(type='amqp', exchange_name=self.getUniqueString())
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing routing_key key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_missing_host_gives_error(self):
        publisher_defn = dict(type='amqp', exchange_name=self.getUniqueString(),
                routing_key=self.getUniqueString())
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing host key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_missing_user_gives_error(self):
        publisher_defn = dict(type='amqp', exchange_name=self.getUniqueString(),
                routing_key=self.getUniqueString(), host=self.getUniqueString())
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing user key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_missing_password_gives_error(self):
        publisher_defn = dict(type='amqp', exchange_name=self.getUniqueString(),
                routing_key=self.getUniqueString(), host=self.getUniqueString(),
                user=self.getUniqueString())
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing password key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_missing_vhost_gives_error(self):
        publisher_defn = dict(type='amqp', exchange_name=self.getUniqueString(),
                routing_key=self.getUniqueString(), host=self.getUniqueString(),
                user=self.getUniqueString(), password=self.getUniqueString())
        e = self.assertRaises(AssertionError,
                self.get_config_from_dict, [publisher_defn])
        self.assertEqual('Missing vhost key: %s' % str(publisher_defn),
                e.message)

    def test_amqp_gives_amqp_publisher(self):
        publisher_defn = self.get_basic_ampq_definition()
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(1, len(config.publishers))
        self.assertIsInstance(config.publishers[0], oops_amqp.Publisher)

    def get_basic_ampq_definition(self):
        return dict(type='amqp', exchange_name=self.getUniqueString(),
                routing_key=self.getUniqueString(), host=self.getUniqueString(),
                user=self.getUniqueString(), password=self.getUniqueString(),
                vhost=self.getUniqueString())

    def test_amqp_sets_exchange_name(self):
        publisher_defn = self.get_basic_ampq_definition()
        exchange_name = publisher_defn['exchange_name']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(exchange_name, config.publishers[0].exchange_name)

    def test_amqp_sets_routing_key(self):
        publisher_defn = self.get_basic_ampq_definition()
        routing_key = publisher_defn['routing_key']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(routing_key, config.publishers[0].routing_key)

    def test_amqp_sets_host(self):
        publisher_defn = self.get_basic_ampq_definition()
        host = publisher_defn['host']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(
            host, config.publishers[0].connection_factory.keywords['host'])

    def test_amqp_sets_user(self):
        publisher_defn = self.get_basic_ampq_definition()
        user = publisher_defn['user']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(
            user, config.publishers[0].connection_factory.keywords['userid'])

    def test_amqp_sets_password(self):
        publisher_defn = self.get_basic_ampq_definition()
        password = publisher_defn['password']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(
            password,
            config.publishers[0].connection_factory.keywords['password'])

    def test_amqp_sets_vhost(self):
        publisher_defn = self.get_basic_ampq_definition()
        vhost = publisher_defn['vhost']
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(
            vhost,
            config.publishers[0].connection_factory.keywords['virtual_host'])

    def test_amqp_sets_insist(self):
        publisher_defn = self.get_basic_ampq_definition()
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(
            False,
            config.publishers[0].connection_factory.keywords['insist'])

    def test_amqp_sets_inherit_id(self):
        publisher_defn = self.get_basic_ampq_definition()
        publisher_defn['inherit_id'] = True
        config = self.get_config_from_dict([publisher_defn])
        self.assertEqual(True, config.publishers[0].inherit_id)

    def test_amqp_wraps_if_new_only(self):
        """If new_only is set in the definition then the publisher method is wrapped."""
        publisher_defn = self.get_basic_ampq_definition()
        publisher_defn['new_only'] = True
        config = self.get_config_from_dict([publisher_defn])
        # FIXME: brittle test, dependent on implementation details of
        #   oops.publish_new_only. Find a better way of testing that the
        #   publish method was wrapped by oops.publish_new_only
        self.assertEquals('result', config.publishers[0].func_name)

    def test_amqp_doesnt_wrap_if_new_only_is_False(self):
        publisher_defn = self.get_basic_ampq_definition()
        publisher_defn['new_only'] = False
        config = self.get_config_from_dict([publisher_defn])
        # FIXME: brittle test, dependent on implementation details of
        #   oops.publish_new_only. Find a better way of testing that the
        #   publish method was not wrapped by oops.publish_new_only
        self.assertIsInstance(config.publishers[0], oops_amqp.Publisher)

    def test_no_template_gives_blank_template(self):
        config = config_from_dict(dict())
        self.assertEqual({}, config.template)

    def test_empty_template_gives_blank_template(self):
        config = config_from_dict(dict(template={}))
        self.assertEqual({}, config.template)

    def test_non_empty_template_gives_non_empty_template(self):
        config = config_from_dict(dict(template=dict(foo='bar')))
        self.assertEqual(dict(foo='bar'), config.template)
