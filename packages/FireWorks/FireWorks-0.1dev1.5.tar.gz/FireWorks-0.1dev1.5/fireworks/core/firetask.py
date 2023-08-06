#!/usr/bin/env python

"""
TODO: add docs
"""
from fireworks.utilities.fw_serializers import serialize_fw, FWSerializable


__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 15, 2013'


class FireTaskBase(FWSerializable):
    """
    TODO: add docs
    """

    def __init__(self, parameters=None):
        # Add the following line to your FireTasks to get to_dict to work
        self.parameters = parameters if parameters else {}

    def run_task(self, fw):
        raise NotImplementedError('Need to implement run_task!')

    @serialize_fw
    def to_dict(self):
        return {"parameters": self.parameters}

    @classmethod
    def from_dict(cls, m_dict):
        return cls(m_dict['parameters'])

        # TODO: add a write to log method

        # TODO: Task for committing a file to DB?
        # TODO: add checkpoint function