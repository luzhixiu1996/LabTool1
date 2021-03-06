import os
import sys



# take in a file
# label the attributes by their hashing 
# feature select them through script(export.sh)
# format the data for processing(rid the weka markers)
#recover the hash 
# process the files (cv.py)

# take in a file


userFolder=sys.argv[1]   #first arguement from command line should be the name of the user, this name is used for folder name
# userFolder="user1"
#create feature selected folder
if not os.path.exists(os.path.join(os.getcwd(),userFolder,"FeatureSelected")):
    os.mkdir(os.path.join(os.getcwd(),userFolder,"FeatureSelected"))
f=open(os.path.join(os.getcwd(),userFolder,"raw.csv"),"r")

baseName=os.path.basename(f.name)
commandString="python csvToarff.py "+baseName+" "+userFolder

print commandString
os.system(commandString)
#set the top feature here
def getMaxFeature():
    path=os.path.join(os.getcwd(),userFolder,"raw.arff")
    f=open(path,"r")
    cnt=0
    for line in f:
        cnt+=1
        splitList=line.split(" ")
        if 'class' in splitList[1]:
            break
    return cnt-2   

import configparser
configPath=os.path.join(os.getcwd(),userFolder,"config.txt")
settings = configparser.ConfigParser()
settings._interpolation = configparser.ExtendedInterpolation()
settings.read(configPath)
settings.set('SectionOne', 'top feature', str(getMaxFeature()))
with open(configPath, 'wb') as configfile:
    settings.write(configfile)   






f=open(os.path.join(os.getcwd(),userFolder,"raw.arff"),"r")



outputFolder=os.path.join(os.getcwd(),userFolder,"FeatureSelected")
scriptPath=os.path.join(os.getcwd(),"RankFeature.sh")
print scriptPath
from subprocess import call
# call(["./RankFeature.sh",f.name,outputFolder]) call doesnt work, quited trying after spending half an hour on it
command="./RankFeature.sh "+f.name+" "+outputFolder
os.system(command) #works like a charm!


# format the data for processing(rid the weka markers)
os.chdir(os.path.join(os.getcwd(),userFolder))

import rawToArff_mrmr
import Format

# process the files (cv.py)
avg=settings.get('SectionOne','average the result')
if avg.find("e")>0:
    import cv_Average
else:
    import cv






 