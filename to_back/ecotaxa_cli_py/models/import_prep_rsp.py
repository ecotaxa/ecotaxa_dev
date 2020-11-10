# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.5
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ImportPrepRsp(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'source_path': 'str',
        'mappings': 'dict(str, dict(str, str))',
        'found_users': 'dict(str, object)',
        'found_taxa': 'dict(str, int)',
        'warnings': 'list[str]',
        'errors': 'list[str]',
        'rowcount': 'int'
    }

    attribute_map = {
        'source_path': 'source_path',
        'mappings': 'mappings',
        'found_users': 'found_users',
        'found_taxa': 'found_taxa',
        'warnings': 'warnings',
        'errors': 'errors',
        'rowcount': 'rowcount'
    }

    def __init__(self, source_path=None, mappings=None, found_users=None, found_taxa=None, warnings=[], errors=[], rowcount=0, local_vars_configuration=None):  # noqa: E501
        """ImportPrepRsp - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._source_path = None
        self._mappings = None
        self._found_users = None
        self._found_taxa = None
        self._warnings = None
        self._errors = None
        self._rowcount = None
        self.discriminator = None

        self.source_path = source_path
        if mappings is not None:
            self.mappings = mappings
        if found_users is not None:
            self.found_users = found_users
        if found_taxa is not None:
            self.found_taxa = found_taxa
        if warnings is not None:
            self.warnings = warnings
        if errors is not None:
            self.errors = errors
        if rowcount is not None:
            self.rowcount = rowcount

    @property
    def source_path(self):
        """Gets the source_path of this ImportPrepRsp.  # noqa: E501


        :return: The source_path of this ImportPrepRsp.  # noqa: E501
        :rtype: str
        """
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        """Sets the source_path of this ImportPrepRsp.


        :param source_path: The source_path of this ImportPrepRsp.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and source_path is None:  # noqa: E501
            raise ValueError("Invalid value for `source_path`, must not be `None`")  # noqa: E501

        self._source_path = source_path

    @property
    def mappings(self):
        """Gets the mappings of this ImportPrepRsp.  # noqa: E501


        :return: The mappings of this ImportPrepRsp.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._mappings

    @mappings.setter
    def mappings(self, mappings):
        """Sets the mappings of this ImportPrepRsp.


        :param mappings: The mappings of this ImportPrepRsp.  # noqa: E501
        :type: dict(str, dict(str, str))
        """

        self._mappings = mappings

    @property
    def found_users(self):
        """Gets the found_users of this ImportPrepRsp.  # noqa: E501

        key = user name; value = dict with (key = 'id' if resolved, else 'email')  # noqa: E501

        :return: The found_users of this ImportPrepRsp.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._found_users

    @found_users.setter
    def found_users(self, found_users):
        """Sets the found_users of this ImportPrepRsp.

        key = user name; value = dict with (key = 'id' if resolved, else 'email')  # noqa: E501

        :param found_users: The found_users of this ImportPrepRsp.  # noqa: E501
        :type: dict(str, object)
        """

        self._found_users = found_users

    @property
    def found_taxa(self):
        """Gets the found_taxa of this ImportPrepRsp.  # noqa: E501

        key = taxon NAME; value = taxon ID if resolved, else None  # noqa: E501

        :return: The found_taxa of this ImportPrepRsp.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._found_taxa

    @found_taxa.setter
    def found_taxa(self, found_taxa):
        """Sets the found_taxa of this ImportPrepRsp.

        key = taxon NAME; value = taxon ID if resolved, else None  # noqa: E501

        :param found_taxa: The found_taxa of this ImportPrepRsp.  # noqa: E501
        :type: dict(str, int)
        """

        self._found_taxa = found_taxa

    @property
    def warnings(self):
        """Gets the warnings of this ImportPrepRsp.  # noqa: E501


        :return: The warnings of this ImportPrepRsp.  # noqa: E501
        :rtype: list[str]
        """
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        """Sets the warnings of this ImportPrepRsp.


        :param warnings: The warnings of this ImportPrepRsp.  # noqa: E501
        :type: list[str]
        """

        self._warnings = warnings

    @property
    def errors(self):
        """Gets the errors of this ImportPrepRsp.  # noqa: E501

        Do NOT proceed to real import if not empty.  # noqa: E501

        :return: The errors of this ImportPrepRsp.  # noqa: E501
        :rtype: list[str]
        """
        return self._errors

    @errors.setter
    def errors(self, errors):
        """Sets the errors of this ImportPrepRsp.

        Do NOT proceed to real import if not empty.  # noqa: E501

        :param errors: The errors of this ImportPrepRsp.  # noqa: E501
        :type: list[str]
        """

        self._errors = errors

    @property
    def rowcount(self):
        """Gets the rowcount of this ImportPrepRsp.  # noqa: E501


        :return: The rowcount of this ImportPrepRsp.  # noqa: E501
        :rtype: int
        """
        return self._rowcount

    @rowcount.setter
    def rowcount(self, rowcount):
        """Sets the rowcount of this ImportPrepRsp.


        :param rowcount: The rowcount of this ImportPrepRsp.  # noqa: E501
        :type: int
        """

        self._rowcount = rowcount

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ImportPrepRsp):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImportPrepRsp):
            return True

        return self.to_dict() != other.to_dict()
