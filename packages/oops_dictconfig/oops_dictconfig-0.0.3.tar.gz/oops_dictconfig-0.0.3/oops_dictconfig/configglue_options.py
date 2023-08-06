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

from configglue import schema


class PublisherDescriptionOption(schema.DictOption):

    def __init__(self, **kwargs):
        if 'spec' not in kwargs:
            kwargs['spec'] = dict(
                type=schema.StringOption(
                    help="Type of publisher; amqp or datedir are supported.",
                    ),
                new_only=schema.StringOption(
                    help="Only publish if a previous publisher hasn't.",
                    ),
                error_dir=schema.StringOption(
                    help="For datedir: the path to write the oopses to.",
                    ),
                host=schema.StringOption(
                    help="For amqp: the host:port for the amqp broker.",
                    ),
                user=schema.StringOption(
                    help="For amqp: the user for the amqp broker.",
                    ),
                password=schema.StringOption(
                    help="For amqp: the password for the amqp broker.",
                    ),
                vhost=schema.StringOption(
                    help="For amqp: the vhost for the amqp broker.",
                    ),
                exchange_name=schema.StringOption(
                    help=("For amqp: the name of the exchange for the"
                          "amqp broker."),
                    ),
                routing_key=schema.StringOption(
                    help=("For amqp: the routing key for the amqp broker."),
                    ),
                )
        if 'help' not in kwargs:
            kwargs['help'] = "Config for an oops publisher."
        super(PublisherDescriptionOption, self).__init__(**kwargs)


class PublishersOption(schema.ListOption):

    def __init__(self, **kwargs):
        if 'item' not in kwargs:
            kwargs['item'] = PublisherDescriptionOption()
        if 'help' not in kwargs:
            kwargs['help'] = "List of oops publishers in order to publish to."
        super(PublishersOption, self).__init__(**kwargs)


class OopsOption(schema.DictOption):

    def __init__(self, **kwargs):
        if 'spec' not in kwargs:
            kwargs['spec'] = dict(
                publishers=PublishersOption(),
                template=schema.DictOption(help=("A dict containing a default "
                    "values for oopses created from this config.")),
                )
        if 'help' not in kwargs:
            kwargs['help'] = "Configuration for publishing oopses."
        super(OopsOption, self).__init__(**kwargs)
