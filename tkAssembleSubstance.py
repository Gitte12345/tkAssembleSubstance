# tkAssembleSubstance.py
'''
WHAT FOR
	Adds a scene timewarp to the complete scene. 

USAGE
1. Apply General Scene Time Warp:
	Adds a timewarp to the complete scene. Use this as well to reset to an ordinary timewarp,
	which does not change the timing. 
2. Select Substance Value File:
	Browse to the location where the nuke artist stored his Substance value file. This file is supposed to be
	a simple text file containing 1. the new frame, 2. the old frame.
3. (Optional) List Values:
	Lists the content of the file in the script editor.
4. Apply (Float) Values To Time Warp:
	Replaces the ordinary timewarp curve with the collected values in the file. 
	OR
4. Apply (Int) Values To Time Warp:
	Replaces the ordinary timewarp curve with the found values in the file, 
	but rounds the frames to full frames. That way we keep the full frames of the image plane sequences. 
	

'''
import maya.cmds as cmds
import maya.mel as mel
from functools import partial 

ver = 0.1

colDarkGrey			= [0.1, 0.1, 0.1]
colSilverLight 		= [0.39, 0.46, 0.50]
colSilverDark 		= [0.08, 0.09, 0.10]
colSilverMid 		= [0.23, 0.28, 0.30]
colRed 				= [0.42, 0.30, 0.30]
colGreen 			= [0.35, 0.50, 0.32]
colBlue 			= [0.20, 0.25, 0.47]

windowStartHeight = 50
windowStartWidth = 450
bh1 = 18


def cHelp(*args):
	if cmds.window('win_tkAssembleSubstanceHelp', exists=1):
		cmds.deleteUI('win_tkAssembleSubstanceHelp')
	myWindow = cmds.window('win_tkAssembleSubstanceHelp', s=1, t='help', wh=[200, 200])
	helpText = '\nWHAT FOR\n	Adds a scene timewarp to the complete scene. \n\nUSAGE\n1. Apply General Scene Time Warp:\n	Adds a timewarp to the complete scene. Use this as well to reset to an ordinary timewarp,\n	which does not change the timing. \n2. Select Substance Value File:\n	Browse to the location where the nuke artist stored his Substance value file. This file is supposed to be\n	a simple text file containing 1. the new frame, 2. the old frame.\n3. (Optional) List Values:\n	Lists the content of the file in the script editor.\n4. Apply (Float) Values To Time Warp:\n	Replaces the ordinary timewarp curve with the collected values in the file. \n	OR\n4. Apply (Int) Values To Time Warp:\n	Replaces the ordinary timewarp curve with the found values in the file, \n	but rounds the frames to full frames. That way we keep the full frames of the image plane sequences. \n	'
	cmds.columnLayout(adj=1)
	cmds.text(helpText, al='left')
	cmds.showWindow(myWindow )


def cShrinkWin(windowToClose, *args):
	cmds.window(windowToClose, e=1, h=20, w=360)


def tkDeleteUnusedShadingNodes(*args):
	mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
		

