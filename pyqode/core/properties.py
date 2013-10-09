#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the definition of the QCodeEdit settings
"""
import json
import re
import sys
from pyqode.core.constants import TAB_SIZE
from pyqode.core.system import TextStyle
from pyqode.qt import QtCore, QtGui


class PropertyRegistry(QtCore.QObject):
    """
    PropertyRegistry is a class that manage a registry/dictionary of properties.

    For a better organisation, properties are grouped by sections.

    Each property is described by:
        - a **key**: the name of the property
        - a **value**: the value of the property, stored as a string
        - a **section**: the section which contains the property.
          Default section is *"General"*

    **Signals**
        - valueChanged(str key, str section)

    .. note:: Even if the value is stored as a string, the class will try its
              best to *"cast"* the string value to its original type.

              Here are the supported types:
                - int
                - float
                - bool
                - QColor
                - :class:`pyqode.core.TextStyle`
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

    def sections(self):
        """
        Generates the list of sections
        """
        for k in sorted(self.__dict.keys()):
            yield k

    def allProperties(self):
        """
        Generates the list of properties dictionaries.
        """
        for k, v in self.__dict.items():
            yield v

    def properties(self, section):
        """
        Gets the dictionary of properties of a specific section.

        :param section: The properties' section
        :return: dict of properties
        """
        return self.__dict[section]

    def update(self, propertyRegistry):
        """
        Updates the values of the current instance from the value of the
        registry passed as a parameter.

        .. note:: This will emit the :attr:`pyqode.core.PropertyRegistry.valueChanged` signal
                  with a key and section parameter set to an empty string.

        :param propertyRegistry: The source of the update.
        :type propertyRegistry: pyqode.core.PropertyRegistry
        """
        for sk, sv in propertyRegistry.__dict.items():
            for pk, pv in sv.items():
                if sk in self.__dict:
                    if pk in self.__dict[sk]:
                        self.__dict[sk][pk] = pv
        self.valueChanged.emit("", "")

    def clone(self):
        return PropertyRegistry(copy=self)

    def addProperty(self, key, value, section="General"):
        """
        Adds a property with a default value.

        .. note:: If the property already exists in the given section,
                  the original value is kept and returned as a result. To change
                  a value use :meth:`pyqode.core.PropertyRegistry.setValue`.

        :param key: The name/key of the property
        :type key: str

        :param value: The value of the property.

        :return: The original value if the property does not already exists,
                 else it return the existing value.
        """
        value = self.__value_to_str(value)
        if section in self.__dict:
            if key in self.__dict[section]:
                value = self.value(key, section)
                return value
            else:
                self.__dict[section][key] = value
        else:
            self.__dict[section] = {key: value}
        return self.__value_from_str(value)

    def removeProperty(self, key, section="General"):
        """
        Remove a property from the registry.

        :param section: The section of the property to remove.
        :type section: str

        :param key: The name/key of the property to remove
        :type key: str
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
        """
        if section in self.__dict:
            if key in self.__dict[section]:
                return self.__value_from_str(self.__dict[section][key])
        return default

    @staticmethod
    def __value_to_str(value):
        """
        Convert a value to a string

        :param value: Value (int, float, bool, string, QColor)

        :return: The value as a string
        """
        if isinstance(value, QtGui.QColor):
            return value.name()
        elif isinstance(value, list):
            try:
                return "[%s]" % '²'.join(value)
            except TypeError:
                txt = ""
                for v in value:
                    txt += "%s," % str(value)
                txt = txt[0:len(txt) - 2]
                txt += "]"
                return txt
        else:
            return str(value)

    @staticmethod
    def __value_from_str(value_str):
        """
        Get a value from a string, try to cast the value_str to the proper type.

        :param value_str: Value string to convert

        :rtype int or float or bool or string or QColor or TextStyle
        """
        if sys.version_info[0] == 2:
            value_str = value_str.decode("utf-8")
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
            value_str = value_str[1:len(value_str)-1]
            if sys.version_info[0] == 2:
                lst = value_str.split("²".decode("utf-8"))
            else:
                lst = value_str.split("²")
            try:
                lst.remove("")
            except ValueError:
                pass
            return lst
        elif value_str == "None":
            return None
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
