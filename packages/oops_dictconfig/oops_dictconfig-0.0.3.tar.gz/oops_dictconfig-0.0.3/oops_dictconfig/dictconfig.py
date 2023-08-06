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

import oops


def _amqp_publisher_from_defn(publisher_defn):
    from oops_amqp import Publisher
    from functools import partial
    from amqplib import client_0_8 as amqp
    args = {}
    for arg in ('exchange_name', 'routing_key', 'host', 'user', 'password',
                'vhost'):
        args[arg] = publisher_defn.get(arg)
        if args[arg] is None:
            raise AssertionError(
                    "Missing %s key: %s" % (arg, str(publisher_defn)))
    factory = partial(amqp.Connection,
            host=args['host'],
            userid=args['user'],
            password=args['password'],
            virtual_host=args['vhost'],
            insist=False
        )
    kwargs = {}
    if 'inherit_id' in publisher_defn:
        kwargs['inherit_id'] = publisher_defn.get('inherit_id')
    return Publisher(factory, args['exchange_name'],
            args['routing_key'], **kwargs)


def _datedir_repo_from_defn(publisher_defn):
    from oops_datedir_repo import DateDirRepo
    kwargs = {}
    error_dir = publisher_defn.get('error_dir')
    if error_dir is None:
        raise AssertionError(
                "Missing error_dir key: %s" % str(publisher_defn))
    for arg in ('inherit_id', 'stash_path'):
        if arg in publisher_defn:
            kwargs[arg] = publisher_defn[arg]
    return DateDirRepo(error_dir, **kwargs).publish


publishers = {
    'amqp': _amqp_publisher_from_defn,
    'datedir': _datedir_repo_from_defn,
    }


def config_from_dict(dict_config):
    """Create an `oops.Config` object from `dict_config`.

    Given a description of an oops config in the form of a dictionary
    this function will create the `oops.Config` to match.

    This allows you to have some flexibilty in your code about how
    exactly the oopses will be handled in different environments.
    Hooking this up to your config system means that you can
    change between oops delivery methods with a simple config change,
    rather than having to change the code to send oopses over AMQP
    rather than to a datedir, or putting the logic to decide what
    to do based on the configuration in your application code.

    Where the function doesn't allow for creating exactly what you
    need you can alter the returned `oops.Config` as desired.

    :param dict_config: a dict containing the description of the
        desired oops config. See the README for detailed information
        on what can be configured.
    :returns: an `oops.Config` object configured as specified.
    :raises AssertionError: if the dict doesn't contain required
        information.
    """
    oops_config = oops.Config()
    if 'publishers' in dict_config:
        for publisher_defn in dict_config['publishers']:
            publisher_type = publisher_defn.get('type')
            if publisher_type is None:
                raise AssertionError(
                        "Missing publisher type: %s" % str(publisher_defn))
            publisher_factory = publishers.get(publisher_type)
            if publisher_factory is None:
                raise AssertionError(
                        "Unknown publisher type: %s" % str(publisher_type))
            publish_method = publisher_factory(publisher_defn)
            if 'new_only' in publisher_defn:
                publish_method = oops.publish_new_only(publish_method)
            oops_config.publishers.append(publish_method)
    oops_config.template.update(dict_config.get('template', {}))
    return oops_config
