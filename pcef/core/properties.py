#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the definition of the QCodeEdit settings
"""
import json
import pcef
from pcef.constants import TAB_SIZE


class PropertyRegistry(pcef.QtCore.QObject):
    """
    PropertyRegistry is a class that manage a registry/dictionary of properties.

    Each property is described by:
        - a key: string - name of the property
        - a value: string - value of the property as a string
        - a section:

    For a better organisation, properties are grouped by sections.

    When a property value is changed, the valueChanged signal is emitted.
    """

    #: Signal emitted when the value of a property changed. The first parameter
    #: holds the property's section, the second parameter holds the property's
    #: key and the last parameter holds the property's value
    valueChanged = pcef.QtCore.Signal(str, str, str)

    def __init__(self):
        pcef.QtCore.QObject.__init__(self)
        self.__dict = {"General": {}}

    def addProperty(self, key, value, section="General"):
        """
        Adds a property with a default value. If the property already exists in
        the given section,
        the default value is not used and the current property value is returned
        instead.

        :param key: The name/key of the property
        :param value: The value string.

        :return: The value string. Because this might be the old property value
        that is used if the property already exists
        """
        if section in self.__dict:
            if key in self.__dict[section]:
                value = self.__dict[section][key]
            else:
                self.__dict[section][key] = str(value)
        else:
            self.__dict[section] = {key: value}
        return value

    def setValue(self, key, value, section="General"):
        """
        Sets a property value
        :param key:
        :param value:
        :return:
        """
        value = str(value)
        if self.__dict[section][key] != value:
            self.__dict[section][key] = value
            self.valueChanged.emit(section, key, value)

    def value(self, key, section="General", default=""):
        """
        Gets the value of a property. The default value as the return value if
        the property does not exists.

        :param key: The property's key
        :param default: The property's default value, used if the property does
                        not exists
        :return: The property's value
        """
        if section in self.__dict:
            if key in self.__dict[section]:
                return self.__dict[section][key]
        return default

    def dump(self):
        """
        Dumps the settings dictionary to a json string.

        :return: str
        """
        return json.dumps(self.__dict, indent=TAB_SIZE, sort_keys=True)

    def load(self, data):
        """
        Loads the registry from a json data buffer.

        :param data: Json data string
        """
        self.__dict = json.loads(data)

    def open(self, filepath):
        """
        Opens the file and loads its data

        :param filepath: Path to the property registry JSON file.
        """
        with open(filepath, 'r') as f:
            self.load(f.read())
        for section in self.__dict:
            for key in self.__dict[section]:
                self.valueChanged.emit(
                    section, key, self.__dict[section][key])

    def save(self, filepath):
        """
        Save the registry to a json file.

        :param filepath: Save path
        """
        with open(filepath, 'w') as f:
            f.write(self.dump())
