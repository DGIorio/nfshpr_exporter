#-*- coding:utf-8 -*-

def custom_shaders():
	shaders = {}
	shaders['Glass'] = '14_AF_13_00' 						# Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
	shaders['Window'] = '14_AF_13_00' 						# Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
	shaders['Windows'] = '14_AF_13_00' 						# Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
	shaders['Glass_Black'] = '14_AF_13_00' 					# Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
	shaders['Glass_black'] = '14_AF_13_00' 					# Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
	shaders['Glass_Doublesided'] = 'DB_6C_13_00' 			# Vehicle_Glass_Emissive_Coloured_Wrap
	shaders['Glass_doublesided'] = 'DB_6C_13_00' 			# Vehicle_Glass_Emissive_Coloured_Wrap
	shaders['VehicleNFS13_Mirror'] = 'F3_D3_03_00' 			# Vehicle_Opaque_Reflective
	shaders['Mirror'] = 'F3_D3_03_00' 						# Vehicle_Opaque_Reflective
	shaders['VehicleNFS13_Body_Chrome'] = '1B_D4_03_00' 	# Vehicle_Opaque_Emissive_Reflective_AO
	shaders['VehicleNFS13_Chrome'] = '1B_D4_03_00' 			# Vehicle_Opaque_Emissive_Reflective_AO
	shaders['Chrome'] = '1B_D4_03_00' 						# Vehicle_Opaque_Emissive_Reflective_AO
	shaders['VehicleNFS13_Body_Tyre'] = 'BB_1E_00_00' 		# Vehicle_Tyre
	shaders['VehicleNFS13_Tyre'] = 'BB_1E_00_00' 			# Vehicle_Tyre
	shaders['Tyre'] = 'BB_1E_00_00' 						# Vehicle_Tyre
	shaders['Tire'] = 'BB_1E_00_00' 						# Vehicle_Tyre
	shaders['Licenseplate'] = 'F3_D0_03_00' 				# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['LicensePlate'] = 'F3_D0_03_00' 				# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['License_Plate'] = 'F3_D0_03_00' 				# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['VehicleNFS13_Licenseplate'] = 'F3_D0_03_00' 	# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['VehicleNFS13_License_Plate'] = 'F3_D0_03_00' 	# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['DullPlastic'] = '19_D4_03_00'					# Vehicle_Opaque_Emissive_AO
	shaders['Dull_Plastic'] = '19_D4_03_00'					# Vehicle_Opaque_Emissive_AO
	shaders['Interior'] = '4A_62_02_00' 					# Vehicle_Opaque_Textured_Phong
	shaders['VehicleNFS13_Interior'] = '4A_62_02_00' 		# Vehicle_Opaque_Textured_Phong
	shaders['Metal'] = '1B_D4_03_00' 						# Vehicle_Opaque_Emissive_Reflective_AO
	shaders['BodyPaint_Livery'] = 'B8_6C_13_00'				# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery_Wrap
	shaders['BodyLivery'] = '56_C6_01_00'					# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
	shaders['BodyPaint'] = 'BA_6C_13_00'					# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap
	shaders['BodyColor'] = '41_C6_01_00'					# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride
	shaders['Badge'] = '50_62_02_00'						# Vehicle_Greyscale_Textured_Normalmapped_Reflective
	shaders['Emblem'] = '50_62_02_00'						# Vehicle_Greyscale_Textured_Normalmapped_Reflective
	shaders['Symbol'] = '50_62_02_00'						# Vehicle_Greyscale_Textured_Normalmapped_Reflective
	shaders['Grill'] = '06_35_03_00'						# Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery
	shaders['Transparent'] = '50_62_02_00'					# Vehicle_Greyscale_Textured_Normalmapped_Reflective
	shaders['VehicleNFS13_Caliper'] = '43_52_04_00' 		# Vehicle_Wheel_1Bit_Alpha_Normalmap
	shaders['Caliper'] = '43_52_04_00' 						# Vehicle_Wheel_1Bit_Alpha_Normalmap
	shaders['Caliper_Textured'] = '43_52_04_00' 			# Vehicle_Wheel_1Bit_Alpha_Normalmap
	shaders['VehicleNFS13_BrakeDisc'] = 'CB_A9_01_00'		# Vehicle_Wheel_Brakedisc_1Bit_Blur_Normalmap
	shaders['BrakeDisc'] = 'CB_A9_01_00'					# Vehicle_Wheel_Brakedisc_1Bit_Blur_Normalmap
	shaders['VehicleNFS13_Chassis'] = '56_62_02_00'			# Vehicle_Opaque_Textured
	shaders['Chassis'] = '56_62_02_00'						# Vehicle_Opaque_Textured
	shaders['VehicleNFS13_Carbonfiber'] = '56_C6_01_00'		# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
	shaders['CarbonFiber'] = '56_C6_01_00'					# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
	shaders['Rim'] = 'BD_1E_00_00'							# Vehicle_Wheel_Opaque
	shaders['Engine'] = '58_62_02_00' 						# Vehicle_Opaque_Textured_Normalmapped_AO
	shaders['CarbonFiber2'] = '56_C6_01_00'					# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
	shaders['GlassColourise'] = '45_C6_01_00'				# Vehicle_Glass_Emissive_Coloured
	shaders['GlassColour'] = '45_C6_01_00'					# Vehicle_Glass_Emissive_Coloured
	shaders['GlassColor'] = '45_C6_01_00'					# Vehicle_Glass_Emissive_Coloured
	shaders['CopLight'] = 'E6_92_01_00' 					# Vehicle_Glass_LocalEmissive_Coloured
	shaders['CarPaint'] = 'BA_6C_13_00'						# Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap
	shaders['CaliperBadge'] = '45_52_04_00'					# Vehicle_Wheel_1Bit_Alpha
	shaders['RimBadge'] = '3B_58_05_00'						# Vehicle_Wheel_Alpha_Normalmap
	#shaders['RimBadgeFade'] = 'BB_EF_09_00'
	#shaders['RimFade'] = 'B9_EF_09_00'
	#shaders['RimBlur'] = 'B9_EF_09_00'
	#shaders['RimSpin'] = 'B9_EF_09_00'
	#shaders['BodypaintLight'] = '74_EF_09_00'
	#shaders['CarpaintLight'] = '74_EF_09_00'
	#shaders['BodyPaintNormal'] = '6E_EF_09_00'
	#shaders['CarPaintNormal'] = '6E_EF_09_00'
	#shaders['LightGlass'] = 'A7_EF_09_00'
	#shaders['LightCluster'] = '7C_EF_09_00'
	#shaders['LightRefracted'] = 'A1_EF_09_00'
	#CharacterSpec
	shaders['Character'] = 'CB_51_04_00' 					# Character_Opaque_Textured_NormalMap_SpecMap_Skin
	shaders['Driver'] = 'CB_51_04_00' 						# Character_Opaque_Textured_NormalMap_SpecMap_Skin
	shaders['CharacterSkin'] = 'CB_51_04_00'				# Character_Opaque_Textured_NormalMap_SpecMap_Skin
	shaders['Skin'] = 'CB_51_04_00' 						# Character_Opaque_Textured_NormalMap_SpecMap_Skin
	shaders['Hair'] = 'CF_51_04_00' 						# Character_Greyscale_Textured_Doublesided_Skin
	
	
	# For compatibility with mw exporter
	shaders['Tire_test'] = 'BB_1E_00_00' 					# Vehicle_Tyre
	shaders['TyreNew'] = 'BB_1E_00_00' 						# Vehicle_Tyre
	shaders['LicensePlate_Number'] = 'F3_D0_03_00'			# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['Licenseplate_Number'] = 'F3_D0_03_00' 			# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['License_Plate_Number'] = 'F3_D0_03_00' 		# Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['VehicleNFS13_Licenseplate_Number'] = 'F3_D0_03_00' # Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	shaders['VehicleNFS13_License_Plate_Number'] = 'F3_D0_03_00' # Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
	
	return shaders


