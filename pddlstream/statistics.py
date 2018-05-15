import os
from collections import defaultdict, namedtuple

from pddlstream.utils import INF, read_pickle, ensure_dir, write_pickle


class ActionInfo(object):
    def __init__(self, terminal=False, p_success=None, overhead=None):
        """
        :param terminal: Indicates the action may require replanning after use
        """
        self.terminal = terminal # TODO: infer from p_success?
        if self.terminal:
            self.p_success, self.overhead = 1e-3, 0
        else:
            self.p_success, self.overhead = 1, INF
        if p_success is not None:
            self.p_success = p_success
        if overhead is not None:
            self.overhead = overhead
        # TODO: should overhead just be cost here then?


def get_action_info(action_info):
    action_execution = defaultdict(ActionInfo)
    for name, info in action_info.items():
        action_execution[name] = info
    return action_execution


def update_stream_info(externals, stream_info):
    for external in externals:
        if external.name in stream_info:
            external.info = stream_info[external.name]


SamplingProblem = namedtuple('SamplingProblem', ['stream_plan', 'action_plan', 'cost']) # TODO: alternatively just preimage
DATA_DIR = 'data/'


def get_stream_data_filename(stream_name):
    return os.path.join(DATA_DIR, '{}.pp'.format(stream_name))


def load_stream_statistics(stream_name, externals):
    filename = get_stream_data_filename(stream_name)
    if not os.path.exists(filename):
        return
    data = read_pickle(filename)
    for external in externals:
        if external.name in data:
            statistics = data[external.name]
            external.total_calls += statistics['calls']
            external.total_overhead += statistics['overhead']
            external.total_successes += statistics['successes']


def write_stream_statistics(stream_name, externals):
    print('\nExternal Statistics')
    data = {}
    for external in externals:
        data[external.name] = {
            'calls': external.total_calls,
            'overhead': external.total_overhead,
            'successes': external.total_successes,
        }
        print(external.name, external.get_p_success(), external.get_overhead(), external.get_effort()) #, data[external.name])
    filename = get_stream_data_filename(stream_name)
    ensure_dir(filename)
    write_pickle(filename, data)
    print('Wrote:', filename)