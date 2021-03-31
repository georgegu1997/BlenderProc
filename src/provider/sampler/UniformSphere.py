import random
import numpy as np
import pickle

import mathutils

from src.main.Provider import Provider
from src.main.GlobalStorage import GlobalStorage


class UniformSphere(Provider):
    """ Uniformly samples a 3-dimensional vector.

        Example 1: Return a uniform;y sampled 3d vector from a range [min, max].

        {
          "provider": "sampler.UniformSphere",
          "radius": 1.0
          "center": [0, 0, 0],
        }

    **Configuration**:

    .. csv-table::
        :header: "Parameter", "Description"

        "radius", "Radius of the sphere."
        "center", "Center of the sphere."
    """

    def __init__(self, config):
        Provider.__init__(self, config)

        self._count = 0
        self._total_points = pickle.load(open("/home/qiaog/src/BlenderProc/notebooks/sphere_grid_42.pkl", 'rb'))

        # Center of the sphere.
        self._center = np.array(self.config.get_list("center", [0.0, 0.0, 0.0]))
        # Radius of the sphere.
        self._radius = self.config.get_float("radius", GlobalStorage.get("obj_diamater")) * 1.25

        # How many times each value repeats
        self._repeat = self.config.get_int("repeat", 1)

    def run(self):
        """
        :return: Sampled value. Type: Mathutils Vector
        """

        position = mathutils.Vector()
        current = self._count // self._repeat
        # print("UniformSphere current:", current)
        for i in range(3):
            position[i] = self._total_points[current, i] * self._radius + self._center[i]
        self._count += 1

        return position
