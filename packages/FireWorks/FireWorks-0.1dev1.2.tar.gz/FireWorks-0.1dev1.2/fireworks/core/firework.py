#!/usr/bin/env python

"""
A FireWork defines a workflow step.

An FWorkflow connects FireWorks by their fw_ids.

A Launch is a describes a FireWork's run on a computing resource. The same Launch might apply to multiple FireWorks,
e.g. if they are identical.

A FWDecision encapsulates the output of that launch.
"""
from StringIO import StringIO
from collections import defaultdict
import datetime
import tarfile
from fireworks.utilities.fw_serializers import FWSerializable, load_object
from fireworks.core.fw_constants import LAUNCH_RANKS
from fireworks.core.fworker import FWorker

__author__ = "Anubhav Jain"
__copyright__ = "Copyright 2013, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Anubhav Jain"
__email__ = "ajain@lbl.gov"
__date__ = "Feb 5, 2013"


# TODO: add ability to block ports
# TODO: consider using Mongo oid as fw_id. How important is readability?

class FireWork(FWSerializable):
    def __init__(self, tasks, spec=None, fw_id=-1, launch_data=None, state='WAITING'):
        """
        TODO: add more docs
        
        reserved spec keywords:
            _tasks - a list of FireTasks to run
            _priority - the priority of the FW
        
        :param tasks: a list of FireTasks
        :param spec: a dict specification of the job to run
        :param fw_id: the FW's database id to the LaunchPad. Negative numbers will be re-assigned dynamically when they are entered in the database through the LaunchPad.
        :param launch_data: a list of Launch objects of this FireWork
        :param state: the state of the FW (e.g. WAITING, RUNNING, COMPLETED, CANCELED)
        """
        # transform tasks into a list, if not in that format
        if not isinstance(tasks, list):
            tasks = [tasks]

        self.tasks = tasks
        self.spec = spec if spec else {}
        self.spec['_tasks'] = [t.to_dict() for t in tasks]
        self.fw_id = fw_id
        self.launch_data = launch_data if launch_data else []
        self.state = state

    def to_dict(self):
        """
        This is a 'minimal' or 'compact' dict representation of the FireWork
        """
        m_dict = {'spec': self.spec, 'fw_id': self.fw_id}
        if len(self.launch_data) > 0:
            m_dict['launch_data'] = [l.to_dict() for l in self.launch_data]

        if self.state != 'WAITING':
            m_dict['state'] = self.state

        return m_dict

    # TODO: consider using a kwarg on the to_dict method, and carrying that over to the serialization class (
    # to_format, to_file)

    def to_db_dict(self):
        """
        This is a 'full' dict representation of a FireWork. It contains redundant fields that enhance information
        retrieval.
        """
        m_dict = self.to_dict()
        m_dict['launch_data'] = [l.to_db_dict() for l in self.launch_data]
        m_dict['state'] = self.state
        return m_dict

    @classmethod
    def from_dict(cls, m_dict):
        tasks = [load_object(t) for t in m_dict['spec']['_tasks']]
        fw_id = m_dict.get('fw_id', None)
        ld = m_dict.get('launch_data', None)
        if ld:
            ld = [Launch.from_dict(tmp) for tmp in ld]
        state = m_dict.get('state', 'WAITING')
        return FireWork(tasks, m_dict['spec'], fw_id, ld, state)


class WFConnections(FWSerializable):
    # TODO: add methods for adding children, removing children

    def __init__(self, child_nodes_dict=None):

        child_nodes_dict = child_nodes_dict if child_nodes_dict else {}
        self._parent_links = defaultdict(list)
        self.child_links = defaultdict(set)

        for (parent, children) in child_nodes_dict.iteritems():
            # make sure children is a list
            if not isinstance(children, list):
                children = [children]

            # make sure parents and children are ints
            parent = int(parent)
            children = [int(c) for c in children]

            # add the children
            self.child_links[parent].update(children)

            # add the parents
            for child in children:
                self._parent_links[child].append(parent)

    def to_dict(self):
        return dict([(k, list(v)) for (k, v) in self.child_links.iteritems()])

    def to_db_dict(self):
        m_dict = {}
        m_dict['children_links'] = dict([(str(k), list(v)) for (k, v) in self.child_links.iteritems()])
        m_dict['parent_links'] = dict([(str(k), v) for (k, v) in self._parent_links.iteritems()])
        return m_dict

    @classmethod
    def from_dict(cls, m_dict):
        return WFConnections(m_dict)


