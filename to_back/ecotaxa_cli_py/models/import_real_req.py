# coding: utf-8

"""
    EcoTaxa

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from to_back.ecotaxa_cli_py.configuration import Configuration


class ImportRealReq(object):
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
        'task_id': 'int',
        'source_path': 'str',
        'taxo_mappings': 'dict(str, int)',
        'skip_loaded_files': 'bool',
        'skip_existing_objects': 'bool',
        'mappings': 'dict(str, dict(str, str))',
        'found_users': 'dict(str, object)',
        'found_taxa': 'dict(str, int)',
        'rowcount': 'int'
    }

    attribute_map = {
        'task_id': 'task_id',
        'source_path': 'source_path',
        'taxo_mappings': 'taxo_mappings',
        'skip_loaded_files': 'skip_loaded_files',
        'skip_existing_objects': 'skip_existing_objects',
        'mappings': 'mappings',
        'found_users': 'found_users',
        'found_taxa': 'found_taxa',
        'rowcount': 'rowcount'
    }

    def __init__(self, task_id=None, source_path=None, taxo_mappings=None, skip_loaded_files=False, skip_existing_objects=False, mappings=None, found_users=None, found_taxa=None, rowcount=0, local_vars_configuration=None):  # noqa: E501
        """ImportRealReq - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._task_id = None
        self._source_path = None
        self._taxo_mappings = None
        self._skip_loaded_files = None
        self._skip_existing_objects = None
        self._mappings = None
        self._found_users = None
        self._found_taxa = None
        self._rowcount = None
        self.discriminator = None

        self.task_id = task_id
        self.source_path = source_path
        if taxo_mappings is not None:
            self.taxo_mappings = taxo_mappings
        if skip_loaded_files is not None:
            self.skip_loaded_files = skip_loaded_files
        if skip_existing_objects is not None:
            self.skip_existing_objects = skip_existing_objects
        if mappings is not None:
            self.mappings = mappings
        if found_users is not None:
            self.found_users = found_users
        if found_taxa is not None:
            self.found_taxa = found_taxa
        if rowcount is not None:
            self.rowcount = rowcount

    @property
    def task_id(self):
        """Gets the task_id of this ImportRealReq.  # noqa: E501


        :return: The task_id of this ImportRealReq.  # noqa: E501
        :rtype: int
        """
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Sets the task_id of this ImportRealReq.


        :param task_id: The task_id of this ImportRealReq.  # noqa: E501
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and task_id is None:  # noqa: E501
            raise ValueError("Invalid value for `task_id`, must not be `None`")  # noqa: E501

        self._task_id = task_id

    @property
    def source_path(self):
        """Gets the source_path of this ImportRealReq.  # noqa: E501


        :return: The source_path of this ImportRealReq.  # noqa: E501
        :rtype: str
        """
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        """Sets the source_path of this ImportRealReq.


        :param source_path: The source_path of this ImportRealReq.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and source_path is None:  # noqa: E501
            raise ValueError("Invalid value for `source_path`, must not be `None`")  # noqa: E501

        self._source_path = source_path

    @property
    def taxo_mappings(self):
        """Gets the taxo_mappings of this ImportRealReq.  # noqa: E501


        :return: The taxo_mappings of this ImportRealReq.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._taxo_mappings

    @taxo_mappings.setter
    def taxo_mappings(self, taxo_mappings):
        """Sets the taxo_mappings of this ImportRealReq.


        :param taxo_mappings: The taxo_mappings of this ImportRealReq.  # noqa: E501
        :type: dict(str, int)
        """

        self._taxo_mappings = taxo_mappings

    @property
    def skip_loaded_files(self):
        """Gets the skip_loaded_files of this ImportRealReq.  # noqa: E501


        :return: The skip_loaded_files of this ImportRealReq.  # noqa: E501
        :rtype: bool
        """
        return self._skip_loaded_files

    @skip_loaded_files.setter
    def skip_loaded_files(self, skip_loaded_files):
        """Sets the skip_loaded_files of this ImportRealReq.


        :param skip_loaded_files: The skip_loaded_files of this ImportRealReq.  # noqa: E501
        :type: bool
        """

        self._skip_loaded_files = skip_loaded_files

    @property
    def skip_existing_objects(self):
        """Gets the skip_existing_objects of this ImportRealReq.  # noqa: E501


        :return: The skip_existing_objects of this ImportRealReq.  # noqa: E501
        :rtype: bool
        """
        return self._skip_existing_objects

    @skip_existing_objects.setter
    def skip_existing_objects(self, skip_existing_objects):
        """Sets the skip_existing_objects of this ImportRealReq.


        :param skip_existing_objects: The skip_existing_objects of this ImportRealReq.  # noqa: E501
        :type: bool
        """

        self._skip_existing_objects = skip_existing_objects

    @property
    def mappings(self):
        """Gets the mappings of this ImportRealReq.  # noqa: E501


        :return: The mappings of this ImportRealReq.  # noqa: E501
        :rtype: dict(str, dict(str, str))
        """
        return self._mappings

    @mappings.setter
    def mappings(self, mappings):
        """Sets the mappings of this ImportRealReq.


        :param mappings: The mappings of this ImportRealReq.  # noqa: E501
        :type: dict(str, dict(str, str))
        """

        self._mappings = mappings

    @property
    def found_users(self):
        """Gets the found_users of this ImportRealReq.  # noqa: E501

        key = user name; value = dict with (key = 'id' if resolved, else 'email')  # noqa: E501

        :return: The found_users of this ImportRealReq.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._found_users

    @found_users.setter
    def found_users(self, found_users):
        """Sets the found_users of this ImportRealReq.

        key = user name; value = dict with (key = 'id' if resolved, else 'email')  # noqa: E501

        :param found_users: The found_users of this ImportRealReq.  # noqa: E501
        :type: dict(str, object)
        """

        self._found_users = found_users

    @property
    def found_taxa(self):
        """Gets the found_taxa of this ImportRealReq.  # noqa: E501

        key = taxon NAME; value = taxon ID if resolved, else None  # noqa: E501

        :return: The found_taxa of this ImportRealReq.  # noqa: E501
        :rtype: dict(str, int)
        """
        return self._found_taxa

    @found_taxa.setter
    def found_taxa(self, found_taxa):
        """Sets the found_taxa of this ImportRealReq.

        key = taxon NAME; value = taxon ID if resolved, else None  # noqa: E501

        :param found_taxa: The found_taxa of this ImportRealReq.  # noqa: E501
        :type: dict(str, int)
        """

        self._found_taxa = found_taxa

    @property
    def rowcount(self):
        """Gets the rowcount of this ImportRealReq.  # noqa: E501


        :return: The rowcount of this ImportRealReq.  # noqa: E501
        :rtype: int
        """
        return self._rowcount

    @rowcount.setter
    def rowcount(self, rowcount):
        """Sets the rowcount of this ImportRealReq.


        :param rowcount: The rowcount of this ImportRealReq.  # noqa: E501
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
        if not isinstance(other, ImportRealReq):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ImportRealReq):
            return True

        return self.to_dict() != other.to_dict()
