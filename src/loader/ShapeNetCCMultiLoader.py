import glob
import json
import os
import random
from src.loader.ShapeNetMultiLoader import OBJ_LIST_PATH

import bpy

from src.loader.LoaderInterface import LoaderInterface
from src.utility.Utility import Utility
from src.utility.LabelIdMapping import LabelIdMapping
from src.main.GlobalStorage import GlobalStorage

import json

SHAPNET_PATH = "/home/qiaog/datasets/shapenet/ShapeNetCore.v2/"
CCTEXTURE_PATH = "/home/qiaog/datasets/cctextures_processed/"

SHAPENET_OBJECTS_JSON_PATH = "examples/shapenet_with_scenenet/training_shapenet_objects.json"
SHAPENET_TABLES_JSON_PATH = "examples/shapenet_with_scenenet/training_shapenet_tables.json"
TAXNOMY_FILE_PATH = '/home/qiaog/datasets/shapenet/ShapeNetCore.v2/taxonomy.json'
OBJ_LIST_PATH = "notebooks/shapenet_cc_objs.json"

OBJECT_ID_OFFSET = 10000

class ShapeNetCCMultiLoader(LoaderInterface):
    def __init__(self, config):
        LoaderInterface.__init__(self, config)

        self._shapenet_path = Utility.resolve_path(self.config.get_string("shapenet_path", SHAPNET_PATH))
        self._obj_ids = [int(_) for _ in self.config.get_list("obj_ids", [])]
        self._num_objects = self.config.get_int("num_objects", 3)
        self._object_scale = self.config.get_float("object_scale", 0.4)
        self._output_dir = Utility.resolve_path(self.config.get_string("output_dir"))

        self._shapenet_objects_used = json.load(open(Utility.resolve_path(SHAPENET_OBJECTS_JSON_PATH), 'r'))
        self._tables_used = json.load(open(Utility.resolve_path(SHAPENET_TABLES_JSON_PATH), 'r'))
        self._taxonomy = json.load(open(Utility.resolve_path(TAXNOMY_FILE_PATH), 'r'))

        self._files_used = []
        for synset_name, obj_ids in self._shapenet_objects_used.items():
            synset_id = next(tax['synsetId'] for tax in self._taxonomy if tax['name'] == synset_name)
            for obj_id in obj_ids:
                self._files_used.append({
                    "shapenet_synset_id": synset_id,
                    "shapenet_obj_id": obj_id,
                    "shapenet_synset_name": synset_name
                })

        self._cctexture_path = Utility.resolve_path(self.config.get_string("cctexture_path", CCTEXTURE_PATH))
        self._cc_assets = [f.split("/")[-1] for f in glob.glob(os.path.join(self._cctexture_path, "*"))]

        self._obj_list_path = Utility.resolve_path(self.config.get_string("obj_list_path", OBJ_LIST_PATH))
        with open(self._obj_list_path) as f:
            self._obj_list = json.load(f)

        print("Total number of distinguished objects:", len(self._obj_list))

    def run(self):
        if len(self._obj_ids) > 0:
            bpy.context.scene.world.light_settings.use_ambient_occlusion = True  # turn AO on
            # bpy.context.scene.world.light_settings.ao_factor = 0.5  # set it to 0.5
            used_shapenet_objs = [_ for _ in self._obj_list if _['obj_id'] in self._obj_ids]
        else:
            used_shapenet_objs = random.choices(self._obj_list, k = self._num_objects)
        
        for i, selected_obj_info in enumerate(used_shapenet_objs):
            selected_obj_path = os.path.join(
                self._shapenet_path, 
                selected_obj_info['shapenet_synset_id'], 
                selected_obj_info['shapenet_obj_id'], 
                "models", "model_normalized.obj"
            )

            loaded_obj = Utility.import_objects(selected_obj_path)
            obj_id_output = selected_obj_info['obj_id'] + OBJECT_ID_OFFSET

            for obj in loaded_obj:
                obj_name = "obj_%06d" % obj_id_output
                obj.name = obj_name
                obj['category_id'] = obj_id_output
                obj.scale = (self._object_scale, self._object_scale, self._object_scale)

                print("len(obj.material_slots)", len(obj.material_slots))
                cc_asset_names = selected_obj_info['cc_asset_names']
                for j in range(len(obj.material_slots)):
                    if j >= len(cc_asset_names):
                        break
                    mat = obj.material_slots[j]
                    mat_folder_name = cc_asset_names[j]
                    cc_mat = self._load_cc_mat(mat_folder_name)
                    mat.material = cc_mat

                # Remap the object uv coordinates
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.uv.sphere_project()
                bpy.ops.object.editmode_toggle()

                #  # Save the object meshes to .obj file if not already done so. 
                # save_obj_path = os.path.join(self._output_dir, "objects", "%s.obj" % i)
                # if not os.path.exists(os.path.dirname(save_obj_path)):
                #     if not os.path.exists(os.path.dirname(save_obj_path)):
                #         os.makedirs(os.path.dirname(save_obj_path))
                # bpy.ops.export_scene.obj(filepath=save_obj_path, use_selection=True)

                obj_diameter = (obj.dimensions[0]**2 + obj.dimensions[1]**2 + obj.dimensions[2]**2) ** (0.5)
                GlobalStorage.set("obj_diamater", obj_diameter)
                
            self._set_properties(loaded_obj)

    def _load_cc_mat(self, folder_name):
        x_texture_node = -1500
        y_texture_node = 300

        asset = folder_name.split("_")[0]

        current_path = os.path.join(self._cctexture_path, folder_name)

        base_image_path = os.path.join(current_path, "{}_2K_Color.jpg".format(asset))
        if not os.path.exists(base_image_path):
            return None

        # create a new material with the name of the asset
        new_mat = bpy.data.materials.new(folder_name)
        new_mat["is_cc_texture"] = True
        new_mat["asset_name"] = asset
        new_mat["folder_name"] = folder_name
        new_mat.use_nodes = True
        # for key, value in self._add_cp.items():
        #     cp_key = key
        #     if key.startswith("cp_"):
        #         cp_key = key[len("cp_"):]
        #     else:
        #         raise Exception("All cp have to start with cp_")
        #     new_mat[cp_key] = value

        collection_of_texture_nodes = []

        nodes = new_mat.node_tree.nodes
        links = new_mat.node_tree.links

        principled_bsdf = Utility.get_the_one_node_with_type(nodes, "BsdfPrincipled")
        output_node = Utility.get_the_one_node_with_type(nodes, "OutputMaterial")

        base_color = nodes.new('ShaderNodeTexImage')
        base_color.image = bpy.data.images.load(base_image_path, check_existing=True)
        base_color.location.x = x_texture_node
        base_color.location.y = y_texture_node
        collection_of_texture_nodes.append(base_color)

        links.new(base_color.outputs["Color"], principled_bsdf.inputs["Base Color"])

        principled_bsdf.inputs["Specular"].default_value = 0.333

        ambient_occlusion_image_path = base_image_path.replace("Color", "AmbientOcclusion")
        if os.path.exists(ambient_occlusion_image_path):
            ao_color = nodes.new('ShaderNodeTexImage')
            ao_color.image = bpy.data.images.load(ambient_occlusion_image_path, check_existing=True)
            ao_color.location.x = x_texture_node
            ao_color.location.y = y_texture_node * 2
            collection_of_texture_nodes.append(ao_color)

            math_node = nodes.new(type='ShaderNodeMixRGB')
            math_node.blend_type = "MULTIPLY"
            math_node.location.x = x_texture_node * 0.5
            math_node.location.y = y_texture_node * 1.5
            math_node.inputs["Fac"].default_value = 0.333

            links.new(base_color.outputs["Color"], math_node.inputs[1])
            links.new(ao_color.outputs["Color"], math_node.inputs[2])
            links.new(math_node.outputs["Color"], principled_bsdf.inputs["Base Color"])

        metalness_image_path = base_image_path.replace("Color", "Metalness")
        if os.path.exists(metalness_image_path):
            metalness_texture = nodes.new('ShaderNodeTexImage')
            metalness_texture.image = bpy.data.images.load(metalness_image_path, check_existing=True)
            metalness_texture.location.x = x_texture_node
            metalness_texture.location.y = y_texture_node * 0
            collection_of_texture_nodes.append(metalness_texture)

            links.new(metalness_texture.outputs["Color"], principled_bsdf.inputs["Metallic"])

        roughness_image_path = base_image_path.replace("Color", "Roughness")
        if os.path.exists(roughness_image_path):
            roughness_texture = nodes.new('ShaderNodeTexImage')
            roughness_texture.image = bpy.data.images.load(roughness_image_path, check_existing=True)
            roughness_texture.location.x = x_texture_node
            roughness_texture.location.y = y_texture_node * -1
            collection_of_texture_nodes.append(roughness_texture)

            links.new(roughness_texture.outputs["Color"], principled_bsdf.inputs["Roughness"])

        alpha_image_path = base_image_path.replace("Color", "Opacity")
        if os.path.exists(alpha_image_path):
            alpha_texture = nodes.new('ShaderNodeTexImage')
            alpha_texture.image = bpy.data.images.load(alpha_image_path, check_existing=True)
            alpha_texture.location.x = x_texture_node
            alpha_texture.location.y = y_texture_node * -2
            collection_of_texture_nodes.append(alpha_texture)

            links.new(alpha_texture.outputs["Color"], principled_bsdf.inputs["Alpha"])

        normal_image_path = base_image_path.replace("Color", "Normal")
        normal_y_value = y_texture_node * -3
        if os.path.exists(normal_image_path):
            normal_texture = nodes.new('ShaderNodeTexImage')
            normal_texture.image = bpy.data.images.load(normal_image_path, check_existing=True)
            normal_texture.location.x = x_texture_node
            normal_texture.location.y = normal_y_value
            collection_of_texture_nodes.append(normal_texture)
            direct_x_mode = True
            if direct_x_mode:

                separate_rgba = nodes.new('ShaderNodeSeparateRGB')
                separate_rgba.location.x = 4.0/5.0 * x_texture_node
                separate_rgba.location.y = normal_y_value
                links.new(normal_texture.outputs["Color"], separate_rgba.inputs["Image"])

                invert_node = nodes.new("ShaderNodeInvert")
                invert_node.inputs["Fac"].default_value = 1.0
                invert_node.location.x = 3.0/5.0 * x_texture_node
                invert_node.location.y = normal_y_value

                links.new(separate_rgba.outputs["G"], invert_node.inputs["Color"])

                combine_rgba = nodes.new('ShaderNodeCombineRGB')
                combine_rgba.location.x = 2.0/5.0 * x_texture_node
                combine_rgba.location.y = normal_y_value
                links.new(separate_rgba.outputs["R"], combine_rgba.inputs["R"])
                links.new(invert_node.outputs["Color"], combine_rgba.inputs["G"])
                links.new(separate_rgba.outputs["B"], combine_rgba.inputs["B"])

                current_output = combine_rgba.outputs["Image"]
            else:
                current_output = normal_texture.outputs["Color"]

            normal_map = nodes.new("ShaderNodeNormalMap")
            normal_map.inputs["Strength"].default_value = 1.0
            normal_map.location.x = 1.0 / 5.0 * x_texture_node
            normal_map.location.y = normal_y_value
            links.new(current_output, normal_map.inputs["Color"])
            links.new(normal_map.outputs["Normal"], principled_bsdf.inputs["Normal"])


        displacement_image_path = base_image_path.replace("Color", "Displacement")
        if os.path.exists(displacement_image_path):
            displacement_texture = nodes.new('ShaderNodeTexImage')
            displacement_texture.image = bpy.data.images.load(displacement_image_path, check_existing=True)
            displacement_texture.location.x = x_texture_node
            displacement_texture.location.y = y_texture_node * -4
            collection_of_texture_nodes.append(displacement_texture)

            displacement_node = nodes.new("ShaderNodeDisplacement")
            displacement_node.inputs["Midlevel"].default_value = 0.5
            displacement_node.inputs["Scale"].default_value = 0.05
            displacement_node.location.x = x_texture_node * 0.5
            displacement_node.location.y = y_texture_node * -4
            links.new(displacement_texture.outputs["Color"], displacement_node.inputs["Height"])
            links.new(displacement_node.outputs["Displacement"], output_node.inputs["Displacement"])


        if len(collection_of_texture_nodes) > 0:
            texture_coords = nodes.new("ShaderNodeTexCoord")
            texture_coords.location.x = x_texture_node * 1.4
            mapping_node = nodes.new("ShaderNodeMapping")
            mapping_node.location.x = x_texture_node * 1.2

            links.new(texture_coords.outputs["UV"], mapping_node.inputs["Vector"])
            for texture_node in collection_of_texture_nodes:
                links.new(mapping_node.outputs["Vector"], texture_node.inputs["Vector"])

        return new_mat