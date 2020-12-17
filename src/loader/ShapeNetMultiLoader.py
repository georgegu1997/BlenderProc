import glob
import json
import os
import random

import bpy

from src.loader.LoaderInterface import LoaderInterface
from src.utility.Utility import Utility
from src.utility.LabelIdMapping import LabelIdMapping

import json
# SHAPENET_OBJECTS_JSON_PATH = "/home/qiaog/pose-est/BlenderProc/examples/shapenet_with_scenenet/training_shapenet_objects.json"
# SHAPENET_TABLES_JSON_PATH = "/home/qiaog/pose-est/BlenderProc/examples/shapenet_with_scenenet/training_shapenet_tables.json"

OBJ_LIST_PATH = "/home/qiaog/pose-est/BlenderProc/notebooks/objs.txt"
SHAPNET_PATH = "/home/qiaog/datasets/shapenet/ShapeNetCore.v2/"
MSCOCO_PATH = "/home/qiaog/datasets/mscoco/train2017/"

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

        self._shapenet_path = Utility.resolve_path(self.config.get_string("shapenet_path", SHAPNET_PATH))
        self._mscoco_path = Utility.resolve_path(self.config.get_string("mscoco_path", MSCOCO_PATH))
        self._obj_list_path = Utility.resolve_path(self.config.get_string("obj_list_path", OBJ_LIST_PATH))

        self._num_objects = self.config.get_int("num_objects", 3)

        with open(self._obj_list_path) as f:
            self._obj_list = json.load(f)

    def run(self):
        """
        Uses the loaded .obj files and picks one randomly and loads it
        """
        # selected_obj = random.choice(self._files_with_fitting_synset)
        # selected_obj = self._files_with_fitting_synset[0]
        for i in range(self._num_objects):
            selected_obj_info = random.choice(self._obj_list)
            selected_obj_path = os.path.join(
                self._shapenet_path, 
                selected_obj_info['shapenet_synset_id'], 
                selected_obj_info['shapenet_obj_id'], 
                "models", "model_normalized.obj"
            )

            loaded_obj = Utility.import_objects(selected_obj_path)

            print("len(loaded_obj)", len(loaded_obj))
            for obj in loaded_obj:
                obj_name = "obj_%04d" % selected_obj_info['obj_id']
                obj.name = obj_name
                obj.scale = (0.4, 0.4, 0.4)
                
                # Load and assign COCO images into materials of this object
                print("len(obj.material_slots)", len(obj.material_slots))
                for j in range(len(obj.material_slots)):
                    mat = obj.material_slots[j]

                    coco_filename = selected_obj_info['coco_filenames'][j % len(selected_obj_info['coco_filenames'])]
                    texture_path = os.path.join(self._mscoco_path, coco_filename)
                    mat_coco = self._load_mat(texture_path)
                    mat.material = mat_coco

                # Remap the object uv coordinates
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.uv.sphere_project()
                bpy.ops.object.editmode_toggle()

                # Save the object meshes to .obj file if not already done so. 
                save_obj_path = os.path.join(self._output_dir, "objects", "%s.obj" % obj_name)
                if not os.path.exists(save_obj_path):
                    if not os.path.exists(os.path.dirname(save_obj_path)):
                        os.makedirs(os.path.dirname(save_obj_path))
                    bpy.ops.export_scene.obj(filepath=save_obj_path, use_selection=True)

            self._correct_materials(loaded_obj)
            self._set_properties(loaded_obj)

            for obj in loaded_obj:
                obj['category_id'] = selected_obj_info['obj_id']

    def _load_mat(self, image_path):
        image_name = os.path.basename(image_path).split(".")[0]

        new_mat = bpy.data.materials.new(image_name)
        new_mat["is_coco_texture"] = True
        new_mat["image_name"] = image_name
        new_mat.use_nodes = True

        nodes = new_mat.node_tree.nodes
        links = new_mat.node_tree.links

        principled_bsdf = Utility.get_the_one_node_with_type(nodes, "BsdfPrincipled")
        base_color = nodes.new('ShaderNodeTexImage')
        if not os.path.exists(image_path):
            raise Exception("The texture file {} does not exist".format(image_path))
        base_color.image = bpy.data.images.load(image_path, check_existing=True)
        
        links.new(base_color.outputs["Color"], principled_bsdf.inputs["Base Color"])
        return new_mat

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
