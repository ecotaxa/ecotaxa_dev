# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.6
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class CreateProjectReq(object):
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
        'clone_of_id': 'int',
        'title': 'str',
        'visible': 'bool'
    }

    attribute_map = {
        'clone_of_id': 'clone_of_id',
        'title': 'title',
        'visible': 'visible'
    }

    def __init__(self, clone_of_id=None, title=None, visible=True, local_vars_configuration=None):  # noqa: E501
        """CreateProjectReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._clone_of_id = None
        self._title = None
        self._visible = None
        self.discriminator = None

        if clone_of_id is not None:
            self.clone_of_id = clone_of_id
        self.title = title
        if visible is not None:
            self.visible = visible

    @property
    def clone_of_id(self):
        """Gets the clone_of_id of this CreateProjectReq.  # noqa: E501


        :return: The clone_of_id of this CreateProjectReq.  # noqa: E501
        :rtype: int
        """
        return self._clone_of_id

    @clone_of_id.setter
    def clone_of_id(self, clone_of_id):
        """Sets the clone_of_id of this CreateProjectReq.


        :param clone_of_id: The clone_of_id of this CreateProjectReq.  # noqa: E501
        :type: int
        """

        self._clone_of_id = clone_of_id

    @property
    def title(self):
        """Gets the title of this CreateProjectReq.  # noqa: E501


        :return: The title of this CreateProjectReq.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this CreateProjectReq.


        :param title: The title of this CreateProjectReq.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and title is None:  # noqa: E501
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def visible(self):
        """Gets the visible of this CreateProjectReq.  # noqa: E501


        :return: The visible of this CreateProjectReq.  # noqa: E501
        :rtype: bool
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        """Sets the visible of this CreateProjectReq.


        :param visible: The visible of this CreateProjectReq.  # noqa: E501
        :type: bool
        """

        self._visible = visible

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
        if not isinstance(other, CreateProjectReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateProjectReq):
            return True

        return self.to_dict() != other.to_dict()