def cSubstanceTex(action, *args):
	global tkFileList
	objList = []
	objList = cmds.textField('tfModelName', tx=1, q=1).split()
	if action == 'browse':
		cBrowseFiles()
		print 'Found Textures:'
		for file in tkFileList: 
			print file.split('/')[-1]
		cSubstanceTex('build')


	if action == 'build':
		shdName = tkFileList[0].split('/')[-1].split('_')[0]
		print shdName
		shader = cmds.shadingNode('aiStandardSurface', asShader=1, n=shdName + '_SHD')
		SG = cmds.createNode('shadingEngine', name=shdName + '_SG')
		cmds.connectAttr(shader + '.outColor', SG + '.surfaceShader', f=1)
		cmds.connectAttr(SG + '.partition', 'renderPartition.sets', na=1)
		for obj in objList:
			print obj
			cmds.select(obj, r=1)
			cmds.sets(forceElement=SG, e=1)

		for tex in tkFileList:
			texName = tex.split('/')[-1].split('.')[0]
			file = cmds.shadingNode('file', asTexture=1, isColorManaged=1, n='Height')
			cmds.setAttr(file + '.ftn', tex, type = 'string')
			cmds.setAttr(file + '.colorSpace', 'sRGB', type = 'string')
			cmds.setAttr(file + '.filterType', 0)
			cmds.setAttr(file + '.alphaIsLuminance', 1)

			if 'Height' in texName or 'Displacement' in texName:
				print 'height'
				displacementShader = cmds.shadingNode('displacementShader', asShader=1)
				cmds.connectAttr(file + '.outAlpha', displacementShader + '.displacement', f=1)
				cmds.connectAttr(displacementShader + '.displacement', SG + '.displacementShader', f=1)

			if 'Normal' in texName:
				bump = cmds.shadingNode('bump2d', asUtility=1)
				cmds.setAttr(bump + '.bumpInterp', 1)
				cmds.connectAttr(file + '.outAlpha', bump + '.bumpValue', f=1)
				cmds.connectAttr(bump + '.outNormal', shader + '.normalCamera', f=1)

			if 'Base_Color' in texName or 'Albedo' in texName:
				cmds.connectAttr(file + '.outColor', shader + '.baseColor', f=1)

			if 'Metallic' in texName:
				cmds.connectAttr(file + '.outAlpha', shader + '.metalness', f=1)

			if 'Roughness' in texName:
				cmds.connectAttr(file + '.outAlpha', shader + '.specularRoughness', f=1)

			if 'Opacity' in texName:
				cmds.connectAttr(file + '.outColor', shader + '.opacity', f=1)
				for obj in objList:
					shapes = cmds.listRelatives(obj, s=1, type='mesh')
					for shp in shapes:
						cmds.setAttr(shp + '.aiOpaque', 0) 

			if 'Translucency' in texName:
				cmds.connectAttr(file + '.outColor', shader + '.transmissionColor', f=1)
				cmds.setAttr(shader + '.transmission', 1) 
				for obj in objList:
					shapes = cmds.listRelatives(obj, shape=1, type='mesh')
					for shp in shapes:
						cmds.setAttr(shp + '.aiOpaque', 0) 



def cBrowseFiles():
	global tkFileList
	ws = cmds.workspace(fn=1)
	ws = ws + '/substance/aphrodite'
	tkFileList = cmds.fileDialog2(dir=ws, okc='Select', fm=4)
	return tkFileList


def tkFillField(field, *args):
	strList = ''
	mySel = cmds.ls(sl=1, l=1)
	for sel in mySel:
		strList += sel + ' '
	
	cmds.textField(field, tx=strList, e=1)




def tkAssembleSubstanceUI(*args):
	if (cmds.window('win_tkAssembleSubstance', exists=1)):
		cmds.deleteUI('win_tkAssembleSubstance')
	myWindow = cmds.window('win_tkAssembleSubstance', t='tkAssembleSubstance ' + str(ver), s=1)

	cmds.columnLayout(adj=1, bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]))
	cmds.frameLayout('flSubstance', l='Substance', bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]), cll=1, cl=0, cc='cShrinkWin("win_tkAssembleSubstance")')

	cmds.rowColumnLayout(nc=2, cw=[(1, 120), (2, 240)])
	cmds.button(l='Models >>', c=partial(tkFillField, 'tfModelName'), bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]))
	cmds.textField('tfModelName', ed=1)
	cmds.setParent('..')

	cmds.button(l='Browse And Assign Substance Texture Files', c=partial(cSubstanceTex, 'browse'), bgc=(colSilverLight[0], colSilverLight[1], colSilverLight[2]))
	cmds.button(l='Delete Unused SHD', c=partial(tkDeleteUnusedShadingNodes), bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]))

	# cmds.button(l='Browse And Assign Substance Texture Files', c=partial(cSubstanceTex, 'browse'), bgc=(colSilverLight[0], colSilverLight[1], colSilverLight[2]))





	cmds.showWindow(myWindow)

tkAssembleSubstanceUI()
partial(cShrinkWin, 'win_tkAssembleSubstance')
