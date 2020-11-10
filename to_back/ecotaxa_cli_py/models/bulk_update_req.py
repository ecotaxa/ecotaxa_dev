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


class BulkUpdateReq(object):
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
        'target_ids': 'list[int]',
        'updates': 'list[object]'
    }

    attribute_map = {
        'target_ids': 'target_ids',
        'updates': 'updates'
    }

    def __init__(self, target_ids=None, updates=None, local_vars_configuration=None):  # noqa: E501
        """BulkUpdateReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._target_ids = None
        self._updates = None
        self.discriminator = None

        self.target_ids = target_ids
        self.updates = updates

    @property
    def target_ids(self):
        """Gets the target_ids of this BulkUpdateReq.  # noqa: E501


        :return: The target_ids of this BulkUpdateReq.  # noqa: E501
        :rtype: list[int]
        """
        return self._target_ids

    @target_ids.setter
    def target_ids(self, target_ids):
        """Sets the target_ids of this BulkUpdateReq.


        :param target_ids: The target_ids of this BulkUpdateReq.  # noqa: E501
        :type: list[int]
        """
        if self.local_vars_configuration.client_side_validation and target_ids is None:  # noqa: E501
            raise ValueError("Invalid value for `target_ids`, must not be `None`")  # noqa: E501

        self._target_ids = target_ids

    @property
    def updates(self):
        """Gets the updates of this BulkUpdateReq.  # noqa: E501


        :return: The updates of this BulkUpdateReq.  # noqa: E501
        :rtype: list[object]
        """
        return self._updates

    @updates.setter
    def updates(self, updates):
        """Sets the updates of this BulkUpdateReq.


        :param updates: The updates of this BulkUpdateReq.  # noqa: E501
        :type: list[object]
        """
        if self.local_vars_configuration.client_side_validation and updates is None:  # noqa: E501
            raise ValueError("Invalid value for `updates`, must not be `None`")  # noqa: E501

        self._updates = updates

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
        if not isinstance(other, BulkUpdateReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BulkUpdateReq):
            return True

        return self.to_dict() != other.to_dict()
