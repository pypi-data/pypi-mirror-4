#!/usr/bin/env python

"""
TODO: add docs
"""
from fireworks.core.firetask import FireTaskBase
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.core.firework import FWAction, FireWork

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 25, 2013'


class FibonacciAdderTask(FireTaskBase, FWSerializable):

    _fw_name = "Fibonacci Adder Task"

    def run_task(self, fw):
        smaller = fw.spec['smaller']
        larger = fw.spec['larger']

        m_sum = smaller + larger

        if m_sum < 100:
            print 'The next Fibonacci number is: {}'.format(m_sum)
            # create a new Fibonacci Adder to add to the workflow
            new_fw = FireWork(FibonacciAdderTask(), {'smaller': larger, 'larger': m_sum})
            return FWAction('CREATE', {'next_fibnum': m_sum}, {'create_fw': new_fw})

        else:
            print 'We have now exceeded our limit; (the next Fibonacci number would have been: {})'.format(m_sum)
            return FWAction('CONTINUE')

