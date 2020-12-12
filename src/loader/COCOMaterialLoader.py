import os
import glob
import random

import bpy

from src.main.Module import Module
from src.utility.Utility import Utility
from src.provider.getter.Material import Material
from src.loader.LoaderInterface import LoaderInterface
from src.loader.TextureLoader import TextureLoader

class COCOMaterialLoader(Module):
    def __init__(self, config):
        Module.__init__(self, config)
        self._data_path = Utility.resolve_path(self.config.get_string("data_path"))

        self._img_files = glob.glob(os.path.join(self._data_path, "*.jpg"))
        self._num_used = self.config.get_int("num_used", 10)
        self._add_cp = self.config.get_raw_dict("add_custom_properties", {})

    def run(self):
        colorspace = self.config.get_string("colorspace", "sRGB")

        image_paths = random.sample(self._img_files, self._num_used)

        # x_texture_node = -200
        # y_texture_node = 300

        for image_path in image_paths:
            image_name = os.path.basename(image_path).split(".")[0]
            new_mat = bpy.data.materials.new("coco")
            new_mat["is_coco_texture"] = True
            new_mat["image_name"] = image_name
            new_mat.use_nodes = True

            for key, value in self._add_cp.items():
                cp_key = key
                if key.startswith("cp_"):
                    cp_key = key[len("cp_"):]
                else:
                    raise Exception("All cp have to start with cp_")
                new_mat[cp_key] = value

            # collection_of_texture_nodes = []

            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            principled_bsdf = Utility.get_the_one_node_with_type(nodes, "BsdfPrincipled")
            base_color = nodes.new('ShaderNodeTexImage')
            if not os.path.exists(image_path):
                raise Exception("The texture file {} does not exist".format(image_path))
            base_color.image = bpy.data.images.load(image_path, check_existing=True)

            # base_color.location.x = x_texture_node
            # base_color.location.y = y_texture_node
            # collection_of_texture_nodes.append(base_color)

            links.new(base_color.outputs["Color"], principled_bsdf.inputs["Base Color"])

            # principled_bsdf.inputs["Specular"].default_value = 0.333

            # if len(collection_of_texture_nodes) > 0:
            #     texture_coords = nodes.new("ShaderNodeTexCoord")
            #     texture_coords.location.x = x_texture_node * 1.4
            #     mapping_node = nodes.new("ShaderNodeMapping")
            #     mapping_node.location.x = x_texture_node * 1.2

            #     links.new(texture_coords.outputs["UV"], mapping_node.inputs["Vector"])
            #     for texture_node in collection_of_texture_nodes:
            #         links.new(mapping_node.outputs["Vector"], texture_node.inputs["Vector"])

        # textures = self._load_and_create(image_paths, colorspace)

        # for tex in textures:
        #     tex['is_coco_texture'] = True

        # self._set_properties(textures)