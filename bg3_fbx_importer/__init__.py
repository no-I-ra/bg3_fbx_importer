'''
Copyright (C) 2024 NoiraFayn
noirafaynmodding@gmail.com

Created by NoiraFayn

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "Noira's BG3 FBX Importer",
    "author": "NoiraFayn",
    "version": (1, 0, 0),
    "blender": (3, 60, 0),
    "location": "",
    "description": "Import Baldur's Gate 3 FBX converted by Noesis into Blender.",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
import os
from pathlib import Path
from mathutils import Matrix
from mathutils import Vector
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
import math
from math import *


bpy.types.Scene.targetArmature = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Scene.str_suffixe_to_remove = bpy.props.PointerProperty(type=bpy.types.Text)
bpy.types.Scene.str_prefix_to_remove = bpy.props.PointerProperty(type=bpy.types.Text)
bpy.types.Scene.str_lsxMeshBoundMin = bpy.props.PointerProperty(type=bpy.types.Text)
bpy.types.Scene.str_lsxMeshBoundMax = bpy.props.PointerProperty(type=bpy.types.Text)

def deselect_all():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

def select_object(obj, isActive):
    if obj is not None:
        if len(bpy.context.selected_objects) > 0:
            bpy.ops.object.mode_set(mode='OBJECT')
            deselect_all()
        obj.select_set(True)
        
        if isActive:
            bpy.context.view_layer.objects.active = obj

def backup_context_mode():
    current_mode = bpy.context.mode
    active_object = bpy.context.view_layer.objects.active
    selected_objects = bpy.context.selected_objects
    
    return current_mode, active_object, selected_objects
    
def restore_context_mode(current_mode, active_object, selected_objects):

    if len(bpy.context.selected_objects) >0:
        bpy.ops.object.mode_set(mode='OBJECT')     
        bpy.ops.object.select_all(action='DESELECT')
      
    if active_object:
        bpy.context.view_layer.objects.active = active_object
        for obj in selected_objects:
            obj.select_set(True)
        
        if 'EDIT' in current_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        elif 'POSE' in current_mode:
            bpy.ops.object.mode_set(mode='POSE')
            
def apply_all_transforms(object, loc=True, rot=True, scale=True):
    current_mode, active_object, selected_objects = backup_context_mode()        
    bpy.ops.object.mode_set(mode='OBJECT')        
    for object in bpy.context.selected_objects:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        object.matrix_basis.identity()            
    restore_context_mode(current_mode, active_object, selected_objects)

def set_pose_as_rest(armature):
    if armature and armature.type == 'ARMATURE': 
    
        current_mode, active_object, selected_objects = backup_context_mode()

        deselect_all()
        select_object(armature,True)
        
        apply_all_transforms(armature)
        
        bpy.ops.object.mode_set(mode='POSE')
        vanillaSelection = bpy.context.selected_pose_bones
        
        for posBone in armature.pose.bones:
            armature.pose.bones[posBone.name].bone.select = True
        
        bpy.ops.pose.armature_apply(selected=True)
        
        for bone in armature.pose.bones:
            bone.bone.select = False
            
        for bone in vanillaSelection:
            bone.bone.select = True        
        
        restore_context_mode(current_mode, active_object, selected_objects)

def rotateObjectEachFrame(obj):
    for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
        bpy.context.scene.frame_set(frame)
        obj.rotation_euler = (0, 0, 0)        
        obj.keyframe_insert(data_path="rotation_euler", index=-1)
        
def is_collection_child(collection, potential_parent):
    for child_collection in potential_parent.children:
        if child_collection == collection:
            return True
    return False

def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def set_layer_collection_active(colName):
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, colName)
    if layerColl:
        bpy.context.view_layer.active_layer_collection = layerColl
        return layerColl
    return None
    
def apply_all_transforms(obj):

    currentMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for object in bpy.context.selected_objects:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        object.matrix_basis.identity()
        
    bpy.ops.object.mode_set(mode=currentMode)

def add_armature_modifier(armature_obj, mesh_obj):
    if mesh_obj and armature_obj and armature_obj.type == 'ARMATURE':
        armature_modifier = None
        for modifier in mesh_obj.modifiers:
            if modifier.type == 'ARMATURE':
                armature_modifier = modifier
                break

        if armature_modifier:
            armature_modifier.object = armature_obj
        else:
            armature_modifier = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
            armature_modifier.object = armature_obj

def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')

def select_object(obj, isActive):
    if obj:
        bpy.ops.object.mode_set(mode='OBJECT')
        deselect_all()
        obj.select_set(True)
        
        if isActive:
            bpy.context.view_layer.objects.active = obj



class OBJECT_OT_Noira_FBXImporter(Operator, ImportHelper):
    bl_idname = "object.noira_fbx_importer"
    bl_label = "Import"
    filter_glob: StringProperty( default='*.fbx', options={'HIDDEN'} )
    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory: StringProperty(
        subtype='DIR_PATH',
    )
    def execute(self, context):
        bpy.ops.outliner.orphans_purge() #to clear cache of deleted objects names

        parent_collection = bpy.context.collection

        if bpy.context.active_object is not None:
            bpy.ops.object.mode_set(mode='OBJECT')
            deselect_all()
        
        importedObjects = []
        for current_file in self.files:
            filepath = os.path.join(self.directory, current_file.name)

            fileNameNoExt = os.path.splitext(os.path.basename(current_file.name))[0]
            
            if context.scene.str_suffixe_to_remove:
                split_string = fileNameNoExt.split(context.scene.str_suffixe_to_remove)
                if split_string[0]:
                    fileNameNoExt = split_string[0]
                
            if context.scene.str_prefix_to_remove:
                split_string = fileNameNoExt.split(context.scene.str_prefix_to_remove)
                if split_string[1]:
                    fileNameNoExt = split_string[1]
                    
            deselect_all()
            bpy.ops.import_scene.fbx(filepath=str(filepath),axis_forward='-Z', axis_up='Y', global_scale=100)             
            importedObjects = bpy.context.selected_objects
                    
            deselect_all()
            
            armatureObj = None
            meshes = []
            
            for obj in importedObjects:
                
                select_object(obj,True)

                obj.rotation_euler = (0, 0, 0)
                obj.rotation_euler.rotate_axis('X', math.radians(90))
                
                apply_all_transforms(obj)
                
                bpy.context.object['source_path'] = filepath
                
                
                if obj.type == 'ARMATURE':
                    armatureObj = obj
                    obj.name = fileNameNoExt      
                    
                    rotateObjectEachFrame(obj)            
                    
                    armature_data = obj.data
                    armature_data.name = obj.name
                    
                    if context.scene.bool_isAnimation == False:                    
                        if obj.animation_data:
                            obj.animation_data.action = None
                            obj.animation_data_clear()
                    
                    apply_all_transforms(obj)                    
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    select_object(obj,True)
                    bpy.ops.object.mode_set(mode='EDIT')

                    bone_Dummy_Root = obj.data.edit_bones.new("Dummy_Root")
                    
                    bone_Dummy_Root.head = (0, 0, 0)
                    bone_Dummy_Root.tail = (0, 0, 1)

                    bpy.context.view_layer.update()
                                       
                    for bone in obj.data.edit_bones:
                        if bone.name is not "Dummy_Root":
                            if bone.parent is None:
                                bone.parent = bone_Dummy_Root

                    bpy.context.view_layer.update()
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                else:
                    if obj.type == "MESH":
                        meshes.append(obj)

                        if obj.data.materials:
                            obj.data.materials.clear()
                        
                        if obj.data:
                            obj.data.name = obj.name
            
            deselect_all()
            
            if armatureObj:    
                for mesh in meshes:
                    select_object(mesh,True)
                    if mesh.name.find("Head") != -1:
                        if mesh.parent is None:
                            mesh.parent = armatureObj
                            add_armature_modifier(armatureObj,mesh)
                            
                        if mesh.name.find("Ears") != -1:
                            vertGroup = bpy.context.active_object.vertex_groups.new(name='Head_M')
                            
                            verts = []
                            for vert in mesh.data.vertices:
                                verts.append(vert.index)
                                
                            vertGroup.add(verts, 1.0, 'REPLACE')
             
                colName = armatureObj.name
                split_string = colName.split("_Base")
                if split_string[0]:
                    colName = split_string[0]

                active_collection = bpy.context.collection

                for obj in importedObjects:

                    collection_name = colName
                    new_collection = bpy.data.collections.get(collection_name)
                    
                    if new_collection is None:

                        new_collection = bpy.data.collections.new(collection_name)
                    else:

                        if new_collection.children:
                            old_parent = new_collection.children[0]  # Assuming only one parent
                            old_parent.children.unlink(new_collection)
                    
                    new_collection_is_child_of_active = is_collection_child(new_collection,active_collection)
                    if not new_collection_is_child_of_active:
                        active_collection.children.link(new_collection)

                    obj = bpy.data.objects.get(obj.name)
                    if obj:
                        old_parent = obj.users_collection[0]  # Assuming only one parent
                        old_parent.objects.unlink(obj)
                        new_collection.objects.link(obj)
                    

                    
                deselect_all()            
                select_object(armatureObj,True)
                
                

                
        return {'FINISHED'}
        

class PANEL_PT_Noira_NoesisImportPanel(bpy.types.Panel):
    bl_idname = "PANEL_PT_Noira_NoesisImportPanel"
    bl_label = "BG3 FBX Importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Noira's BG3 FBX Importer"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "str_prefix_to_remove")
        row = layout.row()
        row.prop(context.scene, "str_suffixe_to_remove")
        row = layout.row()
        row.prop(context.scene, "bool_isAnimation", text="Is animation")
        row = layout.row()
        row.operator("object.noira_fbx_importer", text="Import FBX Files")
           

classes = (
    PANEL_PT_Noira_NoesisImportPanel,
    OBJECT_OT_Noira_FBXImporter
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.str_prefix_to_remove = bpy.props.StringProperty \
      (
        name = "Prefix",
        description = "to remove from the file name",
        default = ""
      )
    bpy.types.Scene.str_suffixe_to_remove = bpy.props.StringProperty \
      (
        name = "Suffixe",
        description = "to remove from the file name",
        default = ""
      )
      
    bpy.types.Scene.bool_isAnimation = bpy.props.BoolProperty \
      (
        name="Is Animation",
        description="Check to import an animation",
        default=False
      )



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.str_prefix_to_remove
    del bpy.types.Scene.str_suffixe_to_remove


if __name__ == "__main__":    
    register()