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

ver = 0.2

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
	cmds.window(windowToClose, e=1, h=20, w=300)


def cApplySceneTimeWarp(action, *args):
	if action == 'apply':
		if cmds.objExists('timewarp'):
			cmds.delete('timewarp')
			print 'deleted old timewarp'
		cmds.AddTimeWarp()

	if action == 'select':
		cmds.select('timewarp', r=1)
		




def cBrowseSubstanceTex(*args):
	timewarp = 'timewarp'
	global tkFileList
	if action == 'read':
		cBrowseFiles()


	if action == 'list':
		f=open(tkFileList[0], "r")
		if f.mode == 'r':
			SubstanceValues = f.read()
			print SubstanceValues


	if action == 'apply': 
		cApplySceneTimeWarp('apply')
		cmds.select(clear=1) 
		numKeys = cmds.keyframe(timewarp, kc=1, q=1) 
		timeLast = cmds.keyframe("timewarp", q=True)[-1] 
		timeFirst =	cmds.keyframe("timewarp", q=True)[0] 
		cmds.setKeyframe(timewarp, t=-1000, v=-1000)
		cmds.cutKey('timewarp',	time=(timeLast,timeLast)) 
		cmds.cutKey('timewarp', time=(timeFirst,timeFirst))
		
		f=open(tkFileList[0], "r")
		if f.mode == 'r':
			SubstanceValues = f.read().split()
			for retValue in range (0, len(SubstanceValues), 2):
				time = float(SubstanceValues[retValue])
				value = float(SubstanceValues[(retValue +1)])
				# print time
				# print value
				if (type == 'float'):
					# print 'float'
					cmds.setKeyframe(timewarp, t=time, v=value)
				if (type == 'int'):
					# print 'int'
					intFrame = int(round(time,0))
					intValue = int(round(value,0))
					# print intValue
					# print 'intValue:'
					cmds.setKeyframe(timewarp, t=intFrame, v=intValue)

			
		cmds.cutKey('timewarp', time=(-1000,-1000))
		
		cmds.select(timewarp, r=1)
		cmds.keyTangent(itt='linear', ott='linear')



def cBrowseFiles():
	global tkFileList
	ws = cmds.workspace(fn=1)
	ws = ws + '/data'
	tkFileList = cmds.fileDialog2(dir=ws, fm=4)
	return tkFileList


def tkFillField(field, *args):
	mySel = cmds.ls(sl=1, l=1)
	cmds.textField(field, tx=mySel, e=1)




def tkAssembleSubstanceUI(*args):
	if (cmds.window('win_tkAssembleSubstance', exists=1)):
		cmds.deleteUI('win_tkAssembleSubstance')
	myWindow = cmds.window('win_tkAssembleSubstance', t='tkAssembleSubstance ' + str(ver), s=1)

	cmds.columnLayout(adj=1, bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]))
	cmds.frameLayout('flSubstance', l='Substance', bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]), cll=1, cl=0, cc='cShrinkWin("win_tkAssembleSubstance")')

	cmds.rowColumnLayout(nc=3, cw=[(1, 120), (2, 240), (3, 120)])
	cmds.button(l='Models >>', c=partial(tkFillField, 'tfModelName'), bgc=(colBlue[0], colBlue[1], colBlue[2]))
	cmds.textField('tfModelName', ed=1)
	cmds.setParent('..')

	cmds.button(l='Browse Substance Texture Files', c=partial(cBrowseSubstanceTex, 'select'), bgc=(colSilverMid[0], colSilverMid[1], colSilverMid[2]))





	cmds.showWindow(myWindow)

tkAssembleSubstanceUI()
partial(cShrinkWin, 'win_tkAssembleSubstance')
