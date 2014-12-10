"""
ATLAS Higgs Machine Learning Challenge 2014

This script is a very simple example,  it uses a simple window on one variable DER_mass_MMC
to compute the score and build a submission file in kaggle format

Author D. Rousseau LAL
"""


import csv

datafile="atlas-higgs-challenge-2014-v2.csv"
 

print "Reading the data file :",datafile
# store everything in memory
alldata = list(csv.reader(open(datafile,"rb"), delimiter=','))

# first line is the list of variables, put it aside
header        = alldata.pop(0)


# get the index of a few variables
iid=header.index("EventId")
ilabel=header.index("Label")
ikaggleset=header.index("KaggleSet")
ikaggleweight=header.index("KaggleWeight")
iweight=header.index("Weight") # original weight     
immc=header.index("DER_mass_MMC")
injet=header.index("PRI_jet_num")

# turn all entries from string to float, except EventId and PRI_jet_num to int, except Label and KaggleSet remains string
for entry in alldata:
        for i in range(len(entry)):
                if i in [iid,injet]:
                    entry[i]=int(entry[i])
                elif i not in [ilabel,ikaggleset]:
                    entry[i]=float(entry[i])

print "Loop on  dataset and compute the score"
header+=["myscore"] # myscore is a new variable

# loop and all entries and compute my score
for entry in alldata:
    myscore=-abs(entry[immc]-125.) # this is a simple discriminating variable. Signal should be closer to zero.
                                   # minus sign so that signal has the highest values
                                   # so we will be making a simple window cut on the Higgs mass estimator
                                   # 125 GeV is the middle of the window
    entry+=[myscore]
    
# at this stage alldata is a list (one entry per line) of list of variables
# which can be conveniently accessed by getting the index from the header 

threshold=-22 # somewhat arbitrary value, should be optimised




print "Loop again to determine the AMS, using threshold:",threshold
sumselsig=0.
sumselbkg=0.
sumallsig=0.
sumallbkg=0.
sumsubsig=0.
sumsubbkg=0.

sumselkagglesig=0.
sumselkagglebkg=0.

iscore=header.index("myscore")
print "only look at kaggle public data set ('b') (other choice training 't', private 'v', unused 'u')"
print "One could make one own dataset (then the weight should be renoramalised)"

for entry in alldata:
    myscore=entry[iscore]
    weight=entry[iweight]
    kaggleweight=entry[ikaggleweight]    

    # compute sum of signal and background weight needed to renormalise
    if entry[ilabel]=="s":
        sumallsig+=weight
    else:
        sumallbkg+=weight    

        

    if entry[ikaggleset]!="b":
        continue
    
    # from now on, only work on subset
    # compute sum of signal and background weight needed to renormalise
    if entry[ilabel]=="s":
        sumsubsig+=weight
    else:
        sumsubbkg+=weight    
    
    
    # sum event weight passing the selection. Of course in real life the threshold should be optimised
    if myscore >threshold:
        if entry[ilabel]=="s":
            sumselsig+=weight
            sumselkagglesig+=kaggleweight
        else:
            sumselbkg+=weight                
            sumselkagglebkg+=kaggleweight    

            
# ok now we have our signal (sumselkagglesig) and background (sumselkagglebkg) estimation
# just as an illustration, also compute the renormalisation myself from weight

sumsig=sumselsig*sumallsig/sumsubsig
sumbkg=sumselbkg*sumallbkg/sumsubbkg

# compute AMS
def ams(s,b):
    from math import sqrt,log
    if b==0:
        return 0

    return sqrt(2*((s+b+10)*log(1+float(s)/(b+10))-s))

print " AMS with recomputed weight: ",ams(sumsig,sumbkg),"( signal=",sumsig," bkg=",sumbkg,")"
print " AMS with kaggle weight : ",ams(sumselkagglesig,sumselkagglebkg),"( signal=",sumselkagglesig," bkg=",sumselkagglebkg,")"
print " recomputed weight and Kaggle weight should be identical if using a predefined kaggle subset"


submissionfilename="submission_simplest.csv"
print " Now build submission file a la Kaggle:",submissionfilename

# build subset with only the needed variables
alltest=[]
for entry in alldata:
    if entry[ikaggleset] not in ["b","v"]:
        continue
    # build the new record with only the needed info    
    outputentry=[]
    outputentry+=[entry[iid]]
    outputentry+=[entry[iscore]]
    alltest+=[outputentry]

#index of variables in the subset     
ioid=0
ioscore=1    
# Sort on the score 
alltestsorted=sorted(alltest,key=lambda entrytest: entrytest[ioscore])
# the RankOrder we want is now simply the entry number in alltestsorted


outputfile=open(submissionfilename,"w")
outputfile.write("EventId,RankOrder,Class\n")

rank=1 # kaggle wants to start at 1
for oentry in alltestsorted:
    # compute label 
    slabel="b"
    if oentry[ioscore]>threshold: # arbitrary threshold
        slabel="s"

    outputfile.write(str(oentry[ioid])+",")
    outputfile.write(str(rank)+",")
    outputfile.write(slabel)            
    outputfile.write("\n")
    rank+=1


outputfile.close()



# delete big objects
del alldata,alltest,alltestsorted

