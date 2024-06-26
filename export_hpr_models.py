#-*- coding:utf-8 -*-

# Blender Need for Speed Hot Pursuit Remastered (2020) exporter Add-on
# Add-on developed by DGIorio with contributions and tests by Piotrek


## TO DO
"""
- Support for more wheels (num_wheels on graphicsSpec)
- Review PolygonSoupList for vehicles
- Review debug_redirect_vehicle
- Review collision tags
"""


bl_info = {
	"name": "Export to Need for Speed Hot Pursuit Remastered (2020) models format (.dat)",
	"description": "Save objects as Need for Speed Hot Pursuit Remastered files",
	"author": "DGIorio",
	"version": (3, 1),
	"blender": (3, 1, 0),
	"location": "File > Export > Need for Speed Hot Pursuit Remastered (2020) (.dat)",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
    "doc_url": "https://docs.google.com/document/d/1Vz9iIKMCYnIFS7giVAUu0WV8m8zIOoiqTzGKOQsXl_Q",
	"support": "COMMUNITY",
	"category": "Import-Export"}


import bpy
from bpy.types import Operator
from bpy.props import (
	StringProperty,
	BoolProperty,
	FloatVectorProperty,
	EnumProperty
)
from bpy_extras.io_utils import (
	ExportHelper,
	orientation_helper,
	axis_conversion,
)
import bmesh
import binascii
import math
from mathutils import Euler, Matrix, Quaternion, Vector
import os
import time
import struct
import sys
import traceback
import numpy as np
import shutil
import zlib
from collections import Counter
from bundle_packer_unpacker import pack_bundle_hp, get_resourcetype_nibble_hpr
try:
	from bundle_cleaner_hpr import clean_model_data
except:
	print("WARNING: bundle_cleaner_hpr.py not found in Blender addons folder. Cleaning original wheel model data will not be possible.")
try:
	from hp_custom_materials import custom_shaders, get_default_sampler_states, get_default_material_parameters, get_default_mRasterId
except:
	print("WARNING: hp_custom_materials.py not found in Blender addons folder. Custom material data will not be available.")


