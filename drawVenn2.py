# -*- coding: utf-8 -*-
#system ask for two argument: filename and number of topFeatures selected  
import sys
import os
import matplotlib as mpl
from numpy import *
import numpy as np
from sklearn import svm, datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
import configparser
import copy
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
import venn
from sklearn.metrics import roc_curve, auc

showClassROC=False
lw=2
def loadClassifier(cls):
    global classifier,title
    if cls=="SVM":
        title="Support Vector Machine"
        classifier= svm.SVC(kernel='linear', probability=True)
    if cls=="NB":
        title="Naive Bayes"
        classifier =GaussianNB()
    if(cls=='RF'):
        title="Random Forest"
        classifier = RandomForestClassifier(n_estimators=int(NumberOfEstimators)) 



settings = configparser.ConfigParser()
settings._interpolation = configparser.ExtendedInterpolation()
settings.read('config.txt')
Classifier=settings.get('SectionOne','Classifier')
if len(Classifier)!=0:
    cls=Classifier
classifier="SVM"
loadClassifier(cls)

N_estimator=settings.get('SectionOne','Number of Estimators')
if len(N_estimator)!=0:
    NumberOfEstimators=int(N_estimator)
    
folds=15



userFolder=sys.argv[1]
topFeature=int(sys.argv[2])
os.chdir(os.path.join(os.getcwd(),userFolder))

outputFile = open(os.path.join(os.getcwd(),"venn.txt"), 'w')
orig_stdout = sys.stdout
# sys.stdout=outputFile








def loadTopFeature(featureList): 
    global userFolder
    filepath=os.path.join(os.getcwd(),"raw.csv")
    
    rawdata=genfromtxt(filepath,delimiter=',')  
    data=rawdata[:,featureList]
    numberOfAttribute=rawdata.shape[1]
    label=rawdata[:,numberOfAttribute-1:numberOfAttribute]
    label=np.squeeze(label)
    changeLabel(data,label)


def changeLabel(data,label):
    originalLabel=copy.copy(label)
    #get the number of classes
    n_classes=np.unique(label)
    loadClassifier(cls)
    global all_test,all_probas,all_fpr,all_fpr,class_fpr,class_tpr
    
    for n in n_classes:
        #reinitialize the labels each iteration
        label=copy.copy(originalLabel)
        #binarize the labels,if the label equals the class n, set it to one,else 
        #set it to zero
        for k in range(0,label.shape[0]):
            if int(label[k])==n:
                label[k]=1
            else:
                label[k]=0
        process(data,label,n)
        
        
def process(X,y,classN):
#     print "process class %d"%(classN)
    global classifier
    cv = KFold(n_splits=folds)
    global all_test,all_probas
    class_test=class_probas=np.array([])
    for train, test in cv.split(X):
        class_test=np.append(class_test,y[test])
        all_test=np.append(all_test,y[test])
#         print X[train]
        probas_ = classifier.fit(X[train], y[train]).predict_proba(X[test])
        class_probas=np.append(class_probas,probas_[:, 1])
        all_probas=np.append(all_probas,probas_[:, 1])


    class_fpr_micro, class_tpr_micro, _ = roc_curve(class_test.ravel(), class_probas.ravel())
    class_fpr[classN],class_tpr[classN],_=roc_curve(class_test, class_probas)

    roc_auc_class_micro = auc(class_fpr_micro,class_tpr_micro)
    print "class %d average: %f" %(classN,roc_auc_class_micro)
    global showClassROC
    if showClassROC:
        print "Not gonna Average the result"
        plt.plot(class_fpr_micro, class_tpr_micro,label='Class  micro-average ROC curve (area = {0:0.2f})'''.format(roc_auc_class_micro ),linewidth=lw)
   
       
    # print all_test.shape
    # print all_probas.shape
    
    
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    fpr["micro"], tpr["micro"], _ = roc_curve(all_test.ravel(), all_probas.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    plt.plot(fpr["micro"], tpr["micro"],
             label='micro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc["micro"]),  linewidth=lw)
    return roc_auc["micro"]




# take in a list of feature list, return elements that appear in all list
def findIntercetion(mylist):
    setList=[]
    for featureList in mylist:
        featureSet=set(featureList)
        setList.append(featureSet)
    return set.intersection(*setList)
    
def getTopFeature(path):
    f=open(path,"r")
    myList=[]
    for line in f:
        splitList=line.split(" ")
        if splitList[0]=="@ATTRIBUTE" or splitList[0]=="@attribute"  and "{" not in splitList[2]:
            myList.append(splitList[1])
    return myList[0:topFeature]

def getMaxFeature(path):
    f=open(path,"r")
    cnt=0
    for line in f:
        cnt+=1
        splitList=line.split(" ")
        if 'class' in splitList[1]:
            break
    return cnt-2   
    


fpath=os.path.join(os.getcwd(),'raw.arff')
getTopFeature(fpath)
maxFeature=getMaxFeature(fpath)
outputFolder=os.path.join(os.getcwd(),"FeatureSelected")
command="../RankFeature.sh "+"raw.arff "+outputFolder
os.system(command)
flist=os.listdir(outputFolder)
sets=[]
labels=[]

for f in flist:
    fpath=os.path.join(os.getcwd(),outputFolder,f)
    featureSet=getTopFeature(fpath)
    sets.append(featureSet)
    label=os.path.basename(f).split(".")[0]
    labels.append(label)

#number of features wont go past thousands, gonna use n^2 
# print sets
methodCnt=[]
FiveList=[]
FourList=[]
ThreeList=[]
TwoList=[]
OneList=[]
for n in range(1,maxFeature+1):
    cnt=0;
#     print n
    
    for ls in sets: ##came up with some bad variable names, sets is a list of list of features selected by different methods
        if ls.count(str(n))>0:
            cnt+=1
    methodCnt.append(cnt)
#     print "Feature %d is selected by %d methods"%(n,cnt)
    
#     
for i in range(len(methodCnt)):
    if methodCnt[i]>=5:
        FiveList.append(i+1)
    if methodCnt[i]>=4:
        FourList.append(i+1)
            
    if methodCnt[i]>=3:
        ThreeList.append(i+1)
    if methodCnt[i]>=2:
        TwoList.append(i+1)         
    if methodCnt[i]>=5:
        OneList.append(i+1)

all_test=all_probas=all_fpr=all_tpr=np.array([])
class_fpr=class_tpr=dict()
roc_auc = dict()
loadTopFeature(FiveList)

aucValues=[]

            
vennLabel=venn.get_labels(sets,fill=['number','logic'])
vennLabel=venn.get_labels(sets,fill=['number'])

# labels.sort(reverse=True)


inv_map = {}
for k, v in vennLabel.iteritems():
    inv_map[v] = inv_map.get(v, [])
    inv_map[v].append(k)

fig, ax = venn.venn5(vennLabel, names=labels)
fig.savefig('venn5.png', bbox_inches='tight')

vennList=[]
keyList=[]
for key in reversed(range(1,topFeature+1)):
    key=str(key)

    
    if inv_map.has_key(key):
        
        for bin in inv_map.get(key):
            
            positiveFeatureList=[]
            outputString=''
            for i in range(len(bin)): 
                if '1' in bin[i]:
                    outputString+=labels[i]+' & '
            
                    positiveFeatureList.append(sets[i])#find the digits with one and the set it concludes 
            outputString=outputString[:len(outputString)-2]   
#             print outputString,           
            interception=findIntercetion(positiveFeatureList)
#             print str(list(interception))
            
            
            



plt.close()
sys.stdout = orig_stdout
outputFile.close()


        
        
    