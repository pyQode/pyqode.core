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
import re
import sys
from pcef.core.constants import TAB_SIZE
from pcef.core.system import TextStyle
from pcef.qt import QtCore, QtGui


class PropertyRegistry(QtCore.QObject):
    """
    PropertyRegistry is a class that manage a registry/dictionary of properties.

    Each property is described by:
        - a key: string - name of the property
        - a value: string - value of the property that is stored as a string
        - a section:

    For a better organisation, properties are grouped by sections.

    When a property value is changed, the valueChanged signal is emitted.

    .. note:: Even if the value is stored as a string, the class will try its
              best to "cast" the value string to its original type.
              Supported types are:
                - int
                - float
                - bool
                - QColor
                - pcef.core.system.TextStyle
                - string
    """

    #: Signal emitted when the value of a property changed. The first parameter
    #: holds the property's section, the second parameter holds the property's
    #: key and the last parameter holds the property's value
    valueChanged = QtCore.Signal(str, str)

    def __init__(self, copy=None):
        QtCore.QObject.__init__(self)
        if copy:
            self.__dict = copy.__dict
        else:
            self.__dict = {"General": {}}

    def copy(self, propertyRegistry):
        self.__dict = propertyRegistry.__dict
        self.valueChanged.emit("", "")

    def clone(self):
        return PropertyRegistry(copy=self)

    def addProperty(self, key, value, section="General"):
        """
        Adds a property with a default value.

        .. remark:: If the property already exists in the given section,
                    the original value is kept and returned as a result.

        :param key: The name/key of the property

        :param value: The value of the property.
        :type value: int or float or bool or string or QColor or TextStyle

        :return The original value if the property does not already exists,
                else it return the exisiting property value.
                (Use setValue to change the value of a property).
        """
        value = self.__value_to_str(value)
        if section in self.__dict:
            if key in self.__dict[section]:
                value = self.value(key, section)
            else:
                self.__dict[section][key] = value
        else:
            self.__dict[section] = {key: value}
        return self.value_from_str(value)

    def removeProperty(self, key, section="General"):
        """
        Adds a property with a default value.

        .. remark:: If the property already exists in the given section,
                    the original value is kept and returned as a result.

        :param key: The name/key of the property

        :param value: The value of the property.
        :type value: int or float or bool or string or QColor or TextStyle

        :return The original value if the property does not already exists,
                else it return the exisiting property value.
                (Use setValue to change the value of a property).
        """
        if section in self.__dict:
            if key in self.__dict[section]:
                self.__dict.pop(key)

    def setValue(self, key, value, section="General"):
        """
        Sets the value of a property

        :param key: The name/key of the property

        :param value: The value of the property.
        :type value: int or float or bool or string or QColor or TextStyle

        :return: The value string. Because this might be the old property value
        that is used if the property already exists
        """
        value = self.__value_to_str(value)
        if self.__dict[section][key] != value:
            self.__dict[section][key] = value
            self.valueChanged.emit(section, key)

    def value(self, key, section="General", default=""):
        """
        Gets the value of a property. This method will try to cast the value
        automatically to the proper builtin type. If the value string is not
        detected as a python builtin type, the string is simply returned.

        :param key: The property's key

        :param default: The property's default value, used if the property does
                        not exists

        :return: The property's value
        :rtype int or float or bool or string or QColor or TextStyle
        """
        if section in self.__dict:
            if key in self.__dict[section]:
                return self.value_from_str(self.__dict[section][key])
        return default

    def __value_to_str(self, value):
        """
        Convert a value to a string

        :param value: Value (int, float, bool, string, QColor)

        :return: The value as a string
        """
        if isinstance(value, QtGui.QColor):
            return value.name()
        else:
            return str(value)

    def value_from_str(self, value_str):
        """
        Get a value from a string, try to cast the value_str to the proper type.

        :param value_str: Value string to convert

        :rtype int or float or bool or string or QColor or TextStyle
        """
        if sys.version_info[0] == 2:
            value_str = unicode(value_str)
        else:
            value_str = str(value_str)
        # color or format
        if value_str.isnumeric():
            if value_str.isdecimal() and ("." in value_str or "," in value_str):
                return float(value_str)
            else:
                return int(value_str)
        elif "TRUE" in value_str.upper():
            return True
        elif "FALSE" in value_str.upper():
            return False
        elif re.match("#......\\Z", value_str.rstrip()):
            return QtGui.QColor(value_str)
        elif value_str.startswith('#'):
            return TextStyle(value_str)
        elif value_str.startswith("[") and value_str.endswith("]"):
            return list(value_str.replace("[", "").replace("]", ""))
        else:
            return value_str

    def dump(self):
        """
        Dumps the settings dictionary to a json **string**.

        :return: str
        """
        return json.dumps(self.__dict, indent=TAB_SIZE, sort_keys=True)

    def load(self, data):
        """
        Loads the registry from a json **string**.

        :param data: Json data string
        """
        self.__dict = json.loads(data)

    def open(self, filepath):
        """
        Loads the registry from a json **file**

        :param filepath: Path to the property registry JSON file.
        """
        with open(filepath, 'r') as f:
            self.load(f.read())
        for section in self.__dict:
            for key in self.__dict[section]:
                self.valueChanged.emit(section, key)

    def save(self, filepath):
        """
        Save the registry to a json **file**

        :param filepath: Save path
        """
        with open(filepath, 'w') as f:
            f.write(self.dump())
