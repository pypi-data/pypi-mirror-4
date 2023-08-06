#   yadtcommons
#   Copyright (C) 2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

try:
    from ConfigParser import SafeConfigParser
except:  # pragma: no cover
    from configparser import SafeConfigParser


class ConfigurationException (Exception):
    """
        to be raised when an configuration error occurs.
    """


class YadtConfigParser (object):
    def __init__(self):
        """
            Creates instance of SafeConfigParser which will be used to parse
            the configuration file.
        """
        self._parser = SafeConfigParser()

    def get_option(self, section, option, default_value):
        """
            @return: the option from the section if it exists,
                     otherwise the given default value.
        """
        if self._parser.has_option(section, option):
            return self._parser.get(section, option)

        return default_value

    def get_option_as_yes_or_no_boolean(self, section, option, default_value):
        """
            @return: the boolean option from the section if it exists,
                     otherwise the given default value.
        """
        option_value = self.get_option(section, option, default_value)

        if option_value != 'yes' and option_value != 'no':
            raise ConfigurationException('Option %s in section %s expected "yes" or "no", but got %s'
                                         % (option, section, option_value))

        return option_value == 'yes'

    def get_option_as_int(self, section, option, default_value):
        """
            @return: the integer option from the section if it exists,
                     otherwise the given default value.
        """
        option_value = self.get_option(section, option, default_value)

        if not option_value.isdigit():
            raise ConfigurationException('Option %s in section %s expected a integer value, but got %s'
                                         % (option, section, option_value))
        return int(option_value)

    def get_option_as_list(self, section, option, default_value):
        """
            @return: the option (list of strings) from the section if it exists
                     otherwise the given default value.
        """
        option_value = self.get_option(section, option, '')

        if option_value == '':
            return default_value

        list_of_unstripped_options = option_value.split(',')

        result = []
        for unstripped_option in list_of_unstripped_options:
            result.append(unstripped_option.strip())

        return result

    def get_option_as_set(self, section, option, default_value):
        """
            @return: the option (set of strings) from the section if it exists,
                     otherwise the given default value.
        """
        option_values = self.get_option_as_list(section, option, default_value)
        return set(option_values)

    def read_configuration_file(self, filename):
        """
            reads the file into the parser. Will exit with error code 1 if
            the configuration file does not exist.
        """
        if not os.path.exists(filename):
            raise ConfigurationException('Configuration file "%s" does not exist.' % filename)

        logging.getLogger('configuration').info('Loading configuration file "%s"' % filename)
        self._parser.read([filename])