def get_default_sampler_states(shader_type, mShaderId, num_sampler_states_shader):	# OK
	sampler_states_info = ["AF_5A_0B_82"]*num_sampler_states_shader
	
	#GraphicsSpec
	if mShaderId == "BB_1E_00_00":		#Vehicle_Tyre
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "BD_1E_00_00":	#Vehicle_Wheel_Opaque
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "E6_92_01_00":	#Vehicle_Glass_LocalEmissive_Coloured
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "CB_A9_01_00":	#Vehicle_Wheel_Brakedisc_1Bit_Blur_Normalmap
		sampler_states_info = ['AF_5A_0B_82', 'D3_42_51_ED', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "41_C6_01_00":	#Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "45_C6_01_00":	#Vehicle_Glass_Emissive_Coloured
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "52_C6_01_00":	#Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery
		sampler_states_info = ['AD_42_2A_75', 'CC_CD_0F_AE', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "56_C6_01_00":	#Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "4A_62_02_00":	#Vehicle_Opaque_Textured_Phong
		sampler_states_info = ['AF_5A_0B_82']
	elif mShaderId == "4E_62_02_00":	#Vehicle_Opaque_Textured_Normalmapped_Reflective_AO
		sampler_states_info = ['25_7A_8E_DB', '25_7A_8E_DB', 'AF_5A_0B_82']
	elif mShaderId == "50_62_02_00":	#Vehicle_Greyscale_Textured_Normalmapped_Reflective
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "56_62_02_00":	#Vehicle_Opaque_Textured
		sampler_states_info = ['AF_5A_0B_82']
	elif mShaderId == "58_62_02_00":	#Vehicle_Opaque_Textured_Normalmapped_AO
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "8A_62_02_00":	#Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "06_35_03_00":	#Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery
		sampler_states_info = ['AF_5A_0B_82', '25_7A_8E_DB', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "EB_6E_03_00":	#Vehicle_Rearlights_Heightmap
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "CD_D0_03_00":	#Vehicle_Opaque_Textured_NormalMapped_Emissive_AO
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "F3_D0_03_00":	#Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
		sampler_states_info = ['25_7A_8E_DB', '25_7A_8E_DB', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "FA_D0_03_00":	#Vehicle_Opaque_Textured_NormalMapped_Emissive_AO_Livery
		sampler_states_info = ['AF_5A_0B_82', '25_7A_8E_DB', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "F1_D3_03_00":	#Vehicle_1Bit_Textured_Normalmapped_Reflective
		sampler_states_info = ['25_7A_8E_DB', '25_7A_8E_DB']
	elif mShaderId == "19_D4_03_00":	#Vehicle_Opaque_Emissive_AO
		sampler_states_info = ['CC_CD_0F_AE', 'AF_5A_0B_82']
	elif mShaderId == "1B_D4_03_00":	#Vehicle_Opaque_Emissive_Reflective_AO
		sampler_states_info = ['CC_CD_0F_AE', 'AF_5A_0B_82']
	elif mShaderId == "43_52_04_00":	#Vehicle_Wheel_1Bit_Alpha_Normalmap
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "45_52_04_00":	#Vehicle_Wheel_1Bit_Alpha
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "3B_58_05_00":	#Vehicle_Wheel_Alpha_Normalmap
		sampler_states_info = ['25_7A_8E_DB', '25_7A_8E_DB', 'AF_5A_0B_82']
	elif mShaderId == "85_0A_0A_00":	#Vehicle_Opaque_Textured_NormalMapped_Reflective_LocalEmissive_AO
		sampler_states_info = ['B0_A0_58_B5', 'D3_37_5C_99', 'D3_37_5C_99', 'D3_37_5C_99']
	elif mShaderId == "B8_6C_13_00":	#Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery_Wrap
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "BA_6C_13_00":	#Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "10_AF_13_00":	#Vehicle_Opaque_Two_PaintGloss_Textured_LightmappedLights_Livery_Wrap
		sampler_states_info = ['8B_5D_A4_E0', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "14_AF_13_00":	#Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	
	#CharacterSpec
	elif mShaderId == "CB_51_04_00":	#Character_Opaque_Textured_NormalMap_SpecMap_Skin
		sampler_states_info = ['AF_5A_0B_82', 'AF_5A_0B_82', 'AF_5A_0B_82']
	elif mShaderId == "CF_51_04_00":	#Character_Greyscale_Textured_Doublesided_Skin
		sampler_states_info = ['AF_5A_0B_82']
	
	#InstanceList
	
	return sampler_states_info


def get_default_material_parameters(shader_type):
	status = 0
	parameters_Indices = []
	parameters_Ones = []
	parameters_NamesHash = []
	parameters_Data = []
	parameters_Names = []
	
	if shader_type.lower() == "glass" or shader_type.lower() == "window" or shader_type.lower() == "windows":
		#shader_type = Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
		parameters_Indices = [1, 2, 9, 4, 5, 6, 0, 8, 3, 7]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 549131089, 843472246, 1350180620, 1444230008, 2342768594, 3143708811, 3681973827, 3743314456, 4272862365]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0), (0.10999999940395355, 3.5, 1.0, 0.0), (0.25, 0.0, 0.0, 1.0), (0.05000000074505806, 0.4000000059604645, 3.0, 0.25), (0.07035999745130539, 0.07035999745130539, 0.07035999745130539, 1.0), (0.0003035269910469651, 0.0027317428030073643, 0.0036765073891729116, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'ReversingColour', 'mSelfIlluminationMultiplier', 'UnusedColour', 'mCrackedGlassSpecularColour', 'mCrackedGlassSpecularControls', 'BrakeColour', 'mGlassControls', 'RunningColour', 'mGlassColour']
	
	elif shader_type.lower() == "glass_black":
		#shader_type = Vehicle_Glass_Emissive_Coloured_Singlesided_Wrap
		parameters_Indices = [1, 2, 9, 4, 5, 6, 0, 8, 3, 7]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 549131089, 843472246, 1350180620, 1444230008, 2342768594, 3143708811, 3681973827, 3743314456, 4272862365]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0), (0.10999999940395355, 3.5, 1.0, 0.0), (0.25, 0.0, 0.0, 1.0), (0.05000000074505806, 0.4000000059604645, 3.5, 0.0), (0.07035999745130539, 0.07035999745130539, 0.07035999745130539, 1.0), (0.0, 0.0, 0.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'ReversingColour', 'mSelfIlluminationMultiplier', 'UnusedColour', 'mCrackedGlassSpecularColour', 'mCrackedGlassSpecularControls', 'BrakeColour', 'mGlassControls', 'RunningColour', 'mGlassColour']
	
	elif shader_type.lower() == "glass_doublesided":
		#shader_type = Vehicle_Glass_Emissive_Coloured_Wrap
		parameters_Indices = [1, 2, 9, 4, 5, 6, 0, 8, 3, 7]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 549131089, 843472246, 1350180620, 1444230008, 2342768594, 3143708811, 3681973827, 3743314456, 4272862365]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0), (0.10999999940395355, 3.5, 1.0, 0.0), (0.25, 0.0, 0.0, 1.0), (0.03999999910593033, 1.0, 3.0, 0.699999988079071), (0.07035999745130539, 0.07035999745130539, 0.07035999745130539, 1.0), (0.0, 0.0, 0.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'ReversingColour', 'mSelfIlluminationMultiplier', 'UnusedColour', 'mCrackedGlassSpecularColour', 'mCrackedGlassSpecularControls', 'BrakeColour', 'mGlassControls', 'RunningColour', 'mGlassColour']
	
	elif shader_type.lower() == "mirror" or shader_type == "VehicleNFS13_Mirror":
		#shader_type = Vehicle_Opaque_Reflective
		parameters_Indices = [1, 0, 2, 3, 4]
		parameters_Ones = [1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1055962784, 1738324391, 1798261942, 4142038186]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 3.0, 0.0), (0.05000000074505806, 0.10000000149011612, 4.0, 0.0), (0.2015562504529953, 0.2015562504529953, 0.2015562504529953, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'materialDiffuse']
	
	elif shader_type.lower() == "chrome" or shader_type == "VehicleNFS13_Chrome" or shader_type == "VehicleNFS13_Body_Chrome":
		#shader_type = Vehicle_Opaque_Emissive_Reflective_AO
		parameters_Indices = [5, 4, 7, 0, 6, 8, 2, 1, 3, 9]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [220664079, 422585019, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.20000000298023224, 0.44999998807907104, 5.0, 0.0), (7.0, 0.0, 30.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.00802319310605526, 0.00802319310605526, 0.00802319310605526, 1.0)]
		parameters_Names = ['mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "metal":
		#shader_type = Vehicle_Opaque_Emissive_Reflective_AO
		parameters_Indices = [5, 4, 7, 0, 6, 8, 2, 1, 3, 9]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [220664079, 422585019, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.20000000298023224, 0.44999998807907104, 5.0, 0.0), (7.0, 0.0, 30.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.00802319310605526, 0.00802319310605526, 0.00802319310605526, 1.0)]
		parameters_Names = ['mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "tyre" or shader_type == "VehicleNFS13_Tyre" or shader_type == "VehicleNFS13_Body_Tyre":
		#shader_type = Vehicle_Tyre
		parameters_Indices = [0, 1]
		parameters_Ones = [1, 1]
		parameters_NamesHash = [1055962784, 1798261942]
		parameters_Data = [(0.800000011920929, 0.4000000059604645, 0.0, 0.0),
						   (0.12200000137090683, 1.0, 35.0, 1.0)]
		parameters_Names = ['LightMultipliers', 'mSpecularControls']
	
	elif shader_type.lower() == "bodypaint_livery":
		#shader_type = Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Livery_Wrap
		parameters_Indices = [3, 5, 4, 1, 0, 2]
		parameters_Ones = [1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 843472246, 922074327, 2143891951, 3328281617, 4064316377]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (1.0, 0.9559733271598816, 0.68668532371521, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.021219009533524513, 0.0030352699104696512, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'mPaintColourIndex', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour']
	
	elif shader_type.lower() == "bodylivery":
		#shader_type = Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
		parameters_Indices = [10, 6, 4, 7, 14, 5, 8, 11, 0, 9, 12, 2, 1, 3, 13]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 469755418, 536136062, 780838486, 784529858, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.4000000059604645, 0.15000000596046448, 50.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (0.699999988079071, 0.20000000298023224, 0.5, 0.0), (0.32314321398735046, 0.32314321398735046, 0.32314321398735046, 1.0), (2.0, 0.0, 1.0, 0.0), (2.0, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (2.0, 0.800000011920929, 1.0, 0.5), (0.03999999910593033, 0.699999988079071, 7.0, 0.0), (2.0, 0.20000000298023224, 55.0, 1.0), (0.9559733271598816, 0.9473065137863159, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.021219009533524513, 0.0030352699104696512, 1.0), (0.015208514407277107, 0.017641954123973846, 0.023153366521000862, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mEnvSpecularControls', 'pearlescentColour', 'mDiffuseFresnel', 'mPearlescentPower', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "bodypaint" or shader_type.lower() == "carpaint":
		#shader_type = Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_Wrap
		parameters_Indices = [3, 5, 4, 1, 0, 2]
		parameters_Ones = [1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 843472246, 922074327, 2143891951, 3328281617, 4064316377]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'mPaintColourIndex', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour']
	
	elif shader_type.lower() == "bodycolor":
		#shader_type = Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride
		parameters_Indices = [10, 6, 4, 7, 14, 5, 8, 11, 0, 9, 12, 2, 1, 3, 13]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 469755418, 536136062, 780838486, 784529858, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.25, 0.25, 50.0, 0.20000000298023224), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (0.20000000298023224, 0.20000000298023224, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (1.0, 0.75, 5.0, 0.0), (4.0, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.009999999776482582, 0.5, 3.0, 0.0), (0.05000000074505806, 0.10000000149011612, 40.0, 0.0), (1.0, 0.9386857151985168, 0.5088813304901123, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.021219009533524513, 0.0030352699104696512, 1.0), (0.0036765073891729116, 0.0036765073891729116, 0.0036765073891729116, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mEnvSpecularControls', 'pearlescentColour', 'mDiffuseFresnel', 'mPearlescentPower', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "badge" or shader_type.lower() == "emblem" or shader_type.lower() == "symbol" or shader_type.lower() == "transparent":
		#shader_type = Vehicle_Greyscale_Textured_Normalmapped_Reflective
		parameters_Indices = [1, 0, 2, 3, 4]
		parameters_Ones = [1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1055962784, 1738324391, 1798261942, 4142038186]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (3.0, 1.0, 0.0, 0.0), (0.013000000268220901, 0.30000001192092896, 3.0, 0.0), (0.5, 1.0, 60.0, 1.0), (0.0, 0.0, 0.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'materialDiffuse']
	
	elif shader_type.lower() == "grill":
		#shader_type = Vehicle_1Bit_Textured_NormalMapped_Emissive_AO_Livery
		parameters_Indices = [6, 5, 4, 7, 0, 8, 2, 1, 3, 9]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 843472246, 1055962784, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.009999999776482582, 0.15000000596046448, 5.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (60.0, 0.0, 0.0, 0.0), (5.0, 0.10000000149011612, 1.0, 0.0), (0.009999999776482582, 0.05000000074505806, 60.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "license_plate_number" or shader_type.lower() == "licenseplate_number" or shader_type == "VehicleNFS13_Licenseplate_Number" or shader_type == "VehicleNFS13_License_Plate_Number":
		#shader_type = Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
		parameters_Indices = [7, 5, 4, 8, 0, 6, 9, 2, 1, 3, 10]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.25, 0.25, 50.0, 0.10000000149011612), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (1.5, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.009999999776482582, 0.009999999776482582, 3.0, 0.0), (0.02500000037252903, 0.800000011920929, 80.0, 1.0), (1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "license_plate" or shader_type.lower() == "licenseplate" or shader_type == "VehicleNFS13_Licenseplate" or shader_type == "VehicleNFS13_License_Plate":
		#shader_type = Vehicle_Opaque_Textured_NormalMapped_Reflective_Emissive_AO_Livery
		parameters_Indices = [7, 5, 4, 8, 0, 6, 9, 2, 1, 3, 10]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.25, 0.25, 50.0, 0.10000000149011612), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (1.5, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.009999999776482582, 0.009999999776482582, 3.0, 0.0), (0.02500000037252903, 0.800000011920929, 80.0, 1.0), (1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "dullplastic" or shader_type.lower() == "dull_plastic":
		#shader_type = Vehicle_Opaque_Emissive_AO
		parameters_Indices = [5, 4, 6, 0, 7, 2, 1, 3, 8]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [220664079, 422585019, 843472246, 1055962784, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.15000000596046448, 0.20000000298023224, 50.0, 0.6000000238418579), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.012983032502233982, 0.012983032502233982, 0.012983032502233982, 1.0)]
		parameters_Names = ['mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "interior" or shader_type == "VehicleNFS13_Interior":
		#shader_type = Vehicle_Opaque_Textured_Phong
		parameters_Indices = [1, 0, 2, 3]
		parameters_Ones = [1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1055962784, 1798261942, 4142038186]
		parameters_Data = [(0.001500000013038516, 0.0, 0.0, 0.0), (1.0, 0.699999988079071, 0.0, 0.0), (0.05000000074505806, 0.8500000238418579, 2.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'LightMultipliers', 'mSpecularControls', 'materialDiffuse']
	
	elif shader_type.lower() == "caliper" or shader_type.lower() == "caliper_textured" or shader_type == "VehicleNFS13_Caliper":
		#shader_type = Vehicle_Wheel_1Bit_Alpha_Normalmap
		parameters_Indices = [2, 4, 1, 6, 7, 5, 3, 0]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 780838486, 1055962784, 1738324391, 1798261942, 1967441240, 3344773910, 3998419168]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (1.0, 0.0, 5.0, 0.0), (5.0, 1.0, 0.0, 0.0), (0.0, 0.0, 30.0, 0.0), (1.0, 1.0, 60.0, 0.0), (0.012983032502233982, 0.012983032502233982, 0.012983032502233982, 1.0), (0.0, 0.0, 3.0, 0.20000000298023224), (0.0, 0.0, 0.0, 0.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mDiffuseFresnel', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'mMaterialDiffuse', 'mBlurredReflectionControls', 'g_flipUvsOnFlippedTechnique']
	
	elif shader_type.lower() == "brakedisc" or shader_type == "VehicleNFS13_BrakeDisc":
		#shader_type = Vehicle_Wheel_Brakedisc_1Bit_Blur_Normalmap
		parameters_Indices = [2, 4, 1, 5, 6, 3, 0]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 780838486, 1055962784, 1738324391, 1798261942, 3344773910, 3998419168]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 0.0), (0.3499999940395355, 0.699999988079071, 1.0, 0.0), (0.0, 0.0, 0.0, 0.0), (32.0, 0.44999998807907104, 55.0, 0.0), (0.16500000655651093, 0.16500000655651093, 12.0, 0.0), (0.0, 0.0, 0.0, 0.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mDiffuseFresnel', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'mBlurredReflectionControls', 'g_flipUvsOnFlippedTechnique']
	
	elif shader_type.lower() == "rim":
		#shader_type = Vehicle_Wheel_Opaque
		parameters_Indices = [2, 4, 1, 5, 6, 3, 0]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 780838486, 1055962784, 1738324391, 1798261942, 3344773910, 3998419168]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (0.699999988079071, 1.0, 5.0, 0.0), (2.0, 1.0, 0.6000000238418579, 0.0), (0.10000000149011612, 0.30000001192092896, 5.0, 0.0), (4.0, 1.0, 15.0, 0.0), (0.10000000149011612, 0.30000001192092896, 12.0, 1.0), (0.0, 0.0, 0.0, 0.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mDiffuseFresnel', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'mBlurredReflectionControls', 'g_flipUvsOnFlippedTechnique']
	
	elif shader_type.lower() == "rimbadge":
		#shader_type = Vehicle_Wheel_Alpha_Normalmap
		parameters_Indices = [2, 4, 1, 5, 6, 3, 0]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 780838486, 1055962784, 1738324391, 1798261942, 3344773910, 3998419168]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (1.0, 1.0, 5.0, 0.0), (2.0, 0.5, 1.0, 0.0), (0.013000000268220901, 0.30000001192092896, 3.0, 0.0), (4.5, 1.0, 50.0, 0.8999999761581421), (0.6000000238418579, 0.0, 3.0, 0.20000000298023224), (1.0, 0.0, 0.0, 0.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mDiffuseFresnel', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'mBlurredReflectionControls', 'g_flipUvsOnFlippedTechnique']
	
	elif shader_type.lower() == "chassis" or shader_type == "VehicleNFS13_Chassis":
		#shader_type = Vehicle_Opaque_Textured
		parameters_Indices = [1, 0, 2, 3]
		parameters_Ones = [1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1055962784, 1798261942, 4142038186]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (2.0, 0.3499999940395355, 0.0, 0.0), (0.03500000014901161, 0.25, 70.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'LightMultipliers', 'mSpecularControls', 'materialDiffuse']
	
	elif shader_type.lower() == "engine":
		#shader_type = Vehicle_Opaque_Textured_Normalmapped_AO
		parameters_Indices = [1, 0, 2, 3]
		parameters_Ones = [1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1055962784, 1798261942, 4142038186]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0), (0.11999999731779099, 0.5, 20.0, 0.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'LightMultipliers', 'mSpecularControls', 'materialDiffuse']
	
	elif shader_type.lower() == "carbonfiber" or shader_type == "VehicleNFS13_Carbonfiber" or shader_type.lower() == "carbonfiber2":
		#shader_type = Vehicle_Opaque_PaintGloss_Textured_LightmappedLights_ColourOverride_Livery
		parameters_Indices = [10, 6, 4, 7, 14, 5, 8, 11, 0, 9, 12, 2, 1, 3, 13]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [83815342, 220664079, 422585019, 469755418, 536136062, 780838486, 784529858, 843472246, 1055962784, 1738324391, 1798261942, 2143891951, 3328281617, 4064316377, 4142038186]
		parameters_Data = [(0.4000000059604645, 0.15000000596046448, 50.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0010000000474974513, 0.0, 0.0, 0.0), (0.44999998807907104, 0.20000000298023224, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.5, 0.0, 4.0, 0.0), (20.0, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 0.699999988079071, 1.0, 0.0), (0.019999999552965164, 0.4000000059604645, 12.0, 0.0), (3.0, 0.4000000059604645, 35.0, 0.9800000190734863), (0.9559733271598816, 0.9473065137863159, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.021219009533524513, 0.0030352699104696512, 1.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['mScratchSpecularControls', 'mEmissiveAdditiveAmount', 'MaterialShadowMapBias', 'mEnvSpecularControls', 'pearlescentColour', 'mDiffuseFresnel', 'mPearlescentPower', 'mSelfIlluminationMultiplier', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'LightmappedLightsGreenChannelColour', 'LightmappedLightsBlueChannelColour', 'LightmappedLightsRedChannelColour', 'materialDiffuse']
	
	elif shader_type.lower() == "glasscolourise" or shader_type.lower() == "glasscolour" or shader_type.lower() == "glasscolor":
		#shader_type = Vehicle_Glass_Emissive_Coloured
		parameters_Indices = [1, 2, 9, 4, 5, 6, 0, 8, 3, 7]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 549131089, 843472246, 1350180620, 1444230008, 2342768594, 3143708811, 3681973827, 3743314456, 4272862365]
		parameters_Data = [(0.0010000000474974513, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0), (0.10999999940395355, 3.5, 1.0, 0.0), (0.25, 0.0, 0.0, 1.0), (0.029999999329447746, 0.6000000238418579, 3.0, 0.949999988079071), (0.07035999745130539, 0.07035999745130539, 0.07035999745130539, 1.0), (1.0, 0.0, 0.01032982300966978, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'ReversingColour', 'mSelfIlluminationMultiplier', 'UnusedColour', 'mCrackedGlassSpecularColour', 'mCrackedGlassSpecularControls', 'BrakeColour', 'mGlassControls', 'RunningColour', 'mGlassColour']
	
	elif shader_type.lower() == "tyrenew":
		#shader_type = Vehicle_Tyre
		parameters_Indices = [0, 1]
		parameters_Ones = [1, 1]
		parameters_NamesHash = [1055962784, 1798261942]
		parameters_Data = [(0.800000011920929, 0.4000000059604645, 0.0, 0.0),
						   (0.12200000137090683, 1.0, 35.0, 1.0)]
		parameters_Names = ['LightMultipliers', 'mSpecularControls']
		
	elif shader_type.lower() == "tire_test":
		#shader_type = Vehicle_Tyre
		parameters_Indices = [0, 1]
		parameters_Ones = [1, 1]
		parameters_NamesHash = [1055962784, 1798261942]
		parameters_Data = [(0.800000011920929, 0.4000000059604645, 0.0, 0.0),
						   (0.12200000137090683, 1.0, 35.0, 1.0)]
		parameters_Names = ['LightMultipliers', 'mSpecularControls']
	
	elif shader_type.lower() == "coplight":
		#shader_type = Vehicle_Glass_LocalEmissive_Coloured
		parameters_Indices = [0, 6, 2, 3, 7, 1, 5, 4]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 843472246, 1444230008, 2342768594, 2727547134, 3178546268, 3681973827, 4272862365]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (2.0, 0.0, 0.0, 0.0), (0.19599999487400055, 0.6549999713897705, 0.7879999876022339, 1.0), (0.10999999940395355, 3.5, 1.0, 0.0), (0.5, 0.0, 0.0, 0.0), (0.0666259378194809, 0.0, 0.0, 1.0), (0.009999999776482582, 1.0, 5.0, 0.5), (0.21223075687885284, 0.0006070539820939302, 0.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mSelfIlluminationMultiplier', 'mCrackedGlassSpecularColour', 'mCrackedGlassSpecularControls', 'mSelfIlluminationRadiusMultiplier', 'gEmissiveColour', 'mGlassControls', 'mGlassColour']
	
	elif shader_type.lower() == "caliperbadge":
		#shader_type = Vehicle_Wheel_1Bit_Alpha
		parameters_Indices = [2, 4, 1, 5, 6, 3, 0]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 780838486, 1055962784, 1738324391, 1798261942, 3344773910, 3998419168]
		parameters_Data = [(9.999999747378752e-06, 0.0, 0.0, 0.0), (1.0, 1.0, 5.0, 0.0), (1.0, 1.0, 0.0, 0.0), (0.0, 0.0, 3.0, 0.0), (0.0, 1.0, 50.0, 0.8999999761581421), (0.0, 0.0, 3.0, 0.20000000298023224), (1.0, 0.0, 0.0, 0.0)]
		parameters_Names = ['MaterialShadowMapBias', 'mDiffuseFresnel', 'LightMultipliers', 'mReflectionControls', 'mSpecularControls', 'mBlurredReflectionControls', 'g_flipUvsOnFlippedTechnique']
	
	elif shader_type.lower() == "character" or shader_type.lower() == "driver":
		#shader_type = Character_Opaque_Textured_NormalMap_SpecMap_Skin
		parameters_Indices = [4, 3, 1, 5, 2, 0, 6]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1437161761, 1500813362, 1798261942, 2448018893, 3773525911, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (2.0, 0.0, 0.0, 0.0), (0.05000000074505806, 0.0, 0.0, 0.0), (0.25, 1.0, 50.0, 0.0), (0.4000000059604645, 0.0, 0.0, 0.0), (1.2999999523162842, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'KeyLightShapePower', 'FillLightBrightness', 'mSpecularControls', 'KeyLightBrightness', 'AmbientLightBrightness', 'materialDiffuse']
	
	elif shader_type.lower() == "characterskin" or shader_type.lower() == "skin":
		#shader_type = Character_Opaque_Textured_NormalMap_SpecMap_Skin
		parameters_Indices = [4, 3, 1, 5, 2, 0, 6]
		parameters_Ones = [1, 1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1437161761, 1500813362, 1798261942, 2448018893, 3773525911, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (2.5, 0.0, 0.0, 0.0), (0.09000000357627869, 0.0, 0.0, 0.0), (3.0, 1.0, 30.0, 1.0), (1.2000000476837158, 0.0, 0.0, 0.0), (1.399999976158142, 0.0, 0.0, 0.0), (0.7379103899002075, 0.7379103899002075, 0.7379103899002075, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'KeyLightShapePower', 'FillLightBrightness', 'mSpecularControls', 'KeyLightBrightness', 'AmbientLightBrightness', 'materialDiffuse']
	
	elif shader_type.lower() == "hair":
		#shader_type = Character_Greyscale_Textured_Doublesided_Skin
		parameters_Indices = [4, 3, 1, 2, 0, 5]
		parameters_Ones = [1, 1, 1, 1, 1, 1]
		parameters_NamesHash = [422585019, 1437161761, 1500813362, 2448018893, 3773525911, 4142038186]
		parameters_Data = [(0.0, 0.0, 0.0, 0.0), (2.0, 0.0, 0.0, 0.0), (0.05000000074505806, 0.0, 0.0, 0.0), (0.4000000059604645, 0.0, 0.0, 0.0), (1.2999999523162842, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0)]
		parameters_Names = ['MaterialShadowMapBias', 'KeyLightShapePower', 'FillLightBrightness', 'KeyLightBrightness', 'AmbientLightBrightness', 'materialDiffuse']
	
	else:
		status = 1
	
	return (status, [parameters_Indices, parameters_Ones, parameters_NamesHash, parameters_Data, parameters_Names])


def	get_default_mRasterId(shader_type, mShaderId, raster_type, resource_type):
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
			#transparent
			mRasterId = "EB_1B_16_5D"
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
	
	return (mRasterId, raster_properties, is_raster_shared_asset, raster_path)
