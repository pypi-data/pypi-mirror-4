import re
from functools import partial
from nlpkit.paths import data_path


class TagMap(object):
    def __init__(self):
        self.strategies = {'identity': self.identity}

    def add_map_fn(self, fn, name=None):
        if name is None:
            name = fn.__name__
        self.strategies[name] = fn

    def available_strategies(self):
        return self.strategies.keys()

    def map_fn(self, arg_str):
        m = re.match(r'(\w+)(\(([\w\/]+)\))?', arg_str)
        if not m:
            raise StandardError('Invalid syntax for tag mapper argument: {}', arg_str)
        strategy_name = m.group(1)
        if strategy_name not in self.strategies:
            raise StandardError('Mapping strategy not recognized: {}', arg_str)
        if m.group(3):
            return partial(self.strategies[strategy_name], data_path(m.group(3)))
        else:
            return self.strategies[strategy_name]


    def identity(self, tag):
        return tag
