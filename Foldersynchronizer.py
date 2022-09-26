import time
import hashlib
import shutil
import os
from platform import platform
import logging
import argparse

"""

Copyright 2022 Juan Jose Villamar Villarreal , @villje


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

cwd = os.getcwd()
logfilename = "log.txt"
# Logging config
logging.basicConfig(filename=logfilename,level=logging.INFO,format="%(asctime)s %(message)s", filemode="w")

#Check the platform for slash
if platform().startswith('Windows'):
	slash = '\\'
else:
	slash = '/'

#Hashoffile
def hashofafile(file):
	with open(file, "rb") as f:
		return hashlib.md5(f.read()).hexdigest()

#deletefiles
def deletefiles(original,replica):
	for delete in replica:
		if delete not in original:
			os.remove(delete)

#Hashcomparison
def hashcomparison(file1,file2):
	if hashofafile(file1) == hashofafile(file2):
		print('True and: ', hashofafile(file1),' ', hashofafile(file2))
		return True
	else:
		print('False and: ', hashofafile(file1),' ', hashofafile(file2))
		return False
############# 1. Compare the folders
def hashofallfiles(patht):
	numoffolders = 0
	hashgroup = []
	for folder, subfolders, files in os.walk(patht):
		numoffolders += 1
		for name in files:
			hashgroup.append(hashofafile(folder+slash+name))
	return hash(tuple(hashgroup)),numoffolders

def listoffiles(file_path):
	folders = []
	filelist = []
	for folder, subfolders, files in os.walk(file_path):
		folders.append(folder.replace(str(file_path),''))
		for name in files:
			filelist.append(folder.replace(str(file_path),'')+ slash +  name)
	return folders,filelist

#Foldercomparison
def pathupdate(original,replica):
	originalhash,originalfolders = hashofallfiles(original)
	foldersa,filesa = listoffiles(original)
	foldersb,filesb = listoffiles(replica)
	if originalhash == hashofallfiles(replica)[0] and originalfolders == hashofallfiles(replica)[1] and filesa == filesb and foldersa == foldersb:
		pass
	else:
		foldersa,filesa = listoffiles(original)
		foldersb,filesb = listoffiles(replica)
		for dltdfolder in foldersb[1:]:
			if (dltdfolder not in foldersa) and os.path.isdir(replica+slash+dltdfolder):
				shutil.rmtree(replica+slash+dltdfolder)
				messagef = 'It was removed: ' + str(replica+slash+dltdfolder)
				print(messagef)
				logging.info(messagef)
		if originalhash == hashofallfiles(replica)[0] and originalfolders == hashofallfiles(replica)[1] and filesa == filesb and foldersa == foldersb:
			pass
		else:
			foldersa,filesa = listoffiles(original)
			foldersb,filesb = listoffiles(replica)
			for dltdfile in filesb:
				if (dltdfile not in filesa) and os.path.isfile(replica+slash+dltdfile):
					os.remove(replica+slash+dltdfile)
					messagefi = 'It was removed: ' + str(replica+slash+dltdfile)
					print(messagefi)
					logging.info(messagefi)
			if originalhash == hashofallfiles(replica)[0] and originalfolders == hashofallfiles(replica)[1] and filesa == filesb and foldersa == foldersb:
				pass
			else:
				for newfolder in foldersa:
					if newfolder not in foldersb and not os.path.isdir(replica+slash+newfolder):
						shutil.copytree(original+slash+newfolder,replica+slash+newfolder, dirs_exist_ok=True)
						messagecref = 'It was created: ' + str(replica+slash+newfolder)
						print(messagecref)
						logging.info(messagecref)
				if originalhash == hashofallfiles(replica)[0] and originalfolders == hashofallfiles(replica)[1] and filesa == filesb and foldersa == foldersb:
					pass
				else:
					for newfiles in filesa:
						if newfiles not in listoffiles(replica)[1] and not os.path.isfile(replica+slash+newfiles):
							shutil.copy(original+slash+newfiles,replica+slash+newfiles)
							messagecrefi = 'It was created: ' + str(replica+slash+newfolder)
							print(messagecrefi)
							logging.info(messagecrefi)
						elif os.path.isfile(replica+slash+newfiles) and (hashofafile(original+slash+newfiles) != hashofafile(replica+slash+newfiles)):
							shutil.copy(original+slash+newfiles,replica+slash+newfiles)
							messagecrefi2 = 'It was modified: ' + str(replica+slash+newfolder)
							print(messagecrefi2)
							logging.info(messagecrefi2)
	if originalhash == hashofallfiles(replica)[0] and originalfolders == hashofallfiles(replica)[1] and filesa == filesb and foldersa == foldersb:
		pass

def updateperiodically(Originpath,Replicapath,intervalinseconds,updateperiod='Indefinit'):
	print('The log file path is: ',cwd+slash+logfilename)
	if updateperiod == 'Indefinit':
		#### If the action is performed indefinitely
		updateinterval = intervalinseconds
		startingtime = round(time.time(),2)
		referencetime = 0
		updatetable = []
		pathupdate(Originpath,Replicapath)
		while time.time() < time.time()+2:
			updatetime = round(startingtime + referencetime + updateinterval,2)
			capture = round(time.time(),2)
			if capture == updatetime and capture not in updatetable:
				pathupdate(Originpath,Replicapath)
				#updatetable.append(capture)
				updatetable = [capture]
				referencetime += updateinterval

	else:
		#### If the action is performed in a certain space time.
		updateinterval = intervalinseconds
		updatelasting = 10
		startingtime = round(time.time(),2)
		referencetime = 0
		updatetable = []
		pathupdate(Originpath,Replicapath)
		while time.time() < round(startingtime+updatelasting,2):
			updatetime = round(startingtime + referencetime + updateinterval,2)
			capture = round(time.time(),2)
			if capture == updatetime and capture not in updatetable:
				pathupdate(Originpath,Replicapath)
				updatetable.append(capture)
				print('Referencetime is: ',referencetime)
				print(updatetable)
				referencetime += updateinterval

parser = argparse.ArgumentParser(prog='Synchronizes the content of a replica folder respect to one original folder')
parser.add_argument_group()
parser.add_argument('originalpath',type=str,nargs=1,help='Path to the original folder, must be string')
parser.add_argument('replicapath',type=str,nargs=1,help='Path to the replica folder, must be string')
parser.add_argument('interval',type=int,nargs=1,help='Interval period to synchronize (in seconds), must be an integer')
args = parser.parse_args()

updateperiodically(args.originalpath[0],args.replicapath[0],args.interval[0])
