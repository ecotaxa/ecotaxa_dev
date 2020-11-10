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


class TaxonModel(object):
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
        'id': 'int',
        'display_name': 'str',
        'lineage': 'list[str]'
    }

    attribute_map = {
        'id': 'id',
        'display_name': 'display_name',
        'lineage': 'lineage'
    }

    def __init__(self, id=None, display_name=None, lineage=None, local_vars_configuration=None):  # noqa: E501
        """TaxonModel - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._display_name = None
        self._lineage = None
        self.discriminator = None

        self.id = id
        self.display_name = display_name
        self.lineage = lineage

    @property
    def id(self):
        """Gets the id of this TaxonModel.  # noqa: E501


        :return: The id of this TaxonModel.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this TaxonModel.


        :param id: The id of this TaxonModel.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and id is None:  # noqa: E501
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def display_name(self):
        """Gets the display_name of this TaxonModel.  # noqa: E501


        :return: The display_name of this TaxonModel.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this TaxonModel.


        :param display_name: The display_name of this TaxonModel.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501

        self._display_name = display_name

    @property
    def lineage(self):
        """Gets the lineage of this TaxonModel.  # noqa: E501


        :return: The lineage of this TaxonModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._lineage

    @lineage.setter
    def lineage(self, lineage):
        """Sets the lineage of this TaxonModel.


        :param lineage: The lineage of this TaxonModel.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and lineage is None:  # noqa: E501
            raise ValueError("Invalid value for `lineage`, must not be `None`")  # noqa: E501

        self._lineage = lineage

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
        if not isinstance(other, TaxonModel):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaxonModel):
            return True

        return self.to_dict() != other.to_dict()
