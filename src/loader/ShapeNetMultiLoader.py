import glob
import json
import os
import random

from mathutils import Matrix, Vector

from numpy.lib.arraypad import _set_reflect_both

from src.loader.LoaderInterface import LoaderInterface
from src.utility.Utility import Utility
from src.utility.LabelIdMapping import LabelIdMapping

import json
SHAPENET_OBJECTS_JSON_PATH = "/home/qiaog/pose-est/BlenderProc/examples/shapenet_with_scenenet/training_shapenet_objects.json"
SHAPENET_TABLES_JSON_PATH = "/home/qiaog/pose-est/BlenderProc/examples/shapenet_with_scenenet/training_shapenet_tables.json"

class ShapeNetMultiLoader(LoaderInterface):
    """
    This loads an object from ShapeNet based on the given synset_id, which specifies the category of objects to use.

    From these objects one is randomly sampled and loaded.

    As for all loaders it is possible to add custom properties to the loaded object, for that use add_properties.

    Finally it sets all objects to have a category_id corresponding to the void class, 
    so it wouldn't trigger an exception in the SegMapRenderer.

    Note: if this module is used with another loader that loads objects with semantic mapping, make sure the other module is loaded first in the config file.

    **Configuration**:

    .. csv-table::
       :header: "Parameter", "Description"

       "data_path", "The path to the ShapeNetCore.v2 folder. Type: string."
       "used_synset_id", "The synset id for example: '02691156', check the data_path folder for more ids. Type: int."
    """

    def __init__(self, config):
        LoaderInterface.__init__(self, config)

        self._data_path = Utility.resolve_path(self.config.get_string("data_path"))
        self._used_synset_id = self.config.get_string("used_synset_id")
        self._num_objects = self.config.get_int("num_objects", 3)

        taxonomy_file_path = os.path.join(self._data_path, "taxonomy.json")
        # self._files_with_fitting_synset = ShapeNetMultiLoader.get_files_with_synset(self._used_synset_id, taxonomy_file_path,
        #                                                                        self._data_path)
        self._objects_used = json.load(open(SHAPENET_OBJECTS_JSON_PATH, 'r'))
        self._tables_used = json.load(open(SHAPENET_TABLES_JSON_PATH, 'r'))
        self._taxonomy = json.load(open(taxonomy_file_path, 'r'))

        self._files_used = []
        for synset_name, obj_ids in self._objects_used.items():
            synset_id = next(tax['synsetId'] for tax in self._taxonomy if tax['name'] == synset_name)
            for obj_id in obj_ids:
                self._files_used.append(os.path.join(self._data_path, synset_id, obj_id, "models", "model_normalized.obj"))

    def run(self):
        """
        Uses the loaded .obj files and picks one randomly and loads it
        """
        # selected_obj = random.choice(self._files_with_fitting_synset)
        # selected_obj = self._files_with_fitting_synset[0]
        for i in range(self._num_objects):
            selected_obj = random.choice(self._files_used)
            loaded_obj = Utility.import_objects(selected_obj)
            
            for obj in loaded_obj:
                obj.scale = (0.2, 0.2, 0.2)

            self._correct_materials(loaded_obj)

            self._set_properties(loaded_obj)

            if "void" in LabelIdMapping.label_id_map:  # Check if using an id map
                for obj in loaded_obj:
                    obj['category_id'] = LabelIdMapping.label_id_map["void"]
                    x, y, z = obj.dimensions

    def _correct_materials(self, objects):
        """
        If the used material contains an alpha texture, the alpha texture has to be flipped to be correct
        :param objects, objects where the material maybe wrong
        """

        for obj in objects:
            for mat_slot in obj.material_slots:
                material = mat_slot.material
                nodes = material.node_tree.nodes
                links = material.node_tree.links
                texture_nodes = Utility.get_nodes_with_type(nodes, "ShaderNodeTexImage")
                if texture_nodes and len(texture_nodes) > 1:
                    principled_bsdf = Utility.get_the_one_node_with_type(nodes, "BsdfPrincipled")
                    # find the image texture node which is connect to alpha
                    node_connected_to_the_alpha = None
                    for node_links in principled_bsdf.inputs["Alpha"].links:
                        if "ShaderNodeTexImage" in node_links.from_node.bl_idname:
                            node_connected_to_the_alpha = node_links.from_node
                    # if a node was found which is connected to the alpha node, add an invert between the two
                    if node_connected_to_the_alpha is not None:
                        invert_node = nodes.new("ShaderNodeInvert")
                        invert_node.inputs["Fac"].default_value = 1.0
                        Utility.insert_node_instead_existing_link(links, node_connected_to_the_alpha.outputs["Color"],
                                                                  invert_node.inputs["Color"],
                                                                  invert_node.outputs["Color"],
                                                                  principled_bsdf.inputs["Alpha"])
