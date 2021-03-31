import numpy as np

from src.main.Provider import Provider


class DefinedValue(Provider):

    def __init__(self, config):
        Provider.__init__(self, config)
        self._values = self.config.get_list("values")
        self._nval = len(self._values)
        self._count = 0
        # print("DefinedValue self._values:", self._values)

    def run(self):
        # print("DefinedValue:", self._count % self._nval)
        val = self._values[self._count % self._nval]
        # print("DefinedValue:", val)
        self._count += 1

        return val