class FWorkflow():
    #TODO: add .gz support
    def __init__(self, fireworks, wf_connections):

        """

        :param fireworks: a list of FireWork objects
        :param wf_connections: A WorkflowConnections object
        """

        self.id_fw = {}
        self.nodes = set()

        # initialize id_fw
        for fw in fireworks:
            if not fw.fw_id or fw.fw_id in self.id_fw:
                raise ValueError("FW ids must be well-defined and unique!")
                # note we have a String key, this matches the WFConnections format
            self.id_fw[fw.fw_id] = fw
            self.nodes.add(fw.fw_id)

        # TODO: validate that the connections is valid given the FW

        # (e.g., all the connection ids must be present in the list of FW)
        self.wf_connections = wf_connections if isinstance(wf_connections, WFConnections) else WFConnections(
            wf_connections)

    def _reassign_ids(self, old_new):
        # update the nodes
        new_nodes = [old_new.get(id, id) for id in self.nodes]
        self.nodes = new_nodes

        # update the WFConnections
        old_cl = self.wf_connections.child_links
        new_cl = {}
        for (parent, children) in old_cl.iteritems():
            # make sure children is a list
            children = list(children)

            new_parent = old_new.get(parent, parent)
            new_children = [old_new.get(child, child) for child in children]
            new_cl[new_parent] = new_children

        self.wf_connections = WFConnections(new_cl)

    def to_db_dict(self):
        m_dict = self.wf_connections.to_db_dict()
        m_dict['nodes'] = list(self.nodes)
        return m_dict

    def to_tarfile(self, f_name='fwf.tar', f_format='json'):
        try:
            out = tarfile.open(f_name, "w")

            # write out the wfconnections
            wfc_str = self.wf_connections.to_format(f_format)
            wfc_info = tarfile.TarInfo('wfconnections.' + f_format)
            wfc_info.size = len(wfc_str)
            out.addfile(wfc_info, StringIO(wfc_str))

            # write out fws
            for fw in self.id_fw.itervalues():
                fw_str = fw.to_format(f_format)
                fw_info = tarfile.TarInfo('fw_' + str(fw.fw_id) + '.' + f_format)
                fw_info.size = len(fw_str)
                out.addfile(fw_info, StringIO(fw_str))

        finally:
            out.close()

    @classmethod
    def from_tarfile(cls, tar_filename):
        t = tarfile.open(tar_filename, 'r')
        wf_connections = None
        fws = []
        for f_name in t.getnames():
            m_file = t.extractfile(f_name)
            m_format = m_file.name.split('.')[-1]
            m_contents = m_file.read()
            if 'wfconnections' in f_name:
                wf_connections = WFConnections.from_format(m_contents, m_format)
            else:
                fws.append(FireWork.from_format(m_contents, m_format))

        return FWorkflow(fws, wf_connections)

    @classmethod
    def from_FireWork(cls, fw):
        return FWorkflow([fw], None)

#TODO: add a working dir at least (maybe inside the Decision?)
#TODO: add a decision to the Launch


class Launch(FWSerializable):
    # TODO: add an expiration date
    def __init__(self, fworker, host=None, ip=None, launch_dir=None, start=None, end=None, state=None, launch_id=None):
        """
        
        :param fworker: A FWorker object describing the worker
        :param host: the hostname where the launch took place (probably automatically set)
        :param ip: the ip address where the launch took place (probably automatically set)
        :param launch_dir: the directory on the host where the launch took place (probably automatically set)
        :param state: the state of the Launch
        :param launch_id: the id of the Launch for the LaunchPad
        """
        if state not in LAUNCH_RANKS:
            raise ValueError("Invalid launch state: {}".format(state))

        self.fworker = fworker
        self.host = host
        self.ip = ip
        self.launch_dir = launch_dir
        self.start = start if start else datetime.datetime.utcnow()
        self.end = end
        self.state = state
        self.launch_id = launch_id

    def to_dict(self):
        return {'fworker': self.fworker.to_dict(), 'start': self.start, 'end': self.end, 'host': self.host,
                'ip': self.ip, 'launch_dir': self.launch_dir, 'state': self.state, 'launch_id': self.launch_id}

    @property
    def time_secs(self):
        return (self.end - self.start).total_seconds() if self.end else None

    def to_db_dict(self):
        m_d = self.to_dict()
        m_d['time_secs'] = self.time_secs
        return m_d

    @classmethod
    def from_dict(cls, m_dict):
        fworker = FWorker.from_dict(m_dict['fworker'])
        return Launch(fworker, m_dict['host'], m_dict['ip'], m_dict['launch_dir'], m_dict['start'], m_dict['end'],
                      m_dict['state'], m_dict['launch_id'])


class FWDecision():
    """
    A FWDecision returns one of several potential actions:
        -CONTINUE means continue to the next stage in the workflow, no changes are made to the firework
        -BRANCH means to insert new Fireworks into the workflow and forget about the current children
        -DETOUR means to insert new Fireworks into the workflow, and then run the current children
        -TERMINATE means to terminate this branch of the workflow (any children of this Stage will NOT be run).

    The output parameter is a dict that gets passed to the 'output' parameter of the LaunchInfo being analyzed.
    The output is a dict that:
        - stores any metadata about the decision
        - is used by Fuses of child FWs to determine how to proceed
         
    """
    actions = ["CONTINUE", "BRANCH", "DETOUR", "TERMINATE"]

    def __init__(self, action, stored_data=None, mod_spec=None, add_fws=None):

        if action not in FWDecision.actions:
            raise ValueError("Invalid decision: " + action)

        if action != "CONTINUE" and mod_spec:
            raise ValueError("You can only modify the spec if you decide to CONTINUE")

        if action not in ["BRANCH", "DETOUR"] and add_fws:
            raise ValueError("You cannot " + str(action) + " whilst also inserting fireworks")

        if action in ["BRANCH", "DETOUR"] and not add_fws:
            raise ValueError("If you " + str(action) + ", you must specify fireworks to insert!")

        self.action = action
        self.add_fws = add_fws
        self.mod_spec = mod_spec
        self.stored_data = stored_data if stored_data else {}

    def to_dict(self):
        return {"action": self.action, "stored_data": self.stored_data, "mod_spec": self.mod_spec,
                "add_fws": self.add_fws}

    @classmethod
    def from_dict(cls, m_dict):
        return FWDecision(m_dict['action'], m_dict['stored_data'], m_dict['mod_spec'], m_dict['add_fws'])


if __name__ == "__main__":
    #a = FireWork(SubprocessTask.from_str('hello'), {}, fw_id=2)
    #b = FWorkflow.from_FireWork(a)
    #print b.to_db_dict()

    #fwf.to_tarfile('../../fw_tutorials/workflow/hello_out.tar')
    fwf = FWorkflow.from_tarfile('../../fw_tutorials/workflow/hello.tar')