def main(context, export_path, pack_bundle_file, ignore_hidden_meshes, copy_uv_layer, force_rotation, transform_args, global_rotation,
		 force_shared_asset_as_false, debug_shared_not_found,
		 debug_use_shader_material_parameters, debug_use_default_samplerstates, debug_redirect_vehicle, new_vehicle_name, m):
	
	os.system('cls')
	start_time = time.time()
	
	if bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')
	
	
	## INITIALIZING
	print("Initializing variables...")
	
	game = "HPR"
	shared_dir = os.path.join(NFSHPLibraryGet(), "NFSHPR_Library_PC")
	shared_model_dir = os.path.join(shared_dir, "Model")
	shared_renderable_dir = os.path.join(shared_dir, "Renderable")
	shared_vertex_descriptor_dir = os.path.join(os.path.join(shared_dir, "SHADERS"), "VertexDescriptor")
	shared_material_dir = os.path.join(shared_dir, "Material")
	shared_shader_dir = os.path.join(os.path.join(shared_dir, "SHADERS"), "Shader")
	shared_samplerstate_dir = os.path.join(shared_dir, "SamplerState")
	shared_raster_dir = os.path.join(shared_dir, "Texture")
	shared_trafficattribs_dir = os.path.join(shared_dir, "TRAFFICATTRIBS")
	shared_characters_dir = os.path.join(shared_dir, "CHARACTERS")
	shared_skeleton_dir = os.path.join(shared_dir, "Skeleton")
	shared_animationlist_dir = os.path.join(shared_dir, "AnimationList")
	shared_pvs_dir = os.path.join(shared_dir, "PVS")
	
	zonelist_path = os.path.join(os.path.join(shared_pvs_dir, "ZoneList"), "F6_05_19_5F.dat")
	globalresources_path = os.path.join(shared_dir, "IDs_GLOBALRESOURCES.BNDL")
	districts_path = []
	for file in os.listdir(shared_dir):
		if "IDs_DISTRICT_" in file:
			districts_path.append(os.path.join(shared_dir, file))
	
	track_unit_number = None
	
	force_shared_model_as_false = False
	force_shared_material_as_false = False
	force_shared_texture_as_false = False
	if 'MODEL' in force_shared_asset_as_false:
		force_shared_model_as_false = True
	if 'MATERIAL' in force_shared_asset_as_false:
		force_shared_material_as_false = True
	if 'TEXTURE' in force_shared_asset_as_false:
		force_shared_texture_as_false = True
	
	for main_collection in bpy.context.scene.collection.children:
		is_hidden = bpy.context.view_layer.layer_collection.children.get(main_collection.name).hide_viewport
		is_excluded = bpy.context.view_layer.layer_collection.children.get(main_collection.name).exclude
		
		if is_hidden or is_excluded:
			print("WARNING: skipping main collection %s since it is hidden or excluded." % (main_collection.name))
			print("")
			continue
		
		main_directory_path = os.path.join(export_path, main_collection.name)
		
		print("Reading scene data for main collection %s..." % (main_collection.name))
		
		if "resource_type" in main_collection:
			resource_type = main_collection["resource_type"]
		else:
			print("WARNING: collection %s is missing parameter %s. Define one of the followings: 'GraphicsSpec', 'InstanceList', 'CharacterSpec', 'ZoneList'." % (main_collection.name, '"resource_type"'))
			resource_type = "GraphicsSpec"
			#return {"CANCELLED"}
		
		try:
			collections_types = {collection["resource_type"] : collection for collection in main_collection.children}
		except:
			print("WARNING: some collection is missing parameter %s. Define one of the followings: 'GraphicsSpec', 'WheelGraphicsSpec', 'PolygonSoupList', 'Character', 'Effects', 'Skeleton', 'ControlMesh', 'CharacterSpec', 'ZoneList'." % '"resource_type"')
			collections_types = {}
			for collection in main_collection.children:
				try:
					collections_types[collection["resource_type"]] = collection
				except:
					collections_types["GraphicsSpec"] = collection
				
			#return {"CANCELLED"}
		
		if resource_type == "InstanceList":
			track_unit_name = main_collection.name
			track_unit_number = track_unit_name.replace("TRK_UNIT", "").replace("TRK", "").replace("UNIT", "")
			track_unit_number = track_unit_number.replace("trk_unit", "").replace("trk", "").replace("unit", "").replace("_", "")
			track_unit_number = track_unit_number.replace("_GR", "").replace("GR", "")
			try:
				track_unit_number = int(track_unit_number)
			except:
				print("ERROR: collection %s name is not in the proper formating. Define it as TRK_UNITXXX where XXX is a number." % track_unit_name)
				return {"CANCELLED"}
			mInstanceListId = calculate_resourceid("trk_unit" + str(track_unit_number) + "_list")
			instancelist_collection = collections_types["InstanceList"]
			collections = [instancelist_collection,]
			
			mDynamicInstanceList = "TRK_UNIT" + str(track_unit_number) + "_dynlist"
			mGroundcoverCollection = "TRK_UNIT" + str(track_unit_number) + "_gcvr"
			mLightInstanceList = "TRK_UNIT" + str(track_unit_number) + "_lightlist"
			mPolygonSoupList = "TRK_COL_" + str(track_unit_number)
			mZoneHeader = "TRK_UNIT" + str(track_unit_number) + "_hdr"
			
			mDynamicInstanceListId = calculate_resourceid(mDynamicInstanceList.lower())
			mGroundcoverCollectionId = calculate_resourceid(mGroundcoverCollection.lower())
			mLightInstanceListId = calculate_resourceid(mLightInstanceList.lower())
			mPolygonSoupListId = calculate_resourceid(mPolygonSoupList.lower())
			mZoneHeaderId = calculate_resourceid(mZoneHeader.lower())
			
			if "PolygonSoupList" in collections_types:
				polygonsouplist_collection = collections_types["PolygonSoupList"]
				collections.append(polygonsouplist_collection)
			elif "Collision" in collections_types:
				polygonsouplist_collection = collections_types["Collision"]
			else:
				print("WARNING: collection %s is missing. An empty one will be created." % '"PolygonSoupList"')
			
			if "Skeleton" in collections_types:
				skeleton_collection = collections_types["Skeleton"]
				collections.append(skeleton_collection)
			
			muDistrictId = -1
			
			models_disctrict = []
			renderables_disctrict = []
			materials_disctrict = []
			textures_disctrict = []
			
			models_globalresources = []
			renderables_globalresources = []
			materials_globalresources = []
			textures_globalresources = []
			
			zones = read_zonelist(zonelist_path)
			for zone in zones:
				muZoneId = zone[0] 
				if muZoneId == track_unit_number:
					muDistrictId = zone[1][2]
					break
			
			if muDistrictId != -1:
				district_path = None
				for path in districts_path:
					if str(muDistrictId) in path:
						district_path = path
						break
				
				if district_path != None:
					models_disctrict, renderables_disctrict, materials_disctrict, textures_disctrict = read_resources_table(district_path)
				else:
					print("WARNING: IDs file of district %d not found in shared folder." % muDistrictId)
			else:
				print("WARNING: DistrictId of track unit number %d not found in PVS file." % track_unit_number)
			
			models_globalresources, renderables_globalresources, materials_globalresources, textures_globalresources = read_resources_table(globalresources_path)
		
		elif resource_type == "GraphicsSpec":
			vehicle_name = main_collection.name
			vehicle_number = vehicle_name.replace("VEH", "").replace("HI", "").replace("LO", "").replace("TR", "").replace("GR", "").replace("MS", "")
			vehicle_number = vehicle_number.replace("veh", "").replace("hi", "").replace("lo", "").replace("tr", "").replace("gr", "").replace("ms", "").replace("_", "")
			try:
				test = int(vehicle_number)
			except:
				print("ERROR: main_collection's name is in the wrong format. Use something like VEH_118608_MS.")
				return {"CANCELLED"}
			mGraphicsSpecId = int_to_id(vehicle_number)
			
			mSkeleton = "VEH_" + str(vehicle_number) + "_skeleton"
			mSkeletonId = calculate_resourceid(mSkeleton.lower())
			mControlMeshId = ""
			
			graphicsspec_collection = collections_types["GraphicsSpec"]
			
			collections = [graphicsspec_collection,]
			
			if "WheelGraphicsSpec" in collections_types:
				wheelgraphicsspec_collection = collections_types["WheelGraphicsSpec"]
				collections.append(wheelgraphicsspec_collection)
			elif "Wheels" in collections_types:
				wheelgraphicsspec_collection = collections_types["Wheels"]
				collections.append(wheelgraphicsspec_collection)
			
			# if "PolygonSoupList" in collections_types:
				# polygonsouplist_collection = collections_types["PolygonSoupList"]
				# collections.append(polygonsouplist_collection)
			# elif "Collision" in collections_types:
				# polygonsouplist_collection = collections_types["Collision"]
				# collections.append(polygonsouplist_collection)
			
			if "Character" in collections_types:
				character_collection = collections_types["Character"]
				collections.append(character_collection)
			elif "Driver" in collections_types:
				character_collection = collections_types["Driver"]
				collections.append(character_collection)
			
			if "Effects" in collections_types:
				effects_collection = collections_types["Effects"]
				collections.append(effects_collection)
			elif "Effect" in collections_types:
				effects_collection = collections_types["Effect"]
				collections.append(effects_collection)
			
			if "Skeleton" in collections_types:
				skeleton_collection = collections_types["Skeleton"]
				collections.append(skeleton_collection)
			
			if "ControlMesh" in collections_types:
				controlmesh_collection = collections_types["ControlMesh"]
				collections.append(controlmesh_collection)
		
		elif resource_type == "CharacterSpec":
			character_name = main_collection.name
			character_number = character_name.replace("CHR", "").replace("CHAR", "").replace("GR", "").replace("TR", "").replace("MS", "").replace("_", "")
			
			try:
				test = int(character_number)
			except:
				print("ERROR: main_collection's name is in the wrong format. Use a number in integer format.")
			
			try:
				mSkeletonId = main_collection["SkeletonID"]
			except:
				try:
					mSkeletonId = main_collection["SkeletonId"]
				except:
					mSkeletonId = 0x00043EB4
			
			try:
				mSkeletonId = int(mSkeletonId)
			except:
				try:
					if is_valid_id(mSkeletonId) == False:
						mSkeletonId = "B4_3E_04_00"
					mSkeletonId = id_to_int(mSkeletonId)
				except:
					mSkeletonId = 0x00043EB4
			
			try:
				mAnimationListId = main_collection["AnimationListID"]
			except:
				try:
					mAnimationListId = main_collection["AnimationListId"]
				except:
					mAnimationListId = 0x0002C332
			
			try:
				mAnimationListId = int(mAnimationListId)
			except:
				try:
					if is_valid_id(mAnimationListId) == False:
						mAnimationListId = "32_C3_02_00"
					mAnimationListId = id_to_int(mAnimationListId)
				except:
					mAnimationListId = 0x0002C332
			
			mCharacterSpecId = int_to_id(character_number)
			mSkeletonId = int_to_id(mSkeletonId)
			mAnimationListId = int_to_id(mAnimationListId)
			characterspec_collection = collections_types["CharacterSpec"]
			
			collections = [characterspec_collection,]
			
			if "Skeleton" in collections_types:
				skeleton_collection = collections_types["Skeleton"]
				collections.append(skeleton_collection)
		
		elif resource_type == "ZoneList":
			try:
				mZoneList = main_collection["world_name"]
			except:
				mZoneList = "SEACREST"
			
			mZoneListId = calculate_resourceid(mZoneList.lower())
			zonelist_collection = collections_types["ZoneList"]
			collections = [zonelist_collection,]
		
		else:
			print("ERROR: resource type %s not supported." % resource_type)
			return {"CANCELLED"}
		
		#directory_path = os.path.join(main_directory_path, vehicle_name)
		directory_path = main_directory_path
		
		instancelist_dir = os.path.join(directory_path, "InstanceList")
		dynamicinstancelist_dir = os.path.join(directory_path, "DynamicInstanceList")
		groundcovercollection_dir = os.path.join(directory_path, "GroundcoverCollection")
		lightinstancelist_dir = os.path.join(directory_path, "LightInstanceList")
		polygonsouplist_dir = os.path.join(directory_path, "PolygonSoupList")
		zoneheader_dir = os.path.join(directory_path, "ZoneHeader")
		zonelist_dir = os.path.join(directory_path, "ZoneList")
		graphicsspec_dir = os.path.join(directory_path, "GraphicsSpec")
		genesysinstance_dir = os.path.join(directory_path, "GenesysInstance")
		characterspec_dir = os.path.join(directory_path, "CharacterSpec")
		model_dir = os.path.join(directory_path, "Model")
		renderable_dir = os.path.join(directory_path, "Renderable")
		vertex_descriptor_dir = os.path.join(directory_path, "VertexDescriptor")
		material_dir = os.path.join(directory_path, "Material")
		samplerstate_dir = os.path.join(directory_path, "SamplerState")
		raster_dir = os.path.join(directory_path, "Texture")
		skeleton_dir = os.path.join(directory_path, "Skeleton")
		controlmesh_dir = os.path.join(directory_path, "ControlMesh")
		animationlist_dir = os.path.join(directory_path, "AnimationList")
		trafficattribs_dir = os.path.join(export_path, "TRAFFICATTRIBS")
		
		export_effects = True
		
		instances = []
		instances_wheel = []
		instances_wheelGroups = {}
		instances_character = []
		instances_effects = []
		instance_collision = []
		PolygonSoups = []
		Skeleton = []
		ControlMeshes = []
		zonelist = []
		models = []
		renderables = []
		materials = []
		shaders = {}
		samplerstates = []
		rasters = []
		
		for collection in collections:
			is_hidden = bpy.context.view_layer.layer_collection.children.get(main_collection.name).children.get(collection.name).hide_viewport
			is_excluded = bpy.context.view_layer.layer_collection.children.get(main_collection.name).children.get(collection.name).exclude
			
			if is_hidden or is_excluded:
				print("WARNING: skipping collection %s since it is hidden or excluded." % (collection.name))
				print("")
				continue
			
			resource_type_child = collection["resource_type"]
			
			objects = collection.objects
			object_index = -1
			
			for object in objects:
				if object.type != "EMPTY":
					continue
				
				is_hidden = object.hide_get()
				if is_hidden == True:
					continue
				
				# Model
				mModelId = object.name
				mModelId = mModelId.split(".")[0]
				
				if resource_type_child in ("InstanceList", "GraphicsSpec", "WheelGraphicsSpec", "Wheels", "CharacterSpec"):
					if is_valid_id(mModelId) == False:
						return {"CANCELLED"}
					
					try:
						is_model_shared_asset = object["is_shared_asset"]
					except:
						is_model_shared_asset = False
					
					if force_shared_model_as_false == True:
						is_model_shared_asset = False
					
					if is_model_shared_asset == True:
						model_path = os.path.join(shared_model_dir, mModelId + ".dat")
						if resource_type_child == "InstanceList":
							if mModelId in models_globalresources:
								pass
							elif mModelId in models_disctrict:
								pass
							else:
								print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("model", mModelId, muDistrictId))
								if debug_shared_not_found == True:
									print("WARNING: setting %s %s is_shared_asset to False." % ("model", mModelId))
									is_model_shared_asset = False
						if not os.path.isfile(model_path):
							print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC." % ("model", mModelId))
							if debug_shared_not_found == True:
								print("WARNING: setting %s %s is_shared_asset to False." % ("model", mModelId))
								is_model_shared_asset = False
				
				if resource_type_child == "InstanceList":
					try:
						object_index = object["object_index"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"object_index"'))
						object_index = object_index + 1
					
					try:
						is_instance_always_loaded = object["is_always_loaded"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"is_always_loaded"'))
						is_instance_always_loaded = True
					
					try:
						mi16BackdropZoneID = object["BackdropZoneID"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"BackdropZoneID"'))
						mi16BackdropZoneID = -1
					
					try:
						unknown_0xC = object["unknown_0xC"]
					except:
						try:
							unknown_0xC = object["unknown_0x8"]
						except:
							print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"unknown_0xC"'))
							unknown_0xC = 1104995
					
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world).transposed()
					instances.append([object_index, [mModelId, [mTransform], is_instance_always_loaded, mi16BackdropZoneID, unknown_0xC]])
				
				elif resource_type_child == "GraphicsSpec":
					try:
						object_index = object["object_index"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"object_index"'))
						object_index = object_index + 1
					
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world).transposed()
					instances.append([object_index, [mModelId, [mTransform]]])
				
				elif resource_type_child == "CharacterSpec":
					try:
						object_index = object["object_index"]
					except:
						object_index = object_index + 1
					
					instances.append([object_index, [mModelId]])
				
				elif resource_type_child == "WheelGraphicsSpec" or resource_type_child == "Wheels":
					try:
						object_index = object["object_index"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"object_index"'))
						object_index = object_index + 1
					
					try:
						is_spinnable = object["spinnable"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming as True (1)." % (object.name, '"spinnable"'))
						is_spinnable = 1
					
					try:
						object_placement = object["placement"].lower()
					except:
						try:
							object_placement = object["location"].lower()
						except:
							print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"placement"'))
							object_placement = "frontleft"
					
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world).transposed()
					
					instances_wheel.append([object_index, [mModelId, [mTransform], is_spinnable, object_placement]])
				
				elif resource_type_child == "PolygonSoupList" or resource_type_child == "Collision":
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world)
					
					try:
						object_index = int(object.name.replace("PolygonSoup", "").replace("_", "").split(".")[0])
					except:
						try:
							object_index = int(object["object_index"])
						except:
							print("WARNING: object %s is missing parameter %s. With it is possible to set an specific order in the exported file. Assuming some value." % (object.name, '"object_index"'))
							object_index = object_index + 1
					
					try:
						child = object.children[0]
					except:
						# No meshes in the object
						continue
					
					#bbox = [list(point[:]) for point in child.bound_box]
					#bboxX, bboxY, bboxZ = zip(*bbox)
					
					mValidMasks = -1
					#PolySoupBox = [[min(bboxX), min(bboxY), min(bboxZ)], [max(bboxX), max(bboxY), max(bboxZ)], mValidMasks]
					maiVertexOffsets = mTransform.translation
					mfComprGranularity = mTransform.to_scale()[0]
					if mTransform.to_scale()[0] != mTransform.to_scale()[1] or mTransform.to_scale()[0] != mTransform.to_scale()[2] or mTransform.to_scale()[1] != mTransform.to_scale()[2]:
						print("WARNING: object %s have different scales per axis. Consider applying the scale." % object.name)
					
					status, PolygonSoupVertices, PolygonSoupPolygons, mu8NumQuads = read_polygonsoup_object(child, maiVertexOffsets, mfComprGranularity, resource_type, track_unit_number)
					if status == 1:
						return {"CANCELLED"}
					
					if len(PolygonSoupVertices) == 0 or len(PolygonSoupPolygons) == 0:
						print("WARNING: collision mesh %s does not have vertices or faces. Skipping it." % child.data.name)
						continue
					
					bboxX, bboxY, bboxZ = zip(*PolygonSoupVertices)
					PolySoupBox = [[min(bboxX)*mfComprGranularity + maiVertexOffsets[0], min(bboxY)*mfComprGranularity + maiVertexOffsets[1], min(bboxZ)*mfComprGranularity + maiVertexOffsets[2]],
								   [max(bboxX)*mfComprGranularity + maiVertexOffsets[0], max(bboxY)*mfComprGranularity + maiVertexOffsets[1], max(bboxZ)*mfComprGranularity + maiVertexOffsets[2]], mValidMasks]
					
					#maiVertexOffsets /= mfComprGranularity
					#maiVertexOffsets = [int(vertex_offset) for vertex_offset in maiVertexOffsets]
					
					PolygonSoup = [object_index, PolySoupBox, maiVertexOffsets, mfComprGranularity, PolygonSoupVertices, PolygonSoupPolygons, mu8NumQuads]
					
					PolygonSoups.append(PolygonSoup)
					
					continue
				
				elif resource_type_child == "Character" or resource_type_child == "Driver":
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world)
					characterOffset = mTransform.translation
					#characterOffset[1] = -characterOffset[1]
					
					try:
						mCharacterSpecID = object["CharacterSpecID"]
					except:
						try:
							mCharacterSpecID = object["CharacterID"]
						except:
							mCharacterSpecID = 117042
					
					try:
						mCharacterSpecID = int(mCharacterSpecID)
					except:
						try:
							if is_valid_id(mCharacterSpecID) == False:
								mCharacterSpecID = "32_C9_01_00"
							mCharacterSpecID = id_to_int(mCharacterSpecID)
						except:
							mCharacterSpecID = 117042
					
					instances_character = [mCharacterSpecID, characterOffset]
					
					continue
				
				elif resource_type_child == "Effects" or resource_type_child == "Effect":
					if object.parent != None:
						continue
					
					try:
						effect_index = int(object.name.split("_")[1].split(".")[0])
					except:
						try:
							effect_index = int(object["effect_index"])
						except:
							print("ERROR: effect object %s is missing parameter %s. Effects will not be exported." % (object.name, '"effect_index"'))
							export_effects = False
							continue
					
					try:
						EffectId = object["EffectId"]
					except:
						print("ERROR: effect object %s is missing parameters %s. Effects will not be exported." % (object.name, '"EffectId"'))
						export_effects = False
						continue
					
					try:
						EffectId = int(EffectId)
					except:
						try:
							EffectId = id_to_int(EffectId)
						except:
							print("ERROR: effect object %s parameter %s is not an integer or an Id. Effects will not be exported." % (object.name, '"EffectId"'))
							export_effects = False
							continue
					
					effect_copy_instance = []
					for child in object.children:
						if child.type != "EMPTY":
							continue
						
						if force_rotation == True:
							transform_args[1] = True
							apply_transfrom(child, global_rotation, *transform_args)
						
						mTransform = Matrix(np.linalg.inv(m) @ child.matrix_world)
						effectLocation = mTransform.translation
						child.rotation_mode = 'QUATERNION'
						effectRotation = [0.0, 0.0, 0.0, 1.0]
						
						#effectRotation = mTransform.to_quaternion()
						effectRotation[3] = mTransform.to_quaternion()[0]
						effectRotation[0] = mTransform.to_quaternion()[1]
						effectRotation[1] = mTransform.to_quaternion()[2]
						effectRotation[2] = mTransform.to_quaternion()[3]
						
						try:
							effect_copy = int(child.name.split("_")[3].split(".")[0])
						except:
							try:
								effect_copy = int(child["effect_copy"])
							except:
								#print("ERROR: effect object %s is missing parameters %s. Effects will not be exported." % (child.name, '"effect_copy"'))
								#continue
								effect_copy = 0
						
						sensor_index = -1
						try:
							EffectData = child["sensor_hash"]
							EffectData = id_to_int(EffectData)
						except:
							try:
								EffectData = child["EffectData"]
								if EffectData < 0:
									EffectData += 2**32 #converting to uint32
							except:
								EffectData = None
								try:
									sensor_index = int(child["sensor_index"])
								except:
									sensor_index = -1
						
						effect_copy_instance.append([effect_copy, [effectLocation, effectRotation], EffectData, sensor_index])
						
					
					effect_instance = [EffectId, effect_index, effect_copy_instance[:]]
					instances_effects.append(effect_instance)
					
					continue
				
				elif resource_type_child == "Skeleton":
					mTransform = Matrix(np.linalg.inv(m) @ object.matrix_world)
					mSensorPosition = mTransform.translation
					
					try:
						sensor_index = int(object.name.split("_")[1].split(".")[0])
					except:
						try:
							sensor_index = int(object["sensor_index"])
						except:
							sensor_index = len(Skeleton)
					
					try:
						parent_sensor = object["parent_sensor"]
					except:
						parent_sensor = 0
					
					try:
						relative_sensor = object["correlated_sensor"]
					except:
						relative_sensor = -1
					
					try:
						child_sensor = object["child_sensor"]
					except:
						child_sensor = -1
					
					try:
						sensor_hash = object["sensor_hash"]
						if not is_sensor_hash_valid(sensor_hash, resource_type):
							#print("WARNING: sensor hash %s from object %s is not valid (not in HPR). Assuming as 9A_A9_39_49." % (sensor_hash, object.name))
							#sensor_hash = "9A_A9_39_49"
							print("WARNING: sensor hash %s from object %s is not valid (not in HPR). Trying to use it." % (sensor_hash, object.name))
							#continue
					except:
						#sensor_hash = "9A_A9_39_49"
						print("WARNING: object %s is missing parameter %s. Skipping sensor." % (object.name, '"sensor_hash"'))
						continue
					
					mSensorRotation = []
					sensor = [sensor_index, mSensorPosition, mSensorRotation, parent_sensor, relative_sensor, child_sensor, sensor_hash]
					Skeleton.append(sensor)
					
					continue
				
				if mModelId in (rows[0] for rows in models):
					continue
				
				try:
					is_model_shared_asset = object["is_shared_asset"]
				except:
					print("WARNING: object %s is missing parameter %s. Assuming as False." % (object.name, '"is_shared_asset"'))
					is_model_shared_asset = False
				
				if force_shared_model_as_false == True:
					is_model_shared_asset = False
				
				if is_model_shared_asset == True:
					model_path = os.path.join(shared_model_dir, mModelId + ".dat")
					if resource_type_child == "InstanceList":
						if mModelId in models_globalresources:
							pass
						elif mModelId in models_disctrict:
							pass
						else:
							#print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("model", mModelId, muDistrictId))
							if debug_shared_not_found == True:
								#print("WARNING: setting %s %s is_shared_asset to False." % ("model", mModelId))
								is_model_shared_asset = False
					if not os.path.isfile(model_path):
						#print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC." % ("model", mModelId))
						if debug_shared_not_found == True:
							#print("WARNING: setting %s %s is_shared_asset to False." % ("model", mModelId))
							is_model_shared_asset = False
				
				if is_model_shared_asset == True:
					models.append([mModelId, [[], []], is_model_shared_asset])
					continue
				
				renderables_info = []
				
				num_objects = 0
				renderable_indices = []
				for child in object.children:
					if child.type != "MESH":
						continue
					if child.hide_get() == True and ignore_hidden_meshes == True:
						continue
					num_objects += 1
					
					try:
						renderable_index = child["renderable_index"]
					except:
						print("WARNING: object %s is missing parameter %s. Defining it based on the number of polygons." % (child.name, '"renderable_index"'))
					renderable_indices.append([child.name, len(child.data.polygons)])
				renderable_indices.sort(key=lambda x: x[1], reverse=True)
				
				if num_objects == 0:
					# It is an empty dummy, probably a duplicated model making reference to the same renderables
					continue
				
				for child in object.children:
					if child.type != "MESH":
						continue
					
					if child.hide_get() == True and ignore_hidden_meshes == True:
						continue
					
					if force_rotation == True:
						transform_args[1] = True
						apply_transfrom(child, global_rotation, *transform_args)
					
					
					mRenderableId = child.name
					mRenderableId = mRenderableId.split(".")[0]
					if is_valid_id(mRenderableId) == False:
						return {"CANCELLED"}
					
					try:
						is_shared_asset = child["is_shared_asset"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming as False." % (child.name, '"is_shared_asset"'))
						is_shared_asset = False
					
					if force_shared_model_as_false == True:
						is_shared_asset = False
					
					if is_shared_asset == True:
						renderable_path = os.path.join(shared_renderable_dir, mRenderableId + ".dat")
						if resource_type_child == "InstanceList":
							if mRenderableId in renderables_globalresources:
								pass
							elif mRenderableId in renderables_disctrict:
								pass
							else:
								print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("renderable", mRenderableId, muDistrictId))
								if debug_shared_not_found == True:
									print("WARNING: setting %s %s is_shared_asset to False." % ("renderable", mRenderableId))
									is_shared_asset = False
						if not os.path.isfile(renderable_path):
							print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC." % ("renderable", mRenderableId))
							if debug_shared_not_found == True:
								print("WARNING: setting %s %s is_shared_asset to False." % ("renderable", mRenderableId))
								is_shared_asset = False
					
					try:
						renderable_index = child["renderable_index"]
					except:
						if num_objects == 1:
							renderable_index = 0
						else:
							#print("ERROR: object %s is missing parameter %s." % (child.name, '"renderable_index"'))
							#return {"CANCELLED"}
							for rend_index, rend_list in enumerate(renderable_indices):
								if rend_list[0] == child.name:
									renderable_index = rend_index
									break
					
					renderables_info.append([mRenderableId, [renderable_index]])
					
					if mRenderableId in (rows[0] for rows in renderables):
						continue
					
					if is_shared_asset == True:
						renderables.append([mRenderableId, [[], [], [], []], is_shared_asset, ""])
						continue
					
					bbox_x, bbox_y, bbox_z = [[point[i] for point in child.bound_box] for i in range(3)]
					object_center = [(max(bbox_x) + min(bbox_x))*0.5, (max(bbox_y) + min(bbox_y))*0.5, (max(bbox_z) + min(bbox_z))*0.5]
					object_radius = math.dist(object_center, child.bound_box[0])
					
					meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, status = read_object(child, resource_type_child, shared_dir, copy_uv_layer)
					
					if status == 1:
						return {'CANCELLED'}
					
					num_meshes = len(meshes_info)
					renderable_properties = [object_center, object_radius, submeshes_bounding_box, num_meshes]
					
					renderables.append([mRenderableId, [meshes_info, renderable_properties, indices_buffer, vertices_buffer], is_shared_asset, ""])
					
					for k, mesh_info in enumerate(meshes_info):
						mMaterialId = mesh_info[1]
						if is_valid_id(mMaterialId) == False:
							return {"CANCELLED"}
						
						mat = bpy.data.materials.get(mMaterialId) or bpy.data.materials.get(id_swap(mMaterialId))
						
						if mat == None:
							print("ERROR: material %s returned a NoneType. Check if it is a duplicated material, for example AA_BB_CC_DD.001" % mMaterialId)
							return {"CANCELLED"}
						
						try:
							is_material_shared_asset = mat["is_shared_asset"]
						except:
							print("WARNING: material %s is missing parameter %s. Assuming as False." % (mat.name, '"is_shared_asset"'))
							is_material_shared_asset = False
						
						if force_shared_material_as_false == True:
							is_material_shared_asset = False
						
						if is_material_shared_asset == True:
							material_path = os.path.join(shared_material_dir, mMaterialId + ".dat")
							if resource_type_child == "InstanceList":
								if mMaterialId in materials_globalresources:
									pass
								elif mMaterialId in materials_disctrict:
									pass
								else:
									print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("material", mMaterialId, muDistrictId))
									if debug_shared_not_found == True:
										print("WARNING: setting %s %s is_shared_asset to False." % ("material", mMaterialId))
										is_material_shared_asset = False
							
							if not os.path.isfile(material_path):
								print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC. Add it to the library and export again." % ("material", mMaterialId))
								if debug_shared_not_found == True:
									print("WARNING: setting %s %s is_shared_asset parameter to False." % ("material", mMaterialId))
									is_material_shared_asset = False
							else:
								mShaderId, mSamplerStateIds, = read_material_get_shader_type(material_path)
								shader_path = os.path.join(shared_shader_dir, mShaderId + "_83.dat")
								shader_type, _, _, _, _, _, _ = read_shader(shader_path)
								
								for mSamplerStateId in mSamplerStateIds:
									if mSamplerStateId not in samplerstates:
										samplerstates.append(mSamplerStateId)
						
						try:
							if is_material_shared_asset == False:
								shader_type = mat["shader_type"]
						except:
							print("WARNING: material %s is missing parameter %s." % (mat.name, '"shader_type"'))
							shader_type = ""
						
						mShaderId, shader_type = get_mShaderID(shader_type, resource_type)
						if mShaderId == "":
							print("ERROR: material %s is set to a nonexistent %s: %s." % (mat.name, '"shader_type"', shader_type))
							return {"CANCELLED"}
						
						# Reading shader for getting required raster types and properties
						if mShaderId in shaders:
							mVertexDescriptorId, num_sampler_states_shader, required_raster_types, material_parameters_from_shader, material_constants_from_shader, texture_samplers = shaders[mShaderId]
						else:
							shader_path = os.path.join(shared_shader_dir, mShaderId + "_83.dat")
							shader_description_, mVertexDescriptorId, num_sampler_states_shader, required_raster_types, material_parameters_from_shader, material_constants_from_shader, texture_samplers = read_shader(shader_path)
							shaders[mShaderId] = (mVertexDescriptorId, num_sampler_states_shader, required_raster_types, material_parameters_from_shader, material_constants_from_shader, texture_samplers)
						required_raster_types = dict((v,k) for k,v in required_raster_types.items())
						
						mesh_info.append(mVertexDescriptorId)
						
						if mMaterialId in (rows[0] for rows in materials):
							continue
						
						if is_material_shared_asset == True:
							materials.append([mMaterialId, ["", [], [], [], [], [], []], is_material_shared_asset])
							continue
						
						material_color = []
						for node in mat.node_tree.nodes:
							if node.type in ["BSDF_GLOSSY", "BSDF_DIFFUSE", "EMISSION", "BSDF_GLASS", "BSDF_REFRACTION", "EEVEE_SPECULAR", "SUBSURFACE_SCATTERING", "BSDF_PRINCIPLED", "PRINCIPLED_VOLUME", "BSDF_TRANSLUCENT", "VOLUME_ABSORPTION", "VOLUME_SCATTER"]:
								material_color = node.inputs[0].default_value[:]
						
						parameters_Indices = []
						parameters_Ones = []
						parameters_NamesHash = []
						parameters_Data = []
						parameters_Names = []
						material_constants = []
						miChannel = []
						raster_type_offsets = []
						
						try:
							if debug_use_default_samplerstates == True:
								raise Exception
							sampler_states_info = mat["SamplerStateIds"]
						except:
							if debug_use_default_samplerstates == False:
								print("WARNING: material %s is missing parameter %s. Using default ones." % (mat.name, '"SamplerStateIds"'))
							
							try:
								sampler_states_info = get_default_sampler_states(shader_type, mShaderId, num_sampler_states_shader)
							except:
								print("WARNING: get_default_sampler_states function not found. Custom data will not be available.")
								sampler_states_info = ["AF_5A_0B_82"]*num_sampler_states_shader
						
						num_sampler_states = len(sampler_states_info)
						if num_sampler_states != num_sampler_states_shader:
							print("WARNING: number of sampler states (%d) on material %s is different from the %d required by the shader %s. Replacing sampler states with default ones." % (num_sampler_states, mMaterialId, num_sampler_states_shader, mShaderId))
							
							try:
								sampler_states_info = get_default_sampler_states(shader_type, mShaderId, num_sampler_states_shader)
							except:
								print("WARNING: get_default_sampler_states function not found. Setting AF_5A_0B_82 as default sampler state.")
								sampler_states_info = ["AF_5A_0B_82"]*num_sampler_states_shader
						
						if debug_use_shader_material_parameters == True:
							parameters_Indices = material_parameters_from_shader[0]
							parameters_Ones = material_parameters_from_shader[1]
							parameters_NamesHash = material_parameters_from_shader[2]
							parameters_Data = material_parameters_from_shader[3][:]
							parameters_Names = material_parameters_from_shader[4]
						else:
							try:
								status, material_parameters = get_default_material_parameters(shader_type)
								material_parameters = [list(param) for param in material_parameters]
							except:
								print("WARNING: get_default_material_parameters function not found. Custom data will not be available.")
								status = 1
							
							if status == 0:
								parameters_Indices = material_parameters[0]
								parameters_Ones = material_parameters[1]
								parameters_NamesHash = material_parameters[2]
								parameters_Data = material_parameters[3][:]
								parameters_Names = material_parameters[4]
							else:
								parameters_Indices = material_parameters_from_shader[0]
								parameters_Ones = material_parameters_from_shader[1]
								parameters_NamesHash = material_parameters_from_shader[2]
								parameters_Data = material_parameters_from_shader[3][:]
								parameters_Names = material_parameters_from_shader[4]
							
							for i in range(0, len(parameters_Names)):
								if parameters_Names[i] in mat:
									parameters_Data[i] = mat[parameters_Names[i]]
								elif (parameters_Names[i] == "materialDiffuse" or parameters_Names[i] == "mMaterialDiffuse" or parameters_Names[i] == "mGlassColour") and material_color != [] and status != 0:
									parameters_Data[i] = material_color[:]
						
						material_constants = material_constants_from_shader
						miChannel = [0]*num_sampler_states_shader
						raster_type_offsets = [0]*num_sampler_states_shader
						
						material_parameters = [parameters_Indices[:], parameters_Ones[:], parameters_NamesHash[:], parameters_Data[:], parameters_Names[:]]
						sampler_properties = [material_constants, miChannel, raster_type_offsets]
						textures_info = []
						
						for i, mSamplerStateId in enumerate(sampler_states_info):
							if is_valid_id(mSamplerStateId) == False:
								return {"CANCELLED"}
							
							if mSamplerStateId not in samplerstates:
								samplerstates.append(mSamplerStateId)
						
						for node in mat.node_tree.nodes:
							if node.type == "TEX_IMAGE":
								raster_type = node.name.split(".")[0]
								
								try:
									texture_sampler_code = required_raster_types[raster_type]
								except:
									texture_sampler_code = 0xFF
								
								raster = node.image
								if raster == None:
									print("WARNING: no image on texture node %s of the material %s. Ignoring it." % (node.label, mMaterialId))
									continue
								
								mRasterId = raster.name.split(".")[0]
								if is_valid_id(mRasterId) == False:
									return {"CANCELLED"}
								
								# Only keeping textures used by shader
								if texture_sampler_code != 0xFF:
									if texture_sampler_code in (rows[1] for rows in textures_info):
										print("WARNING: two or more texture nodes of the material %s have the same raster type (%s). Assuming the first one is the correct one." % (mMaterialId, raster_type))
									else:
										textures_info.append([mRasterId, texture_sampler_code, raster_type])
								
								try:
									is_raster_shared_asset = raster.is_shared_asset
								except:
									print("WARNING: image %s is missing parameter %s. Assuming as False." % (raster.name, '"is_shared_asset"'))
									is_raster_shared_asset = False
								
								if force_shared_texture_as_false == True:
									is_raster_shared_asset = False
								
								if is_raster_shared_asset == True:
									raster_path = os.path.join(shared_raster_dir, mRasterId + ".dat")
									raster_dds_path = os.path.join(shared_raster_dir, mRasterId + ".dds")
									
									if resource_type_child == "InstanceList":
										if mRasterId in textures_globalresources:
											pass
										elif mRasterId in textures_disctrict:
											pass
										else:
											print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("texture", mRasterId, muDistrictId))
											if debug_shared_not_found == True:
												print("WARNING: setting %s %s is_shared_asset to False." % ("texture", mRasterId))
												is_raster_shared_asset = False
									
									if os.path.isfile(raster_path) or os.path.isfile(raster_dds_path):
										mRasterId = mRasterId
									else:
										print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC." % ("texture", mRasterId))
										if debug_shared_not_found == True:
											print("WARNING: setting %s %s is_shared_asset to False." % ("texture", mRasterId))
											is_raster_shared_asset = False
								
								if mRasterId in (rows[0] for rows in rasters):
									continue
								
								if is_raster_shared_asset == True:
									rasters.append([mRasterId, [], is_raster_shared_asset, ""])
									continue
								
								width, height = raster.size
								if width < 4 or height < 4:
									print("ERROR: image %s resolution smaller than the supported by the game. It must be bigger than or equal to 4x4." % raster.name)
									return {"CANCELLED"}
								
								if not ((width & (width-1) == 0) and width != 0):
										print("ERROR: image %s width %d is not a power of two. It must be a power of two." % (raster.name, width))
										return {"CANCELLED"}
								
								if not ((height & (height-1) == 0) and height != 0):
									print("ERROR: image %s height %d is not a power of two. It must be a power of two." % (raster.name, height))
									return {"CANCELLED"}
								
								is_packed = False
								if len(raster.packed_files) > 0:
									is_packed = True
									raster.unpack(method='WRITE_LOCAL')	# Default method, it unpacks to the current .blend directory
								
								#raster_path = bpy.path.abspath(raster.filepath)
								raster_path = os.path.realpath(bpy.path.abspath(raster.filepath))
								raster.filepath = raster_path
								
								raster_source_extension = os.path.splitext(os.path.basename(raster_path))[-1]
								if raster_source_extension != ".dds":
									if raster_source_extension in (".tga", ".png", ".psd", ".jpg", ".bmp"):
										if nvidiaGet() == None:
											print("ERROR: NVIDIA Texture Tools not found. Unable to convert %s to .dds" % raster_source_extension)
											return {"CANCELLED"}
										print("WARNING: converting texture %s format from %s to .dds." % (os.path.splitext(os.path.basename(raster_path))[0], raster_source_extension))
										raster_path = convert_texture_to_dxt5(raster_path, False)
									else:
										print("ERROR: texture format %s not supported. Please use .dds format." % raster_source_extension)
										return {"CANCELLED"}
								
								try:
									unknown_0x20 = raster.flags
									if unknown_0x20 == -1:
										raise Exception
								except:
									try:
										unknown_0x20 = raster.unknown_0x20
										if unknown_0x20 == -1:
											raise Exception
									except:
										try:
											unknown_0x20 = raster["unknown_0x20"]
											if unknown_0x20 == -1:
												raise Exception
										except:
											if raster_type == "NormalTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (NormalTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "ScratchTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (ScratchTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "CrumpleTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (CrumpleTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "LightmapLightsTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (LightmapLightsTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "EmissiveTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (EmissiveTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "DisplacementSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (DisplacementSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "AmbientOcclusionTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (AmbientOcclusionTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "AoMapTextureSampler" or raster_type == "AOMapTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (AoMapTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif "Normal" in raster_type:
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (normal texture)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											else:
												print("WARNING: image %s is missing parameter %s. Setting as 0x10" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
								
								try:
									main_mipmap = raster.main_mipmap
									if main_mipmap == -1:
										raise Exception
								except:
									try:
										main_mipmap = raster["main_mipmap"]
										if main_mipmap == -1:
											raise Exception
									except:
										#print("WARNING: image %s is missing parameter %s. Assuming as 0." % (raster.name, '"main_mipmap"'))
										main_mipmap = 0
								
								try:
									dimension = raster.dimension
									if dimension == -1:
										raise Exception
								except:
									try:
										dimension = raster["dimension"]
										if dimension == -1:
											raise Exception
									except:
										#print("WARNING: image %s is missing parameter %s. Assuming as 2D (2)." % (raster.name, '"dimension"'))
										dimension = 2
								
								raster_properties = [unknown_0x20, dimension, main_mipmap]
								
								rasters.append([mRasterId, [raster_properties], is_raster_shared_asset, raster_path])
								
								if is_packed == True:
									raster.pack()
						
						if len(textures_info) != num_sampler_states_shader:
							print("WARNING: number of textures (%d) on material %s is different from the %d required by the shader %s." % (len(textures_info), mMaterialId, num_sampler_states_shader, mShaderId))
							
							texture_sampler_codes = [texture_info[1] for texture_info in textures_info]
							for raster_type, miChannel in required_raster_types.items():
								if miChannel in texture_sampler_codes:
									continue
								
								try:
									mRasterId, raster_properties, is_raster_shared_asset, raster_path = get_default_mRasterId(shader_type, mShaderId, raster_type, resource_type)
								except:
									print("WARNING: get_default_mRasterId function not found. Custom data will not be available.")
									
									is_raster_shared_asset = True
									raster_path = ""
									raster_properties = [0x10, 2, 0]
									
									if resource_type == "InstanceList":	#OK
										#grey
										mRasterId = "AA_62_F3_0A"
										is_raster_shared_asset = False
										raster_path = "create_texture"
									elif resource_type == "CharacterSpec":
										mRasterId = "AA_62_F3_0A"
										raster_properties = [0x10, 2, 0]
										is_raster_shared_asset = False
										raster_path = "create_texture"
										
										if raster_type == 'DiffuseTextureSampler':	#OK
											#grey
											mRasterId = "AA_62_F3_0A"
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'AoSpecMapTextureSampler':	#OK
											#green
											mRasterId = "7D_A1_02_A1"
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'NormalTextureSampler':	#OK
											#pink alpha
											mRasterId = "B4_2D_C6_D4"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										
									else:
										if raster_type == 'DiffuseTextureSampler':	#OK
											#grey
											mRasterId = "AA_62_F3_0A"
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'DiffuseSampler': #OK
											#grey
											mRasterId = "AA_62_F3_0A"
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'NormalTextureSampler':	#OK
											#grey alpha
											mRasterId = "C5_1A_CE_8A"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'ExternalNormalTextureSampler':	#OK
											#grey alpha
											mRasterId = "C5_1A_CE_8A"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'InternalNormalTextureSampler':	#OK
											#grey alpha
											mRasterId = "C5_1A_CE_8A"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'CrackedGlassNormalTextureSampler': #OK
											#grey alpha
											mRasterId = "C5_1A_CE_8A"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'AoMapTextureSampler':	#OK
											#white
											mRasterId = "13_94_2A_CA"
										elif raster_type == 'CrumpleTextureSampler':	#OK
											#crumple
											mRasterId = "A1_39_98_23"
											raster_properties = [0x0, 2, 0]
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'ScratchTextureSampler':	#OK
											#scratch
											mRasterId = "85_68_7E_F0"
										elif raster_type == 'LightmapLightsTextureSampler': #OK
											#transparent
											mRasterId = "EB_1B_16_5D"
										elif raster_type == 'EmissiveTextureSampler':	#OK
											#transparent
											mRasterId = "EB_1B_16_5D"
										elif raster_type == 'DisplacementSampler': #OK
											mRasterId = "7D_A1_02_A1"
											is_raster_shared_asset = False
											raster_path = "create_texture"
										elif raster_type == 'CrackedGlassTextureSampler':	#OK
											#cracked
											mRasterId = "BE_12_78_F1"
										else:
											#grey
											mRasterId = "AA_62_F3_0A"
											is_raster_shared_asset = False
											raster_path = "create_texture"
								
								textures_info.append([mRasterId, miChannel, raster_type])
								rasters.append([mRasterId, [raster_properties[:]], is_raster_shared_asset, raster_path])
								
							
						materials.append([mMaterialId, [mShaderId, textures_info, sampler_states_info, material_parameters, sampler_properties, texture_samplers], is_material_shared_asset])
				
				renderable_indices = [renderable_info[1][0] for renderable_info in renderables_info]
				indices_range = list(range(0, max(renderable_indices) + 1))
				if sorted(renderable_indices) != indices_range:
					print("ERROR: missing or duplicated renderable indices on object %s childs. Verify the %s parameters for skipped or duplicated entries." % (object.name, '"renderable_index"'))
					print("renderable_indices =", renderable_indices, indices_range)
					return {"CANCELLED"}
				
				mu8NumRenderables = len(renderables_info)
				mu8NumStates = 5
				
				try:
					unknown_0x19 = object["unknown_0x25"]
				except:
					try:
						unknown_0x19 = object["unknown_0x19"]		#MW2012
					except:
						if resource_type == "InstanceList":
							print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"unknown_0x25"'))
						unknown_0x19 = 0
				
				try:
					lod_distances = object["lod_distances"]
				except:
					print("WARNING: object %s is missing parameter %s. Assuming default value." % (object.name, '"lod_distances"'))
					lod_distances = []
				
				try:
					model_states = object["model_states"]
					mu8NumStates = len(model_states)
				except:
					try:
						model_states = object["renderable_indices"]
						mu8NumStates = len(model_states)
					except:
						print("WARNING: object %s is missing parameter %s (or %s). Assuming default values." % (object.name, '"renderable_indices"', '"model_states"'))
						model_states = []
						mu8NumStates = 5
				
				has_tint_data = 0
				TintData = []
				try:
					has_tint_data = object["model_has_tint_data"]
				except:
					if resource_type == "InstanceList":
						print("WARNING: object %s is missing parameter %s. Assuming some value." % (object.name, '"model_has_tint_data"'))
						has_tint_data = 0
						
						mRasterIdWhite = "A2_70_79_2C"	#white
						if mRasterIdWhite in (rows[0] for rows in rasters):
							pass
						else:
							raster_properties = [0x10, 2, 0]
							is_raster_shared_asset = False
							raster_path = "create_texture"
							rasters.append([mRasterIdWhite, [raster_properties], is_raster_shared_asset, raster_path])
						
						mRasterIdBlack = "4F_1F_A7_2D"	#black
						if mRasterIdBlack in (rows[0] for rows in rasters):
							pass
						else:
							raster_properties = [0x10, 2, 0]
							is_raster_shared_asset = False
							raster_path = "create_texture"
							rasters.append([mRasterIdBlack, [raster_properties], is_raster_shared_asset, raster_path])
						
						TintData = [[], [], ["AOMapTextureSampler", "LightMapTextureSampler"], ["D3_37_5C_99", "D3_37_5C_99"], [mRasterIdWhite, mRasterIdBlack]]
						if "D3_37_5C_99" not in samplerstates:
							samplerstates.append("D3_37_5C_99")
					else:
						pass
				
				if has_tint_data == True:
					all_parameters_names = ["model_diffuseTintColour", "model_InstanceAdditiveAndAO", "model_AdditiveIntensities"]
					parameters_names = []
					parameters_data = []
					
					for parameter_name in all_parameters_names:
						try:
							tint_data = object[parameter_name]
							parameters_names.append(parameter_name.replace("model_", ""))
							parameters_data.append(tint_data)
						except:
							pass
					
					try:
						samplers_names = object["model_samplers_names"]
						sampler_states = object["model_SamplerStateIds"]
						textures = object["model_TextureIds"]
						
						if debug_use_default_samplerstates == True:
							sampler_states = ["D3_37_5C_99"]*len(sampler_states)
						
						for mSamplerStateId in sampler_states:
							if mSamplerStateId not in samplerstates:
								samplerstates.append(mSamplerStateId)
					except:
						samplers_names = []
						sampler_states = []
						textures = []
					
					if parameters_data == [] and samplers_names == []:
						has_tint_data = False
						
						mRasterIdWhite = "A2_70_79_2C"	#white
						if mRasterIdWhite in (rows[0] for rows in rasters):
							pass
						else:
							raster_properties = [0x10, 2, 0]
							is_raster_shared_asset = False
							raster_path = "create_texture"
							rasters.append([mRasterIdWhite, [raster_properties], is_raster_shared_asset, raster_path])
						
						mRasterIdBlack = "4F_1F_A7_2D"	#black
						if mRasterIdBlack in (rows[0] for rows in rasters):
							pass
						else:
							raster_properties = [0x10, 2, 0]
							is_raster_shared_asset = False
							raster_path = "create_texture"
							rasters.append([mRasterIdBlack, [raster_properties], is_raster_shared_asset, raster_path])
						
						TintData = [[], [], ["AOMapTextureSampler", "LightMapTextureSampler"], ["D3_37_5C_99", "D3_37_5C_99"], [mRasterIdWhite, mRasterIdBlack]]
						if "D3_37_5C_99" not in samplerstates:
							samplerstates.append("D3_37_5C_99")
					else:
						TintData = [parameters_names, parameters_data, samplers_names, sampler_states, textures]
						
						# Collecting texture data (same/similar loop is used later)
						if len(textures) != 0:
							for mRasterId, raster_type in zip(textures, samplers_names):
								try:
									raster = bpy.data.images[mRasterId]
								except:
									print("WARNING: No image data for texture %s. Ignoring it." % (mRasterId))
									continue
								
								if raster == None:
									print("WARNING: No image for texture %s. Ignoring it." % (mRasterId))
									continue
								
								if is_valid_id(mRasterId) == False:
									return {"CANCELLED"}
								
								try:
									is_raster_shared_asset = raster.is_shared_asset
								except:
									print("WARNING: image %s is missing parameter %s. Assuming as False." % (raster.name, '"is_shared_asset"'))
									is_raster_shared_asset = False
								
								if force_shared_texture_as_false == True:
									is_raster_shared_asset = False
								
								if is_raster_shared_asset == True:
									raster_path = os.path.join(shared_raster_dir, mRasterId + ".dat")
									raster_dds_path = os.path.join(shared_raster_dir, mRasterId + ".dds")
									
									if resource_type_child == "InstanceList":
										if mRasterId in textures_globalresources:
											pass
										elif mRasterId in textures_disctrict:
											pass
										else:
											print("ERROR: %s %s is set as a shared asset although its not in the globalresources or its district %d." % ("texture", mRasterId, muDistrictId))
											if debug_shared_not_found == True:
												print("WARNING: setting %s %s is_shared_asset to False." % ("texture", mRasterId))
												is_raster_shared_asset = False
									
									if os.path.isfile(raster_path) or os.path.isfile(raster_dds_path):
										mRasterId = mRasterId
									else:
										print("WARNING: %s %s is set as a shared asset although it may not exist on NFSHPR PC." % ("texture", mRasterId))
										if debug_shared_not_found == True:
											print("WARNING: setting %s %s is_shared_asset to False." % ("texture", mRasterId))
											is_raster_shared_asset = False
								
								if mRasterId in (rows[0] for rows in rasters):
									continue
								
								if is_raster_shared_asset == True:
									rasters.append([mRasterId, [], is_raster_shared_asset, ""])
									continue
								
								width, height = raster.size
								if width < 4 or height < 4:
									print("ERROR: image %s resolution smaller than the supported by the game. It must be bigger than or equal to 4x4." % raster.name)
									return {"CANCELLED"}
								
								if not ((width & (width-1) == 0) and width != 0):
									print("ERROR: image %s width %d is not a power of two. It must be a power of two." % (raster.name, width))
									return {"CANCELLED"}
								
								if not ((height & (height-1) == 0) and height != 0):
									print("ERROR: image %s height %d is not a power of two. It must be a power of two." % (raster.name, height))
									return {"CANCELLED"}
								
								is_packed = False
								if len(raster.packed_files) > 0:
									is_packed = True
									raster.unpack(method='WRITE_LOCAL')	# Default method, it unpacks to the current .blend directory
								
								#raster_path = bpy.path.abspath(raster.filepath)
								raster_path = os.path.realpath(bpy.path.abspath(raster.filepath))
								raster.filepath = raster_path
								
								raster_source_extension = os.path.splitext(os.path.basename(raster_path))[-1]
								if raster_source_extension != ".dds":
									if raster_source_extension in (".tga", ".png", ".psd", ".jpg", ".bmp"):
										if nvidiaGet() == None:
											print("ERROR: NVIDIA Texture Tools not found. Unable to convert %s to .dds" % raster_source_extension)
											return {"CANCELLED"}
										print("WARNING: converting texture %s format from %s to .dds." % (os.path.splitext(os.path.basename(raster_path))[0], raster_source_extension))
										raster_path = convert_texture_to_dxt5(raster_path, False)
									else:
										print("ERROR: texture format %s not supported. Please use .dds format." % raster_source_extension)
										return {"CANCELLED"}
								
								try:
									unknown_0x20 = raster.flags
									if unknown_0x20 == -1:
										raise Exception
								except:
									try:
										unknown_0x20 = raster.unknown_0x20
										if unknown_0x20 == -1:
											raise Exception
									except:
										try:
											unknown_0x20 = raster["unknown_0x20"]
											if unknown_0x20 == -1:
												raise Exception
										except:
											if raster_type == "NormalTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (NormalTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "ScratchTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (ScratchTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "CrumpleTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (CrumpleTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											elif raster_type == "LightmapLightsTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (LightmapLightsTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "EmissiveTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (EmissiveTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "DisplacementSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (DisplacementSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "AmbientOcclusionTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (AmbientOcclusionTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif raster_type == "AoMapTextureSampler" or raster_type == "AOMapTextureSampler":
												print("WARNING: image %s is missing parameter %s. Setting as 0x10 (AoMapTextureSampler)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
											elif "Normal" in raster_type:
												print("WARNING: image %s is missing parameter %s. Setting as 0x0 (normal texture)" % (raster.name, '"flags"'))
												unknown_0x20 = 0x0
											else:
												print("WARNING: image %s is missing parameter %s. Setting as 0x10" % (raster.name, '"flags"'))
												unknown_0x20 = 0x10
								
								try:
									main_mipmap = raster.main_mipmap
									if main_mipmap == -1:
										raise Exception
								except:
									try:
										main_mipmap = raster["main_mipmap"]
										if main_mipmap == -1:
											raise Exception
									except:
										#print("WARNING: image %s is missing parameter %s. Assuming as 0." % (raster.name, '"main_mipmap"'))
										main_mipmap = 0
								
								try:
									dimension = raster.dimension
									if dimension == -1:
										raise Exception
								except:
									try:
										dimension = raster["dimension"]
										if dimension == -1:
											raise Exception
									except:
										#print("WARNING: image %s is missing parameter %s. Assuming as 2D (2)." % (raster.name, '"dimension"'))
										dimension = 2
								
								raster_properties = [unknown_0x20, dimension, main_mipmap]
								
								rasters.append([mRasterId, [raster_properties], is_raster_shared_asset, raster_path])
								
								if is_packed == True:
									raster.pack()
				
				model_properties = [mu8NumRenderables, mu8NumStates, TintData, unknown_0x19, lod_distances, model_states, resource_type_child]
				
				models.append([mModelId, [renderables_info, model_properties], is_model_shared_asset])
			
			# Removing models from intancesList that do not have a model file (generic or not)
			instances[:] = [instance for instance in instances if instance[1][0] in (rows[0] for rows in models)]
			instances_wheel[:] = [instance for instance in instances_wheel if instance[1][0] in (rows[0] for rows in models)]
			
			if resource_type_child == "Skeleton":
				for object in objects:
					if object.type != "ARMATURE":
						continue
					
					is_hidden = object.hide_get()
					if is_hidden == True:
						continue
					
					# Armature
					mArmatureId = object.data.name
					mArmatureId = mArmatureId.split(".")[0]
					
					if is_valid_id(mArmatureId) == False:
						mArmatureId = object.name
						mArmatureId = mArmatureId.split(".")[0]
						if is_valid_id(mArmatureId) == False:
							if resource_type == "GraphicsSpec":
								print("... using a calculated Id for %s" % mArmatureId)
								mArmatureId = mSkeletonId
							elif resource_type == "CharacterSpec":
								print("... using the Id defined in the CharacterSpec collection for %s" % mArmatureId)
								mArmatureId = mSkeletonId
							else:
								return {"CANCELLED"}
					
					Skeleton = []
					mSkeletonId = mArmatureId
					for b in object.data.bones[:]:
						#sensor_Transform = object.pose.bones[b.name].bone.matrix_local
						#mSensorPosition, mSensorRotation_, mSensorScale = sensor_Transform.decompose()
						
						#mSensorPosition = list(object.pose.bones[b.name].bone.tail_local[:])
						mSensorPosition = list(object.pose.bones[b.name].bone.head_local[:])
						mSensorRotation = [0.0, 0.0, 0.0, 1.0]
						
						try:
							sensor_index = int(b.name.split(".")[0].split("_")[-1].lower().replace("sensor", "").replace("bone", ""))
						except:
							try:
								sensor_index = int(''.join(n for n in b.name if n.isdigit()))
							except:
								print("WARNING: bone %s name is in the wrong format. It should be 'Sensor_001' or 'Bone_001'" % b.name)
								continue
						
						if b.parent == None:
							parent_sensor = -1
							older_sensor = 0
						else:
							try:
								parent_sensor = int(b.parent.name.split(".")[0].split("_")[-1].lower().replace("sensor", "").replace("bone", ""))
							except:
								try:
									parent_sensor = int(''.join(n for n in b.parent.name if n.isdigit()))
								except:
									#print("WARNING: bone %s name is in the wrong format. It should be 'Sensor_001' or 'Bone_001'" % b.parent.name)
									continue
							
							older_sensor = -1
							for brother in b.parent.children:
								if brother == b:
									break
								
								try:
									older_sensor = int(brother.name.split(".")[0].split("_")[-1].lower().replace("sensor", "").replace("bone", ""))
								except:
									try:
										older_sensor = int(''.join(n for n in brother.name if n.isdigit()))
									except:
										#print("WARNING: bone %s name is in the wrong format. It should be 'Sensor_001' or 'Bone_001'" % brother.name)
										continue
						
						if len(b.children) == 0:
							child_sensor = -1
						else:
							try:
								child_sensor = int(b.children[-1].name.split(".")[0].split("_")[-1].lower().replace("sensor", "").replace("bone", ""))
							except:
								try:
									child_sensor = int(''.join(n for n in b.children[-1].name if n.isdigit()))
								except:
									#print("WARNING: bone %s name is in the wrong format. It should be 'Sensor_001' or 'Bone_001'" % b.children[-1].name)
									continue
						
						try:
							sensor_hash = b["hash"]
							if not is_sensor_hash_valid(sensor_hash, resource_type):
								#print("WARNING: sensor hash %s from bone %s is not valid (not in MW). Assuming as 9A_A9_39_49." % (sensor_hash, b.name))
								#sensor_hash = "9A_A9_39_49"
								print("WARNING: sensor hash %s from bone %s is not valid (not in MW). Trying to use it." % (sensor_hash, b.name))
								#continue
						except:
							#sensor_hash = "9A_A9_39_49"
							print("WARNING: bone %s is missing parameter %s. Skipping sensor." % (b.name, '"hash"'))
							continue
						
						# if round(b.length, 2) == 0.12:
							# # When the bone length is zero in the game file, the imports adds an increment to its length
							# for sensor_ in Skeleton:
								# if sensor_[0] == parent_sensor:
									# sensor_[1][2] -= 0.12
									# break
						
						sensor = [sensor_index, mSensorPosition, mSensorRotation, parent_sensor, older_sensor, child_sensor, sensor_hash]
						Skeleton.append(sensor)
			
			elif resource_type_child == "ControlMesh":
				for object in objects:
					if object.type != "ARMATURE":
						continue
					
					is_hidden = object.hide_get()
					if is_hidden == True:
						continue
					
					# Armature
					mArmatureId = object.data.name
					mArmatureId = mArmatureId.split(".")[0]
					
					if is_valid_id(mArmatureId) == False:
						mArmatureId = object.name
						mArmatureId = mArmatureId.split(".")[0]
						if is_valid_id(mArmatureId) == False:
							return {"CANCELLED"}
					
					ControlMeshes = []
					mControlMeshId = mArmatureId
					for b in object.data.bones[:]:
						cm_coordinates_A = list(object.pose.bones[b.name].bone.head_local[:])
						cm_coordinates_B = list(object.pose.bones[b.name].bone.tail_local[:])
						
						try:
							cm_index = int(b.name.split(".")[0].split("_")[-1].lower().replace("sensor", "").replace("bone", ""))
						except:
							try:
								cm_index = int(''.join(n for n in b.name if n.isdigit()))
							except:
								print("WARNING: bone %s name is in the wrong format. It should be 'Bone_001' or 'Sensor_001'" % b.name)
								continue
						
						try:
							cm_limit = b["Limit"]
						except:
							try:
								cm_limit = b["limit"]
							except:
								print("WARNING: bone %s is missing parameter %s. Assuming default value 0.125." % (b.name, '"Limit"'))
								cm_limit = 0.125
						
						if round(b.length, 2) == 0.12:
							# When the bone length is zero in the game file, the imports adds an increment to its length
							cm_coordinates_A[2] = cm_coordinates_B[2] - 0.12
						
						ControlMesh = [cm_index, cm_coordinates_A, cm_coordinates_B, cm_limit]
						ControlMeshes.append(ControlMesh)
					
					if len(ControlMeshes) != 0x40:
						print("WARNING: ControlMesh doesn't have 64 bones. The game moy or may not support it.")
		
		# PVS (ZoneList)
		if resource_type == "ZoneList":
			for collection in collections:
				is_hidden = bpy.context.view_layer.layer_collection.children.get(main_collection.name).children.get(collection.name).hide_viewport
				is_excluded = bpy.context.view_layer.layer_collection.children.get(main_collection.name).children.get(collection.name).exclude
				
				if is_hidden or is_excluded:
					print("WARNING: skipping collection %s since it is hidden or excluded." % (collection.name))
					print("")
					continue
				
				resource_type_child = collection["resource_type"]
				
				objects = collection.objects
				object_index = -1
				
				for zone_object in objects:
					if zone_object.type != "MESH":
						continue
					
					is_hidden = zone_object.hide_get()
					if is_hidden == True:
						continue
					
					# Zone
					zone_object_name = zone_object.name
					try:
						muZoneId = int(zone_object_name.split(".")[0].split("_")[-1])
					except:
						print("ERROR: zone object's name not in the proper format: %s. The format should be like Zone_0071.NFSHPR." % zone_object_name)
						return {"CANCELLED"}
					
					try:
						miZoneType = zone_object["ZoneType"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming some value (0)." % (muZoneId, '"ZoneType"'))
						miZoneType = 0
					
					try:
						miNumSafeNeighbours = zone_object["NumSafeNeighbours"]
					except:
						try:
							miNumSafeNeighbours = zone_object["unknown_0x40"]
						except:
							print("WARNING: object %s is missing parameter %s. Assuming some value (0)." % (muZoneId, '"NumSafeNeighbours"'))
							miNumSafeNeighbours = 0
					
					try:
						mauNeighbourId = zone_object["NeighbourIds"]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming as none." % (muZoneId, '"NeighbourIds"'))
						mauNeighbourId = []
					
					try:
						mauNeighbourFlags = zone_object["NeighbourFlags"]
						
						neighbourFlags = []
						for neighbourFlag in mauNeighbourFlags:
							neighbourFlags.append(get_neighbour_flags_code(neighbourFlag))
						mauNeighbourFlags = neighbourFlags[:]
					except:
						print("WARNING: object %s is missing parameter %s. Assuming all flags as E_NEIGHBOURFLAG_IMMEDIATE." % (muZoneId, '"NeighbourFlags"'))
						mauNeighbourFlags = [0x3,]*len(mauNeighbourId)
					
					if len(mauNeighbourId) > len(mauNeighbourFlags):
						print("WARNING: object %s contains less NeighbourFlags than NeighbourIds %s. Assuming missing flags as E_NEIGHBOURFLAG_IMMEDIATE." % (muZoneId, '"NeighbourFlags"'))
						mauNeighbourFlags.extend([0x3,]*(len(mauNeighbourId) - len(mauNeighbourId)))
					elif len(mauNeighbourId) < len(mauNeighbourFlags):
						print("WARNING: object %s contains more NeighbourFlags than NeighbourIds %s." % (muZoneId, '"NeighbourFlags"'))
					
					status, muDistrictId, zonepoints = read_zone_object(zone_object)
					
					mTransform = Matrix(np.linalg.inv(m) @ zone_object.matrix_world)
					for i, zonepoint in enumerate(zonepoints):
						zonepoint = list(zonepoint)
						zonepoint = Vector(zonepoint)
						zonepoint = mTransform @ zonepoint
						zonepoints[i] = [zonepoint[0], zonepoint[2]]
					
					if status == 1:
						return {"CANCELLED"}
					
					if muDistrictId == 0:
						print("WARNING: object %s using an invalid %s. Assuming some value (0)." % (muZoneId, '"muDistrictId"'))
					
					muArenaId = 0
					zonelist.append([muZoneId, [mauNeighbourId, mauNeighbourFlags, muDistrictId, miZoneType, muArenaId, miNumSafeNeighbours], zonepoints[:]])
		
		if len(instances) == 0 and len(instances_wheel) == 0 and len(instances_character) == 0 and resource_type != "InstanceList" and (resource_type != "PolygonSoupList" and resource_type != "Collision" and resource_type != "ZoneList"):
			print("ERROR: no models in the proper structure. Nothing to export on this collection.")
			return {"CANCELLED"}
		
		if resource_type == "GraphicsSpec":
			object_indices = [instance[0] for instance in instances]
			indices_range = list(range(0, max(object_indices) + 1))
			if sorted(object_indices) != indices_range:
				print("ERROR: missing or duplicated object indices. Verify the %s parameters for skipped or duplicated entries." % '"ObjectIndex"')
				print("object_indices =", object_indices)
				return {"CANCELLED"}
		
		if len(instances_wheel) > 0:
			instances_wheelGroups = {object[1][3]: [] for object in instances_wheel}
			for object in instances_wheel:
				object_index, [mModelId, [mTransform], is_spinnable, object_placement] = object
				mModelId = object[1][0]
				is_spinnable = object[1][2]
				object_placement = object[1][3]
				
				instances_wheelGroups[object_placement].append([object_index, [mModelId, [mTransform], is_spinnable, object_placement]])
			
			for object in instances_wheelGroups.items():
				object[1].sort(key=lambda x:x[0])
			
			if len(instances_wheelGroups) < 4:
				print("ERROR: missing a wheel placement. Verify if the scene has all four wheels correctly placed and if their custom properties are properly set.")
				return {"CANCELLED"}
		
		if len(PolygonSoups) > 0:
			if resource_type == "InstanceList":
				mPolygonSoupList = "TRK_COL_" + str(track_unit_number)
			elif resource_type == "GraphicsSpec":
				mPolygonSoupList = "VEH_COL_" + str(vehicle_number)
			mPolygonSoupListId = calculate_resourceid(mPolygonSoupList.lower())
			PolygonSoups.sort(key=lambda x:x[0])
			instance_collision = [mPolygonSoupListId, PolygonSoups]
		
		if len(instances_effects) > 0:
			effect_indices = [effect_instance[1] for effect_instance in instances_effects]
			indices_range = list(range(0, max(effect_indices) + 1))
			for i in indices_range:
				if i not in effect_indices:
					print("ERROR: effects instance is missing effect %d. Effects will not be exported." % i)
					export_effects = False
					break
			
			instances_effects.sort(key=lambda x:x[1])
		
		if len(Skeleton) > 0:
			Skeleton.sort(key=lambda x:x[0])
		
		if len(ControlMeshes) > 0:
			ControlMeshes.sort(key=lambda x:x[0])
		
		## Writing data
		print("\tWriting data...")
		writing_time = time.time()
		
		mResourceIds = []
		mPolygonSoupListId_previous = ""
		if resource_type == "InstanceList":
			library_trk_path = os.path.join(shared_dir, "TRKs", track_unit_name)
			if os.path.isdir(library_trk_path):
				print("WARNING: track unit folder %s exists on library. Copying it." % track_unit_name)
				shutil.copytree(library_trk_path, directory_path)
			else:
				print("WARNING: track unit folder %s does not exist on library." % track_unit_name)
				pass
			
			instancelist_path = os.path.join(instancelist_dir, mInstanceListId + ".dat")
			dynamicinstancelist_path = os.path.join(dynamicinstancelist_dir, mDynamicInstanceListId + ".dat")
			groundcovercollection_path = os.path.join(groundcovercollection_dir, mGroundcoverCollectionId + ".dat")
			lightinstancelist_path = os.path.join(lightinstancelist_dir, mLightInstanceListId + ".dat")
			polygonsouplist_path = os.path.join(polygonsouplist_dir, mPolygonSoupListId + ".dat")
			zoneheader_path = os.path.join(zoneheader_dir, mZoneHeaderId + ".dat")
			
			if len(PolygonSoups) == 0:
				instance_collision = [mPolygonSoupListId, []]
			
			if os.path.isfile(instancelist_path):
				print("WARNING: file %s already exists in track unit %s. Replacing it with new file if there are entries." % (mInstanceListId, track_unit_name))
				if len(instances) > 0:
					write_instancelist(instancelist_path, instances)
			else:
				write_instancelist(instancelist_path, instances)
				mResourceIds.append([mInstanceListId, "InstanceList", id_to_int(mInstanceListId)])
			
			if os.path.isfile(polygonsouplist_path):
				print("WARNING: file %s already exists in track unit %s. Replacing it with new file if there are entries." % (mPolygonSoupListId, track_unit_name))
				if len(instance_collision[1]) > 0:
					write_polygonsouplist(polygonsouplist_path, instance_collision[1])
			else:
				write_polygonsouplist(polygonsouplist_path, instance_collision[1])
				mResourceIds.append([mPolygonSoupListId, "PolygonSoupList", id_to_int(mPolygonSoupListId)])
			
			if os.path.isfile(dynamicinstancelist_path):
				print("WARNING: file %s already exists in track unit %s. Skipping it." % (mDynamicInstanceListId, track_unit_name))
			else:
				write_dynamicinstancelist(dynamicinstancelist_path)
				mResourceIds.append([mDynamicInstanceListId, "DynamicInstanceList", id_to_int(mDynamicInstanceListId)])
			
			if os.path.isfile(groundcovercollection_path):
				print("WARNING: file %s already exists in track unit %s. Skipping it." % (mGroundcoverCollectionId, track_unit_name))
			else:
				write_groundcovercollection(groundcovercollection_path)
				mResourceIds.append([mGroundcoverCollectionId, "GroundcoverCollection", id_to_int(mGroundcoverCollectionId)])
			
			if os.path.isfile(lightinstancelist_path):
				print("WARNING: file %s already exists in track unit %s. Skipping it." % (mLightInstanceListId, track_unit_name))
			else:
				write_lightinstancelist(lightinstancelist_path)
				mResourceIds.append([mLightInstanceListId, "LightInstanceList", id_to_int(mLightInstanceListId)])
			
			if os.path.isfile(zoneheader_path):
				print("WARNING: file %s already exists in track unit %s. Skipping it." % (mZoneHeaderId, track_unit_name))
			else:
				write_zoneheader(zoneheader_path, mInstanceListId, mDynamicInstanceListId, mLightInstanceListId, mGroundcoverCollectionId)
				mResourceIds.append([mZoneHeaderId, "ZoneHeader", id_to_int(mZoneHeaderId)])
		
		elif resource_type == "GraphicsSpec":
			library_vehicle_path = os.path.join(shared_dir, "VEHICLES", vehicle_name)
			if os.path.isdir(library_vehicle_path):
				shutil.copytree(library_vehicle_path, directory_path)
				if len(instances_wheel) > 0:
					try:
						with Suppressor():
							clean_model_data(directory_path, True, True)
					except:
						print("WARNING: clean_model_data function not found. Cleaning original wheel data will not be possible.")
				#else:
				#	clean_model_data(directory_path, True, False)
			else:
				print("WARNING: vehicle folder %s does not exist on library." % vehicle_name)
			
			graphicsspec_path = os.path.join(graphicsspec_dir, mGraphicsSpecId + ".dat")
			if os.path.exists(graphicsspec_dir):
				for file in os.listdir(graphicsspec_dir):
					if mGraphicsSpecId in file:
						graphicsspec_path = os.path.join(graphicsspec_dir, file)
						break
			
			status, mSkeletonId_previous, mControlMeshId_previous = edit_graphicsspec(graphicsspec_path, instances, instances_wheelGroups, len(Skeleton) > 0, mSkeletonId, len(ControlMeshes) > 0, mControlMeshId)
			
			if len(instances_wheel) > 0:
				genesysinstance_path = os.path.join(genesysinstance_dir, mGraphicsSpecId + "_2.dat")
				if os.path.exists(genesysinstance_dir):
					for file in os.listdir(genesysinstance_dir):
						if mGraphicsSpecId in file and mGraphicsSpecId + '.dat' != file:
							genesysinstance_path = os.path.join(genesysinstance_dir, file)
							break
				
				if os.path.isfile(genesysinstance_path) == True:
					edit_genesysinstance2(genesysinstance_dir, genesysinstance_path, instances_wheelGroups)
				
				elif os.path.isfile(genesysinstance_path) == False:
					if os.path.exists(shared_trafficattribs_dir):
						shutil.copytree(shared_trafficattribs_dir, trafficattribs_dir)
						traffic_genesysinstance_dir = os.path.join(trafficattribs_dir, "GenesysInstance")
						for file in os.listdir(traffic_genesysinstance_dir):
							if mGraphicsSpecId in file and mGraphicsSpecId + '.dat' != file:
								genesysinstance_path = os.path.join(traffic_genesysinstance_dir, file)
								break
						edit_genesysinstance2(traffic_genesysinstance_dir, genesysinstance_path, instances_wheelGroups)
						if pack_bundle_file == True:
							tr_resources_table_path = os.path.join(trafficattribs_dir, "IDs_TRAFFICATTRIBS.BNDL")
							tr_resources_table_path2 = os.path.join(trafficattribs_dir, "IDs.BNDL")
							if os.path.isfile(tr_resources_table_path):
								status = pack_bundle_hp(tr_resources_table_path, trafficattribs_dir, "TRAFFICATTRIBS.BNDL", game)
							elif os.path.isfile(tr_resources_table_path2):
								status = pack_bundle_hp(tr_resources_table_path2, trafficattribs_dir, "TRAFFICATTRIBS.BNDL", game)
					else:
						print("WARNING: it was not possible to edit the wheels coordinates. Consider adding the unpacked TRAFFICATTRIBS in the library folder")
			
			if len(instances_character) > 0:
				genesysinstance_path = os.path.join(genesysinstance_dir, mGraphicsSpecId + ".dat")
				edit_genesysinstance1(genesysinstance_dir, genesysinstance_path, instances_character)
			
			if len(instances_effects) > 0:
				for effect_instance in instances_effects:
					for effect_copy_instance in effect_instance[2]:
						if effect_copy_instance[2] == None and effect_copy_instance[3] != -1:
							for sensor in Skeleton:
								if sensor[0] == effect_copy_instance[3]:
									effect_copy_instance[2] = id_to_int(sensor[6])
									break
				
				edit_graphicsspec_effects(graphicsspec_path, instances_effects)
			
			if len(Skeleton) > 0:
				# Deleting default file (deleting before writing the exported one, in case it is the same ID)
				skeleton_default_path = os.path.join(skeleton_dir, mSkeletonId_previous + ".dat")
				if os.path.isfile(skeleton_default_path):
					os.remove(skeleton_default_path)
				
				skeleton_path = os.path.join(skeleton_dir, mSkeletonId + ".dat")
				write_skeleton(skeleton_path, Skeleton)
				mResourceIds.append([mSkeletonId, "Skeleton", id_to_int(mSkeletonId)])
			
			if len(ControlMeshes) > 0:
				# Deleting default file (deleting before writing the exported one, in case it is the same ID)
				controlmesh_default_path = os.path.join(controlmesh_dir, mControlMeshId_previous + "_16.dat")
				if os.path.isfile(controlmesh_default_path):
					os.remove(controlmesh_default_path)
				
				controlmesh_path = os.path.join(controlmesh_dir, mControlMeshId + "_16.dat")
				write_controlmesh(controlmesh_path, ControlMeshes)
				mResourceIds.append([mControlMeshId, "ControlMesh", id_to_int(mControlMeshId)])
		
		elif resource_type == "CharacterSpec":
			if len(instances) > 0:
				#characterspec_path = os.path.join(characterspec_dir, mCharacterSpecId + ".dat")
				#write_characterspec(characterspec_path, mSkeletonId, mAnimationListId, instances)
				#mResourceIds.append([mCharacterSpecId, "CharacterSpec", id_to_int(mCharacterSpecId)])
				##mResourceIds.append([mSkeletonId, "Skeleton", id_to_int(mSkeletonId)])
				##mResourceIds.append([mAnimationListId, "AnimationList", id_to_int(mAnimationListId)])
				
				characterspec_path = os.path.join(characterspec_dir, mCharacterSpecId + ".dat")
				already_is_file = False
				if os.path.isfile(characterspec_path):
					print("WARNING: file %s already exists in %s. Replacing it with new file." % (mCharacterSpecId, main_collection.name))
					already_is_file = True
				write_characterspec(characterspec_path, mSkeletonId, mAnimationListId, instances)
				if already_is_file == False:
					mResourceIds.append([mCharacterSpecId, "CharacterSpec", id_to_int(mCharacterSpecId)])
			
			#Skeleton
			if len(Skeleton) > 0:
				skeleton_path = os.path.join(skeleton_dir, mSkeletonId + ".dat")
				write_skeleton(skeleton_path, Skeleton)
				mResourceIds.append([mSkeletonId, "Skeleton", id_to_int(mSkeletonId)])
			else:
				library_skeleton_path = os.path.join(shared_skeleton_dir, mSkeletonId + ".dat")
				if os.path.isfile(library_skeleton_path):
					os.makedirs(skeleton_dir, exist_ok = True)
					shutil.copy2(library_skeleton_path, skeleton_dir)
					mResourceIds.append([mSkeletonId, "Skeleton", id_to_int(mSkeletonId)])
				else:
					print("WARNING: skeleton %s does not exist on library." % mSkeletonId)
			
			# AnimationList
			library_animationlist_path = os.path.join(shared_animationlist_dir, mAnimationListId + ".dat")
			if os.path.isfile(library_animationlist_path):
				os.makedirs(animationlist_dir, exist_ok = True)
				shutil.copy2(library_animationlist_path, animationlist_dir)
				mResourceIds.append([mAnimationListId, "AnimationList", id_to_int(mAnimationListId)])
			else:
				print("WARNING: animationList %s does not exist on library." % mAnimationListId)
		
		elif resource_type == "ZoneList":
			zonelist_path = os.path.join(zonelist_dir, mZoneListId + ".dat")
			write_zonelist(zonelist_path, zonelist)
			mResourceIds.append([mZoneListId, "ZoneList", id_to_int(mZoneListId)])
		
		
		for model in models:
			mModelId = model[0]
			is_shared_asset = model[2]
			if is_shared_asset == True:
				continue
			
			model_path = os.path.join(model_dir, mModelId + ".dat")
			already_is_file = False
			if os.path.isfile(model_path):
				print("WARNING: file %s already exists in %s. Replacing it with new file." % (mModelId, main_collection.name))
				already_is_file = True
			write_model(model_path, model, resource_type)
			if already_is_file == False:
				mResourceIds.append([mModelId, "Model", id_to_int(mModelId)])
		
		
		for renderable in renderables:
			mRenderableId = renderable[0]
			is_shared_asset = renderable[2]
			if is_shared_asset == True:
				continue
			
			renderable_path = os.path.join(renderable_dir, mRenderableId + ".dat")
			already_is_file = False
			if os.path.isfile(renderable_path):
				print("WARNING: file %s already exists in %s. Replacing it with new file." % (mRenderableId, main_collection.name))
				already_is_file = True
			write_renderable(renderable_path, renderable, resource_type, shared_dir)
			if already_is_file == False:
				mResourceIds.append([mRenderableId, "Renderable", id_to_int(mRenderableId)])
		
		
		for material in materials:
			mMaterialId = material[0]
			is_shared_asset = material[2]
			if is_shared_asset == True:
				shared_material_path = os.path.join(shared_material_dir, mMaterialId + ".dat")
				
				if os.path.isfile(shared_material_path) and (resource_type == "GraphicsSpec" or resource_type == "CharacterSpec"):
					# Vehicles and character does not have truely shared materials, but can use the same material
					print("WARNING: moving shared material %s. Be sure its textures are shared or they exist in the output file." % mMaterialId)
					material_path = os.path.join(material_dir, mMaterialId + ".dat")
					if os.path.isfile(material_path):
						print("WARNING: material %s already exists in vehicle %s. Skipping it." % (mMaterialId, main_collection.name))
						continue
					
					status = move_shared_resource(material_path, mMaterialId, shared_material_dir)
					if status == 0:
						mResourceIds.append([mMaterialId, "Material", id_to_int(mMaterialId)])
					else:
						print("WARNING: material %s does not exist on library. Add it manually to the Material folder." % mMaterialId)
						mResourceIds.append([mMaterialId, "Material", id_to_int(mMaterialId)])
				elif not os.path.isfile(shared_material_path) and (resource_type == "GraphicsSpec" or resource_type == "CharacterSpec"):
					print("ERROR: not possible to move shared material %s. Be sure it is shared or it exists in the game library." % mMaterialId)
				continue
			
			material_path = os.path.join(material_dir, mMaterialId + ".dat")
			already_is_file = False
			if os.path.isfile(material_path):
				print("WARNING: file %s already exists in %s. Replacing it with new file." % (mMaterialId, main_collection.name))
				already_is_file = True
			write_material(material_path, material)
			if already_is_file == False:
				mResourceIds.append([mMaterialId, "Material", id_to_int(mMaterialId)])
		
		
		for raster in rasters:
			mRasterId = raster[0]
			is_shared_asset = raster[2]
			if is_shared_asset == True:
				continue
			
			raster_path = os.path.join(raster_dir, mRasterId + ".dat")
			already_is_file = False
			if os.path.isfile(raster_path):
				print("WARNING: file %s already exists in %s. Replacing it with new file." % (mRasterId, main_collection.name))
				already_is_file = True
			write_raster(raster_path, raster)
			if already_is_file == False:
				mResourceIds.append([mRasterId, "Texture", id_to_int(mRasterId)])
		
		
		for mSamplerStateId in samplerstates:
			samplerstate_path = os.path.join(samplerstate_dir, mSamplerStateId + ".dat")
			if os.path.isfile(samplerstate_path):
				print("WARNING: SamplerState %s already exists in %s. Skipping it." % (mSamplerStateId, main_collection.name))
				continue
			
			status = move_shared_resource(samplerstate_path, mSamplerStateId, shared_samplerstate_dir)
			if status == 0:
				mResourceIds.append([mSamplerStateId, "SamplerState", id_to_int(mSamplerStateId)])
			else:
				print("ERROR: SamplerState %s does not exist on library. Add it manually to the SamplerState folder. Continuing to export." % mSamplerStateId)
				mResourceIds.append([mSamplerStateId, "SamplerState", id_to_int(mSamplerStateId)])
		
		
		mResourceIds_ = [mResourceId[0] for mResourceId in mResourceIds]
		if len(mResourceIds_) != len(set(mResourceIds_)):
			print("ERROR: duplicated resource IDs. Verify the list below for the duplicated IDs and do the proper fixes:")
			duplicated_ids = [k for k,v in Counter(mResourceIds_).items() if v>1]
			duplicated_ids_ = [[mResourceId[0], mResourceId[1]] for mResourceId in mResourceIds if mResourceId[0] in duplicated_ids]
			print(duplicated_ids_)
			return {'CANCELLED'}
		
		ids_table_path = os.path.join(directory_path, "IDs.BIN")
		if resource_type == "InstanceList":
			resources_table_path = os.path.join(directory_path, "IDs_" + track_unit_name + ".BIN")
			resources_table_path2 = os.path.join(directory_path, "IDs_" + track_unit_name + ".BNDL")
			if os.path.isfile(resources_table_path2):
				resources_table_path = resources_table_path2
		
		elif resource_type == "GraphicsSpec":
			resources_table_path = os.path.join(directory_path, "IDs_" + vehicle_name + ".BIN")
		elif resource_type == "CharacterSpec":
			resources_table_path = os.path.join(directory_path, "IDs_ALL_CHARS.BNDL")
		else:
			resources_table_path = os.path.join(directory_path, "IDs_chr" + ".BIN")
		
		if os.path.isfile(resources_table_path):
			write_header = False
		else:
			write_header = True
		
		write_resources_table(ids_table_path, mResourceIds, resource_type, write_header)
		if os.path.isfile(resources_table_path) and resource_type == "GraphicsSpec":
			if len(Skeleton) > 0:
				# Removing default skeleton file
				remove_resource_from_resources_table(resources_table_path, mSkeletonId_previous)
			if len(ControlMeshes) > 0:
				# Removing default controlmesh file
				remove_resource_from_resources_table(resources_table_path, mControlMeshId_previous)
			merge_resources_table(ids_table_path, resources_table_path)
			os.remove(ids_table_path)
		elif os.path.isfile(resources_table_path) and resource_type == "InstanceList":
			merge_resources_table(ids_table_path, resources_table_path)
			os.remove(ids_table_path)
		elif os.path.isfile(resources_table_path) and resource_type == "CharacterSpec":
			merge_resources_table(ids_table_path, resources_table_path)
			os.remove(ids_table_path)
		else:
			resources_table_path = ids_table_path
		
		
		if resource_type == "GraphicsSpec" and debug_redirect_vehicle == True:
			new_vehicle_number = new_vehicle_name.upper().replace("VEH", "").replace("HI", "").replace("LO", "").replace("TR", "").replace("GR", "").replace("MS", "").replace("_", "")
			try:
				test = int(new_vehicle_number)
			except:
				print("ERROR: redirect vehicle name is in the wrong format. Use something like VEH_118240_MS.")
			
			# Renaming GraphicsSpec related IDs
			mGraphicsSpecId_new = int_to_id(new_vehicle_number)
			for file in os.listdir(graphicsspec_dir):
				if mGraphicsSpecId in file:
					graphicsspec_path = os.path.join(graphicsspec_dir, file)
					graphicsspec_path_new = os.path.join(graphicsspec_dir, mGraphicsSpecId_new + file[11:])
					os.rename(graphicsspec_path, graphicsspec_path_new)
					change_mResourceId_on_file(resources_table_path, mGraphicsSpecId, mGraphicsSpecId_new, True)
					break
			
			genesysinstance_dir = genesysobject_dir
			genesysinstance_dir2 = os.path.join(trafficattribs_dir, "GenesysInstance")
			genesysinstance_dir_backup = os.path.join(shared_trafficattribs_dir, "GenesysInstance")
			if os.path.isdir(genesysinstance_dir):
				for file in os.listdir(genesysinstance_dir):
					if mGraphicsSpecId in file:
						genesysintance_path = os.path.join(genesysinstance_dir, file)
						genesysintance_path_new = os.path.join(genesysinstance_dir, mGraphicsSpecId_new + file[11:])
						os.rename(genesysintance_path, genesysintance_path_new)
						
						change_mResourceId_on_file(genesysintance_path_new, mGraphicsSpecId, mGraphicsSpecId_new, True)
						change_mResourceId_on_file(resources_table_path, mGraphicsSpecId, mGraphicsSpecId_new, True)
			if os.path.isdir(genesysinstance_dir2):
				for file in os.listdir(genesysinstance_dir2):
					if mGraphicsSpecId in file:
						genesysintance_path = os.path.join(genesysinstance_dir2, file)
						genesysintance_path_new = os.path.join(genesysinstance_dir2, mGraphicsSpecId_new + file[11:])
						shutil.copy2(genesysintance_path, genesysintance_path_new)
						change_mResourceId_on_file(genesysintance_path_new, mGraphicsSpecId, mGraphicsSpecId_new, True)
						shutil.copy2(os.path.join(genesysobject_dir_backup, file), genesysintance_path)
			
			# Renaming VehicleSound related IDs
			vehiclesound_dir = os.path.join(directory_path, "VehicleSound")
			vehiclesound_dir2 = os.path.join(trafficattribs_dir, "VehicleSound")
			vehiclesound_dir_backup = os.path.join(export_path, "TRAFFICATTRIBS", "VehicleSound")
			generic_file = False
			if os.path.isdir(vehiclesound_dir):
				vehiclesound_dir = vehiclesound_dir
			elif os.path.isdir(vehiclesound_dir2):
				vehiclesound_dir = vehiclesound_dir2
				generic_file = True
			
			try:
				vehiclesound = str(vehicle_number) + "_vehiclesound"
				mVehicleSoundID = calculate_resourceid(vehiclesound.lower())
				vehiclesound_new = str(new_vehicle_number) + "_vehiclesound"
				mVehicleSoundID_new = calculate_resourceid(vehiclesound_new.lower())
				vehiclesound_path = os.path.join(vehiclesound_dir, mVehicleSoundID + ".dat")
				vehiclesound_path_new = os.path.join(vehiclesound_dir, mVehicleSoundID_new + ".dat")
				if generic_file == False:
					os.rename(vehiclesound_path, vehiclesound_path_new)
					change_mResourceId_on_file(resources_table_path, mVehicleSoundID, mVehicleSoundID_new, True)
				elif generic_file == True:
					shutil.copy2(vehiclesound_path, vehiclesound_path_new)
					shutil.copy2(os.path.join(vehiclesound_dir_backup, mVehicleSoundID + ".dat"), vehiclesound_path)
			except:
				pass
			
			try:
				competitorsound = str(vehicle_number) + "_competitorsound"
				mCompetitorSoundID = calculate_resourceid(competitorsound.lower())
				competitorsound_new = str(new_vehicle_number) + "_competitorsound"
				mCompetitorSoundID_new = calculate_resourceid(competitorsound_new.lower())
				competitorsound_path = os.path.join(vehiclesound_dir, mCompetitorSoundID + ".dat")
				competitorsound_path_new = os.path.join(vehiclesound_dir, mCompetitorSoundID_new + ".dat")
				if generic_file == False:
					os.rename(competitorsound_path, competitorsound_path_new)
					change_mResourceId_on_file(resources_table_path, mCompetitorSoundID, mCompetitorSoundID_new, True)
				elif generic_file == True:
					shutil.copy2(competitorsound_path, competitorsound_path_new)
					shutil.copy2(os.path.join(vehiclesound_dir_backup, mCompetitorSoundID + ".dat"), competitorsound_path)
			except:
				pass
			
			if pack_bundle_file == True and os.path.isdir(trafficattribs_dir):
				tr_resources_table_path = os.path.join(trafficattribs_dir, "IDs_TRAFFICATTRIBS.BNDL")
				tr_resources_table_path2 = os.path.join(trafficattribs_dir, "IDs.BNDL")
				if os.path.isfile(tr_resources_table_path):
					status = pack_bundle_hp(tr_resources_table_path, trafficattribs_dir, "TRAFFICATTRIBS.BNDL", game)
				elif os.path.isfile(tr_resources_table_path2):
					status = pack_bundle_hp(tr_resources_table_path2, trafficattribs_dir, "TRAFFICATTRIBS.BNDL", game)
		
		if pack_bundle_file == True:
			if os.path.isfile(resources_table_path):
				if resource_type == "ZoneList":
					status = pack_bundle_hp(resources_table_path, directory_path, "PVS.BNDL", game)
				else:
					#status = pack_bundle_hp(resources_table_path, directory_path, main_collection.name + ".BIN", game)
					if resource_type == "GraphicsSpec" and debug_redirect_vehicle == True:
						status = pack_bundle_hp(resources_table_path, directory_path, new_vehicle_name + ".BIN", game)
					elif resource_type == "GraphicsSpec":
						status = pack_bundle_hp(resources_table_path, directory_path, main_collection.name + ".BIN", game)
					else:
						status = pack_bundle_hp(resources_table_path, directory_path, main_collection.name + ".BNDL", game)
		
		elapsed_time = time.time() - writing_time
		print("\t... %.4fs" % elapsed_time)
	
	print("Finished")
	elapsed_time = time.time() - start_time
	print("Elapsed time: %.4fs" % elapsed_time)
	return {'FINISHED'}


def read_object(object, resource_type, shared_dir, copy_uv_layer):
	# Definitions
	shared_material_dir = os.path.join(shared_dir, "Material")
	
	# Mesh data definitions
	num_meshes = len(object.material_slots)
	not_used_material_slots = [x for x in range(num_meshes)]
	indices_buffer = [[] for _ in range(num_meshes)]
	vertices_buffer = [[] for _ in range(num_meshes)]
	meshes_info = [[] for _ in range(num_meshes)]
	object_center = []
	object_radius = 1.0
	submeshes_center = [[] for _ in range(num_meshes)]
	submeshes_bounding_box = [[] for _ in range(num_meshes)]
	
	# Inits
	mesh = object.data
	mesh.calc_normals_split()
	loops = mesh.loops
	bm = bmesh.new()
	bm.from_mesh(mesh)
	
	has_uv = len(mesh.uv_layers) > 0
	if has_uv:
		uv_layers = bm.loops.layers.uv
		
		uv_layers_ready_for_hp = True
		for layer in uv_layers:
			if layer.name.upper() in ("TEXCOORD1", "TEXCOORD2", "TEXCOORD3", "TEXCOORD4", "TEXCOORD5", "TEXCOORD6", "TEXCOORD7", "TEXCOORD8"):
				pass
			elif layer.name.upper() in ("UVMAP", "UV1MAP", "UV2MAP", "UV3MAP", "UV4MAP", "UV5MAP", "UV6MAP", "UV7MAP", "UV8MAP"):
				pass
			else:
				uv_layers_ready_for_hp = False
				break
	else:
		uv_layers = []
		uv_layers_ready_for_hp = False
	
	deform_layer = bm.verts.layers.deform.active
	group_names = tuple(vertex_group.name for vertex_group in object.vertex_groups)
	
	if num_meshes == 0:
		print("ERROR: no materials applied on mesh %s." % mesh.name)
		return (meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, 1)
	
	blend_index1 = bm.verts.layers.int.get("blend_index1")
	blend_index2 = bm.verts.layers.int.get("blend_index2")
	blend_index3 = bm.verts.layers.int.get("blend_index3")
	blend_index4 = bm.verts.layers.int.get("blend_index4")
	
	blend_weight1 = bm.verts.layers.float.get("blend_weight1")
	blend_weight2 = bm.verts.layers.float.get("blend_weight2")
	blend_weight3 = bm.verts.layers.float.get("blend_weight3")
	blend_weight4 = bm.verts.layers.float.get("blend_weight4")
	
	mesh_indices = [[] for _ in range(num_meshes)]
	mesh_vertices_buffer = [{} for _ in range(num_meshes)]
	vert_indices = [{} for _ in range(num_meshes)]
	
	ind = [0] * num_meshes
	
	mMaterialIds = [""] * num_meshes
	vertex_properties_list = [""] * num_meshes
	
	vertices_x = []
	vertices_y = []
	vertices_z = []
	positions = [{} for _ in range(num_meshes)]
	normals = [{} for _ in range(num_meshes)]
	blends_indices = [{} for _ in range(num_meshes)]
	blends_weights = [{} for _ in range(num_meshes)]
	uv = [{} for _ in range(num_meshes)]
	
	for face in bm.faces:
		if face.hide == False:
			mesh_index = face.material_index
			indices = []
			
			if mMaterialIds[mesh_index] == "":
				if mesh.materials[mesh_index] == None:
					print("ERROR: face without material found on mesh %s." % mesh.name)
					return (meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, 1)
				material_name = mesh.materials[mesh_index].name
				#mMaterialIds[mesh_index] = material_name.split(".")[0]
				mMaterialIds[mesh_index] = material_name				# Not splitting at ".001". Each one is identifyed as a unique material by Blender and so the exporter
				not_used_material_slots.remove(mesh_index)
				
				mat = bpy.data.materials.get(material_name)
				
				try:
					shader_type = mat["shader_type"]
					
					with Suppressor():
						mShaderId, shader_type = get_mShaderID(shader_type, resource_type)
					
					shared_shader_dir = os.path.join(os.path.join(shared_dir, "SHADERS"), "Shader")
					shader_path = os.path.join(shared_shader_dir, mShaderId + "_83.dat")
					_, mVertexDescriptorId, _, _, _, _, _ = read_shader(shader_path)
					
					shared_vertex_descriptor_dir = os.path.join(os.path.join(shared_dir, "SHADERS"), "VertexDescriptor")
					vertex_descriptor_path = os.path.join(shared_vertex_descriptor_dir, mVertexDescriptorId + ".dat")
					vertex_properties = read_vertex_descriptor(vertex_descriptor_path)
				except:
					vertex_properties = None
				
				vertex_properties_list[mesh_index] = vertex_properties
			
			if len(face.verts) > 3:
				print("ERROR: non triangular face on mesh %s." % mesh.name)
				return (meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, 1)
			
			for vert in face.verts:
				if vert.index not in vert_indices[mesh_index]:
					vert_indices[mesh_index][vert.index] = ind[mesh_index]
					ind[mesh_index] += 1
				vert_index = vert_indices[mesh_index][vert.index]
				indices.append(vert_index)
				if vert_index in positions[mesh_index]:
					continue
				vertices_x.append(vert.co[0])
				vertices_y.append(vert.co[1])
				vertices_z.append(vert.co[2])
				positions[mesh_index][vert_index] = vert.co
				#normals[mesh_index][vert_index] = vert.normal
				#print(vert.normal)
				
				# New method (vertex group)
				deform_sensor_data = []
				deform_bone_data = []
				blend_indices = [0, 0, 0, 0]
				blend_weight = [0xFF, 0, 0, 0]
				
				if deform_layer is not None:
					for vertex_group_index, weight in vert[deform_layer].items():
						name = group_names[vertex_group_index]
						if "sensor_" in name.lower():
							name = int(name.split("_")[1])	# If error: bone and sensor data is in the wrong format. It should be 'Bone_001' or 'Sensor_001'
							deform_sensor_data.append((name, int(round(weight*255.0))))
						elif "bone_" in name.lower():
							name = int(name.split("_")[1])	# If error: bone and sensor data is in the wrong format. It should be 'Bone_001' or 'Sensor_001'
							deform_bone_data.append((name, int(round(weight*255.0))))
					
					# Sort the lists based on the weight in descending order
					deform_sensor_data = sorted(deform_sensor_data, key=lambda x: x[1], reverse=True)
					deform_bone_data = sorted(deform_bone_data, key=lambda x: x[1], reverse=True)
					
					# Just getting the first four
					for i, sensor_data in enumerate(deform_sensor_data[0:4]):
						blend_indices[i] = sensor_data[0]
						blend_weight[i] = sensor_data[1]
					
					for i, bone_data in enumerate(deform_bone_data[0:2]):
						blend_indices[i+2] = bone_data[0]
						blend_weight[i+2] = bone_data[1]
					
					blends_indices[mesh_index][vert_index] = blend_indices
					blends_weights[mesh_index][vert_index] = blend_weight
				else:
					# Keeping for compatibility
					if None in [blend_index1, blend_index2, blend_index3, blend_index4]:
						blends_indices[mesh_index][vert_index] = [0, 0, 0, 0]
					else:
						blends_indices[mesh_index][vert_index] = [vert[blend_index1], vert[blend_index2], vert[blend_index3], vert[blend_index4]]
					if None in [blend_weight1, blend_weight2, blend_weight3, blend_weight4]:
						blends_weights[mesh_index][vert_index] = [0xFF, 0, 0, 0]
					else:
						blends_weights[mesh_index][vert_index] = [int(round(vert[blend_weight1]*255.0/100.0)), int(round(vert[blend_weight2]*255.0/100.0)),
																  int(round(vert[blend_weight3]*255.0/100.0)), int(round(vert[blend_weight4]*255.0/100.0))]
			
			indices_buffer[mesh_index].append(indices)
			
			if has_uv and uv_layers_ready_for_hp == True:
				for loop in face.loops:
					uvs = [None]*8
					for layer in uv_layers:
						if layer.name.upper() == "UVMAP":
							index_layer = 0
						else:
							index_layer = int(layer.name.upper().replace("TEXCOORD", "").replace("UV", "").replace("MAP", "")) - 1
						uvs[index_layer] = loop[layer].uv
					
					# Checking if all necessary uvs are present
					vertex_properties = vertex_properties_list[mesh_index]
					if vertex_properties != None:
						semantic_properties = vertex_properties[1][0]
						for index_layer, uv_ in enumerate(uvs):
							if uv_ == None:
								for semantic in semantic_properties:
									if semantic[0] == "TEXCOORD" + str(index_layer + 1):
										if semantic[1][0] in ("2f", "2e"):
											#print("WARNING: uv layer %d (%s) is missing on model %s (material %s). It is required by the shader %s" %(index_layer, semantic[0], object.name, mMaterialId, shader_type))
											if copy_uv_layer == True and uvs[0] != None:
												#print("... copying layer zero.")
												uvs[index_layer] = uvs[0]
											else:
												#print("... defining as zero.")
												uvs[index_layer] = [0.0, 0.0]
										else:
											# They don't matter
											uvs[index_layer] = [0.0, 0.0]
										break
								else:
									# They don't matter
									uvs[index_layer] = [0.0, 0.0]
					else:
						for index_layer, uv_ in enumerate(uvs):
							if uv_ == None:
								if copy_uv_layer == True and uvs[0] != None:
									#print("... copying layer zero.")
									uvs[index_layer] = uvs[0]
								else:
									#print("... defining as zero.")
									uvs[index_layer] = [0.0, 0.0]
					
					uv[mesh_index][vert_indices[mesh_index][loop.vert.index]] = uvs
			elif has_uv:
				for loop in face.loops:
					uvs = []
					for layer in range(0, len(uv_layers)):
						uv_layer = bm.loops.layers.uv[layer]
						uvs.append(loop[uv_layer].uv)
					uv[mesh_index][vert_indices[mesh_index][loop.vert.index]] = uvs
			
			for index in indices:
				if index in mesh_indices[mesh_index]:
					continue
				mesh_indices[mesh_index].append(index)
				
				position = positions[mesh_index][index]
				#normal = normals[mesh_index][index]
				normal = [0.0, 0.0, 0.0]
				tangent = [0.0, 0.0, 0.0]
				binormal = [0.0, 0.0, 0.0]
				#color = [0, 0, 0, 0xFF]
				color = [0xFF, 0xFF, 0xFF, 0xFF]
				color2 = [0, 0, 0, 0]
				if uv_layers_ready_for_hp == True:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					uv3 = uv[mesh_index][index][2]
					uv4 = uv[mesh_index][index][3]
					uv5 = uv[mesh_index][index][4]
					uv6 = uv[mesh_index][index][5]
				elif len(uv_layers) >= 6:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					uv3 = uv[mesh_index][index][2]
					uv4 = uv[mesh_index][index][3]
					uv5 = uv[mesh_index][index][4]
					uv6 = uv[mesh_index][index][5]
				elif len(uv_layers) == 5:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					uv3 = uv[mesh_index][index][2]
					uv4 = uv[mesh_index][index][3]
					uv5 = uv[mesh_index][index][3]
					if copy_uv_layer == True:
						uv6 = uv1[:]
					else:
						uv6 = [0.0, 0.0]
				elif len(uv_layers) == 4:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					uv3 = uv[mesh_index][index][2]
					uv4 = uv[mesh_index][index][3]
					if copy_uv_layer == True:
						uv5 = uv1[:]
						uv6 = uv1[:]
					else:
						uv5 = [0.0, 0.0]
						uv6 = [0.0, 0.0]
				elif len(uv_layers) == 3:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					uv3 = uv[mesh_index][index][2]
					if copy_uv_layer == True:
						uv4 = uv1[:]
						uv5 = uv1[:]
						uv6 = uv1[:]
					else:
						uv4 = [0.0, 0.0]
						uv5 = [0.0, 0.0]
						uv6 = [0.0, 0.0]
				elif len(uv_layers) == 2:
					uv1 = uv[mesh_index][index][0]
					uv2 = uv[mesh_index][index][1]
					if copy_uv_layer == True:
						uv3 = uv1[:]
						uv4 = uv1[:]
						uv5 = uv1[:]
						uv6 = uv1[:]
					else:
						uv3 = [0.0, 0.0]
						uv4 = [0.0, 0.0]
						uv5 = [0.0, 0.0]
						uv6 = [0.0, 0.0]
				elif len(uv_layers) == 1:
					uv1 = uv[mesh_index][index][0]
					if copy_uv_layer == True:
						uv2 = uv1[:]
						uv3 = uv1[:]
						uv4 = uv1[:]
						uv5 = uv1[:]
						uv6 = uv1[:]
					else:
						uv2 = [0.0, 0.0]
						uv3 = [0.0, 0.0]
						uv4 = [0.0, 0.0]
						uv5 = [0.0, 0.0]
						uv6 = [0.0, 0.0]
				else:
					uv1 = [0.0, 0.0]
					uv2 = [0.0, 0.0]
					uv3 = [0.0, 0.0]
					uv4 = [0.0, 0.0]
					uv5 = [0.0, 0.0]
					uv6 = [0.0, 0.0]
				blend_indices = blends_indices[mesh_index][index]
				blend_weight = blends_weights[mesh_index][index]
				mesh_vertices_buffer[mesh_index][index] = [index, position[:], normal[:], tangent[:], color[:], uv1[:], uv2[:], uv3[:], uv4[:], uv5[:], uv6[:], blend_indices[:], blend_weight[:], binormal[:], color2[:]]
	
	max_vertex = (max(vertices_x), max(vertices_y), max(vertices_z))
	min_vertex = (min(vertices_x), min(vertices_y), min(vertices_z))
	
	for mesh_index in range(0, num_meshes):
		if len(indices_buffer[mesh_index]) == 0:
			continue
		
		max_submesh_vertex_x = [max(v[0] for v in positions[mesh_index].values()), max(v[1] for v in positions[mesh_index].values()), max(v[2] for v in positions[mesh_index].values())]
		min_submesh_vertex_x = [min(v[0] for v in positions[mesh_index].values()), min(v[1] for v in positions[mesh_index].values()), min(v[2] for v in positions[mesh_index].values())]
		submeshes_center[mesh_index] = [(max_submesh_vertex_x[0] + min_submesh_vertex_x[0])*0.5, (max_submesh_vertex_x[1] + min_submesh_vertex_x[1])*0.5, (max_submesh_vertex_x[2] + min_submesh_vertex_x[2])*0.5]
		
		submeshes_bounding_box[mesh_index] = list(get_minimum_bounding_box(mesh, mesh_index))
	
	vertices_x.clear()
	vertices_y.clear()
	vertices_z.clear()
	
	object_center = [(max_vertex[0] + min_vertex[0])*0.5, (max_vertex[1] + min_vertex[1])*0.5, (max_vertex[2] + min_vertex[2])*0.5]
	object_radius = math.dist(object_center, max_vertex)
	
	ao_layer = True
	vcolor2_layer = True
	try:
		mesh_vertex_colors = mesh.color_attributes
		using_color_attributes = True
	except:
		mesh_vertex_colors = mesh.vertex_colors
		using_color_attributes = False
	
	if len(mesh_vertex_colors) > 0:
		if "Ambient Occlusion" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("Ambient Occlusion")
		elif "Ambient occlusion" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("Ambient occlusion")
		elif "AO" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("AO")
		elif "ao" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("ao")
		elif "VColor1" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("VColor1")
		elif "vcolor1" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("vcolor1")
		elif "Col" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("Col")
		elif "col" in mesh_vertex_colors:
			ao_layer_index = mesh_vertex_colors.keys().index("col")
		else:
			#print("WARNING: no Ambient Occlusion or AO layer on mesh %s. Default AO colors will be used." % mesh.name)
			ao_layer = False
		
		if "VColor2" in mesh_vertex_colors:
			vcolor2_layer_index = mesh_vertex_colors.keys().index("VColor2")
		elif "vcolor2" in mesh_vertex_colors:
			vcolor2_layer_index = mesh_vertex_colors.keys().index("vcolor2")
		else:
			vcolor2_layer = False
		
	else:
		#print("WARNING: no vertex colors layer on mesh %s. Default AO colors will be used." % mesh.name)
		ao_layer = False
		vcolor2_layer = False
	
	tangents_on_UV1 = False
	tangents_on_UV2 = False
	use_blender_calc_tangents = False	# In some cases it gives wrong values (1,0,0)
	vertices_list = [[] for _ in range(num_meshes)]
	for mesh_index in range(0, num_meshes):
		if len(indices_buffer[mesh_index]) == 0:
			continue
		
		mMaterialId = mMaterialIds[mesh_index]
		mat = bpy.data.materials.get(mMaterialId)
		
		try:
			shader_type = mat["shader_type"]
		except:
			shader_type = ""
		
		mShaderId, shader_type = get_mShaderID(shader_type, resource_type)
		
		if has_uv and use_blender_calc_tangents:
			if mShaderId in ("A9_EF_09_00", "AB_EF_09_00", "A5_EF_09_00") and tangents_on_UV2 == False:
				mesh.free_tangents()
				mesh.calc_tangents(uvmap="UV2Map")
				tangents_on_UV1 = False
				tangents_on_UV2 = True
			
			elif tangents_on_UV1 == False:
				mesh.free_tangents()
				mesh.calc_tangents(uvmap="UVMap")
				tangents_on_UV1 = True
				tangents_on_UV2 = False
		
		for face in mesh.polygons:
			if face.hide == True:
				continue
			
			if mesh_index != face.material_index:
				continue
			
			for loop_ind in face.loop_indices:
				vert_index = vert_indices[mesh_index][loops[loop_ind].vertex_index]
				
				if vert_index in vertices_list[mesh_index]:
					continue
				
				vertices_list[mesh_index].append(vert_index)
				
				normal = list(loops[loop_ind].normal[:])
				tangent = [0.0, 0.0, 0.0]
				binormal = [0.0, 0.0, 0.0]
				color2 = []
				
				if use_blender_calc_tangents:
					tangent = list(loops[loop_ind].tangent[:])
					binormal = list(loops[loop_ind].bitangent[:])
				
					if mShaderId == "2A_79_00_00":
						binormal = [1.0, 1.0, 0.0]
				
				if ao_layer:
					color = list(mesh_vertex_colors[ao_layer_index].data[loop_ind].color[:])
					for i in range(0, 4):
						if i < 3 and using_color_attributes == True:
							color[i] = lin2s1(color[i])
						color[i] = round(color[i] * 255.0)
				else:
					color = [255, 255, 255, 255]
				if vcolor2_layer: # For compatibility
					# When some new face is added it might not have a proper vcolor2
					color2 = list(mesh_vertex_colors[vcolor2_layer_index].data[loop_ind].color[:])
					for i in range(0, 4):
						if i < 3 and using_color_attributes == True:
							color2[i] = lin2s1(color2[i])
						color2[i] = round(color2[i] * 255.0)
				
				mesh_vertices_buffer[mesh_index][vert_index][2] = normal[:]
				mesh_vertices_buffer[mesh_index][vert_index][3] = tangent[:]
				mesh_vertices_buffer[mesh_index][vert_index][4] = color[:]
				mesh_vertices_buffer[mesh_index][vert_index][13] = binormal[:]
				mesh_vertices_buffer[mesh_index][vert_index][14] = color2[:]
	
	if use_blender_calc_tangents:
		mesh.free_tangents()
	mesh.free_normals_split()
	bm.clear()
	bm.free()
	
	for mesh_index in range(0, num_meshes):
		if len(indices_buffer[mesh_index]) == 0:
			continue
		
		mMaterialId = mMaterialIds[mesh_index]
		mat = bpy.data.materials.get(mMaterialId)
		try:
			shader_type = mat["shader_type"]
		except:
			shader_type = ""
			
		mShaderId, shader_type = get_mShaderID(shader_type, resource_type)
		
		if use_blender_calc_tangents == False:
			calculate_tangents(indices_buffer[mesh_index], mesh_vertices_buffer[mesh_index], mShaderId)
		
		vertices_buffer[mesh_index] = [mesh_vertices_buffer[mesh_index], mesh_indices[mesh_index]]
		
		meshes_info[mesh_index] = [mesh_index, mMaterialId]
		
		if len(vertices_buffer[mesh_index]) >= 0xFFFF:
			terminator = 0xFFFFFFFF
		else:
			terminator = 0xFFFF
		
		triangle_strips = convert_triangle_to_strip(indices_buffer[mesh_index], terminator)
		cte_min = min(triangle_strips)
		cte_max = max(index for index in triangle_strips if index != terminator)
		for j in range(0, len(triangle_strips)):
			if triangle_strips[j] == terminator:
				continue
			triangle_strips[j] = triangle_strips[j] - cte_min
		
		#j=0
		#cte=0
		#v=0
		#while (j < len(triangle_strips)):
		#	if triangle_strips[j] == 0xFFFF:
		#		triangle_strips[j] = triangle_strips[j-1]
		#		index_insert = triangle_strips[j+1]
		#		triangle_strips.insert(j+1, index_insert)
		#		if (v+cte)%2 != 0:
		#			triangle_strips.insert(j+1, index_insert)
		#			j += 2
		#		else:
		#			cte += -1
		#			j += 1
		#	j = j + 1
		#	v = v + 1
		indices_buffer[mesh_index] = triangle_strips[:]
		
		if len(vertices_buffer[mesh_index]) >= 0xFFFF:
			print("ERROR: number of vertices higher than the supported by the game on mesh %s. Each material cannot have more than 65535 vertices." % mesh.name)
			return (meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, 1)
		
	
	# Verifying if some material is not used
	if len(not_used_material_slots) != 0:
		for material_index in reversed(not_used_material_slots):
			mesh_index = material_index
			del meshes_info[mesh_index]
			del indices_buffer[mesh_index]
			del vertices_buffer[mesh_index]
			del submeshes_bounding_box[mesh_index]
		
		num_meshes = num_meshes - len(not_used_material_slots)
		
		for mesh_index in range(0, num_meshes):
			meshes_info[mesh_index][0] = mesh_index
	
	return (meshes_info, indices_buffer, vertices_buffer, object_center, object_radius, submeshes_bounding_box, 0)


def read_polygonsoup_object(object, translation, scale, resource_type, track_unit_number): #OK
	PolygonSoupVertices = []
	PolygonSoupPolygons = []
	PolygonSoupPolygons_triangles = []
	
	# Inits
	mesh = object.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	
	edge_cosine1 = bm.faces.layers.int.get("edge_cosine1")
	edge_cosine2 = bm.faces.layers.int.get("edge_cosine2")
	edge_cosine3 = bm.faces.layers.int.get("edge_cosine3")
	edge_cosine4 = bm.faces.layers.int.get("edge_cosine4")
	#collision_tag0 = bm.faces.layers.int.get("collision_tag0")
	collision_tag1 = bm.faces.layers.int.get("collision_tag1")
	
	for vert in bm.verts:
		if vert.hide == False:
			#PolygonSoupVertices.append(vert.co[:])
			#PolygonSoupVertices.append([round(vert_co) for vert_co in vert.co])
			PolygonSoupVertices.append([vert_co*scale + translation[i] for i, vert_co in enumerate(vert.co)])
	
	if len(PolygonSoupVertices) >= 0xFF:
		print("ERROR: number of vertices higher than the supported by the game on collision mesh %s. It should have less than 255 vertices." % mesh.name)
		return (1, [], [], 0)
	
	for face in bm.faces:
		if face.hide == False:
			if len(face.verts) > 4 or len(face.verts) < 3:
				print("ERROR: non triangular or quad face on mesh %s." % mesh.name)
				return (1, [], [], 0)
			
			material_index = face.material_index
			#if mesh.materials[material_index] == None:
				#print("ERROR: face without material found on mesh %s." % mesh.name)
				#return (1, [], [], 0)
				#print("WARNING: face without material found on mesh %s." % mesh.name)
			
			has_material = True
			try:
				if mesh.materials[material_index] == None:
					print("WARNING: face without material found on mesh %s." % mesh.name)
					has_material = False
			except:
				print("WARNING: face without material found on mesh %s." % mesh.name)
				has_material = False
			
			if collision_tag1 == None:
				mu16CollisionTag_part1 = 0
			else:
				mu16CollisionTag_part1 = face[collision_tag1]
			
			if resource_type == "InstanceList":
				mu16CollisionTag_part1 = mu16CollisionTag_part1 + track_unit_number*0x10
			
			try:
				mu16CollisionTag_part0 = mesh.materials[material_index].name.split(".")[0]
			except:
				print("WARNING: setting a default collision tag to the face without material.")
				if resource_type == "InstanceList":
					mu16CollisionTag_part0 = "Cobble"
				else:
					mu16CollisionTag_part0 = "None"
			
			mu16CollisionTag_part0 = get_collision_tag(mu16CollisionTag_part0)
			if mu16CollisionTag_part0 == -1 and has_material:
				print("WARNING: face material name %s (collision tag) is not in the proper formating. Setting it to a default collision tag." % mesh.materials[material_index].name)
				if resource_type == "InstanceList":
					mu16CollisionTag_part0 = get_collision_tag("Cobble")
				else:
					mu16CollisionTag_part0 = get_collision_tag("None")
			
			mau8VertexIndices = []
			for vert in face.verts:
				#vert_index = PolygonSoupVertices.index([vert_co*scale for vert_co in vert.co])
				vert_index = PolygonSoupVertices.index([vert_co*scale + translation[i] for i, vert_co in enumerate(vert.co)])
				mau8VertexIndices.append(vert_index)
			
			if None in [edge_cosine1, edge_cosine2, edge_cosine3, edge_cosine4]:
				if resource_type == "InstanceList":
					mau8EdgeCosines = [0x0, 0x0, 0x0, 0x0]
				else:
					mau8EdgeCosines = [0xFF, 0xFF, 0xFF, 0xFF]
			else:
				mau8EdgeCosines = [face[edge_cosine1], face[edge_cosine2], face[edge_cosine3], face[edge_cosine4]]
			
			if len(face.verts) == 4:
				mau8VertexIndices = [mau8VertexIndices[0], mau8VertexIndices[1], mau8VertexIndices[3], mau8VertexIndices[2]]
				PolygonSoupPolygons.append([[mu16CollisionTag_part0, mu16CollisionTag_part1], mau8VertexIndices, mau8EdgeCosines])
			elif len(face.verts) == 3:
				PolygonSoupPolygons_triangles.append([[mu16CollisionTag_part0, mu16CollisionTag_part1], mau8VertexIndices, mau8EdgeCosines])
	
	mu8NumQuads = len(PolygonSoupPolygons)
	PolygonSoupPolygons.extend(PolygonSoupPolygons_triangles)
	
	if len(PolygonSoupPolygons) >= 0xFF:
		print("ERROR: number of faces higher than the supported by the game on collision mesh %s. It should have less than 255 faces." % mesh.name)
		return (1, [], [], 0)
	
	return (0, PolygonSoupVertices, PolygonSoupPolygons, mu8NumQuads)


def read_zone_object(object):	#OK
	zonepoints = []
	muDistrictId = 0
	
	# Inits
	mesh = object.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	
	for face in bm.faces:
		if face.hide == True:
			continue
		
		for vert in face.verts:
			if vert.hide == True:
				continue
			zonepoints.append(vert.co[:])
			
		if len(zonepoints) >= 0xFFFF:
			print("ERROR: number of vertices higher than the supported by the game zone object %s. It should have less than 65535 vertices." % mesh.name)
			return (1, 0, [])
		
		material_index = face.material_index
		
		has_material = True
		try:
			if mesh.materials[material_index] == None:
				print("WARNING: DistrictId not set in the material name of the zone object %s." % mesh.name)
				has_material = False
		except:
			print("WARNING: DistrictId not set in the material name of the zone object %s." % mesh.name)
			has_material = False
		
		if has_material:
			try:
				muDistrictId = int(mesh.materials[material_index].name.split(".")[0])
			except:
				print("WARNING: DistrictId not proper set in the material name of the zone object %s. It should be an integer." % mesh.name)
				muDistrictId = 0
		else:
			muDistrictId = 0
	
	return (0, muDistrictId, zonepoints)


def read_vertex_descriptor(vertex_descriptor_path): #OK
	vertex_properties = []
	with open(vertex_descriptor_path, "rb") as f:
		unk1 = struct.unpack("<I", f.read(0x4))[0]
		attibutes_flags = struct.unpack("<I", f.read(0x4))[0]
		_ = struct.unpack("<I", f.read(0x4))[0] #null
		num_vertex_attibutes = struct.unpack("<B", f.read(0x1))[0]
		num_streams = struct.unpack("<B", f.read(0x1))[0]
		elements_hash = struct.unpack("<H", f.read(0x2))[0]
		
		semantic_properties = []
		for i in range(0, num_vertex_attibutes):
			semantic_type = struct.unpack("<B", f.read(0x1))[0]
			semantic_index = struct.unpack("<B", f.read(0x1))[0]
			input_slot = struct.unpack("<B", f.read(0x1))[0]
			element_class = struct.unpack("<B", f.read(0x1))[0]
			data_type = struct.unpack("<i", f.read(0x4))[0]
			data_offset = struct.unpack("<i", f.read(0x4))[0]
			step_rate = struct.unpack("<i", f.read(0x4))[0] #null
			vertex_size = struct.unpack("<i", f.read(0x4))[0]
			
			semantic_type = get_vertex_semantic(semantic_type)
			data_type = get_vertex_data_type(data_type)
			
			semantic_properties.append([semantic_type, data_type, data_offset])
		
		vertex_properties = [vertex_size, [semantic_properties]]
		
	return vertex_properties


def read_material_get_shader_type(material_path): #OK
	mShaderId = ""
	mSamplerStateIds = []
	with open(material_path, "rb") as f:
		f.seek(0x6, 0)
		resources_pointer = struct.unpack("<H", f.read(0x2))[0]
		f.seek(0x38, 0)
		miNumSamplers = struct.unpack("<i", f.read(0x4))[0]
		f.seek(resources_pointer, 0)
		mShaderId = bytes_to_id(f.read(0x4))
		f.seek(0xC, 1)
		f.seek(0x10*miNumSamplers, 1)
		
		for i in range(0, miNumSamplers):
			mSamplerStateId = bytes_to_id(f.read(0x4))
			_ = struct.unpack("<i", f.read(0x4))[0]
			muOffset = struct.unpack("<I", f.read(0x4))[0]
			padding = struct.unpack("<i", f.read(0x4))[0]
			
			mSamplerStateIds.append(mSamplerStateId)
		
	return (mShaderId, mSamplerStateIds)


def read_shader(shader_path): #OK
	ShaderType = ""
	raster_types = []
	texture_samplers = []
	with open(shader_path, "rb") as f:
		file_size = os.path.getsize(shader_path)
		
		# Shader description
		pointer_0 = struct.unpack("<q", f.read(0x8))[0]
		pointer_1 = struct.unpack("<q", f.read(0x8))[0]
		shader_description_offset = struct.unpack("<q", f.read(0x8))[0]
		f.seek(0x4, 1)
		end_sampler_types_offset = struct.unpack("<H", f.read(0x2))[0]
		resources_pointer = struct.unpack("<H", f.read(0x2))[0]
		shader_parameters_pointers = f.tell()
		f.seek(shader_description_offset, 0)
		shader_description = f.read(resources_pointer-shader_description_offset).split(b'\x00')[0]
		shader_description = str(shader_description, 'ascii')
		
		# Shader parameters
		f.seek(shader_parameters_pointers, 0)
		shader_parameters_indices_pointer = struct.unpack("<q", f.read(0x8))[0]
		shader_parameters_ones_pointer = struct.unpack("<q", f.read(0x8))[0]
		shader_parameters_nameshash_pointer = struct.unpack("<q", f.read(0x8))[0]
		shader_parameters_data_pointer = struct.unpack("<q", f.read(0x8))[0]
		num_shader_parameters = struct.unpack("<B", f.read(0x1))[0]
		num_shader_parameters_withdata = struct.unpack("<B", f.read(0x1))[0]
		f.seek(0x2, 1)
		f.seek(0x4, 1)
		shader_parameters_names_pointer = struct.unpack("<q", f.read(0x8))[0]
		shader_parameters_end_pointer = struct.unpack("<q", f.read(0x8))[0]
		if shader_parameters_end_pointer == 0:
			shader_parameters_end_pointer = end_sampler_types_offset
		
		f.seek(shader_parameters_indices_pointer, 0)
		shader_parameters_Indices = list(struct.unpack("<%db" % num_shader_parameters, f.read(0x1*num_shader_parameters)))
		
		f.seek(shader_parameters_ones_pointer, 0)
		shader_parameters_Ones = list(struct.unpack("<%db" % num_shader_parameters, f.read(0x1*num_shader_parameters)))
		
		f.seek(shader_parameters_nameshash_pointer, 0)
		shader_parameters_NamesHash = list(struct.unpack("<%dI" % num_shader_parameters, f.read(0x4*num_shader_parameters)))
		
		f.seek(shader_parameters_data_pointer, 0)
		shader_parameters_Data = []
		# for i in range(0, num_shader_parameters):
			# if shader_parameters_Indices[i] == -1:
				# shader_parameters_Data.append(None)
			# else:
				# shader_parameters_Data.append(struct.unpack("<4f", f.read(0x10)))
		
		for i in range(0, num_shader_parameters):
			if shader_parameters_Indices[i] == -1:
				shader_parameters_Data.append(None)
			else:
				f.seek(shader_parameters_data_pointer + 0x10*shader_parameters_Indices[i], 0)
				shader_parameters_Data.append(struct.unpack("<4f", f.read(0x10)))
				#parameters_names.append(shader_parameters_Names[i])
		
		shader_parameters_Names = []
		#shader_parameters_Names = [""]*num_shader_parameters
		for i in range(0, num_shader_parameters):
			f.seek(shader_parameters_names_pointer + i*0x8, 0)
			pointer = struct.unpack("<q", f.read(0x8))[0]
			f.seek(pointer, 0)
			parameter_name = f.read(shader_parameters_end_pointer-pointer).split(b'\x00')[0]
			parameter_name = str(parameter_name, 'ascii')
			shader_parameters_Names.append(parameter_name)
			#shader_parameters_Names[shader_parameters_Indices[i]] = parameter_name
		
		shader_parameters = [shader_parameters_Indices, shader_parameters_Ones, shader_parameters_NamesHash, shader_parameters_Data, shader_parameters_Names]
		
		# Samplers and material constants
		f.seek(0xB0, 0)
		miNumSamplers = struct.unpack("<B", f.read(0x1))[0]
		f.seek(0x3, 1)
		f.seek(0x4, 1)
		mpaMaterialConstants = struct.unpack("<q", f.read(0x8))[0]
		mpaSamplersChannel = struct.unpack("<q", f.read(0x8))[0]
		mpaSamplers = struct.unpack("<q", f.read(0x8))[0]
		f.seek(0xF8, 0)
		end_raster_types_offset = struct.unpack("<i", f.read(0x4))[0]
		if end_raster_types_offset == 0:
			end_raster_types_offset = end_sampler_types_offset
		
		f.seek(mpaMaterialConstants, 0)
		material_constants = struct.unpack("<%dH" % miNumSamplers, f.read(0x2*miNumSamplers))
		
		f.seek(mpaSamplersChannel, 0)
		miChannel = struct.unpack("<%dB" % miNumSamplers, f.read(0x1*miNumSamplers))
		
		f.seek(mpaSamplers, 0)
		raster_type_offsets = list(struct.unpack("<%dq" % miNumSamplers, f.read(0x8*miNumSamplers)))
		raster_type_offsets.append(end_raster_types_offset)
		
		for i in range(0, miNumSamplers):
			f.seek(raster_type_offsets[i], 0)
			if raster_type_offsets[i] > raster_type_offsets[i+1]:
				raster_type = f.read(end_raster_types_offset-raster_type_offsets[i]).split(b'\x00')[0]
			else:
				raster_type = f.read(raster_type_offsets[i+1]-raster_type_offsets[i]).split(b'\x00')[0]
			raster_type = str(raster_type, 'ascii')
			raster_types.append([miChannel[i], raster_type])
			texture_samplers.append(raster_type)
		
		raster_types.sort(key=lambda x:x[0])
		
		raster_types_dict = {}
		for raster_type_data in raster_types:
			raster_types_dict[raster_type_data[0]] = raster_type_data[1]
		
		# VertexDescriptor
		f.seek(resources_pointer, 0)
		mVertexDescriptorId = bytes_to_id(f.read(0x4))
		
		#shared_dir = os.path.join(NFSHPLibraryGet(), "NFSHPR_Library_PC")
		#shared_vertex_descriptor_dir = os.path.join(shared_dir, "VertexDescriptor")
		#vertex_descriptor_path = os.path.join(shared_vertex_descriptor_dir, mVertexDescriptorId + ".dat")
		#vertex_properties = read_vertex_descriptor(vertex_descriptor_path)
	
	return (shader_description, mVertexDescriptorId, miNumSamplers, raster_types_dict, shader_parameters, material_constants, texture_samplers)


def read_zonelist(zonelist_path): #ok
	zones = []
	with open(zonelist_path, "rb") as f:
		mpPoints = struct.unpack("<Q", f.read(0x8))[0]
		mpZones = struct.unpack("<Q", f.read(0x8))[0]
		mpuZonePointStarts = struct.unpack("<Q", f.read(0x8))[0]
		mpiZonePointCounts = struct.unpack("<Q", f.read(0x8))[0]
		muTotalZones = struct.unpack("<I", f.read(0x4))[0]
		muTotalPoints = struct.unpack("<I", f.read(0x4))[0]
		const_0x18 = struct.unpack("<B", f.read(0x1))[0]
		
		points = []
		f.seek(mpPoints, 0)
		for i in range(0, muTotalPoints):
			points.append(list(struct.unpack("<2f", f.read(0x8))))
			padding = struct.unpack("<2I", f.read(0x8))
		
		f.seek(mpZones, 0)
		for i in range(0, muTotalZones):
			f.seek(mpZones + 0x28*i, 0)
			mpPoints = struct.unpack("<Q", f.read(0x8))[0]
			null_0x8 = struct.unpack("<I", f.read(0x4))[0]
			null_0xC = struct.unpack("<I", f.read(0x4))[0]
			
			mpNeighbours = struct.unpack("<Q", f.read(0x8))[0]		# mpSafeNeighbours or mpUnsafeNeighbours?
			muZoneId = struct.unpack("<H", f.read(0x2))[0]
			null_0x1A = struct.unpack("<H", f.read(0x2))[0]
			muDistrictId = struct.unpack("<I", f.read(0x4))[0]
			
			miZoneType = struct.unpack("<H", f.read(0x2))[0]		# 1 or 0
			miNumPoints = struct.unpack("<H", f.read(0x2))[0]
			miNumSafeNeighbours = struct.unpack("<H", f.read(0x2))[0]
			miNumNeighbours = struct.unpack("<H", f.read(0x2))[0]	# 	miNumUnsafeNeighbours?
			
			
			#mpNeighbours
			mauNeighbourId = []
			mauNeighbourFlags = []
			f.seek(mpNeighbours, 0)
			for j in range(0, miNumNeighbours):
				f.seek(mpNeighbours + 0x10*j, 0)
				mpZone = struct.unpack("<Q", f.read(0x8))[0]
				muNeighbourFlags = struct.unpack("<I", f.read(0x4))[0]	#1 or 3
				if muNeighbourFlags != 1 and muNeighbourFlags != 3:
					print("DEBUG INFO: muNeighbourFlags is different from 1 and 3.")
				f.seek(mpZone + 0x18, 0)
				muNeighbourId = struct.unpack("<H", f.read(0x2))[0]
				mauNeighbourId.append(muNeighbourId)
				mauNeighbourFlags.append(get_neighbour_flags(muNeighbourFlags))
			
			#mpPoints
			f.seek(mpPoints, 0)
			zonepoints = []
			for j in range(miNumPoints):
				zonepoints.append(list(struct.unpack("<2f", f.read(0x8))))
				padding = struct.unpack("<2I", f.read(0x8))
			
			muArenaId = 0
			zones.append([muZoneId, [mauNeighbourId, mauNeighbourFlags, muDistrictId, miZoneType, muArenaId, miNumSafeNeighbours], zonepoints[:]])
	
	return zones


def read_resources_table(resource_entries_path):
	models = []
	renderables = []
	materials  = []
	textures = []
	
	len_resource_entries_data = os.path.getsize(resource_entries_path)
	
	with open(resource_entries_path, "rb") as f:
		macMagicNumber = str(f.read(0x4), 'ascii')
		
		data_type = ["I", 0x4]
		numDataOffsets = 4
		
		muVersion = struct.unpack("<%s" % data_type[0], f.read(data_type[1]))[0]
		muPlatform = struct.unpack("<%s" % data_type[0], f.read(data_type[1]))[0]
		muDebugDataOffset = struct.unpack("<I", f.read(0x4))[0]
		muResourceEntriesCount = struct.unpack("<I", f.read(0x4))[0]
		muResourceEntriesOffset = struct.unpack("<I", f.read(0x4))[0]
		mauResourceDataOffset = struct.unpack("<%dI" % numDataOffsets, f.read(numDataOffsets*0x4))
		muFlags = struct.unpack("<I", f.read(0x4))[0]
		pad1 = struct.unpack("<I", f.read(0x4))[0]
		
		muResourceEntriesCount_verification = (len_resource_entries_data - muResourceEntriesOffset)//0x50
		if muResourceEntriesCount != muResourceEntriesCount_verification:
			muResourceEntriesCount = muResourceEntriesCount_verification
		
		if muDebugDataOffset < muResourceEntriesOffset:
			notes_data = f.read(muDebugDataOffset - f.tell())
			
			f.seek(muDebugDataOffset, 0)
			debug_data = f.read(muResourceEntriesOffset - muDebugDataOffset)
			len_resource_entries_data = len_resource_entries_data - len(debug_data)
			
			# Removing padding on the end
			k = 0
			for l in range(len(debug_data), 0, -1):
				if debug_data[l-1] != 0:
					break
				k += 1
			k -= 1
			if k > 0:
				debug_data = debug_data[:-k]
			
		else:
			notes_data = f.read(muResourceEntriesOffset - f.tell())
			debug_data = b''
		
		for i in range(0, muResourceEntriesCount):
			f.seek(muResourceEntriesOffset + i*0x50, 0)
			mResourceId = bytes_to_id(f.read(0x4))
			countBlock, null = struct.unpack("<2B", f.read(0x2))	# null always equal to zero
			count, isIdInteger = struct.unpack("<2B", f.read(0x2))	# isIdInteger seems to be related with CRC32 ids or unique IDs; always zero or one
			f.seek(0x3C, 1)
			muResourceTypeId = struct.unpack("<I", f.read(0x4))[0]
			f.seek(0x2, 1)
			unused_muFlags = struct.unpack("<B", f.read(0x1))[0]
			muStreamIndex = struct.unpack("<B", f.read(0x1))[0]
			
			muResourceType, nibbles = get_resourcetype_nibble_hpr(muResourceTypeId)
			
			if muResourceType == "Model":
				models.append(mResourceId)
			elif muResourceType == "Renderable":
				renderables.append(mResourceId)
			elif muResourceType == "Material":
				materials.append(mResourceId)
			elif muResourceType == "Texture":
				textures.append(mResourceId)
	
	return (models, renderables, materials, textures)


def write_instancelist(instancelist_path, instances):	#OK
	os.makedirs(os.path.dirname(instancelist_path), exist_ok = True)
	
	with open(instancelist_path, "wb") as f:
		mpaInstances = 0x20
		muArraySize = len(instances)
		if muArraySize == 0:
			mpaInstances = 0
		muNumInstances = 0
		muVersionNumber = 0x1
		
		instances_properties = []
		instances_properties_backdrop = []
		
		for instance in instances:
			if instance[1][2] == True:
				muNumInstances += 1
				instances_properties.append(instance)
			else:
				instances_properties_backdrop.append(instance)
		instances_properties.sort(key=lambda x:x[0])
		instances_properties_backdrop.sort(key=lambda x:x[0])
		
		instances_properties.extend(instances_properties_backdrop)
		instances = instances_properties[:]
		
		f.write(struct.pack('<Q', mpaInstances))
		f.write(struct.pack('<I', muArraySize))
		f.write(struct.pack('<I', muNumInstances))
		f.write(struct.pack('<I', muVersionNumber))
		
		for i in range(0, muArraySize):
			instance = instances[i]
			object_index, [mModelId, [mTransform], is_instance_always_loaded, mi16BackdropZoneID, unknown_0xC] = instance
			
			mpModel = 0
			mi16BackdropZoneID = instance[1][3]
			mu16Pad = 0
			unknown_0xC = instance[1][4]
			unknown_0x10 = 0
			unknown_0x14 = 0
			unknown_0x18 = 0
			unknown_0x1C = 0
			
			f.seek(mpaInstances + 0x60*i, 0)
			f.write(struct.pack('<q', mpModel))
			f.write(struct.pack('<h', mi16BackdropZoneID))
			f.write(struct.pack('<H', mu16Pad))
			f.write(struct.pack('<I', unknown_0xC))
			
			f.write(struct.pack('<i', unknown_0x10))
			f.write(struct.pack('<i', unknown_0x14))
			f.write(struct.pack('<i', unknown_0x18))
			f.write(struct.pack('<i', unknown_0x1C))
			
			f.write(struct.pack('<4f', *mTransform[0][:-1], 1.0))
			f.write(struct.pack('<4f', *mTransform[1][:-1], 1.0))
			f.write(struct.pack('<4f', *mTransform[2][:-1], 1.0))
			f.write(struct.pack('<4f', *mTransform[3]))
		
		for i in range(0, muArraySize):
			instance = instances[i]
			mModelId = instance[1][0]
			f.seek(mpaInstances + 0x60*muArraySize + 0x10*i, 0)
			f.write(id_to_bytes(mModelId))
			f.write(struct.pack("<i", 0))
			f.write(struct.pack("<i", mpaInstances + 0x60*i))
			f.write(struct.pack("<i", 0))
	
	return 0


def write_dynamicinstancelist(dynamicinstancelist_path): #OK
	os.makedirs(os.path.dirname(dynamicinstancelist_path), exist_ok = True)
	
	with open(dynamicinstancelist_path, "wb") as f:
		f.write(struct.pack("<Q", 1))
		f.write(struct.pack("<Q", 0x20))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<Q", 0))
	
	return 0


def write_lightinstancelist(lightinstancelist_path): #OK
	os.makedirs(os.path.dirname(lightinstancelist_path), exist_ok = True)
	
	with open(lightinstancelist_path, "wb") as f:
		f.write(struct.pack("<Q", 1))
		f.write(struct.pack("<Q", 0x20))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<Q", 0))
	
	return 0


def write_groundcovercollection(groundcovercollection_path): #OK
	os.makedirs(os.path.dirname(groundcovercollection_path), exist_ok = True)
	
	with open(groundcovercollection_path, "wb") as f:
		f.write(struct.pack("<Q", 3))
		f.write(struct.pack("<Q", 0x60))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<Q", 0x60))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<Q", 0x60))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<I", 3))
		f.write(struct.pack("<I", 0x60))
		f.write(struct.pack("<Q", 0x60))
		f.write(struct.pack("<Q", 0))
		f.write(struct.pack("<Q", 0x60))
		f.write(struct.pack("<Q", 0))
	
	return 0


def write_zoneheader(zoneheader_path, mInstanceListId, mDynamicInstanceListId, mLightInstanceListId, mGroundcoverCollectionId): #OK
	os.makedirs(os.path.dirname(zoneheader_path), exist_ok = True)
	
	with open(zoneheader_path, "wb") as f:
		f.write(struct.pack("<i", 7))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		f.write(struct.pack("<i", 0x60))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		f.write(struct.pack("<i", 0))
		
		# IDs
		f.write(id_to_bytes(mInstanceListId))
		f.write(struct.pack("<i", 0))
		f.write(b'\x08\x00\x00\x80')
		f.write(struct.pack("<i", 0))
		f.write(id_to_bytes(mDynamicInstanceListId))
		f.write(struct.pack("<i", 0))
		f.write(b'\x18\x00\x00\x80')
		f.write(struct.pack("<i", 0))
		f.write(id_to_bytes(mLightInstanceListId))
		f.write(struct.pack("<i", 0))
		f.write(b'\x28\x00\x00\x80')
		f.write(struct.pack("<i", 0))
		f.write(id_to_bytes(mGroundcoverCollectionId))
		f.write(struct.pack("<i", 0))
		f.write(b'\x38\x00\x00\x80')
		f.write(struct.pack("<i", 0))
	
	return 0


def write_characterspec(characterspec_path, mSkeletonId, mAnimationListId, instances): #OK
	os.makedirs(os.path.dirname(characterspec_path), exist_ok = True)
	
	with open(characterspec_path, "wb") as f:
		muNumInstances = len(instances)
		muImportCount = len(instances) + 1 + 1
		mppModels = 0x20
		muOffsets = [mppModels + 0x8*x for x in range(muNumInstances)]
		padding = calculate_padding(muOffsets[-1] + 0x8, 0x10)
		size = muOffsets[-1] + 0x8
		
		# Writing
		f.write(struct.pack('<Q', mppModels))
		f.write(struct.pack('<Q', 0))
		f.write(struct.pack('<Q', 0))
		f.write(struct.pack('<I', muNumInstances))
		f.write(struct.pack('<H', muImportCount))
		f.write(struct.pack('<H', size))
		
		for muOffset in muOffsets:
			f.seek(muOffset, 0)
			f.write(struct.pack('<Q', 0))
		f.write(bytearray([0])*padding)
		
		f.write(id_to_bytes(mSkeletonId))
		f.write(struct.pack('<H', 0))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 1))
		f.write(struct.pack('<I', 0x8))
		f.write(struct.pack('<i', 0))
		
		f.write(id_to_bytes(mAnimationListId))
		f.write(struct.pack('<H', 0))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 1))
		f.write(struct.pack('<I', 0x10))
		f.write(struct.pack('<i', 0))
		
		for instance, muOffset in zip(instances, muOffsets):
			f.write(id_to_bytes(instance[1][0]))
			f.write(struct.pack('<H', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<I', muOffset))
			f.write(struct.pack('<i', 0))
		
	return 0


def write_model(model_path, model, resource_type):	#OK
	os.makedirs(os.path.dirname(model_path), exist_ok = True)
	
	with open(model_path, "wb") as f:
		renderables_info = model[1][0]
		model_properties = model[1][1]
		
		minLodDistance = 200
		maxLodDistance = 1500
		mpTintData = 0
		mu8NumRenderables = model_properties[0]
		mu8Flags = 0
		mu8NumStates = model_properties[1]
		TintData = model_properties[2]
		unknown_0x25 = model_properties[3]
		unknown_0x26 = 0
		unknown_0x27 = 0
		lod_distances = model_properties[4]
		model_states = model_properties[5]
		resource_type_child = model_properties[6]
		mu8VersionNumber = 3
		
		if model_states == []:
			if resource_type_child == "InstanceList":
				mu8NumStates = 7
			elif mu8NumRenderables == 1:
				mu8NumStates = 5
			else:
				mu8NumStates = 5
		
		if len(lod_distances) > 0:
			muNumLodDistances = len(lod_distances)
		else:
			muNumLodDistances = mu8NumStates
			if resource_type_child == "InstanceList":
				lod_distances = [300, 600, 900, 1200, 1500, 1800, 2100]
			else:
				lod_distances = [200, 400, 600, 800, 1000]
			if muNumLodDistances == 1:
				lod_distances = lod_distances[-1:]
		
		if mu8NumStates < mu8NumRenderables and model_states == []:
			mu8NumStates = mu8NumRenderables + 2
			# Not updating the muNumLodDistances, it can be lower
		
		renderable_indices = [0]*mu8NumStates
		if model_states == []:
			for i in range(0, mu8NumRenderables):
				renderable_indices[-1-i] = (mu8NumRenderables-1) - i
			
			if resource_type_child == "WheelGraphicsSpec" and mu8NumRenderables == 2:
				renderable_indices = [1]*mu8NumStates
				renderable_indices[0] = 0
			#elif resource_type_child == "GraphicsSpec":
			#	renderable_indices = [0]*mu8NumStates
		elif model_states != []:
			renderable_indices = list(model_states[:])
			for i, x in enumerate(renderable_indices):
				if x == -1 or x == 255:
					renderable_indices[i] = 255
				elif x >= mu8NumRenderables:
					renderable_indices[i] = mu8NumRenderables - 1
		
		mpu8StateRenderableIndices = 0x28
		mpfLodDistances = mpu8StateRenderableIndices + 0x1*mu8NumStates
		mpfLodDistances += calculate_padding(mpfLodDistances, 0x4)
		mppRenderables = mpfLodDistances + 0x4*muNumLodDistances
		mppRenderables += calculate_padding(mppRenderables, 0x8)
		padding = calculate_padding(mppRenderables + 0x8*mu8NumRenderables, 0x10)
		
		tint_data_size = 0
		muTintOffsets = []
		mTintResourceIds = []
		mBTintUnknowns = []
		
		if TintData != []:
			mpTintData = mppRenderables + 0x8*mu8NumRenderables + padding
		
		if mpTintData != 0:
			parameters_names, parameters_data, samplers_names, sampler_states, textures = TintData
			#f.seek(mpTintData, 0)
			unknown_0x0 = 1
			num_parameters = len(parameters_names)
			num_samplers = len(samplers_names)
			unknown_0x3 = 0
			offset_0 = 0
			offset_0_1 = []
			offset_1 = 0
			offset_2 = 0
			offset_3 = 0
			offset_3_1 = []
			offset_4 = 0
			mpaSamplersStates = 0
			mpaTextures = 0
			offset_end = mpTintData + 0x40
			
			if num_samplers != 0:
				offset_4 = offset_end
				mpaSamplersStates = offset_4 + num_samplers*0x1 + calculate_padding(offset_4 + num_samplers*0x1, 0x8)
				mpaTextures = mpaSamplersStates + num_samplers*0x8
				offset_3 = mpaTextures + num_samplers*0x8
				
				offset = offset_3 + num_samplers*0x8
				offset_3_1 = []
				for sampler_name in samplers_names:
					offset_3_1.append(offset)
					offset += len(sampler_name) + 1
				
				offset_end = offset
				
				muOffsets_samplers = []
				muOffsets_textures = []
				mResourceIds_samplers = []
				mResourceIds_textures = []
				mBUnknowns_samplers = []
				mBUnknowns_textures = []
				
				for j in range(0, num_samplers):
					mSamplerStateId = sampler_states[j]
					mTextureId = textures[j]
					
					muOffsets_samplers.append(mpaSamplersStates + 0x8*j)
					muOffsets_textures.append(mpaTextures + 0x8*j)
					mResourceIds_samplers.append(mSamplerStateId)
					mResourceIds_textures.append(mTextureId)
					mBUnknowns_samplers.append(0)
					mBUnknowns_textures.append(0)
				
				muTintOffsets.extend(muOffsets_samplers)
				muTintOffsets.extend(muOffsets_textures)
				mTintResourceIds.extend(mResourceIds_samplers)
				mTintResourceIds.extend(mResourceIds_textures)
				mBTintUnknowns.extend(mBUnknowns_samplers)
				mBTintUnknowns.extend(mBUnknowns_textures)
			
			if num_parameters != 0:
				offset_1 = offset_end
				offset_2 = offset_1 + num_parameters + calculate_padding(offset_1 + num_parameters, 0x10)
				offset_0 = offset_2 + num_parameters*0x10
				
				offset = offset_0 + num_parameters*0x8
				offset_0_1 = []
				for parameters_name in parameters_names:
					offset_0_1.append(offset)
					offset += len(parameters_name) + 1
					offset += calculate_padding(offset, 0x4)
				
				offset_end = offset
			
			tint_data_size += offset_end - mpTintData
			padding = calculate_padding(tint_data_size, 0x10)
		
		mppRenderables_ = [0]*mu8NumRenderables
		
		mResourceIds = [None]*mu8NumRenderables
		for renderable_info in renderables_info:
			mResourceId = renderable_info[0]
			renderable_index = renderable_info[1][0]
			mResourceIds[renderable_index] = mResourceId
		
		muOffsets = [mppRenderables + 0x8*x for x in range(mu8NumRenderables)]
		
		# Writing
		f.write(struct.pack('<q', mppRenderables))
		f.write(struct.pack('<q', mpu8StateRenderableIndices))
		f.write(struct.pack('<q', mpfLodDistances))
		f.write(struct.pack('<q', mpTintData))
		f.write(struct.pack('<B', mu8NumRenderables))
		f.write(struct.pack('<B', mu8Flags))
		f.write(struct.pack('<B', mu8NumStates))
		f.write(struct.pack('<B', mu8VersionNumber))
		f.write(struct.pack('<B', muNumLodDistances))
		f.write(struct.pack('<B', unknown_0x25))
		f.write(struct.pack('<B', unknown_0x26))
		f.write(struct.pack('<B', unknown_0x27))
		
		f.seek(mpu8StateRenderableIndices, 0)
		f.write(struct.pack('<%dB' % mu8NumStates, *renderable_indices))
		
		f.seek(mpfLodDistances, 0)
		f.write(struct.pack('<%df' % muNumLodDistances, *lod_distances))
		
		f.seek(mppRenderables, 0)
		f.write(struct.pack('<%dq' % mu8NumRenderables, *mppRenderables_))
		
		if mpTintData != 0:
			f.seek(mpTintData, 0)
			f.write(struct.pack('<B', unknown_0x0))
			f.write(struct.pack('<B', num_parameters))
			f.write(struct.pack('<B', num_samplers))
			f.write(struct.pack('<B', unknown_0x3))
			f.write(struct.pack('<i', 0))
			f.write(struct.pack('<Q', offset_0))
			f.write(struct.pack('<Q', offset_1))
			f.write(struct.pack('<Q', offset_2))
			f.write(struct.pack('<Q', offset_3))
			f.write(struct.pack('<Q', offset_4))
			f.write(struct.pack('<Q', mpaSamplersStates))
			f.write(struct.pack('<Q', mpaTextures))
			
			f.seek(offset_0, 0)
			f.write(struct.pack('<%dQ' % num_parameters, *offset_0_1))
			for j, parameters_name in enumerate(parameters_names):
				f.seek(offset_0_1[j], 0)
				f.write(parameters_name.encode('utf-8'))
			
			f.seek(offset_1, 0)
			f.write(struct.pack('<%db' % num_parameters, *[-1]*num_parameters))
			
			f.seek(offset_2, 0)
			for parameter_data in parameters_data:
				f.write(struct.pack('<4f', *parameter_data))
			
			f.seek(offset_3, 0)
			f.write(struct.pack('<%dQ' % num_samplers, *offset_3_1))
			for j, sampler_name in enumerate(samplers_names):
				f.seek(offset_3_1[j], 0)
				f.write(sampler_name.encode('utf-8'))
			
			f.seek(offset_4, 0)
			f.write(struct.pack('<%db' % num_samplers, *[-1]*num_samplers))
			
			#tint_data_size += calculate_padding(tint_data_size, 0x10)
		
			f.seek(mpTintData + tint_data_size, 0)
		
		f.write(bytearray([0])*padding)
		
		for mResourceId, muOffset in zip(mResourceIds, muOffsets):
			f.write(id_to_bytes(mResourceId))
			f.write(struct.pack('<i', 0))
			f.write(struct.pack('<I', muOffset))
			f.write(struct.pack('<i', 0))
		
		for mResourceId, muOffset, mBUnknown in zip(mTintResourceIds, muTintOffsets, mBTintUnknowns):
			f.write(id_to_bytes(mResourceId))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', mBUnknown))
			f.write(struct.pack('<I', muOffset))
			f.write(struct.pack('<i', 0))
	
	return 0


def write_renderable(renderable_path, renderable, resource_type, shared_dir): #OK
	shared_vertex_descriptor_dir = os.path.join(os.path.join(shared_dir, "SHADERS"), "VertexDescriptor")
	
	os.makedirs(os.path.dirname(renderable_path), exist_ok = True)
	
	renderable_body_path = renderable_path[:-4] + "_model" + renderable_path[-4:]
	
	with open(renderable_path, "wb") as f, open(renderable_body_path, "wb") as g:
		mRenderableId = renderable[0]
		meshes_info = renderable[1][0]
		renderable_properties = renderable[1][1]
		indices_buffer = renderable[1][2]
		vertices_buffer = renderable[1][3]
		
		object_center = renderable_properties[0]
		object_radius = renderable_properties[1]
		submeshes_bounding_box = renderable_properties[2]
		mu16VersionNumber = 0xC
		num_meshes = renderable_properties[3]
		meshes_table_pointer = 0x30
		flags0 = 0
		flags1 = -1
		padding = 0
		
		meshes_data_pointer = meshes_table_pointer + 0x8*num_meshes
		meshes_data_pointer += calculate_padding(meshes_data_pointer, 0x10)
		
		mesh_header_size = 0xA0
		meshes_data_pointers = [meshes_data_pointer + mesh_header_size*x for x in range(num_meshes)]
		
		primitive_topology = 5
		constant_0x14 = 0
		constant_0x18 = 0
		null_0x20 = 0
		null_0x24 = 0
		mu8Flags = 0
		mu8NumVertexBuffers = 1
		mu8InstanceCount = 0
		mu8NumVertexDescriptors = 0
		null_0x2C = 0
		
		constant_0x40 = 0
		constant_0x48 = 0
		
		buffer_interface = 0
		buffer_usage = 0
		buffer_type_indices = 3
		#indices_size = 2
		buffer_type_vertices = 2
		vertices_unk1 = 0
		vertices_unk2 = 0
		
		for i in range(0, num_meshes):
			coordinate_factor = 0x4000
			max_value = abs(max(submeshes_bounding_box[i][0], key=abs))
			test = round(max_value*coordinate_factor)
			count = 0
			while test > 0x7FFF:
				count += 1
				coordinate_factor /= 2
				test = round(max_value*coordinate_factor)
			
			for j, coordinate in enumerate(submeshes_bounding_box[i][0]):
				submeshes_bounding_box[i][0][j] = round(coordinate*coordinate_factor)
			coordinate_factor = int(0x4000 + 0x80*count)
			
			scale_factor = 0x80
			max_value = max(submeshes_bounding_box[i][1])
			test = round(max_value*scale_factor)
			count = 0
			while test > 0xFF:
				count += 1
				scale_factor /= 2
				test = round(max_value*scale_factor)
			
			for j, scale in enumerate(submeshes_bounding_box[i][1]):
				submeshes_bounding_box[i][1][j] = round(scale*scale_factor)
			scale_factor = int(0x80 + count)
			
			quaternion_factor = 0x7E
			for j, quaternion in enumerate(submeshes_bounding_box[i][2]):
				submeshes_bounding_box[i][2][j] = round(quaternion*quaternion_factor)
			
			submeshes_bounding_box[i].append([coordinate_factor, scale_factor, quaternion_factor])
		
		
		mMaterialIds = [0]*num_meshes
		pointers_1 = [0]*num_meshes
		pointers_2 = [0]*num_meshes
		indices_size = [2]*num_meshes
		indices_buffer_offset = [0]*num_meshes
		indices_buffer_counts = [0]*num_meshes
		indices_buffer_sizes = [0]*num_meshes
		vertices_buffer_offset = [0]*num_meshes
		vertices_buffer_sizes = [0]*num_meshes
		vertices_properties = [[] for _ in range(num_meshes)]
		for mesh_info in meshes_info:
			mesh_index = mesh_info[0]
			mMaterialId = mesh_info[1]
			mVertexDescriptorId = mesh_info[2]
			
			vertex_descriptor_path = os.path.join(shared_vertex_descriptor_dir, mVertexDescriptorId + ".dat")
			vertex_properties = read_vertex_descriptor(vertex_descriptor_path)
			vertex_size = vertex_properties[0]
			vertices_properties[mesh_index] = vertex_properties[:]
			
			pointers_1[mesh_index] = meshes_data_pointers[mesh_index] + 0x50
			pointers_2[mesh_index] = pointers_1[mesh_index] + 0x20
			
			if mesh_index == 0:
				indices_buffer_offset[mesh_index] = 0
			else:
				indices_buffer_offset[mesh_index] = vertices_buffer_offset[mesh_index - 1] + vertices_buffer_sizes[mesh_index - 1]
				indices_buffer_offset[mesh_index] += calculate_padding(indices_buffer_offset[mesh_index], 0x10)
			
			indices_buffer_counts[mesh_index] = len(indices_buffer[mesh_index])
			if len(vertices_buffer[mesh_index]) >= 0xFFFF:
				indices_size[mesh_index] = 4
			else:
				indices_size[mesh_index] = 2
			indices_buffer_sizes[mesh_index] = indices_buffer_counts[mesh_index] * indices_size[mesh_index]
			
			
			vertices_buffer_offset[mesh_index] = indices_buffer_offset[mesh_index] + indices_buffer_sizes[mesh_index]
			vertices_buffer_offset[mesh_index] += calculate_padding(vertices_buffer_offset[mesh_index], 0x10)
			vertices_buffer_sizes[mesh_index] = len(vertices_buffer[mesh_index][0]) * vertex_size
			
			mMaterialIds[mesh_index] = mMaterialId
		
		muOffsets_material = [x + 0x20 for x in meshes_data_pointers]
		
		
		# Writing header
		f.write(struct.pack('<fff', *object_center))
		f.write(struct.pack('<f', object_radius))
		f.write(struct.pack('<H', mu16VersionNumber))
		f.write(struct.pack('<H', num_meshes))
		f.write(struct.pack('<i', 0))
		f.write(struct.pack('<q', meshes_table_pointer))
		f.write(struct.pack('<b', flags0))
		f.write(struct.pack('<b', flags1)) #not always -1
		f.write(struct.pack('<H', padding))
		f.write(struct.pack('<i', padding))
		
		f.seek(meshes_table_pointer, 0)
		f.write(struct.pack('<%dq' % num_meshes, *meshes_data_pointers))
		
		for i in range(0, num_meshes):
			f.seek(meshes_data_pointers[i], 0)
			
			f.write(struct.pack('<h', submeshes_bounding_box[i][0][0]))		#ok, XZY (021)
			f.write(struct.pack('<H', submeshes_bounding_box[i][3][0]))
			f.write(struct.pack('<h', submeshes_bounding_box[i][0][2]))
			f.write(struct.pack('<h', submeshes_bounding_box[i][0][1]))
			
			# Scale
			#f.write(struct.pack('<B', submeshes_bounding_box[i][1][1]))	#nok, ZYX (210)
			#f.write(struct.pack('<B', submeshes_bounding_box[i][1][2]))
			#f.write(struct.pack('<B', submeshes_bounding_box[i][1][0]))
			f.write(struct.pack('<B', submeshes_bounding_box[i][1][2]))		#ok, ZYX (210)
			f.write(struct.pack('<B', submeshes_bounding_box[i][1][1]))
			f.write(struct.pack('<B', submeshes_bounding_box[i][1][0]))
			
			
			f.write(struct.pack('<B', submeshes_bounding_box[i][3][1]))
			
			#f.write(struct.pack('<bbbb', *submeshes_bounding_box[i][2]))	#nok, WZXy (0312), WZYx (0321)
			f.write(struct.pack('<b', submeshes_bounding_box[i][2][0]))
			f.write(struct.pack('<b', submeshes_bounding_box[i][2][3]))
			f.write(struct.pack('<b', submeshes_bounding_box[i][2][2]))
			f.write(struct.pack('<b', submeshes_bounding_box[i][2][1]))
			
			f.write(struct.pack('<i', primitive_topology))
			f.write(struct.pack('<i', constant_0x14))
			f.write(struct.pack('<i', constant_0x18))
			f.write(struct.pack('<i', indices_buffer_counts[i]))
			f.write(struct.pack('<i', null_0x20))
			f.write(struct.pack('<i', null_0x24))
			
			f.write(struct.pack('<B', mu8Flags))
			f.write(struct.pack('<B', mu8NumVertexBuffers))
			f.write(struct.pack('<B', mu8InstanceCount))
			f.write(struct.pack('<B', mu8NumVertexDescriptors))
			f.write(struct.pack('<i', null_0x2C))
			
			f.write(struct.pack('<q', pointers_1[i]))
			f.write(struct.pack('<q', pointers_2[i]))
			f.write(struct.pack('<q', constant_0x40))
			f.write(struct.pack('<q', constant_0x48))
			
			f.write(struct.pack('<q', buffer_interface))
			f.write(struct.pack('<i', buffer_usage))
			f.write(struct.pack('<i', buffer_type_indices))
			f.write(struct.pack('<q', indices_buffer_offset[i]))
			f.write(struct.pack('<i', indices_buffer_sizes[i]))
			f.write(struct.pack('<i', indices_size[i]))
			
			f.write(struct.pack('<q', buffer_interface))
			f.write(struct.pack('<i', buffer_usage))
			f.write(struct.pack('<i', buffer_type_vertices))
			f.write(struct.pack('<q', vertices_buffer_offset[i]))
			f.write(struct.pack('<i', vertices_buffer_sizes[i]))
			f.write(struct.pack('<i', vertices_unk1))
			f.write(struct.pack('<i', vertices_unk2))
		
		f.seek(meshes_data_pointers[-1] + mesh_header_size, 0)
		for i in range(0, num_meshes):
			f.write(id_to_bytes(mMaterialIds[i]))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<I', muOffsets_material[i]))
			f.write(struct.pack('<i', 0))
		
		# Writing body
		for mesh_index in range(0, num_meshes):
			mesh_index_error = -1
			g.seek(indices_buffer_offset[mesh_index], 0)
			if indices_size[mesh_index] == 2:
				g.write(struct.pack('<%sH' % indices_buffer_counts[mesh_index], *indices_buffer[mesh_index]))
			elif indices_size[mesh_index] == 4:
				g.write(struct.pack('<%sI' % indices_buffer_counts[mesh_index], *indices_buffer[mesh_index]))
			
			padding = calculate_padding(indices_buffer_sizes[mesh_index], 0x10)
			if padding == 0:
				padding = 0x10
			padding_buffer = padding // 2
			g.write(struct.pack("<%sH" % (padding_buffer), *[0]*(padding_buffer)))
			
			g.seek(vertices_buffer_offset[mesh_index], 0)
			
			vertex_size = vertices_properties[mesh_index][0]
			semantic_properties = vertices_properties[mesh_index][1][0]
			
			mesh_vertices_buffer, mesh_indices = vertices_buffer[mesh_index]
			for index in sorted(mesh_indices):
				index_, position, normal, tangent, color, uv1, uv2, uv3, uv4, uv5, uv6, blend_indices, blend_weight, binormal, color2 = mesh_vertices_buffer[index]
				
				for semantic in semantic_properties:
					g.seek(vertices_buffer_offset[mesh_index] + index * vertex_size, 0)
					
					semantic_type = semantic[0]
					data_type = semantic[1]
					data_offset = semantic[2]
					g.seek(data_offset, 1)
					
					if semantic_type == "POSITION":
						values = position
					elif semantic_type == "POSITIONT":
						print("Skipping POSITIONT")
						pass
					elif semantic_type == "NORMAL":
						values = normal
					elif semantic_type == "COLOR":
						values = color
					elif semantic_type == "TEXCOORD1":
						values = [uv1[0], 1.0 - uv1[1]]
					elif semantic_type == "TEXCOORD2":
						values = [uv2[0], 1.0 - uv2[1]]
					elif semantic_type == "TEXCOORD3":
						values = [uv3[0], 1.0 - uv3[1]]
					elif semantic_type == "TEXCOORD4":
						values = [uv4[0], 1.0 - uv4[1]]
					elif semantic_type == "TEXCOORD5":		#custom normal
						if data_type[0] == "2e":
							values = [uv5[0], 1.0 - uv5[1]]
						else:
							values = normal
					elif semantic_type == "TEXCOORD6":
						if data_type[0] == "2e":
							values = [uv6[0], 1.0 - uv6[1]]
						else:
							values = normal
					elif semantic_type == "TEXCOORD7":
						print("Skipping TEXCOORD7")
						pass
					elif semantic_type == "TEXCOORD8":
						print("Skipping TEXCOORD8")
						pass
					elif semantic_type == "BLENDINDICES":
						values = blend_indices
						#values = [0, 0, 0, 0]
					elif semantic_type == "BLENDWEIGHT":
						values = blend_weight
						#values = [0xFF, 0, 0, 0]
					elif semantic_type == "TANGENT":
						values = tangent
					elif semantic_type == "BINORMAL":
						values = binormal
					elif semantic_type == "COLOR2":
						print("Skipping COLOR2")
						pass
					elif semantic_type == "PSIZE":
						print("Skipping PSIZE")
						pass
					
					if data_type[0][-1] == "e":
						try:
							g.write(struct.pack("<%s" % data_type[0], *values))
						except:
							g.write(struct.pack("<%s" % data_type[0], *[0]*int(data_type[0][0])))
					elif "norm" in data_type[0]:
						data_type = data_type[0].replace("norm", "")
						if semantic_type == "TEXCOORD5" or semantic_type == "TEXCOORD6":	#NORMAL_PACKED and NORMAL_PACKED for wheels
							quat = normal_to_quaternion(values)
							x, y, z, w = quaternion_to_short(quat)
						else:
							scale = 8.0
							w = 32767.0
							x = round(values[0]/scale*w)
							y = round(values[1]/scale*w)
							z = round(values[2]/scale*w)
							w = round(32767.0)
						g.write(struct.pack("<%s" % data_type, x, y, z, w))
					else:
						try:
							g.write(struct.pack("<%s" % data_type[0], *values[:int(data_type[0][0])]))
						except:
							if mesh_index_error != mesh_index:
								print("WARNING: unknown vertex type found on %s mesh index %i. It is a type %s with data type %s with length %s. Writing a null data." % (mRenderableId, mesh_index, semantic_type, data_type[0], str(hex(data_type[1]))))
								mesh_index_error = mesh_index
							g.write(struct.pack("<%s" % data_type[0], *[0]*int(data_type[0][0])))
		
		#g.seek(vertices_buffer_offset[-1] + vertices_buffer_sizes[-1], 0)
		padding = calculate_padding(vertices_buffer_offset[-1] + vertices_buffer_sizes[-1], 0x80)
		g.write(bytearray([0])*padding)
	
	return 0


def write_material(material_path, material): #OK
	os.makedirs(os.path.dirname(material_path), exist_ok = True)
	
	with open(material_path, "wb") as f:
		#[mMaterialId, [mShaderId, textures_info, sampler_states_info, material_parameters, sampler_properties, texture_samplers], is_shared_asset] = material
		mMaterialId = material[0]
		mShaderId = material[1][0]
		textures_info = material[1][1]
		sampler_states_info = material[1][2]
		material_parameters = material[1][3]
		sampler_properties = material[1][4]
		texture_samplers = material[1][5]
		
		parameters_Indices, parameters_Ones, parameters_NamesHash, parameters_Data, parameters_Names = material_parameters
		material_constants, miChannel, raster_type_offsets = sampler_properties
		
		num_parameters = len(parameters_Indices)
		num_parameters_withdata = len(parameters_Data)
		miNumSamplers = len(textures_info)
		
		mMaterialId = material[0]
		unk_0x4 = 0
		const_0x5 = 4
		null = 0
		parameters_indices_pointer = 0x58
		parameters_ones_pointer = parameters_indices_pointer + num_parameters
		_ = parameters_ones_pointer + num_parameters
		padding0 = calculate_padding(_, 0x4)
		parameters_nameshash_pointer = _ + padding0
		_ = parameters_nameshash_pointer + 0x4*num_parameters
		padding1 = calculate_padding(_, 0x10)
		parameters_data_pointer = _ + padding1
		mpaMaterialConstants = parameters_data_pointer + 0x10*num_parameters_withdata
		_ = mpaMaterialConstants + 0x2*miNumSamplers
		padding2 = calculate_padding(_, 0x8)
		mpaSamplers = _ + padding2
		mpaSamplersChannel = mpaSamplers + 0x8*miNumSamplers
		#_ = mpaSamplers + 0x4*num_parameters + 0x4*miNumSamplers
		_ = mpaSamplersChannel + 0x8*miNumSamplers
		padding3 = calculate_padding(_, 0x10)
		resources_pointer = _ + padding3
		
		# Writing header
		f.write(id_to_bytes(mMaterialId))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', const_0x5))
		f.write(struct.pack('<H', resources_pointer))
		f.write(struct.pack('<Q', null))
		if num_parameters > 0:
			f.write(struct.pack('<Q', parameters_indices_pointer))
			f.write(struct.pack('<Q', parameters_ones_pointer))
			f.write(struct.pack('<Q', parameters_nameshash_pointer))
			f.write(struct.pack('<Q', parameters_data_pointer))
		else:
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
		f.write(struct.pack('<B', num_parameters))
		f.write(struct.pack('<B', num_parameters_withdata))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<I', null))
		f.write(struct.pack('<B', miNumSamplers))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<I', null))
		if miNumSamplers > 0:
			f.write(struct.pack('<Q', mpaMaterialConstants))
			f.write(struct.pack('<Q', mpaSamplersChannel))
			f.write(struct.pack('<Q', mpaSamplers))
		else:
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
		
		if num_parameters > 0:
			f.seek(parameters_indices_pointer, 0)
			for i in range(0, num_parameters):
				f.write(struct.pack('<b', parameters_Indices[i]))
			f.seek(parameters_ones_pointer, 0)
			for i in range(0, num_parameters):
				f.write(struct.pack('<b', parameters_Ones[i]))
			f.seek(parameters_nameshash_pointer, 0)
			for i in range(0, num_parameters):
				f.write(struct.pack('<I', parameters_NamesHash[i]))
			f.seek(parameters_data_pointer, 0)
			for i in range(0, num_parameters):
				if parameters_Indices[i] != -1:
					f.seek(parameters_data_pointer + 0x10*parameters_Indices[i], 0)
					f.write(struct.pack('<4f', *parameters_Data[i]))
		
		if miNumSamplers > 0:
			f.seek(mpaMaterialConstants, 0)
			for i in range(0, miNumSamplers):
				f.write(struct.pack('<H', material_constants[i]))
			f.seek(mpaSamplersChannel, 0)
			for i in range(0, miNumSamplers):
				f.write(struct.pack('<B', miChannel[i]))
			f.seek(mpaSamplers, 0)
			for i in range(0, miNumSamplers):
				f.write(struct.pack('<Q', raster_type_offsets[i]))
		
		f.seek(resources_pointer, 0)
		# mResourceIds
		f.write(id_to_bytes(mShaderId))
		f.write(struct.pack('<H', 0x53))
		f.write(struct.pack('<B', 0))
		f.write(struct.pack('<B', 1))
		f.write(struct.pack('<I', 0x8))
		f.write(struct.pack('<i', 0))
		
		for i in range(0, miNumSamplers):
			raster_type = texture_samplers[i]
			for texture_info in textures_info:
				if texture_info[2] == raster_type:
					break
					
			f.write(id_to_bytes(texture_info[0]))
			f.write(struct.pack('<H', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<I', mpaSamplers + 0x8*i))
			f.write(struct.pack('<i', 0))
		
		for i in range(0, miNumSamplers):
			f.write(id_to_bytes(sampler_states_info[i]))
			f.write(struct.pack('<H', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<B', 0))
			f.write(struct.pack('<I', mpaSamplers + 0x8*miNumSamplers + 0x8*i))
			f.write(struct.pack('<i', 0))
	
	return 0


def write_raster(raster_path, raster): #OK
	os.makedirs(os.path.dirname(raster_path), exist_ok = True)
	
	raster_body_path = raster_path[:-4] + "_texture" + raster_path[-4:]
	raster_source_path = raster[3]
	
	if raster_source_path == "create_texture":
		raster_source_path = raster_path.replace(".dat", ".dds")
		if raster[0] == "7D_A1_02_A1":
			create_displacementsampler(raster_source_path)
		elif raster[0] == "4F_1F_A7_2D":
			create_blacksampler(raster_source_path)
		elif raster[0] == "A2_70_79_2C":
			create_whitesampler(raster_source_path)
		elif raster[0] == "AA_62_F3_0A":
			create_greysampler(raster_source_path)
		elif raster[0] == "C5_1A_CE_8A":
			create_greyalphasampler(raster_source_path)
		elif raster[0] == "B4_2D_C6_D4":
			create_pinkalphasampler(raster_source_path)
		elif raster[0] == "06_88_13_FF":
			create_normalsampler(raster_source_path)
		elif raster[0] == "A1_39_98_23":
			create_crumplesampler(raster_source_path)
		else:
			create_blacksampler(raster_source_path)
	
	with open(raster_source_path, "rb") as f:
		DDS_MAGIC = struct.unpack("<I", f.read(0x4))[0]
		header_size = struct.unpack("<I", f.read(0x4))[0]
		flags = struct.unpack("<I", f.read(0x4))[0]
		height = struct.unpack("<I", f.read(0x4))[0]
		width = struct.unpack("<I", f.read(0x4))[0]
		pitchOrLinearSize = struct.unpack("<I", f.read(0x4))[0]
		depth = struct.unpack("<I", f.read(0x4))[0]
		mipMapCount = struct.unpack("<I", f.read(0x4))[0]
		reserved1 = struct.unpack("<11I", f.read(0x4*11))
		
		# DDS_PIXELFORMAT
		dwSize = struct.unpack("<I", f.read(0x4))[0]
		dwFlags = struct.unpack("<I", f.read(0x4))[0]
		dwFourCC = f.read(0x4)
		dwRGBBitCount = struct.unpack("<I", f.read(0x4))[0]
		dwRBitMask = struct.unpack("<I", f.read(0x4))[0]
		dwGBitMask = struct.unpack("<I", f.read(0x4))[0]
		dwBBitMask = struct.unpack("<I", f.read(0x4))[0]
		dwABitMask = struct.unpack("<I", f.read(0x4))[0]
		
		caps = struct.unpack("<I", f.read(0x4))[0]
		caps2 = struct.unpack("<I", f.read(0x4))[0]
		caps3 = struct.unpack("<I", f.read(0x4))[0]
		caps4 = struct.unpack("<I", f.read(0x4))[0]
		reserved2 = struct.unpack("<I", f.read(0x4))[0]
		
		if dwFlags < 0x40:
			dwFourCC = dwFourCC.decode()
		else:
			dwFourCC = ''
			RGBA_order = sorted([dwRBitMask, dwGBitMask, dwBBitMask, dwABitMask])
			RGBA_order = [mask for mask in RGBA_order if mask != 0]
			bits = str(dwRGBBitCount // len(RGBA_order))
			for mask in RGBA_order:
				if mask == dwRBitMask:
					dwFourCC += 'R'
				elif mask == dwGBitMask:
					dwFourCC += 'G'
				elif mask == dwBBitMask:
					dwFourCC += 'B'
				elif mask == dwABitMask:
					dwFourCC += 'A'
				dwFourCC += bits
		
		data = f.read()
	
	if depth == 0:
		depth = 1
	
	with open(raster_path, "wb") as f, open(raster_body_path, "wb") as g:
		usage = 0
		dimension = raster[1][0][1]
		format = get_raster_format(dwFourCC)
		#flags = 0x10		# normal is 0x00
		flags = raster[1][0][0]
		array_size = 1
		#main_mipmap = 1
		main_mipmap = raster[1][0][2]
		mipmap = mipMapCount
		padding_texture = calculate_padding(len(data), 0x80)
		
		if dimension == 1:	 # 1D
			dimension = 6
		elif dimension == 2: # 2D
			dimension = 7
		elif dimension == 3: # 3D
			dimension = 8
		elif dimension == 4: # 4D
			dimension = 9
		
		f.write(struct.pack('<q', 0))
		f.write(struct.pack('<i', usage))
		f.write(struct.pack('<i', dimension))
		f.write(struct.pack('<q', 0))
		f.write(struct.pack('<q', 0))
		f.write(struct.pack('<q', 0))
		f.write(struct.pack('<i', 0))
		f.write(struct.pack('<i', format))
		f.write(struct.pack('<I', flags))
		f.write(struct.pack('<HHH', width, height, depth))
		f.write(struct.pack('<H', array_size))
		f.write(struct.pack('<BB', main_mipmap, mipmap))
		f.write(struct.pack('<H', 0))
		
		f.write(struct.pack('<q', 0))
		f.write(struct.pack('<i', 0x80))
		f.write(struct.pack('<I', 0x4))
		f.write(struct.pack('<q', 0))
		f.write(bytearray([0])*8)
		
		g.write(data)
		g.write(bytearray([0])*padding_texture)
	
	return 0


def write_skeleton(skeleton_path, Skeleton): #OK
	os.makedirs(os.path.dirname(skeleton_path), exist_ok = True)
	
	with open(skeleton_path, "wb") as f:
		mppPointer = 0x20
		muCount = len(Skeleton)
		mppPointer2 = mppPointer + 0x20*muCount
		mppPointer3 = mppPointer2
		
		f.write(struct.pack('<Q', mppPointer))
		f.write(struct.pack('<Q', mppPointer2))
		f.write(struct.pack('<Q', mppPointer3))
		f.write(struct.pack('<Q', muCount))
				
		f.seek(mppPointer, 0)
		for i in range(0, muCount):
			sensor_index, location, rotation, parent_sensor, older_sensor, child_sensor, hash = Skeleton[i]
			
			f.seek(mppPointer + 0x20*i, 0)
			f.write(struct.pack('<3f', *location))
			f.write(struct.pack('<I', 0))
			
			f.write(struct.pack('<i', parent_sensor))
			f.write(struct.pack('<i', older_sensor))
			f.write(struct.pack('<i', child_sensor))
			f.write(struct.pack('<i', sensor_index))
		
		f.seek(mppPointer3, 0)
		for i in range(0, muCount):
			hash = Skeleton[i][-1]
			f.write(id_to_bytes(hash))
		
		for i in range(0, muCount):
			f.write(struct.pack('<i', 0))
		
		padding = calculate_padding(mppPointer3 + muCount*0x4*2, 0x10)
		f.write(bytearray([0])*padding)
		
	return 0


def write_controlmesh(controlmesh_path, ControlMeshes): #OK
	os.makedirs(os.path.dirname(controlmesh_path), exist_ok = True)
	
	with open(controlmesh_path, "wb") as f:
		num_bones = len(ControlMeshes)
		
		unknown_0x0 = 0x1
		size = num_bones*3*0x10 + 0x10
		null_0x8 = 0
		null_0xC = 0
		
		f.write(struct.pack('<I', unknown_0x0))
		f.write(struct.pack('<I', size))
		f.write(struct.pack('<I', null_0x8))
		f.write(struct.pack('<I', null_0xC))
		
		f.seek(0x10, 0)
		for i in range(0, num_bones):
			index, cm_coordinates_A, cm_coordinates_B, cm_limit = ControlMeshes[i]
			
			f.seek(0x10 + 0x10*index, 0)
			f.write(struct.pack('<3f', *cm_coordinates_A))
			f.write(struct.pack('<f', 0))
			
			f.seek(0x10 + num_bones*0x10 + 0x10*index, 0)
			f.write(struct.pack('<3f', *cm_coordinates_B))
			f.write(struct.pack('<f', 0))
			
			f.seek(0x10 + num_bones*0x10*2 + 0x10*index, 0)
			f.write(struct.pack('<4f', *[cm_limit]*4))
	
	return 0


def write_polygonsouplist(polygonsouplist_path, PolygonSoups): #OK
	os.makedirs(os.path.dirname(polygonsouplist_path), exist_ok = True)
	
	with open(polygonsouplist_path, "wb") as f:
		scale = 500/0x8000 #0.0152587890625
		miVertexOffsetConstant = 500.0

		miNumPolySoups = len(PolygonSoups)
		if miNumPolySoups == 0:
			f.write(struct.pack('<3f', 0, 0, 0))
			f.write(struct.pack('<f', 0))
			f.write(struct.pack('<3f', 0, 0, 0))
			f.write(struct.pack('<f', 0))
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<Q', 0))
			f.write(struct.pack('<i', 0))
			f.write(struct.pack('<i', 0x40))
			f.write(struct.pack('<i', 0))
			f.write(struct.pack('<i', 0))
			return 0
		
		mMin_w = 0
		mMax_w = 0
		mpapPolySoups = 0x40
		miNumPolySoups = len(PolygonSoups)
		mpaPolySoupBoxes = mpapPolySoups + 0x8*miNumPolySoups
		padding = calculate_padding(mpaPolySoupBoxes, 0x10)
		mpaPolySoupBoxes += padding
		mpaPolySoupBoxesEnd = mpaPolySoupBoxes + math.ceil(miNumPolySoups/4.0)*0x70
		
		mpPolySoup_0 = calculate_mpPolySoup(miNumPolySoups, mpaPolySoupBoxesEnd)
		#mpPolySoup_0 -= 0x20
		padding_PolySoup = calculate_padding(mpPolySoup_0 + 0x40, 0x80)
		mpPolySoup_0 += padding_PolySoup
		
		mpPolySoups = []
		PolySoupBoxes = []
		maabVertexOffsetMultiply = [[] for _ in range(miNumPolySoups)]
		header_size = 0x20
		mpPolySoups.append(mpPolySoup_0)
		for i in range(0, miNumPolySoups):
			#mpPolySoups.append(cte)
			object_index, PolySoupBox, maiVertexOffsets, mfComprGranularity, PolygonSoupVertices, PolygonSoupPolygons, mu8NumQuads = PolygonSoups[i]
			
			PolySoupBoxes.append(PolySoupBox)
			
			mpaVertices = mpPolySoups[i] + header_size
			
			mu8TotalNumPolys = len(PolygonSoupPolygons)
			mu8NumQuads = mu8NumQuads
			mu8NumVertices = len(PolygonSoupVertices)
			
			mpaPolygons = mpaVertices + mu8NumVertices*0x6
			mpaPolygons += calculate_padding(mpaPolygons, 0x10)
			mu16DataSize = mpaPolygons + mu8TotalNumPolys*0xC - mpPolySoups[i] + padding_PolySoup
			
			# Transforming PolygonSoupVertices
			for mAabbMin in PolySoupBoxes[i][0]:
				mbVertexOffsetMultiply = int(math.floor(mAabbMin/miVertexOffsetConstant))
				#if mbVertexOffsetMultiply > 0:
				#	mbVertexOffsetMultiply -= 1
				maabVertexOffsetMultiply[i].append(mbVertexOffsetMultiply)
			
			for PolygonSoupVertex in PolygonSoupVertices:
				for j, vertex_co in enumerate(PolygonSoupVertex):
					PolygonSoupVertex[j] = int((vertex_co - maabVertexOffsetMultiply[i][j] * miVertexOffsetConstant) / scale)
			
			#Checking out of bounds coordinates
			coordinates = list(zip(*PolygonSoupVertices))
			translation = [0, 0, 0]
			for j in range(0, 3):
				if min(coordinates[j]) < 0:
					translation[j] = min(coordinates[j])
			
			# if translation != [0, 0, 0]:
				# print("WARNING: Negative value on PolygonSoupMesh %d. Translate your mesh origin and the empty coordinates. Trying to apply a solution." % object_index)
				# maiVertexOffsets[0] += translation[0]
				# maiVertexOffsets[1] += translation[1]
				# maiVertexOffsets[2] += translation[2]
				# for j in range(0, mu8NumVertices):
					# PolygonSoupVertices[j][0] -= translation[0]
					# PolygonSoupVertices[j][1] -= translation[1]
					# PolygonSoupVertices[j][2] -= translation[2]
			
			coordinates = list(zip(*PolygonSoupVertices))
			min_coord = 0xFFFF
			max_coord = 0
			for j in range(0, 3):
				if max(coordinates[j]) > max_coord:
					max_coord = max(coordinates[j])
				if min(coordinates[j]) < min_coord:
					min_coord = min(coordinates[j])
			
			if max_coord > 0xFFFF:
				print("ERROR: Out of bounds (>0xFFFF) value on PolygonSoupMesh %d. Split your mesh in smaller parts. Translate your mesh origin and the empty coordinates or modify the object scale." % object_index)
			if min_coord < 0x0:
				print("ERROR: Out of bounds (<0x0) value on PolygonSoupMesh %d. Split your mesh in smaller parts. Translate your mesh origin and the empty coordinates or modify the object scale." % object_index)
			
			PolygonSoups[i] = [maabVertexOffsetMultiply[i][:], mfComprGranularity, mpaPolygons, mpaVertices, mu16DataSize, mu8TotalNumPolys, mu8NumQuads, mu8NumVertices, PolygonSoupVertices, PolygonSoupPolygons]
			
			mpPolySoup_next = mpaPolygons + mu8TotalNumPolys*0xC
			padding_PolySoup = calculate_padding(mpPolySoup_next - mpPolySoup_0, 0x80)
			mpPolySoup_next += padding_PolySoup
			mpPolySoups.append(mpPolySoup_next)
		
		del mpPolySoups[-1]
		
		mMin = [min([mAabbMin[0][i] for mAabbMin in PolySoupBoxes]) for i in range(0, 3)]
		mMax = [max([mAabbMax[1][i] for mAabbMax in PolySoupBoxes]) for i in range(0, 3)]
		
		miDataSize = PolygonSoups[-1][2] + PolygonSoups[-1][5]*0xC # mpPolySoups[-1] + PolygonSoups[-1][4] - padding_PolySoup
		#miDataSize += 0x60
		
		
		#Writing
		f.write(struct.pack('<3f', *mMin))
		f.write(struct.pack('<f', mMin_w))
		f.write(struct.pack('<3f', *mMax))
		f.write(struct.pack('<f', mMax_w))
		f.write(struct.pack('<Q', mpapPolySoups))
		f.write(struct.pack('<Q', mpaPolySoupBoxes))
		f.write(struct.pack('<i', miNumPolySoups))
		f.write(struct.pack('<i', miDataSize))			# Verify
		
		f.seek(mpapPolySoups, 0)
		f.write(struct.pack('<%dQ' % miNumPolySoups, *mpPolySoups))
		
		f.seek(mpaPolySoupBoxes, 0)
		for i in range(0, miNumPolySoups):
			f.seek(int(mpaPolySoupBoxes + 0x70*(i//4) + 0x4*(i%4)), 0)
			f.write(struct.pack('<f', PolySoupBoxes[i][0][0]))
			f.seek(0xC, 1)
			f.write(struct.pack('<f', PolySoupBoxes[i][0][1]))
			f.seek(0xC, 1)
			f.write(struct.pack('<f', PolySoupBoxes[i][0][2]))
			f.seek(0xC, 1)
			f.write(struct.pack('<f', PolySoupBoxes[i][1][0]))
			f.seek(0xC, 1)
			f.write(struct.pack('<f', PolySoupBoxes[i][1][1]))
			f.seek(0xC, 1)
			f.write(struct.pack('<f', PolySoupBoxes[i][1][2]))
			f.seek(0xC, 1)
			f.write(struct.pack('<i', PolySoupBoxes[i][2]))
		
		# Todo
		for i in range(0, miNumPolySoups):
			f.seek(mpPolySoups[i], 0)
			
			mabVertexOffsetMultiply, mfComprGranularity, mpaPolygons, mpaVertices, mu16DataSize, mu8TotalNumPolys, mu8NumQuads, mu8NumVertices, PolygonSoupVertices, PolygonSoupPolygons = PolygonSoups[i]
			f.write(struct.pack('<Q', mpaPolygons))
			f.write(struct.pack('<Q', mpaVertices))
			f.write(struct.pack('<H', mu16DataSize))
			
			f.write(struct.pack('<bbb', *mabVertexOffsetMultiply))
			
			f.write(struct.pack('<B', mu8NumQuads))
			f.write(struct.pack('<B', mu8TotalNumPolys))
			f.write(struct.pack('<B', mu8NumVertices))
			
			f.seek(mpaVertices, 0)
			for j in range(0, mu8NumVertices):
				f.write(struct.pack('<3H', *PolygonSoupVertices[j]))
			
			f.seek(mpaPolygons, 0)
			for j in range(0, mu8NumQuads):
				mu16CollisionTag, mau8VertexIndices, mau8EdgeCosines = PolygonSoupPolygons[j]
				f.write(struct.pack('<H', mu16CollisionTag[0]))
				f.write(struct.pack('<H', mu16CollisionTag[1]))
				f.write(struct.pack('<4B', *mau8VertexIndices))
				f.write(struct.pack('<4B', *mau8EdgeCosines))
			
			for j in range(mu8NumQuads, mu8TotalNumPolys):
				mu16CollisionTag, mau8VertexIndices, mau8EdgeCosines = PolygonSoupPolygons[j]
				f.write(struct.pack('<H', mu16CollisionTag[0]))
				f.write(struct.pack('<H', mu16CollisionTag[1]))
				f.write(struct.pack('<3B', *mau8VertexIndices))
				f.write(struct.pack('<B', 0xFF))
				f.write(struct.pack('<4B', *mau8EdgeCosines))
		
		#f.write(bytearray([0])*0x60)
		padding = calculate_padding(miDataSize, 0x10)
		f.write(bytearray([0])*padding)
	
	return 0


def write_zonelist(zonelist_path, zones):	#OK
	os.makedirs(os.path.dirname(zonelist_path), exist_ok = True)
	
	with open(zonelist_path, "wb") as f: 
		mpZones = 0x30
		muTotalZones = len(zones)
		muTotalPoints = sum(len(zone[-1]) for zone in zones)
		const_0x18 = 0x0
		
		mpNeighbour0 = mpZones + muTotalZones*0x28
		mpNeighbours = mpNeighbour0
		mauTotalNeighbours = 0
		for zone in zones:
			mTotalNeighbours = len(zone[1][0])
			# if mTotalNeighbours % 2 == 0:
				# mauTotalNeighbours += mTotalNeighbours
			# else:
				# mauTotalNeighbours += mTotalNeighbours + 1
			mauTotalNeighbours += mTotalNeighbours
		
		mpPoints = mpNeighbour0 + mauTotalNeighbours*0x10
		padding = calculate_padding(mpPoints, 0x10)
		mpPoints += padding
		
		mpuZonePointStarts = mpPoints + muTotalPoints*0x10
		padding = calculate_padding(mpuZonePointStarts, 0x10)
		mpuZonePointStarts += padding
		
		mpiZonePointCounts = mpuZonePointStarts + muTotalZones*0x4
		padding = calculate_padding(mpiZonePointCounts, 0x10)
		mpiZonePointCounts += padding
		
		miTotalNumPoints = 0
		mpZoneDict = {}
		for i in range(0, muTotalZones):
			muZoneId = zones[i][0]
			mpZoneDict[muZoneId] = mpZones + 0x28*i
		
		
		#Writing
		f.write(struct.pack('<Q', mpPoints))
		f.write(struct.pack('<Q', mpZones))
		f.write(struct.pack('<Q', mpuZonePointStarts))
		f.write(struct.pack('<Q', mpiZonePointCounts))
		f.write(struct.pack('<I', muTotalZones))
		f.write(struct.pack('<I', muTotalPoints))
		f.write(struct.pack('<B', const_0x18))
		
		f.seek(mpZones, 0)
		for i in range(0, muTotalZones):
			zone = zones[i]
			muZoneId, [mauNeighbourId, mauNeighbourFlags, muDistrictId, miZoneType, muArenaId, miNumSafeNeighbours], zonepoints = zone
			miNumPoints = len(zonepoints)
			miNumNeighbours = len(mauNeighbourId)
			null_0x8 = 0
			null_0xC = 0
			null_0x1A = 0
			
			f.seek(mpZones + 0x28*i, 0)
			f.write(struct.pack('<Q', mpPoints))
			f.write(struct.pack('<I', null_0x8))
			f.write(struct.pack('<I', null_0xC))
			
			if miNumNeighbours == 0:
				f.write(struct.pack('<Q', 0))
			else:
				f.write(struct.pack('<Q', mpNeighbours))	# mpSafeNeighbours or mpUnsafeNeighbours?
			f.write(struct.pack('<H', muZoneId))
			f.write(struct.pack('<H', null_0x1A))
			f.write(struct.pack('<I', muDistrictId))
			
			f.write(struct.pack('<H', miZoneType))				# 1 or 0
			f.write(struct.pack('<H', miNumPoints))
			f.write(struct.pack('<H', miNumSafeNeighbours))
			f.write(struct.pack('<H', miNumNeighbours))			# miNumUnsafeNeighbours?
			
			
			f.seek(mpNeighbours, 0)
			for j in range(0, miNumNeighbours):
				f.seek(mpNeighbours + 0x10*j, 0)
				try:
					mpZone = mpZoneDict[mauNeighbourId[j]]
					muNeighbourFlag = mauNeighbourFlags[j]
					f.write(struct.pack('<Q', mpZone))
					f.write(struct.pack('<I', muNeighbourFlag))
				except:
					print("ERROR: zone object %d is missing. It is referenced as a neighbour of zone %d. Writing a null one, but it might crash your game." % (mauNeighbourId[j], muZoneId))
					f.write(struct.pack('<Q', 0))
					f.write(struct.pack('<I', 0))
			
			f.seek(mpPoints, 0)
			for j in range(0, miNumPoints):
				f.write(struct.pack('<2f', *zonepoints[j]))
				f.write(struct.pack('<2I', 0, 0))
			
			f.seek(mpuZonePointStarts + 0x4*i, 0)
			f.write(struct.pack('<I', miTotalNumPoints))
			
			f.seek(mpiZonePointCounts + 0x2*i, 0)
			f.write(struct.pack('<H', miNumPoints))
			
			mpPoints += miNumPoints*0x10
			mpNeighbours += miNumNeighbours*0x10
			padding = calculate_padding(mpNeighbours, 0x10)
			mpNeighbours += padding
			
			miTotalNumPoints += miNumPoints
		
		padding = calculate_padding(mpiZonePointCounts + 0x2*muTotalZones, 0x10)
		f.write(bytearray([0])*padding)
	
	return 0


def write_resources_table(resources_table_path, mResourceIds, resource_type, write_header): #OK
	with open(resources_table_path, "wb") as f:
		#if resource_type == "InstanceList" and write_header == True:
		if write_header == True:
			macMagicNumber = b'bnd2'
			muVersion = 3
			muPlatform = 1
			muHeaderOffset = 0x30
			muDebugDataOffset = 0x90
			muResourceEntriesCount = len(mResourceIds)
			muResourceEntriesOffset = 0x90
			mauResourceDataOffset = [0x0, 0x0, 0x0, 0x0]
			if resource_type == "CharacterSpec":
				muFlags = 0x1
			elif resource_type == "ZoneList":
				muFlags = 0x7
			else:
				muFlags = 0x27
			pad1 = 0
			
			f.write(macMagicNumber)
			f.write(struct.pack("<I", muVersion))
			f.write(struct.pack("<I", muPlatform))
			f.write(struct.pack("<I", muDebugDataOffset))
			f.write(struct.pack("<I", muResourceEntriesCount))
			f.write(struct.pack("<I", muResourceEntriesOffset))
			f.write(struct.pack("<IIII", *mauResourceDataOffset))
			f.write(struct.pack("<I", muFlags))
			f.write(struct.pack("<I", pad1))
			
			f.seek(muHeaderOffset, 0)
			f.write(b'Resources generated by NFSHP 2020 Exporter 3.1 for Blender by DGIorio')
			f.write(b'...........Hash:.3bb42e1d')
			f.seek(muResourceEntriesOffset, 0)
		
		muStreamIndex_0 = b''
		muStreamIndex_1 = b''
		muStreamIndex_2 = b''
		muStreamIndex_3 = b''
		
		mResourceIds.sort(key=lambda x:x[2])
		for mResourceId, muResourceType, _ in mResourceIds:
			count = 0
			unkByte_0x4 = 0
			unkByte_0x5 = 0
			isIdInteger = 0
			muStreamIndex = 0
			if muResourceType == 'ControlMesh':
				unkByte_0x4 = 0x10
				unkByte_0x5 = 0x2
				isIdInteger = 1
				muStreamIndex = 0
			elif muResourceType in ('AnimationList', 'Skeleton', 'PathAnimation', 'CharacterSpec'):
				unkByte_0x4 = 0x0
				unkByte_0x5 = 0x0
				isIdInteger = 1
				muStreamIndex = 0
			elif muResourceType == 'PolygonSoupList':
				unkByte_0x4 = 0x0
				unkByte_0x5 = 0x0
				isIdInteger = 0
				muStreamIndex = 1
			elif muResourceType == 'ConvexHull':
				isIdInteger = 1
				muStreamIndex = 1
			
			muResourceTypeId = int_to_id(resourcetype_to_type_id(muResourceType))
			
			resource_entry = b''
			resource_entry += id_to_bytes(mResourceId)
			resource_entry += struct.pack("<B", unkByte_0x4)
			resource_entry += struct.pack("<B", unkByte_0x5)
			resource_entry += struct.pack("<B", count)
			resource_entry += struct.pack("<B", isIdInteger)
			
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<B", 0)
			resource_entry += struct.pack("<B", 0)
			resource_entry += struct.pack("<B", 0)
			resource_entry += struct.pack("<B", 0)


			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			resource_entry += struct.pack("<I", 0)
			
			resource_entry += struct.pack("<I", 0)
			resource_entry += id_to_bytes(muResourceTypeId)
			resource_entry += struct.pack("<H", 0)
			resource_entry += struct.pack("<B", 0)
			resource_entry += struct.pack("<B", muStreamIndex)
			resource_entry += struct.pack("<I", 0)
			
			if muStreamIndex == 0:
				muStreamIndex_0 += resource_entry
			elif muStreamIndex == 1:
				muStreamIndex_1 += resource_entry
			elif muStreamIndex == 2:
				muStreamIndex_2 += resource_entry
			elif muStreamIndex == 3:
				muStreamIndex_3 += resource_entry
		
		f.write(muStreamIndex_0)
		f.write(muStreamIndex_1)
		f.write(muStreamIndex_2)
		f.write(muStreamIndex_3)
	
	return 0


def edit_graphicsspec(graphicsspec_path, instances, instances_wheelGroups, has_skeleton, mSkeletonId, has_controlmesh, mControlMeshId): #OK
	if os.path.isfile(graphicsspec_path) == False:
		return (0, "", "")
	
	with open(graphicsspec_path, "rb") as f:
		file_size = os.path.getsize(graphicsspec_path)
		
		mppModels = struct.unpack("<Q", f.read(0x8))[0]
		null_0x4 = struct.unpack("<Q", f.read(0x8))[0]
		null_0x8 = struct.unpack("<Q", f.read(0x8))[0]
		mpWheelsData = struct.unpack("<Q", f.read(0x8))[0]
		muPartsCount = struct.unpack("<H", f.read(0x2))[0]
		unknown_0x12 = struct.unpack("<B", f.read(0x1))[0]
		num_wheels = struct.unpack("<B", f.read(0x1))[0]
		
		mpWheelAllocateSpace = []
		object_placements = []
		mNumWheelParts = 0
		for i in range(0, num_wheels):
			f.seek(mpWheelsData + 0x60*i, 0)
			mpWheelAllocateSpace.append(struct.unpack("<Q", f.read(0x8))[0])
			spinnable_models = struct.unpack("<I", f.read(0x4))[0]
			mNumWheelParts += struct.unpack("<H", f.read(0x2))[0]
			padding = f.read(0x2)
			object_placement = f.read(0x10).split(b'\x00')[0]
			object_placement = str(object_placement, 'ascii').lower()
			object_placements.append(object_placement)
		
		first_wheel_pointer = min(mpWheelAllocateSpace)
		
		f.seek(-0x8, 2)
		last_resource_pointer = struct.unpack("<I", f.read(0x4))[0]
		mpResourceIds = last_resource_pointer + 0x4
		mpResourceIds += calculate_padding(mpResourceIds, 0x10)
		f.seek(mpResourceIds, 0)
		muOffset = 0
		mpModel = mpResourceIds
		while muOffset != mppModels:
			f.seek(0x8, 1)
			muOffset = struct.unpack("<I", f.read(0x4))[0]
			_ = struct.unpack("<I", f.read(0x4))[0]
			mpModel += 0x10
		mpModel -= 0x10
		
		f.seek(0x0, 0)
		header_data = f.read(first_wheel_pointer)
		wheel_allocate_space = f.read(mpResourceIds - first_wheel_pointer)
		resources_up_data = f.read(mpModel - mpResourceIds)
		f.seek(0x10*muPartsCount, 1)
		resources_down_data = f.read(file_size - (mpModel + 0x10*muPartsCount) - 0x10*mNumWheelParts)
		resouces_wheel = f.read(0x10*mNumWheelParts)
		
		f.seek(mpResourceIds + 0x8, 0)
		muOffset = struct.unpack("<I", f.read(0x4))[0]
		if muOffset == 0x10:
			f.seek(-0xC, 1)
			mSkeletonId_ = ""
		else:
			f.seek(-0xC, 1)
			mSkeletonId_ = bytes_to_id(f.read(0x4))
			f.seek(0xC, 1)
		mpControlMeshId_relative = f.tell() - mpResourceIds
		mControlMeshId_ = bytes_to_id(f.read(0x4))
	
	instances.sort(key=lambda x:x[0])
	
	if len(instances_wheelGroups) > 0:
		mResourceIds = []
		muOffsets = []
		# mpWheelAllocateSpace = []
		# spinnable_models = []
		# maNumWheelParts = []
		# muNumWheelParts = 0
		
		# for i, (object_placement, group) in enumerate(instances_wheelGroups.items()):
			# mpWheelAllocateSpace.append(first_wheel_pointer + muNumWheelParts*0x4)
			
			# is_spinnable = ''
			# for j, instance in enumerate(group):
				# is_spinnable += str(instance[1][2])
				# mResourceIds.append(instance[1][0])
				# muOffsets.append(mpWheelAllocateSpace[i] + j*0x4)
			
			# spinnable_models.append(int(is_spinnable, 2))
			# maNumWheelParts.append(len(group))
			
			# muNumWheelParts += len(group)
		
		mpWheelAllocateSpace = {}
		spinnable_models = {}
		wheels_offset = {}
		maNumWheelParts = {}
		muNumWheelParts = 0
		for i in range(0, num_wheels):
			try:
				group = instances_wheelGroups[object_placements[i]]
			except:
				continue
			mpWheelAllocateSpace[object_placements[i]] = first_wheel_pointer + muNumWheelParts*0x8
			
			is_spinnable = ''
			for j, instance in enumerate(group):
				is_spinnable += str(int(instance[1][2]))
				mResourceIds.append(instance[1][0])
				muOffsets.append(mpWheelAllocateSpace[object_placements[i]] + j*0x8)
			
			is_spinnable = is_spinnable[::-1]
			spinnable_models[object_placements[i]] = int(is_spinnable, 2)
			maNumWheelParts[object_placements[i]] = len(group)
			#wheels_offset[object_placements[i]] = list(group[0][1][1][0].transposed().translation)[::-1]
			wheels_offset[object_placements[i]] = list(group[0][1][1][0].transposed().translation)
			
			muNumWheelParts += len(group)
		
		mpResourceIds = first_wheel_pointer + muNumWheelParts*0x8
		mpResourceIds += calculate_padding(mpResourceIds, 0x10)
	
	if len(instances) > 2:
		mppModels = mpResourceIds
		mpResourceIds += len(instances)*0x8
		mpResourceIds += calculate_padding(mpResourceIds, 0x10)
	
	with open(graphicsspec_path, "wb") as f:
		f.write(header_data)
		#f.write(wheel_allocate_space)
		f.seek(mpResourceIds, 0)
		f.write(resources_up_data)
		for i, instance in enumerate(instances):
			mModelId = instance[1][0]
			f.write(id_to_bytes(mModelId))
			f.write(struct.pack('<i', 0))
			f.write(struct.pack('<I', mppModels + i*0x8))
			f.write(struct.pack('<i', 0))
		f.write(resources_down_data)
		f.seek(0x0, 0)
		f.write(struct.pack('<Q', mppModels))
		f.seek(0x20, 0)
		f.write(struct.pack('<H', len(instances)))
		
		f.seek(0, 2)
		if len(instances_wheelGroups) > 0:
			#instances_wheelGroups[object_placement].append([object_index, [mModelId, [mTransform], is_spinnable, object_placement]])
			#{"FR", [[object_index, [mModelId, [mTransform], is_spinnable, object_placement]], [object_index, [mModelId, [mTransform], is_spinnable, object_placement]]]
			
			# Erasing original wheel data in order to avoid using them in case len(instances_wheelGroups) < 4
			for i in range(0, num_wheels):
				f.seek(mpWheelsData + 0x60*i, 0)
				f.write(struct.pack('<Q', first_wheel_pointer))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<H', 0))
				
			#for i in range(0, len(instances_wheelGroups)):
			for i in range(0, num_wheels):
				f.seek(mpWheelsData + 0x60*i, 0)
				try:
					f.write(struct.pack('<Q', mpWheelAllocateSpace[object_placements[i]]))
					f.write(struct.pack('<I', spinnable_models[object_placements[i]]))
					f.write(struct.pack('<H', maNumWheelParts[object_placements[i]]))
					f.seek(0x22, 1)
					f.write(struct.pack('<3f', *wheels_offset[object_placements[i]]))
					f.write(struct.pack('<f', 0.0))
				except:
					continue
				
			f.seek(0, 2)
			for mResourceId, muOffset in zip(mResourceIds, muOffsets):
				f.write(id_to_bytes(mResourceId))
				f.write(struct.pack('<i', 0))
				f.write(struct.pack('<I', muOffset))
				f.write(struct.pack('<i', 0))
		
		else:
			f.write(resouces_wheel)
		
		if has_skeleton == True:
			if mSkeletonId_ != "":
				f.seek(mpResourceIds, 0)
				f.write(id_to_bytes(mSkeletonId))
		
		if has_controlmesh == True:
			f.seek(mpResourceIds, 0)
			f.seek(mpControlMeshId_relative, 1)
			f.write(id_to_bytes(mControlMeshId))
	
	return (0, mSkeletonId_, mControlMeshId_)


def edit_graphicsspec_effects(graphicsspec_path, instances_effects): #OK
	if os.path.isfile(graphicsspec_path) == False:
		return 1
	
	with open(graphicsspec_path, "rb") as f:
		file_size = os.path.getsize(graphicsspec_path)
		
		mppModels = struct.unpack("<Q", f.read(0x8))[0]
		null_0x4 = struct.unpack("<Q", f.read(0x8))[0]
		null_0x8 = struct.unpack("<Q", f.read(0x8))[0]
		mpWheelsData = struct.unpack("<Q", f.read(0x8))[0]
		muPartsCount = struct.unpack("<H", f.read(0x2))[0]
		unknown_0x12 = struct.unpack("<B", f.read(0x1))[0]
		unknown_0x13 = struct.unpack("<B", f.read(0x1))[0]
		num_behaviours = struct.unpack("<I", f.read(0x4))[0]
		mppBehaviour = struct.unpack("<Q", f.read(0x8))[0]
		num_effects = struct.unpack("<I", f.read(0x4))[0]
		unknown_0x34 = struct.unpack("<I", f.read(0x4))[0]		#new null
		mpEffectsId = struct.unpack("<Q", f.read(0x8))[0]
		mpEffectsTable = struct.unpack("<Q", f.read(0x8))[0]
		padding = f.read(0x8)
		padding = f.read(0x10)		
		
		mpWheelAllocateSpace = []
		object_placements = []
		mNumWheelParts = 0
		for i in range(0, 4):
			f.seek(mpWheelsData + 0x60*i, 0)
			mpWheelAllocateSpace.append(struct.unpack("<Q", f.read(0x8))[0])
			spinnable_models = struct.unpack("<I", f.read(0x4))[0]
			mNumWheelParts += struct.unpack("<H", f.read(0x2))[0]
			padding = f.read(0x2)
			object_placement = f.read(0x10).split(b'\x00')[0]
			object_placement = str(object_placement, 'ascii').lower()
			object_placements.append(object_placement)
		
		first_wheel_pointer = min(mpWheelAllocateSpace)
		
		f.seek(0x0, 0)
		data_up = f.read(file_size - mpEffectsId)
		
		f.seek(first_wheel_pointer, 0)
		data = f.read(file_size - first_wheel_pointer)
	
	if len(instances_effects) != num_effects:
		print("ERROR: number of effect objects %d is different than the original model data %d. Effects will not be exported." % (len(instances_effects), num_effects))
		return 1
	
	num_effects = len(instances_effects)
	mpEffectsId = mpEffectsId
	mpEffectsTable = mpEffectsTable
	
	mpEffect0 = mpEffectsTable + 0x18*num_effects
	mpEffect0 += calculate_padding(mpEffect0, 0x10)
	
	mpEffects = []
	mpEffect = mpEffect0
	effect_copies_previous = 0
	num_effects_data = 0
	for i in range(0, num_effects):
		_, _, effect_copies = instances_effects[i]
		mpEffect = mpEffect + 0x20*effect_copies_previous
		effect_copies_previous = len(effect_copies)
		mpEffects.append(mpEffect)
		
		has_unknow_value = any(value[2] is not None for value in effect_copies)
		if has_unknow_value == True:
			num_effects_data += len(effect_copies)
	
	# Fixing pointers
	first_wheel_pointer_fixed = mpEffects[-1] + 0x20*effect_copies_previous + num_effects_data*0x4
	first_wheel_pointer_fixed += calculate_padding(first_wheel_pointer_fixed, 0x10)
	delta_pointer = first_wheel_pointer_fixed - first_wheel_pointer
	for i in range(0, 4):
		mpWheelAllocateSpace[i] += delta_pointer
	
	muOffsets_Wheels = []
	for i in range(0, mNumWheelParts):
		muOffsets_Wheels.append(first_wheel_pointer_fixed + 0x8*i)
	
	muOffsets_Models = []
	if mppModels >= first_wheel_pointer:
		mppModels += delta_pointer
		for i in range(0, muPartsCount):
			muOffsets_Models.append(mppModels + 0x8*i)
	
	mpResourceIds = first_wheel_pointer_fixed + mNumWheelParts*0x8
	mpResourceIds += calculate_padding(mpResourceIds, 0x10)
	if mppModels >= first_wheel_pointer:
		mpResourceIds += muPartsCount*0x8
		mpResourceIds += calculate_padding(mpResourceIds, 0x10)
	
	k = 0
	with open(graphicsspec_path, "wb") as f:
		f.write(data_up)
		
		f.seek(0x0, 0)
		f.write(struct.pack('<Q', mppModels))
		f.write(struct.pack('<Q', null_0x4))
		f.write(struct.pack('<Q', null_0x8))
		f.write(struct.pack('<Q', mpWheelsData))
		f.write(struct.pack('<H', muPartsCount))
		f.write(struct.pack('<B', unknown_0x12))
		f.write(struct.pack('<B', unknown_0x13))
		f.write(struct.pack('<I', num_behaviours))
		f.write(struct.pack('<Q', mppBehaviour))
		f.write(struct.pack('<I', num_effects))
		f.write(struct.pack('<I', unknown_0x34))
		f.write(struct.pack('<Q', mpEffectsId))
		f.write(struct.pack('<Q', mpEffectsTable))
		
		for i in range(0, 4):
			f.seek(mpWheelsData + 0x60*i, 0)
			f.write(struct.pack('<Q', mpWheelAllocateSpace[i]))
		
		for i in range(0, num_effects):
			mEffectId, effect_index_, effect_copies = instances_effects[i]
			effect_count = len(effect_copies)
			unknown_pointer = 0
			
			has_unknow_value = any(value[2] is not None for value in effect_copies)
			if has_unknow_value == True:
				unknown_pointer = mpEffects[-1] + 0x20*effect_copies_previous + k*0x4
				k += effect_count
			
			f.seek(mpEffectsId + 0x4*i, 0)
			f.write(struct.pack('<I', mEffectId))
			
			f.seek(mpEffectsTable + 0x18*i, 0)
			f.write(struct.pack('<Q', effect_count))
			f.write(struct.pack('<Q', mpEffects[i]))
			f.write(struct.pack('<Q', unknown_pointer))
			
			for j in range(0, effect_count):
				f.seek(mpEffects[i] + 0x20*j, 0)
				f.write(struct.pack('<ffff', *effect_copies[j][1][1]))
				f.write(struct.pack('<fff', *effect_copies[j][1][0]))
				f.write(struct.pack('<f', 0.0))
			
				if has_unknow_value == True:
					f.seek(unknown_pointer + j*0x4, 0)
					if effect_copies[j][2] == None:
						print("ERROR: effect %d copy %d is missing parameter %s (or %s)." % (effect_index_, effect_copies[j][0], '"sensor_hash"', '"EffectData"'))
					f.write(struct.pack('<I', effect_copies[j][2]))
		
		f.seek(first_wheel_pointer_fixed, 0)
		f.write(data)
		
		f.seek(mpResourceIds, 0)
		f.seek(0x20, 1)
		if mppModels >= first_wheel_pointer:
			for i in range(0, muPartsCount):
				f.seek(0x8, 1)
				f.write(struct.pack('<I', muOffsets_Models[i]))
				f.seek(0x4, 1)
		else:
			f.seek(0x10*muPartsCount, 1)
		
		f.seek(-0x10*mNumWheelParts, 2)
		for i in range(0, mNumWheelParts):
			f.seek(0x8, 1)
			f.write(struct.pack('<I', muOffsets_Wheels[i]))
			f.seek(0x4, 1)
		
	return 0


def edit_genesysinstance1(genesysinstance_dir, genesysinstance_path, instances_character): #OK
	if os.path.isfile(genesysinstance_path) == False:
		return 1
	
	with open(genesysinstance_path, "r+b") as f:
		f.seek(0x30, 0)
		f.write(struct.pack('<fff', *instances_character[1]))
	
	return 0


def edit_genesysinstance2(genesysinstance_dir, genesysinstance_path, instances_wheelGroups): #OK
	if os.path.isfile(genesysinstance_path) == False:
		return 1
	
	with open(genesysinstance_path, "r+b") as f:
		#RigidBody
		#Not necessary to write
		f.seek(0x128, 0)
		table_pointer = struct.unpack("<Q", f.read(0x8))[0]
		count = struct.unpack("<I", f.read(0x4))[0]
		
		f.seek(table_pointer, 0)
		data_pointers = list(struct.unpack("<%dQ" % count, f.read(0x8*count)))
		placements = ["unknown", "rearright", "rearleft", "frontright", "frontleft"]
		
		for i in range(1, count):	# skipping first one
			wheel_data = instances_wheelGroups[placements[i]]
			
			f.seek(data_pointers[i], 0)
			f.seek(0x10, 1)
			wheel_data_pointer = struct.unpack("<Q", f.read(0x8))[0]
			
			f.seek(wheel_data_pointer, 0)
			
			mTransform = wheel_data[0][1][1][0]
			f.write(struct.pack('<4f', *mTransform[0]))
			f.write(struct.pack('<4f', *mTransform[1]))
			f.write(struct.pack('<4f', *mTransform[2]))
			f.write(struct.pack('<4f', *mTransform[3]))
	
		#WheelSuspensionConstraint
		f.seek(0x158, 0)
		wheel_suspesion_table_pointer = struct.unpack("<Q", f.read(0x8))[0]
		wheel_count = struct.unpack("<I", f.read(0x4))[0]
		
		for i in range(0, wheel_count):
			wheel_data = instances_wheelGroups[placements[i+1]]
			mTransform = wheel_data[0][1][1][0]
			location = mTransform[3]
			suspension_up = [location[0] + 0.000233, location[1] + 0.056, location[2], 0.0]
			suspension_down = [location[0] - 0.000267, location[1] - 0.049, location[2], 0.0]
			
			f.seek(wheel_suspesion_table_pointer + 0x8*i, 0)
			wheel_suspesion_data_pointer = struct.unpack("<Q", f.read(0x8))[0]
			
			f.seek(wheel_suspesion_data_pointer + 0x10, 0)
			wheel_suspension_coordinates_pointer = struct.unpack("<Q", f.read(0x8))[0]
			
			f.seek(wheel_suspension_coordinates_pointer, 0)
			f.write(struct.pack('<4f', *suspension_up))
			f.write(struct.pack('<4f', *suspension_down))
	
	return 0


def change_mResourceId_on_file(file_path, mResourceId, mResourceId_new, stop): #OK
	if os.path.isfile(file_path) == False:
		return 1
	
	file_size = os.path.getsize(file_path)
	count = int(file_size/0x4)
	offsets = []
	
	# with open(file_path, "rb") as f:
		# for i in range(0, count):
			# id = bytes_to_id(f.read(0x4))
			# if id == mResourceId:
				# offsets.append(f.tell() - 0x4)
				# if stop == True:
					# break
	
	# with open(file_path, "wb+") as f:
		# for offset in offsets:
			# f.seek(offset, 0)
			# f.write(id_to_bytes(mResourceId_new))
	
	with open(file_path, "rb+") as f:
		for i in range(0, count):
			id = bytes_to_id(f.read(0x4))
			if id == mResourceId:
				f.seek(-0x4, 1)
				f.write(id_to_bytes(mResourceId_new))
				if stop == True:
					break
	
	return 0


def merge_resources_table(ids_table_path, resources_table_path): #OK
	with open(resources_table_path, "rb") as f, open(ids_table_path, "rb") as g:
		f.seek(0xC, 0)
		muDebugDataOffset = struct.unpack("<I", f.read(0x4))[0]
		f.seek(0x14, 0)
		muResourceEntriesOffset = struct.unpack("<I", f.read(0x4))[0]
		f.seek(0x28, 0)
		muFlags = struct.unpack("<I", f.read(0x4))[0]
		
		f.seek(0x0, 0)
		if (muFlags>>3)&1 == 1: # Cheking if debug data bit is equal 1
			header_data = f.read(muDebugDataOffset)
			debug_data = f.read(muResourceEntriesOffset - muDebugDataOffset)
		else:
			header_data = f.read(muResourceEntriesOffset)
			debug_data = b''
		resource_data = f.read()
		append_data = g.read()
		f.seek(0x30, 0)
		text = f.read(0x2A)
	
	with open(resources_table_path, "wb") as f:
		muDebugDataOffset += 0x60
		muResourceEntriesOffset += 0x60
		f.write(header_data)
		if text != b'Resources generated by NFSHP 2020 Exporter':
			f.write(b'Resources generated by NFSHP 2020 Exporter 3.1 for Blender by DGIorio')
			f.write(b'...........Hash:.3bb42e1d')
			f.seek(0xC, 0)
			f.write(struct.pack("<I", muDebugDataOffset))
			f.seek(0x14, 0)
			f.write(struct.pack("<I", muResourceEntriesOffset))
		
		if (muFlags>>3)&1 == 1: # Cheking if debug data bit is equal 1
			f.seek(muDebugDataOffset, 0)
			f.write(debug_data)
		else:
			f.seek(muResourceEntriesOffset, 0)
		f.write(append_data)
		f.write(resource_data)
	
	return 0


def remove_resource_from_resources_table(resources_table_path, mResourceId): #OK
	# Header is not edited at this point, number of IDs is not correct
	with open(resources_table_path, "rb") as f:
		file_size = os.path.getsize(resources_table_path)
		f.seek(0x14, 0)
		header_size = struct.unpack("<I", f.read(0x4))[0]
		muResourceEntriesCount = int((file_size - header_size) / 0x50)
		muResourceEntryOffset = -1
		for i in range(0, muResourceEntriesCount):
			f.seek(header_size + i*0x50, 0)
			mResourceId_ = bytes_to_id(f.read(0x4))
			if mResourceId_ == mResourceId:
				muResourceEntryOffset = header_size + i*0x50
				f.seek(0, 0)
				resource_data_before = f.read(muResourceEntryOffset)
				f.seek(muResourceEntryOffset + 0x50, 0)
				resource_data_after = f.read()
				break
		
	if muResourceEntryOffset != -1:
		with open(resources_table_path, "wb") as f:
			f.write(resource_data_before)
			f.write(resource_data_after)
		

def move_shared_resource(resource_path, mResourceId, shared_resource_dir):
	os.makedirs(os.path.dirname(resource_path), exist_ok = True)
	
	shared_resource = os.path.join(shared_resource_dir, mResourceId + ".dat")
	if os.path.isfile(shared_resource):
		shutil.copy2(shared_resource, resource_path)
	else:
		return 1
	
	return 0


def create_displacementsampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x20\x00\x00\x00')
		f.write(b'\x20\x00\x00\x00\x00\x02\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 87):
			f.write(b'\xE0\x07\xE0\x07\x00\x00\x00\x00')
	
	return 0


def create_blacksampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x10\x00\x00\x00')
		f.write(b'\x10\x00\x00\x00\x80\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 17):
			f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
	
	return 0


def create_whitesampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 7):
			f.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
	
	return 0


def create_greysampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 7):
			f.write(b'\x34\xA5\x34\xA5\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
	
	return 0


def create_greyalphasampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x35\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 7):
			f.write(b'\x80\x80\x00\x00\x00\x00\x00\x00')
			f.write(b'\x10\x84\x10\x84\x00\x00\x00\x00')
	
	return 0


def create_pinkalphasampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x35\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 7):
			f.write(b'\x81\x81\x00\x00\x00\x00\x00\x00')
			f.write(b'\x1F\xFC\x1F\xFC\x00\x00\x00\x00')
	
	return 0


def create_normalsampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x20\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		
		f.write(b'\x1E\x84\xFE\x7B\xFB\x75\xBB\x75\x1E\x84\xFE\x7B\xAA\xBF\xAA\xFF')
		f.write(b'\xFE\x83\x1E\x7C\xFF\xAE\xFF\xAB\x1E\x84\xFE\x7B\xAA\xFF\xAA\xFF')
		f.write(b'\x1E\x84\xFE\x7B\xB5\xF5\xFB\xFA\xFE\x83\xFE\x7B\xDD\xEE\xDD\xEE')
		f.write(b'\xFE\x7B\xFE\x7B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
	
	return 0


def create_crumplesampler(raster_source_path):
	os.makedirs(os.path.dirname(raster_source_path), exist_ok = True)
	
	with open(raster_source_path, "wb") as f:
		f.write(b'\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x08\x00\x00\x00')
		f.write(b'\x08\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00')
		f.write(b'\x04\x00\x00\x00\x44\x58\x54\x35\x00\x00\x00\x00\x00\x00\x00\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00')
		f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		for i in range(0, 7):
			f.write(b'\x7F\x7F\x00\x00\x00\x00\x00\x00')
			f.write(b'\xE0\xFB\xE0\xFB\x00\x00\x00\x00')
	
	return 0


def convert_texture_to_dxt1(raster_path, make_backup):
	if make_backup == True:
		shutil.copy2(raster_path, raster_path + ".bak")
	out_raster_path = os.path.splitext(raster_path)[0] + ".dds"
	nvidia_path = nvidiaGet()

	compress_type = "bc1" # DXT1

	os.system('"%s -%s -silent "%s" "%s""' % (nvidia_path, compress_type, raster_path, out_raster_path))

	return out_raster_path


def convert_texture_to_dxt3(raster_path, make_backup):
	if make_backup == True:
		shutil.copy2(raster_path, raster_path + ".bak")
	out_raster_path = os.path.splitext(raster_path)[0] + ".dds"
	nvidia_path = nvidiaGet()

	compress_type = "bc2" # DXT3

	os.system('"%s -%s -silent "%s" "%s""' % (nvidia_path, compress_type, raster_path, out_raster_path))

	return out_raster_path


def convert_texture_to_dxt5(raster_path, make_backup):
	if make_backup == True:
		shutil.copy2(raster_path, raster_path + ".bak")
	out_raster_path = os.path.splitext(raster_path)[0] + ".dds"
	nvidia_path = nvidiaGet()
	
	compress_type = "bc3" # DXT5
	
	os.system('"%s -alpha -%s -silent "%s" "%s""' % (nvidia_path, compress_type, raster_path, out_raster_path))
	
	return out_raster_path


def apply_transfrom(ob, global_rotation, use_location=False, use_rotation=False, use_scale=False):
	mb = ob.matrix_basis
	I = Matrix()
	loc, rot, scale = mb.decompose()
	
	euler = Euler(map(math.radians, global_rotation), rot.to_euler().order).to_matrix().to_4x4()
	
	# rotation
	T = Matrix.Translation(loc)
	#R = rot.to_matrix().to_4x4()
	R = mb.to_3x3().normalized().to_4x4()
	S = Matrix.Diagonal(scale).to_4x4()

	transform = [I, I, I]
	#basis = [T, R, S]
	
	basis = [T, euler, S]
	

	def swap(i):
		transform[i], basis[i] = basis[i], transform[i]

	if use_location:
		swap(0)
	if use_rotation:
		swap(1)
	if use_scale:
		swap(2)

	M = transform[0] @ transform[1] @ transform[2]
	if hasattr(ob.data, "transform"):
		ob.data.transform(M)
	for c in ob.children:
		c.matrix_local = M @ c.matrix_local

	ob.matrix_basis = basis[0] @ basis[1] @ basis[2]


def convert_triangle_to_strip(TriangleList, terminator):
	TriangleStrip = []
	cte = 0
	for i, Triangle in enumerate(TriangleList):
		if i == 0:
			a, b, c = Triangle
			TriangleStrip.extend([a,b,c])
		else:
			PreviousTriangle = TriangleList[i-1]
			a, b, c = Triangle
			if (i+cte)%2==0:
				if a != PreviousTriangle[0] or b != PreviousTriangle[2]:
					TriangleStrip.extend([terminator, a, b, c])
					cte += 0
				else:
					TriangleStrip.append(c)
			else:
				if a != PreviousTriangle[2] or b != PreviousTriangle[1]:
					TriangleStrip.extend([terminator, a, b, c])
					cte += -1
				else:
					TriangleStrip.append(c)
	return (TriangleStrip)


def calculate_packed_normals(normal):
	normal = np.asarray(normal)
	
	nx = normal[0]
	ny = normal[1]
	nz = normal[2]
	
	packed_normal = [0.0, 0.0, 1.0, 0.0]
	if nx == 0.0 and ny == 0.0:
		if nz < 0.0:
			packed_normal[0] = 1.0
			packed_normal[1] = 0.0
			packed_normal[2] = 0.0
	
	elif math.sqrt(nx*nx + ny*ny + nz*nz) == -nz:		# 1e-5 rounds to zero
		if nz < 0.0:
			packed_normal[0] = 1.0
			packed_normal[1] = 0.0
			packed_normal[2] = 0.0
	
	else:
		#signal = 1.0 if math.sqrt(nx*nx + ny*ny) >= 0.0 else -1.0
		const = 1.0/(nz + math.sqrt(nx*nx + ny*ny + nz*nz))
		
		if math.sqrt(nx*nx + ny*ny) < 0.0:
			const = (math.sqrt(nx*nx + ny*ny + nz*nz) - nz)/(nx*nx + ny*ny)
		
		packed_normal[0] = const * nx
		packed_normal[1] = const * ny
	
	#ChebyshevNorm = max(normal, key=abs)
	#if ChebyshevNorm == 0:
	#	packed_normal = [1.0, 0.0, 1.0, 0.0]
	#packed_normal = [nx/ChebyshevNorm, ny/ChebyshevNorm, nz/ChebyshevNorm, 0.0]
	
	#if nz == 0.0:
	#	nz = 1.0
	#packed_normal = [nx/nz, ny/nz, 1.0, 0.0]
	
	# Normalize
	length = 0
	
	for norm in packed_normal:
		length += norm*norm
	
	length = math.sqrt(length)
	for i, norm in enumerate(packed_normal):
		norm /= length
		if norm == 1:
			norm = 0x7FFF
		else:
			norm *= 0x8000
		packed_normal[i] = np.short(norm)
		
	return packed_normal


def normal_to_quaternion(direction):
	# Converting to Vector object
	direction = Vector(direction)
	
	# Normalizing input vector
	direction = direction.normalized()
	
	# Reference vector
	reference_vector = Vector((0.0, 0.0, 1.0))
	reference_quaternion = Quaternion()
	
	# Checking if the vectors are in opposite direction
	if direction.dot(reference_vector) <= -0.99995:
		reference_vector *= -1.0
		reference_quaternion *= -1.0
	
	# Calculate the rotation matrix that rotates the reference vector to the rotated vector
	rotation_matrix = reference_vector.rotation_difference(direction).to_matrix()

	# Convert the rotation matrix back to a quaternion
	reversed_quaternion = rotation_matrix.to_quaternion()

	# Ensure the quaternion has the same sign as the original quaternion
	if reversed_quaternion.dot(reference_quaternion) < 0:
		reversed_quaternion.negate()

	return reversed_quaternion


def normal_to_quaternion_old(direction):
	orig_direction = direction.copy()
	forward = Vector((0.0, 0.0, 1.0))
	up = Vector((0.0, 1.0, 0.0))
	
	# if direction.z < 0:
		# forward.z = -forward.z
	# else:
		# forward.z = forward.z
	
	rot1 = RotationBetweenVectors(forward, direction)
	right = direction.cross(up)
	up = right.cross(direction)
	real_up = Vector((0.0, 1.0, 0.0))
	new_up = rot1 @ real_up
	
	rot2 = RotationBetweenVectors(new_up, up)
	res = rot2 @ rot1
	
	q = Quaternion()
	q.x, q.y, q.z, q.w = res.x, res.y, res.z, res.w
	q = q.normalized()
	
	# a = direction.cross(forward)
	# q2 = Quaternion()
	# q2.x, q2.y, q2.z = a
	# q2.w = math.sqrt((direction.length**2) * (forward.length**2)) + direction.dot(forward)
	# q2 = q2.normalized()
	
	return q


def RotationBetweenVectors(forward, direction):
	forward = forward.normalized()
	direction = direction.normalized()
	
	cosTheta = forward.dot(direction)
	if cosTheta < -1.0 + 0.001:
		## special case when vectors in opposite directions:
		## there is no "ideal" rotation axis
		## So guess one; any will do as long as it's perpendicular to start
		
		axis = Vector((0.0, 1.0, 0.0)).cross(forward)

		axis = axis.normalized()
		
		q = Quaternion()
		q.x, q.y, q.z = axis
		q.w = 0.0
		
		return q
		
	axis = forward.cross(direction)
	s = math.sqrt((1.0 + cosTheta) * 2.0)
	invs = 1.0 / s
	q = Quaternion()
	q.x, q.y, q.z = axis * invs
	q.w = s * 0.5
	
	return q


def quaternion_to_short(quaternion):
	quaternion = Vector(quaternion)
	quaternion = np.short((quaternion/quaternion.magnitude)*0x7FFF)
	quat3 = [quaternion[1], quaternion[2], quaternion[3], quaternion[0]]
	
	return quat3


def quaternion_to_ubyte(quaternion):
	quaternion = Vector(quaternion)
	
	quaternion = quaternion*0.5 + Vector((0.5,) * 4)
	quaternion = np.ubyte(quaternion*0xFF)
	quat3 = [quaternion[1], quaternion[2], quaternion[3], quaternion[0]]
	
	return quat3


def swizzle_normals(result, vec, index, prop):
	if prop == '+X':
		result[index] = vec[0]
	elif prop == '-X':
		result[index] = -vec[0]
	elif prop == '+Y':
		result[index] = vec[1]
	elif prop == '-Y':
		result[index] = -vec[1]
	elif prop == '+Z':
		result[index] = vec[2]
	elif prop == '-Z':
		result[index] = -vec[2]


def calculate_tangents(indices_buffer, mesh_vertices_buffer, mShaderId):
	tan1 = {}
	tan2 = {}
	
	for face in indices_buffer:
		i1 = face[0]
		i2 = face[1]
		i3 = face[2]
		
		v1 = mesh_vertices_buffer[i1][1]
		v2 = mesh_vertices_buffer[i2][1]
		v3 = mesh_vertices_buffer[i3][1]
		
		if mShaderId in ("A9_EF_09_00", "AB_EF_09_00", "A5_EF_09_00"):
			w1 = mesh_vertices_buffer[i1][6]
			w2 = mesh_vertices_buffer[i2][6]
			w3 = mesh_vertices_buffer[i3][6]
		else:
			w1 = mesh_vertices_buffer[i1][5]
			w2 = mesh_vertices_buffer[i2][5]
			w3 = mesh_vertices_buffer[i3][5]
		
		x1 = v2[0] - v1[0]
		x2 = v3[0] - v1[0]
		y1 = v2[1] - v1[1]
		y2 = v3[1] - v1[1]
		z1 = v2[2] - v1[2]
		z2 = v3[2] - v1[2]
		
		s1 = w2[0] - w1[0]
		s2 = w3[0] - w1[0]
		t1 = w2[1] - w1[1]
		t2 = w3[1] - w1[1]
		
		try:
			r = 1.0/(s1*t2 - s2*t1)
		except:
			#r = 0.0
			r = 1.0
		
		sdir = [(t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r, (t2 * z1 - t1 * z2) * r]
		tdir = [(s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r, (s1 * z2 - s2 * z1) * r]
		
		try:
			_ = tan1[i1]
			_ = tan2[i1]
		except:
			tan1[i1] = [0.0, 0.0, 0.0]
			tan2[i1] = [0.0, 0.0, 0.0]
		
		try:
			_ = tan1[i2]
			_ = tan2[i2]
		except:
			tan1[i2] = [0.0, 0.0, 0.0]
			tan2[i2] = [0.0, 0.0, 0.0]
		
		try:
			_ = tan1[i3]
			_ = tan2[i3]
		except:
			tan1[i3] = [0.0, 0.0, 0.0]
			tan2[i3] = [0.0, 0.0, 0.0]
		
		
		tan1[i1] = list(map(float.__add__, tan1[i1], sdir))
		tan1[i2] = list(map(float.__add__, tan1[i2], sdir))
		tan1[i3] = list(map(float.__add__, tan1[i3], sdir))
		
		tan2[i1] = list(map(float.__add__, tan2[i1], tdir))
		tan2[i2] = list(map(float.__add__, tan2[i2], tdir))
		tan2[i3] = list(map(float.__add__, tan2[i3], tdir))
	
	import warnings
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore", message="invalid value encountered in divide")
		warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")
		for index, vertex in mesh_vertices_buffer.items():
			n = np.asarray(vertex[2])
			t = np.asarray(tan1[index])
			
			if mShaderId == "2A_79_00_00":
				t = t * -1.0
			
			#if use_Rotation:
			#	n = np.asarray([n[0], n[2], -n[1]])
			
			# Gram-Schmidt orthogonalize
			tmp = t - n* np.dot(n, t)
			tmp = tmp/np.linalg.norm(tmp)
			
			if np.any(np.isnan(tmp)):
				tmp = [0.0, 0.0, 1.0]
			
			mesh_vertices_buffer[index][3] = tmp[:]
			
			# Calculate handedness
			#t_2 = np.asarray(tan2[index])
			#signal = -1.0 if (np.dot(np.cross(n, t), t_2) < 0.0) else 1.0
			##if mShaderId == "2A_79_00_00":
			##	tmp[0] = -1.0 * tmp[0]
			##	tmp[1] = -1.0 * tmp[1]
			##	tmp[2] = -1.0 * tmp[2]
			
			##binormal = np.cross(n, t) #bad result
			#binormal = np.cross(t, n)
			#if mShaderId == "2A_79_00_00":
			#	binormal = np.cross(n, t)
			#binormal = binormal/np.linalg.norm(binormal)
			#mesh_vertices_buffer[index][13] = binormal[:]
			
			##tangents[a][0] = signal*tmp[0]
			##tangents[a][1] = signal*tmp[1]
			##tangents[a][2] = signal*tmp[2]
			
			##tangents[a][0] =  tmp[0]
			##tangents[a][1] =  tmp[2]
			##tangents[a][2] = -tmp[1]
			
			# Binormal (or bitangent)
			t_2 = np.asarray(tan2[index])
			binormal_sign = -1.0 if (np.dot(np.cross(n, tmp), t_2) < 0.0) else 1.0
			binormal = binormal_sign * np.cross(n, tmp)
			binormal = binormal/np.linalg.norm(binormal)
			if mShaderId == "2A_79_00_00":
				binormal = np.asarray((1.0, 1.0, 0.0))
			mesh_vertices_buffer[index][13] = binormal[:]
	
	return 0


def calculate_mpPolySoup(miNumPolySoups, mpaPolySoupBoxesEnd):
	mpPolySoup = mpaPolySoupBoxesEnd
	for i in range(0, math.ceil(miNumPolySoups/4)):
		mpPolySoup += 0x150
	return int(mpPolySoup)


def get_vertex_semantic(semantic_type):
	semantics = ["", "POSITION", "POSITIONT", "NORMAL", "COLOR",
				 "TEXCOORD1", "TEXCOORD2", "TEXCOORD3", "TEXCOORD4", "TEXCOORD5", "TEXCOORD6", "TEXCOORD7", "TEXCOORD8",
				 "BLENDINDICES", "BLENDWEIGHT", "TANGENT", "BINORMAL", "COLOR2", "PSIZE"]
	
	return semantics[semantic_type]


def get_vertex_data_type(data_type):
	data_types = {2 : ["4f", 0x10],
				  3 : ["4I", 0x10],
				  4 : ["4i", 0x10],
				  6 : ["3f", 0xC],
				  7 : ["3I", 0xC],
				  8 : ["3i", 0xC],
				  10 : ["4e", 0x8], # numpy
				  11 : ["4H", 0x8], #normalized
				  12 : ["4I", 0x10],
				  13 : ["4hnorm", 0x8], #normalized
				  14 : ["4i", 0x10],
				  16 : ["2f", 0x8],
				  17 : ["2I", 0x8],
				  18 : ["2i", 0x8],
				  28 : ["4B", 0x4], #normalized
				  30 : ["4B", 0x4],
				  32 : ["4b", 0x4],
				  34 : ["2e", 0x4],
				  35 : ["2H", 0x4], #normalized
				  36 : ["2H", 0x4],
				  37 : ["2h", 0x4], #normalized
				  38 : ["2h", 0x4],
				  40 : ["1f", 0x4],
				  41 : ["1f", 0x4],
				  42 : ["1I", 0x4],
				  43 : ["1i", 0x4],
				  49 : ["2B", 0x2], #normalized
				  50 : ["2B", 0x2],
				  51 : ["2b", 0x2], #normalized
				  52 : ["2b", 0x2],
				  54 : ["1e", 0x2],
				  57 : ["1H", 0x2],
				  59 : ["1h", 0x2],
				  61 : ["1B", 0x1], #normalized
				  62 : ["1B", 0x1],
				  63 : ["1b", 0x1], #normalized
				  64 : ["1b", 0x1]}
	
	return data_types[data_type]


def get_raster_format(fourcc):
	format_from_fourcc = {	"B8G8R8A8" : 87, #21
							"R8G8B8A8" : 28,
							"A8R8G8B8" : 255,
							"DXT1" : 71,
							"DXT3" : 73,
							"DXT5" : 77}
	
	try:
		return format_from_fourcc[fourcc]
	except:
		print("WARNING: DXT compression not identified: %s. Setting as 'R8G8B8A8'" % fourcc)
		return 28


def get_mShaderID(shader_description, resource_type): #OK
	shaders = {	'UIMapShader': '00_2F_0C_00',
				'UIFlameShaderNonAdditive': '01_66_0B_00',
				'World_Diffuse_Dirt_Normal_Specular_Overlay_Singlesided': '02_E8_12_00',
				'Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery': '06_35_03_00',
				'VfxMesh': '06_93_03_00',
				'World_Diffuse_Specular_Normal_Parallax_Singlesided': '06_E8_12_00',
				'Deflicker_World_Diffuse_Normal_Specular_Singlesided': '08_E8_12_00',
				'Deflicker_World_Diffuse_Normal_Specular_Overlay_Singlesided': '0A_E8_12_00',
				'World_Diffuse_Reflective_Overlay_Lightmap_Singlesided': '0B_6C_07_00',
				'Deflicker_World_Diffuse_Normal_Specular_Overlay_IlluminanceNight_Singlesided': '0C_E8_12_00',
				'Deflicker_World_Diffuse_Normal_Specular_Overlay_Illuminance_Singlesided': '0E_E8_12_00',
				'World_Diffuse_Specular_Overlay_IlluminanceNight_1Bit_Singlesided': '10_1A_09_00',
				'Vehicle_Opaque_Two_PaintGloss_Textured_LightmappedLights_Livery_Wrap': '10_AF_13_00',
				'World_DiffuseBlend_Normal_Overlay_Lightmap_Singlesided': '12_1A_09_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Wrap': '12_AF_13_00',
				'World_Diffuse_Specular_Singlesided': '13_2F_06_00',
				'World_Diffuse_1Bit_Dirt_Normal_Specular_Overlay_Singlesided': '13_E8_12_00',
				'World_Diffuse_Specular_1Bit_Lightmap_Doublesided': '14_1A_09_00',
				'Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap': '14_AF_13_00',
				'Cable_GreyScale_Doublesided': '15_14_00_00',
				'Vehicle_Opaque_Emissive_AO': '19_D4_03_00',
				'SSAO': '19_E8_12_00',
				'Vehicle_Opaque_Emissive_Reflective_AO': '1B_D4_03_00',
				'World_Normal_Specular_Overlay_Singlesided': '1C_31_06_00',
				'TextBoldShader': '1C_8C_04_00',
				'World_Diffuse_Specular_Parallax_Singlesided': '1D_2F_06_00',
				'Blur': '1D_E8_12_00',
				'TriggerShader': '1E_67_03_00',
				'Flag_Opaque_Doublesided': '1F_1A_09_00',
				'World_Diffuse_Specular_Overlay_Singlesided': '1F_2F_06_00',
				'TextDropShadow': '1F_8C_04_00',
				'LightBuffer_Cone4': '20_95_09_00',
				'World_Diffuse_Dirt_Normal_SpecMap_Overlay_Singlesided': '20_E8_12_00',
				'LightBuffer_KeylightAndAmbient_ProjectedShadowTexture': '21_73_03_00',
				'VfxMeshNormalMap': '21_93_03_00',
				'TextShader': '22_8C_04_00',
				'LightBuffer_Point4': '22_95_09_00',
				'VfxMeshCarPaint': '23_93_03_00',
				'DEBUG_TRIGGER_Illuminance_Greyscale_Singlesided': '23_D0_02_00',
				'TextBoldDropShadow': '24_8C_04_00',
				'DriveableSurface_Car_Select': '24_E8_12_00',
				'CatsEyes': '25_92_03_00',
				'World_DiffuseBlend_Normal_Overlay_Singlesided': '27_6E_07_00',
				'TextOutline': '27_8C_04_00',
				'Vfx_CoronaBeam': '27_E8_12_00',
				'DiffuseSpecmapNormalMap_DirtMap': '28_6C_07_00',
				'LightBuffer_Cone3': '28_95_09_00',
				'Tree_Translucent_1Bit_Doublesided': '29_1A_09_00',
				'World_Diffuse_Normal_SpecMap_Singlesided': '29_E8_12_00',
				'LightBuffer_Cone2': '2A_95_09_00',
				'Vehicle_1Bit_Textured_NormalMapped_Reflective_Emissive_AO_Livery': '2B_58_05_00',
				'DriveableSurface_Car_Select_Simple': '2B_E8_12_00',
				'LightBuffer_Point3': '2D_95_09_00',
				'World_Diffuse_Normal_SpecMap_Overlay_Singlesided': '2D_E8_12_00',
				'Diffuse_Greyscale_Doublesided': '2E_1D_00_00',
				'LightBuffer_Point2': '2F_95_09_00',
				'Vehicle_Glass_Coloured_NoNormalMap': '2F_E8_12_00',
				'Vehicle_Glass_Emissive_Coloured_NoNormalMap': '31_E8_12_00',
				'World_DiffuseBlend_Normal_Overlay_LightmapNight_Singlesided': '33_1A_09_00',
				'Vehicle_Glass_Emissive_Coloured_Singlesided_NoNormalMap': '33_E8_12_00',
				'DICETerrain3_Proto': '35_0E_05_00',
				'World_Diffuse_Specular_1Bit_LightmapNight_Doublesided': '35_1A_09_00',
				'Vehicle_Glass_LocalEmissive_Coloured_NoNormalMap': '35_E8_12_00',
				'Road_Proto': '36_30_02_00',
				'World_Diffuse_Specular_Overlay_LightmapNight_Singlesided': '36_6E_07_00',
				'LightBuffer_Cop4': '36_95_09_00',
				'World_Normal_Specular_Overlay_LightmapNight_Singlesided': '38_6E_07_00',
				'LightBuffer_Cop3': '38_95_09_00',
				'World_Diffuse_Specular_Normal_Parallax_WindowTex_Singlesided': '39_E8_12_00',
				'HidingSpot_Proto_LightmapNight': '3A_6E_07_00',
				'LightBuffer_Cop2': '3A_95_09_00',
				'Vehicle_Wheel_Alpha_Normalmap': '3B_58_05_00',
				'GBufferCompositeRearViewMirror': '3C_73_03_00',
				'LightBuffer_Cop': '3C_95_09_00',
				'World_Diffuse_Specular_Normal_Overlay_Lightmap_Singlesided': '3C_E8_12_00',
				'FlaptGenericShader3D': '3D_CD_03_00',
				'World_Diffuse_Reflective_Overlay_LightmapNight_Singlesided': '3E_6E_07_00',
				'DriveableSurface_AlphaMask_LightmapNight': '40_6E_07_00',
				'Diffuse_Opaque_Singlesided_Skin_ObjectAO': '40_73_03_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride': '41_C6_01_00',
				'DriveableSurface_LightmapNight': '42_6E_07_00',
				'Diffuse_Opaque_Singlesided_ObjectAO': '42_73_03_00',
				'Vehicle_Wheel_1Bit_Alpha_Normalmap': '43_52_04_00',
				'BlitBilateralUpsample': '43_93_03_00',
				'Vehicle_Glass_Coloured': '43_C6_01_00',
				'DriveableSurface_Decal_LightmapNight': '44_6E_07_00',
				'Diffuse_Greyscale_Doublesided_ObjectAO': '44_73_03_00',
				'Vehicle_Wheel_1Bit_Alpha': '45_52_04_00',
				'GBufferComposite': '45_61_04_00',
				'Vehicle_Glass_Emissive_Coloured': '45_C6_01_00',
				'World_CopStudio_Specular_Reflective_Singlesided': '46_0F_05_00',
				'DriveableSurface_RetroreflectivePaint_LightmapNight': '46_6E_07_00',
				'Diffuse_1Bit_Singlesided_ObjectAO': '46_73_03_00',
				'VfxParticles_MotionBlurSpriteUntex': '46_92_03_00',
				'Diffuse_1Bit_Doublesided_Skin_ObjectAO': '48_73_03_00',
				'HelicopterRotor_GreyScale_Doublesided': '49_31_06_00',
				'Vehicle_Opaque_Textured_Phong': '4A_62_02_00',
				'Diffuse_1Bit_Doublesided_ObjectAO': '4A_73_03_00',
				'LineariseDepthDownsample': '4C_E8_12_00',
				'Vehicle_Opaque_Textured_Normalmapped_Reflective_AO': '4E_62_02_00',
				'Vehicle_Greyscale_Textured_Normalmapped_Reflective': '50_62_02_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery': '52_C6_01_00',
				'DICETerrain3Cheap_Proto': '53_6B_07_00',
				'Vehicle_Opaque_Textured_Reflective': '54_62_02_00',
				'World_Diffuse_Specular_Overlay_IlluminanceNight_Singlesided': '55_18_09_00',
				'LightBuffer_KeylightAndAmbient_ProjectedShadowTexture_LowQuality': '55_73_03_00',
				'Vehicle_Opaque_Textured': '56_62_02_00',
				'DriveableSurface_Lightmap_Car_Select': '56_C4_07_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery': '56_C6_01_00',
				'Vehicle_Opaque_Textured_Normalmapped_AO': '58_62_02_00',
				'Blit2d': '59_03_04_00',
				'Diffuse_Opaque_Singlesided': '5A_17_00_00',
				'Flag_VerticalBanner_Opaque_Doublesided': '5A_1A_09_00',
				'DriveableSurface_RetroreflectivePaint_Lightmap_Car_Select': '5A_C4_07_00',
				'LightBuffer_Point': '5B_C6_01_00',
				'Foliage_1Bit_Doublesided': '5D_03_04_00',
				'Vehicle_Opaque_Two_PaintGloss_Textured_LightmappedLights_Livery': '5D_52_04_00',
				'LightBuffer_Cone': '5D_C6_01_00',
				'Diffuse_1Bit_Doublesided': '5E_17_00_00',
				'Water_Proto_Cheap': '5E_18_09_00',
				'NewSky': '60_93_08_00',
				'PlanarReflection_DepthBufferConversion_2d': '61_03_04_00',
				'Illuminance_Diffuse_Opaque_Singlesided': '61_17_00_00',
				'DiffuseSpecmapNormalMap': '61_C6_01_00',
				'UIMovieShader': '62_8C_03_00',
				'SeparableGaussian_2d': '63_03_04_00',
				'World_Tourbus_Normal_Reflective_Overlay_Singlesided': '63_2D_0C_00',
				'DriveableSurface_AlphaMask_Lightmap': '63_6B_07_00',
				'Armco_Opaque_Doublesided': '63_7F_02_00',
				'DriveableSurface_Lightmap': '65_6B_07_00',
				'LightBuffer_KeylightAndAmbientNoShadow': '66_03_04_00',
				'DriveableSurface_Decal_Lightmap': '67_6B_07_00',
				'UIGenericDestAlphaModulateShader': '68_93_08_00',
				'LightBuffer_KeylightAndAmbient': '68_C6_01_00',
				'DriveableSurface_RetroreflectivePaint_Lightmap': '69_6B_07_00',
				'UIGenericAlphaLuminanceShader': '6A_93_08_00',
				'HidingSpot_Proto_Lightmap': '6B_6B_07_00',
				'UIAutologShader': '6B_CD_03_00',
				'UIMovieAdditiveShader': '6E_8C_03_00',
				'Blit2d_GammaCorrection': '70_03_04_00',
				'VfxParticles_DiffusePremultiplied': '70_92_03_00',
				'Blit2d_AlphaAsColour': '73_03_04_00',
				'Chevron': '74_1A_09_00',
				'Bush_Translucent_1Bit_Doublesided': '74_2D_0C_00',
				'LightBuffer_KeylightAndAmbient_SingleCSM': '76_03_04_00',
				'VfxParticles_Diffuse_AlphaErosion': '78_FF_07_00',
				'Blit2d_ClearGBuffer': '79_03_04_00',
				'TextGlow': '79_8B_03_00',
				'UIRearViewMirrorShader': '79_8C_03_00',
				'Foliage_LargeSprites_Proto': '7B_18_09_00',
				'GBufferCompositeNoFog': '7C_03_04_00',
				'VfxParticles_Diffuse_AlphaErosion_SubUV': '7D_FF_07_00',
				'LightBuffer_KeylightAndAmbient_SingleCSM_NoSpecular': '7F_03_04_00',
				'LightBuffer_KeylightAndAmbient_NoSpecular': '81_03_04_00',
				'Vfx_SkidMarks': '82_92_01_00',
				'TextAdditiveShader': '83_8C_03_00',
				'Vehicle_Glass_Emissive_Coloured_Singlesided': '84_52_04_00',
				'Vehicle_Opaque_Textured_NormalMapped_Reflective_LocalEmissive_AO': '85_0A_0A_00',
				'GBufferCompositeDepthWrite': '86_03_04_00',
				'DiffuseSpecNormalMap_1Bit': '86_B5_03_00',
				'DriveableSurface_RetroreflectivePaint_LineFade': '8A_03_04_00',
				'Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO': '8A_62_02_00',
				'CatsEyesGeometry': '8B_93_03_00',
				'DriveableSurface_RetroreflectivePaint_Lightmap_LineFade': '8C_03_04_00',
				'World_Diffuse_Specular_Reflective_Singlesided': '8C_6C_07_00',
				'Blit2d_EdgeDetect_MotionBlur': '8F_03_04_00',
				'Diffuse_1Bit_Doublesided_Skin': '95_26_04_00',
				'Diffuse_1Bit_Singlesided': '97_1A_00_00',
				'Diffuse_Opaque_Singlesided_Skin': '97_26_04_00',
				'DriveableSurface': '97_92_03_00',
				'ChevronBlockRoad': '99_48_06_00',
				'Foliage_Proto': '9A_0D_05_00',
				'World_Normal_Specular_Overlay_Lightmap_Singlesided': '9B_6A_07_00',
				'World_Diffuse_Specular_Overlay_Lightmap_Singlesided': '9D_6A_07_00',
				'UIAdditiveOverlayShader': '9E_8C_03_00',
				'DriveableSurface_Decal': 'A3_92_03_00',
				'UIFlameShader': 'A3_CD_03_00',
				'HidingSpot_Proto': 'A4_30_06_00',
				'DriveableSurface_AlphaMask': 'A5_92_03_00',
				'DriveableSurface_RetroreflectivePaint': 'A7_92_03_00',
				'Water_Proto': 'AC_30_06_00',
				'Fence_GreyScale_Doublesided': 'AF_6C_07_00',
				'DriveableSurface_RetroreflectivePaint_LineFade_Rotated_UV': 'B0_2E_0C_00',
				'World_Normal_Reflective_Overlay_Lightmap_Singlesided': 'B0_4E_08_00',
				'UIAdditivePixelate': 'B5_8C_03_00',
				'Skin_World_Diffuse_Specular_Overlay_Singlesided': 'B7_6C_07_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights': 'B8_1E_00_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery_Wrap': 'B8_6C_13_00',
				'DriveableSurface_CarPark': 'BA_1B_09_00',
				'UIMovieShaderSubOverlay': 'BA_57_0B_00',
				'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap': 'BA_6C_13_00',
				'UIAdditiveShader': 'BA_8B_03_00',
				'Vehicle_Tyre': 'BB_1E_00_00',
				'DriveableSurface_AlphaMask_CarPark': 'BC_1B_09_00',
				'Vehicle_Wheel_Alpha_Blur_Normalmap': 'BC_1E_00_00',
				'UIMovieShaderAddOverlay': 'BC_57_0B_00',
				'Vehicle_Wheel_Opaque': 'BD_1E_00_00',
				'VfxParticles_Diffuse': 'BD_92_01_00',
				'DriveableSurface_RetroreflectivePaint_CarPark': 'BE_1B_09_00',
				'Vehicle_Wheel_Opaque_Blur': 'BE_1E_00_00',
				'DriveableSurface_Decal_CarPark': 'C0_1B_09_00',
				'DriveableSurface_RetroreflectivePaint_LineFade_Rotated_UV_02': 'C0_2E_0C_00',
				'Vfx_Corona': 'C2_92_01_00',
				'DiffuseSpecmapNormalMap_Overlay': 'C6_30_06_00',
				'Vfx_CoronaVisibilityTest': 'C9_92_01_00',
				'Character_Opaque_Textured_NormalMap_SpecMap_Skin': 'CB_51_04_00',
				'Vfx_CoronaFlare': 'CB_92_01_00',
				'Vehicle_Wheel_Brakedisc_1Bit_Blur_Normalmap': 'CB_A9_01_00',
				'Waterfall_Proto': 'CD_30_06_00',
				'Vehicle_Opaque_Textured_NormalMapped_Emissive_AO': 'CD_D0_03_00',
				'Character_Greyscale_Textured_Doublesided_Skin': 'CF_51_04_00',
				'VfxParticles_DiffusePremultiplied_SubUV': 'CF_6E_07_00',
				'Sign_RetroReflective': 'D2_B6_03_00',
				'DICETerrain3NoRGB_Proto': 'D9_1B_09_00',
				'Vehicle_Glass_Emissive_Coloured_Wrap': 'DB_6C_13_00',
				'Fence_GreyScale_Singlesided': 'DC_0E_05_00',
				'MapIconShader': 'DD_9A_05_00',
				'Groundcover_Proto': 'DE_72_03_00',
				'Skin_World_Diffuse_Specular_Reflective_Singlesided': 'DF_6C_07_00',
				'Foliage_1Bit_Normal_Spec_Doublesided': 'DF_E7_12_00',
				'VfxParticles_Diffure_SubUV': 'E0_FE_07_00',
				'Bush_Translucent_1Bit_Normal_Spec_Doublesided': 'E1_E7_12_00',
				'Deflicker_World_Diffuse_Specular_Singlesided': 'E2_0E_05_00',
				'DICETerrain3CliffsOnly_Proto': 'E2_1B_09_00',
				'BlobbyShadow_Greyscale_Doublesided': 'E3_13_00_00',
				'Deflicker_World_Diffuse_Specular_Overlay_Singlesided': 'E4_0E_05_00',
				'Foliage_Proto_Spec_Normal': 'E5_E7_12_00',
				'Deflicker_World_Diffuse_Specular_Overlay_Illuminance_Singlesided': 'E6_0E_05_00',
				'Vehicle_Glass_LocalEmissive_Coloured': 'E6_92_01_00',
				'Foliage_LargeSprites_Proto_Spec_Normal': 'E7_E7_12_00',
				'World_Diffuse_Specular_Overlay_Illuminance_Singlesided': 'E8_6A_07_00',
				'DebugIrradiance_1Bit_Singlesided_2d': 'EA_13_00_00',
				'World_Diffuse_Specular_Illuminance_Singlesided': 'EB_6A_07_00',
				'Vehicle_Rearlights_Heightmap': 'EB_6E_03_00',
				'World_DiffuseBlend_Specular_Overlay_Singlesided': 'F1_30_06_00',
				'Vehicle_1Bit_Textured_Normalmapped_Reflective': 'F1_D3_03_00',
				'Deflicker_World_Diffuse_Specular_Overlay_IlluminanceNight_Singlesided': 'F1_D8_0B_00',
				'Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery': 'F3_D0_03_00',
				'Vehicle_Opaque_Reflective': 'F3_D3_03_00',
				'LightBuffer_ProjectedTexture': 'F6_6E_03_00',
				'DriveableSurface_RetroreflectivePaint_Lightmap_LineFade_rotatedUV': 'F9_2E_0C_00',
				'Vehicle_Opaque_Textured_NormalMapped_Emissive_AO_Livery': 'FA_D0_03_00',
				'DriveableSurface_RetroreflectivePaint_Lightmap_LineFade_rotatedUV_02': 'FB_2E_0C_00',
				'Blit2d_AutomaticExposureMeter': 'FB_72_03_00',
				'FlaptGenericShader': 'FE_27_00_00',
				'Vehicle_Greyscale_Textured_Normalmapped': 'FE_D0_03_00',
				'World_Diffuse_Specular_FlashingNeon_Singlesided': 'FF_0E_05_00'}
	
	# Adding custom shaders
	try:
		shaders.update(custom_shaders())
	except:
		print("WARNING: custom_shaders function not found. Custom data will not be available.")
	
	try:
		mShaderId = shaders[shader_description]
	except:
		mShaderId = ""
		try:
			from difflib import get_close_matches
			shader_description_ = shader_description
			close_shaders = get_close_matches(shader_description.replace("NFS13",""), shaders.keys())
			for i in range(0, len(close_shaders)):
				if resource_type == "InstanceList":
					if not close_shaders[i].startswith("Vehicle"):
						shader_description = close_shaders[i]
						mShaderId = shaders[shader_description]
						print("WARNING: getting similar shader type for shader %s: %s" % (shader_description_, shader_description))
						break
				elif resource_type == "CharacterSpec":
					if close_shaders[i].startswith("Character"):
						shader_description = close_shaders[i]
						mShaderId = shaders[shader_description]
						print("WARNING: getting similar shader type for shader %s: %s" % (shader_description_, shader_description))
						break
				else:
					if close_shaders[i].startswith("Vehicle"):
						shader_description = close_shaders[i]
						mShaderId = shaders[shader_description]
						print("WARNING: getting similar shader type for shader %s: %s" % (shader_description_, shader_description))
						break
		except:
			mShaderId = ""
		if mShaderId == "":
			if resource_type == "InstanceList":
				shader_description = 'World_Diffuse_Specular_Singlesided'
				mShaderId = shaders[shader_description]
			elif resource_type == "GraphicsSpec":
				shader_description = 'Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap'
				mShaderId = shaders[shader_description]
			elif resource_type == "WheelGraphicsSpec":
				shader_description = 'Vehicle_Wheel_Opaque'
				mShaderId = shaders[shader_description]
			elif resource_type == "CharacterSpec":
				shader_description = 'Character_Opaque_Textured_NormalMap_SpecMap_Skin'
				mShaderId = shaders[shader_description]
	
	mShaderId = shaders[shader_description]
	return (mShaderId, shader_description)


def get_collision_tag(mu16CollisionTag_part0):
	mu16CollisionTag_part0 = mu16CollisionTag_part0.lower()
	collisionTag = {'tarmac': 0x0003,
				    'tarmac_dry': 0x6003,
				    'tarmac_halfwet': 0x2003,
				    'tarmac_leaves': 0x2003,
				    'tarmac_leaves_dry': 0xC003,
				    'tarmac_leaves_halfwet': 0x8003,
				    'gutter': 0x0003,
				    'gutter_dry': 0x8003,
				    'gutter_halfWet': 0x4003,
				    'gutter_leaves': 0x0003,
				    'gutter_leaves_dry': 0xA003,
				    'gutter_leaves_halfwet': 0x6003,
				    'urbanoffroad': 0x4001,
				    'urbanoffroad_dry': 0xE001,
				    'urbanoffroad_wet': 0x6001,
				    'urbanoffroad_halfwet': 0xA001,
				    'urbanoffroad_leaves': 0x4001,
				    'urbanoffroad_leaves_dry': 0x0001,
				    'urbanoffroad_leaves_halfwet': 0xC001,
				    'cobble': 0x2001,
				    'concrete_driveable': 0xC001,
				    'dirt': 0xE001,
				    'grass': 0x8001,
				    'metal': 0xA001,
				    'sand': 0xC001,
				    'slow': 0xE001,
				    'standing_water': 0x0001,
				    'teflon': 0x4001,
				    'teflon_no_grip': 0x6001,
				    'wood': 0xE001,
					'none': 0x0000}
	
	
	if mu16CollisionTag_part0 in collisionTag:
		return collisionTag[mu16CollisionTag_part0]
	else:
		try:
			return int(mu16CollisionTag_part0, 16)
		except:
			return -1


def get_neighbour_flags(Flag):
	NeighbourFlags = {0x0: 'E_RENDERFLAG_NONE',
					  0x1: 'E_NEIGHBOURFLAG_RENDER',
					  0x2: 'E_NEIGHBOURFLAG_UNKNOWN_2',
					  0x3: 'E_NEIGHBOURFLAG_IMMEDIATE'}
	
	if Flag in NeighbourFlags:
		return NeighbourFlags[Flag]
	
	return Flag


def get_neighbour_flags_code(NeighbourFlag):
	NeighbourFlags = {'E_RENDERFLAG_NONE': 0x0,
				'E_NEIGHBOURFLAG_RENDER': 0x1,
				'E_NEIGHBOURFLAG_UNKNOWN_2': 0x2,
				'E_NEIGHBOURFLAG_IMMEDIATE': 0x3}
	
	if NeighbourFlag in NeighbourFlags:
		return NeighbourFlags[NeighbourFlag]
	
	return NeighbourFlag


def get_minimum_bounding_box(mesh, index):
	
	def convex_hull_bases(mesh, index):
		bm = bmesh.new()
		bm.from_mesh(mesh)
		
		# Getting vertices
		verts = []
		for face in bm.faces:
			if face.hide == False:
				mesh_index = face.material_index
				
				if mesh_index != index:
					continue
				
				for vert in face.verts:
					if vert in verts:
						continue
					verts.append(vert)
		
		# Getting convex hull
		chull_out = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)

		chull_geom = chull_out["geom"]
		chull_points = np.array([bmelem.co for bmelem in chull_geom if isinstance(bmelem, bmesh.types.BMVert)])

		bases = []

		for elem in chull_geom:
			if not isinstance(elem, bmesh.types.BMFace):
				continue
			if len(elem.verts) != 3:
				continue

			face_normal = elem.normal
			if np.allclose(face_normal, 0, atol=0.00001):
				continue

			for e in elem.edges:
				v0, v1 = e.verts
				edge_vec = (v0.co - v1.co).normalized()
				co_tangent = face_normal.cross(edge_vec)
				basis = (edge_vec.copy(), co_tangent.copy(), face_normal.copy())
				bases.append(basis)
		
		bm.free()
		
		return (chull_points, bases)
		

	def rotating_calipers(hull_points: np.ndarray, bases):
		min_bb_basis = None
		min_bb_min = None
		min_bb_max = None
		min_vol = math.inf
		for basis in bases:
			rot_points = hull_points.dot(np.linalg.inv(basis))
			# Equivalent to: rot_points = hull_points.dot(np.linalg.inv(np.transpose(basis)).T)

			bb_min = rot_points.min(axis=0)
			bb_max = rot_points.max(axis=0)
			volume = (bb_max - bb_min).prod()
			if volume < min_vol:
				min_bb_basis = basis
				min_vol = volume

				min_bb_min = bb_min
				min_bb_max = bb_max

		return np.array(min_bb_basis), min_bb_max, min_bb_min
	
	chull_points, bases = convex_hull_bases(mesh, index)
	bb_basis, bb_max, bb_min = rotating_calipers(chull_points, bases)
	
	bb_basis_mat = bb_basis.T
	
	bb_dim = bb_max - bb_min
	bb_dim = (bb_max - bb_min) + Vector((0.2, 0.2, 0.2))
	bb_center = (bb_max + bb_min) / 2.0
	
	mat = Matrix.Translation(bb_center.dot(bb_basis)) @ Matrix(bb_basis_mat).to_4x4() @ Matrix(np.identity(3) * bb_dim / 2.0).to_4x4()
	translation = mat.to_translation()
	scale = mat.to_scale()
	quaternion = mat.to_quaternion()
	
	return (list(translation[:]), list(scale[:]), list(quaternion[:]))


def resourcetype_to_type_id(resource_type):
	resources_types = {	'Texture': 0x00000001,
						'Material': 0x00000002,
						'VertexDescriptor': 0x00000003,
						'VertexProgramState': 0x00000004,
						'Renderable': 0x00000005,
						'MaterialState': 0x00000006,
						'SamplerState': 0x00000007,
						'ShaderProgramBuffer': 0x00000008,
						'GenesysDefinition': 0x00000012,
						'GenesysInstance': 0x00000013,
						'Font': 0x00000030,
						'InstanceList': 0x00000050,
						'Model': 0x00000051,
						'ColourCube': 0x00000052,
						'Shader': 0x00000053,
						'PolygonSoupList': 0x00000060,
						'TextFile': 0x00000070,
						'Ginsu': 0x00000080,
						'Wave': 0x00000081,
						'ZoneList': 0x00000090,
						'WorldPaintMap': 0x00000091,
						'AnimationList': 0x000000b0,
						'PathAnimation': 0x000000b1,
						'Skeleton': 0x000000b2,
						'VehicleList': 0x00000105,
						'GraphicsSpec': 0x00000106,
						'AIData': 0x00000200,
						'Language': 0x00000201,
						'TriggerData': 0x00000202,
						'RoadData': 0x00000203,
						'DynamicInstanceList': 0x00000204,
						'WorldObject': 0x00000205,
						'ZoneHeader': 0x00000206,
						'VehicleSound': 0x00000207,
						'RoadMapData': 0x00000208,
						'CharacterSpec': 0x00000209,
						'CharacterList': 0x0000020a,
						'ReverbRoadData': 0x0000020c,
						'CameraTake': 0x0000020d,
						'CameraTakeList': 0x0000020e,
						'GroundcoverCollection': 0x0000020f,
						'ControlMesh': 0x00000210,
						'Cutscene': 0x00000211,
						'CutsceneList': 0x00000212,
						'LightInstanceList': 0x00000213,
						'GroundcoverInstances': 0x00000214,
						'BearEffect': 0x00000301,
						'BearGlobalParameters': 0x00000302,
						'ConvexHull': 0x00000303,
						'HSMData': 0x00000501,
						'TrafficData': 0x00000701}
	
	return resources_types[resource_type]


def calculate_resourceid(resource_name):
	ID = hex(zlib.crc32(resource_name.lower().encode()) & 0xffffffff)
	ID = ID[2:].upper().zfill(8)
	ID = '_'.join([ID[::-1][x:x+2][::-1] for x in range(0, len(ID), 2)])
	return ID


def is_sensor_hash_valid(sensor_hash, resource_type):
	sensor_hash = id_to_int(sensor_hash)
	
	hpr_vehicle_hashes = [ 1228515738, 3519270914, 1414867105, 1720035274, 1640180847, 2998789302, 3765218437, 3803230732, 2214824603,
				   1719440823, 1506627702, 2620542409, 1763746883, 2487371287, 1738042927, 950984622, 3969293522, 3247193033,
				   3802643007, 3451996877, 3086769294, 552124085, 3077440739, 2975746644, 12760978, 4094915136, 423717174,
				   3726575266, 3603806162, 2187449469, 1370270881, 1180458428, 389142644, 364896343, 3332757933, 2764340109,
				   2287327543, 2164088672, 2053605152, 4107337161, 3195583546, 2650037437, 2577309593, 2388096960, 2340393187,
				   1907322478, 1264530319, 364590502, 29206738, 3978715724, 575896387, 4263537717, 4255057788, 4146808166,
				   4082154579, 3981679002, 3854983892, 3578477459, 3461569947, 3336904849, 3051761487, 3003223755, 2793911538,
				   2738821590, 2733869466, 2462143042, 2251119103, 2093953902, 2082628764, 2007068982, 1951059167, 1881350704,
				   1528477631, 1254644972, 1113402750, 948666871, 702418594, 611557228, 212191201]
	
	hpr_character_hashes = [4193389566, 4164855389, 4097404144, 3978484263, 3922678795, 3902700559, 3851724589, 3789133558,
							3535380311, 3234641317, 3083568435, 2901491252, 2808575887, 2720759605, 2663933085, 2488010968,
							2408503792, 2376621653, 2323705198, 2315694799, 2288276190, 2201902182, 2161258452, 2145158802,
							2042820099, 2026948428, 1984349567, 1892025777, 1756136100, 1693174227, 1506141215, 1383845371,
							1335897812, 1277500953, 1233783955, 1228515738, 1118774345, 992095887, 763072577, 606936706,
							556726766, 439815644, 343733541, 265811930, 167360538, 78831125]
	
	hpr_trk_hashes = [3805966487, 2077434157, 3959552165, 2600912947, 2092885300, 1213262907, 215224763, 196728226]
	
	if resource_type == "GraphicsSpec":
		return (sensor_hash in hpr_vehicle_hashes)
	elif resource_type == "CharacterSpec":
		return (sensor_hash in hpr_character_hashes)
	elif resource_type == "InstanceList":
		return (sensor_hash in hpr_trk_hashes)
	
	return (sensor_hash in hpr_vehicle_hashes)


def is_valid_id(id):
	id_old = id
	id = id.replace('_', '')
	id = id.replace(' ', '')
	id = id.replace('-', '')
	if len(id) != 8:
		print("ERROR: ResourceId not in the proper format: %s. The format should be like AA_BB_CC_DD." % id_old)
		return False
	try:
		int(id, 16)
	except ValueError:
		print("ERROR: ResourceId is not a valid hexadecimal string: %s" % id_old)
		return False
	
	return True


def bytes_to_id(id):
	id = binascii.hexlify(id)
	id = str(id,'ascii')
	id = id.upper()
	id = '_'.join([id[x : x+2] for x in range(0, len(id), 2)])
	return id


def int_to_id(id):
	id = str(hex(int(id)))[2:].upper().zfill(8)
	id = '_'.join([id[::-1][x : x+2][::-1] for x in range(0, len(id), 2)])
	return id


def id_to_bytes(id):
	id_old = id
	id = id.replace('_', '')
	id = id.replace(' ', '')
	id = id.replace('-', '')
	if len(id) != 8:
		print("ERROR: ResourceId not in the proper format: %s" % id_old)
	try:
		int(id, 16)
	except ValueError:
		print("ERROR: ResourceId is not a valid hexadecimal string: %s" % id_old)
	return bytearray.fromhex(id)


def id_to_int(id):
	id_old = id
	id = id.replace('_', '')
	id = id.replace(' ', '')
	id = id.replace('-', '')
	id = ''.join(id[::-1][x:x+2][::-1] for x in range(0, len(id), 2))
	return int(id, 16)


def id_swap(id):
	id = id.replace('_', '')
	id = id.replace(' ', '')
	id = id.replace('-', '')
	id = '_'.join([id[::-1][x:x+2][::-1] for x in range(0, len(id), 2)])
	return id


def lin2s1(x):
	a = 0.055
	if x <= 0.0031308:
		y = x * 12.92
	elif 0.0031308 < x <= 1 :
		y = 1.055*(x**(1.0/2.4)) - 0.055
	return y


def s2lin(x):
	a = 0.055
	if x <=0.04045 :
		y = x * (1.0 / 12.92)
	else:
		y = pow( (x + a) * (1.0 / (1 + a)), 2.4)
	return y


def calculate_padding(length, alignment):
	division1 = (length/alignment)
	division2 = math.ceil(length/alignment)
	padding = int((division2 - division1)*alignment)
	return padding


def NFSHPLibraryGet():
	spaths = bpy.utils.script_paths()
	for rpath in spaths:
		tpath = rpath + '\\addons\\NeedForSpeedHotPursuit'
		if os.path.exists(tpath):
			npath = '"' + tpath + '"'
			return tpath
	return None


def nvidiaGet():
	spaths = bpy.utils.script_paths()
	for rpath in spaths:
		tpath = rpath + '\\addons\\nvidia-texture-tools-2.1.2-win\\bin64\\nvcompress.exe'
		if os.path.exists(tpath):
			npath = '"' + tpath + '"'
			return npath
		tpath = rpath + '\\addons\\nvidia-texture-tools-2.1.1-win64\\bin64\\nvcompress.exe'
		if os.path.exists(tpath):
			npath = '"' + tpath + '"'
			return npath
	return None


class Suppressor(object):

	def __enter__(self):
		self.stdout = sys.stdout
		sys.stdout = self

	def __exit__(self, type, value, traceback):
		sys.stdout = self.stdout
		if type is not None:
			raise

	def flush(self):
		pass

	def write(self, x):
		pass


@orientation_helper(axis_forward='-Y', axis_up='Z')
class ExportNFSHPR(Operator, ExportHelper):
	"""Export as a Need for Speed Hot Pursuit Remastered (2020) Model file"""
	bl_idname = "export_nfshpr.data"
	bl_label = "Export to folder"
	bl_options = {'PRESET'}

	filename_ext = ""
	use_filter_folder = True

	filter_glob: StringProperty(
			options={'HIDDEN'},
			default="*.dat",
			maxlen=255,
			)
	
	pack_bundle_file: BoolProperty(
			name="Pack bundle",
			description="Check in order to pack the exported files in a bundle",
			default=True,
			)
	
	copy_uv_layer: BoolProperty(
			name="Copy uv layer",
			description="Check in order to allow making a copy of the first UV layer to other if it is non existent on the mesh and it is requested by the shader",
			default=True,
			)
	
	# recalculate_vcolor2: BoolProperty(
			# name="Recalculate vertex normal colors (vcolor2)",
			# description="Check in order to recalculate vertex normal colors. Useful when a game model has been edited",
			# default=False,
			# )
	
	ignore_hidden_meshes: BoolProperty(
			name="Ignore hidden meshes",
			description="Check in order to not export the hidden meshes",
			default=True,
			)
	
	force_shared_asset_as_false: EnumProperty(
		name="Include shared assets",
		options={'ENUM_FLAG'},
		items=(
			  ('MODEL', "Model", "", "MESH_DATA", 2),
			  ('MATERIAL', "Material", "", "MATERIAL", 4),
			  ('TEXTURE', "Texture", "", "TEXTURE", 8),
		),
		description="Which kind of shared asset to force",
		#default={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'},
		)
	
	debug_shared_not_found: BoolProperty(
		name="Resolve is_shared_asset not found",
		description="Check in order to allow setting is_shared_asset as False if an asset is not found in the default library",
		default=True,
		)
	
	debug_use_shader_material_parameters: BoolProperty(
		name="Use default shader parameters",
		description="Check in order to apply the default shader parameters on materials",
		default=False,
		)
	
	debug_use_default_samplerstates: BoolProperty(
		name="Use default sampler states",
		description="Check in order to apply the default sampler states on materials",
		default=False,
		)
	
	if bpy.context.preferences.view.show_developer_ui == True:
		debug_redirect_vehicle: BoolProperty(
			name="Export to another vehicle",
			description="Check in order to redirect the exported vehicle to another one",
			default=False,
			)
		
		debug_new_vehicle_name: StringProperty(
			name="Vehicle ID",
			description="Write the vehicle you want your model to replace",
			default="",
			)
		
	else:
		debug_redirect_vehicle = False
		debug_new_vehicle_name = ""
	
	force_rotation: BoolProperty(
		name="Force rotation on objects",
		description="Check in order to use the global rotation option",
		default=False,
		)
	
	global_rotation: FloatVectorProperty(
		name="Global rotation",
		description="Write the global objects rotation (local space). Use it only if your model got wrongly oriented in-game",
		default=(-90.0, 0.0, 0.0),
		)

	
	def execute(self, context):
		userpath = self.properties.filepath
		if os.path.isfile(userpath):
			self.report({"ERROR"}, "Please select a directory not a file\n" + userpath)
			return {"CANCELLED"}
		if NFSHPLibraryGet() == None:
			self.report({"ERROR"}, "Game library not found, please check if you installed it correctly.")
			return {"CANCELLED"}
		
		global_matrix = axis_conversion(from_forward='Z', from_up='Y', to_forward=self.axis_forward, to_up=self.axis_up).to_4x4()
		
		status = main(context, self.filepath, self.pack_bundle_file, self.ignore_hidden_meshes, self.copy_uv_layer, self.force_rotation, [False, False, False], self.global_rotation,
					  self.force_shared_asset_as_false, self.debug_shared_not_found, self.debug_use_shader_material_parameters,
					  self.debug_use_default_samplerstates, self.debug_redirect_vehicle, self.debug_new_vehicle_name, global_matrix)
		
		if status == {"CANCELLED"}:
			self.report({"ERROR"}, "Exporting has been cancelled. Check the system console for information.")
		return status
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False  # No animation.
		
		sfile = context.space_data
		operator = sfile.active_operator
		
		##
		box = layout.box()
		split = box.split(factor=0.75)
		col = split.column(align=True)
		col.label(text="Settings", icon="SETTINGS")
		
		box.prop(operator, "pack_bundle_file")
		box.prop(operator, "ignore_hidden_meshes")
		box.prop(operator, "copy_uv_layer")
		box.prop(operator, "force_rotation")
		if operator.force_rotation == True:
			box.prop(operator, "global_rotation")
		
		##
		box = layout.box()
		split = box.split(factor=0.75)
		col = split.column(align=True)
		col.label(text="Debug options", icon="MODIFIER")
		
		row = box.row(align=True)
		row.label(text="Include shared assets")
		row.use_property_split = False
		row.prop_enum(operator, "force_shared_asset_as_false", 'MODEL', text="Model", icon="MESH_DATA")
		row.prop_enum(operator, "force_shared_asset_as_false", 'MATERIAL', text="Material", icon="MATERIAL")
		row.prop_enum(operator, "force_shared_asset_as_false", 'TEXTURE', text="Texture", icon="TEXTURE")
		
		box.prop(operator, "debug_shared_not_found")
		box.prop(operator, "debug_use_shader_material_parameters")
		box.prop(operator, "debug_use_default_samplerstates")
		if bpy.context.preferences.view.show_developer_ui == True:
			box.prop(operator, "debug_redirect_vehicle")
			if operator.debug_redirect_vehicle == True:
				box.prop(operator, "debug_new_vehicle_name")
		
		##
		box = layout.box()
		split = box.split(factor=0.75)
		col = split.column(align=True)
		col.label(text="Blender orientation", icon="OBJECT_DATA")
		
		row = box.row(align=True)
		row.label(text="Forward axis")
		row.use_property_split = False
		row.prop_enum(operator, "axis_forward", 'X', text='X')
		row.prop_enum(operator, "axis_forward", 'Y', text='Y')
		row.prop_enum(operator, "axis_forward", 'Z', text='Z')
		row.prop_enum(operator, "axis_forward", '-X', text='-X')
		row.prop_enum(operator, "axis_forward", '-Y', text='-Y')
		row.prop_enum(operator, "axis_forward", '-Z', text='-Z')
		
		row = box.row(align=True)
		row.label(text="Up axis")
		row.use_property_split = False
		row.prop_enum(operator, "axis_up", 'X', text='X')
		row.prop_enum(operator, "axis_up", 'Y', text='Y')
		row.prop_enum(operator, "axis_up", 'Z', text='Z')
		row.prop_enum(operator, "axis_up", '-X', text='-X')
		row.prop_enum(operator, "axis_up", '-Y', text='-Y')
		row.prop_enum(operator, "axis_up", '-Z', text='-Z')


def menu_func_export(self, context):
	pcoll = preview_collections["main"]
	my_icon = pcoll["my_icon"]
	self.layout.operator(ExportNFSHPR.bl_idname, text="Need for Speed Hot Pursuit Remastered (2020) (.dat)", icon_value=my_icon.icon_id)


classes = (
		ExportNFSHPR,
)

preview_collections = {}


def register():
	import bpy.utils.previews
	pcoll = bpy.utils.previews.new()
	
	my_icons_dir = os.path.join(os.path.dirname(__file__), "dgi_icons")
	pcoll.load("my_icon", os.path.join(my_icons_dir, "nfshp_icon.png"), 'IMAGE')

	preview_collections["main"] = pcoll
	
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()
	
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()
