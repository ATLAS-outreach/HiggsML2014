"""
ATLAS Higgs Machine Learning Challenge 2014

Evaluate different AMS score of a submission with kaggle format

Author D. Rousseau LAL evolved from original by J. Noah-Vanhoucke, Kaggle.

"""

import os
import csv
import math


def create_solution_dictionary(solution):
    """ Read solution file, return a dictionary with key EventId and value the row, as well as the header
    Solution file headers: EventId, Label, Weight """
    
    solnDict = {}
    print "Reading solution file ",solution
    with open(solution, 'rb') as f:
        soln = csv.reader(f)
        header=soln.next() # header
        iid=header.index("EventId")
        for row in soln:
                solnDict[row[iid]] = row
    return solnDict,header

        
def check_submission(submission):
    """ Check that submission RankOrder column is correct:
        1. All numbers are in [1,NTestSet]
        2. All numbers are unqiue
    """
    Nelements=550000 # hard coded number of event of a valid submission file
    rankOrderSet = set()    
    with open(submission, 'rb') as f:
        sub = csv.reader(f)
        iline=0 
        lowest_signal_rank=Nelements+1
        largest_background_rank=0         
        sub.next() # header
        iline+=1
        for row in sub:
            rankOrderSet.add(row[1])
            if row[2]=="s":
              lowest_signal_rank=min(lowest_signal_rank,int(row[1]))
              # print "s=",row[1]
            elif row[2]=="b":                    
              largest_background_rank=max(largest_background_rank,int(row[1])) 
              # print "b=",row[1]
            else:
              print "ERROR unrecognised label=",row[2]," at line ",iline
              exit()
            iline+=1
    if len(rankOrderSet) != Nelements:
        print 'ERROR RankOrder column must contain unique values'
        exit()
    elif rankOrderSet.isdisjoint(set(xrange(1,Nelements+1))) == False:
        print 'ERROR RankOrder column must contain all numbers from [1..NTestSset]'
        exit()
        
    if lowest_signal_rank!=largest_background_rank+1:     
        print "ERROR the lowest signal rank is:",lowest_signal_rank
        print "ERROR the largest background rank is:",largest_background_rank
        print "ERROR while all signal rank should be above all background rank!"
        exit()                                          

    return True

    
def AMS(s, b):
    """ Approximate Median Significance defined as:
        AMS = sqrt(
                2 { (s + b + b_r) log[1 + (s/(b+b_r))] - s}
              )        
    where b_r = 10, b = background, s = signal, log is natural logarithm """
    
    br = 10.0
    radicand = 2 *( (s+b+br) * math.log (1.0 + s/(b+br)) -s)
    if radicand < 0:
        print 'radicand is negative. Exiting'
        exit()
    else:
        return math.sqrt(radicand)




if __name__ == "__main__":

    
    #submissionFile = "submission.csv"
    submissionFile = "submission_tmva.csv"
    #submissionFile = "submission_simplest.csv"        
    


    # solution file is the full file from opendata
    solutionFile = "atlas-higgs-challenge-2014-v2.csv"  
    solutionDict,header = create_solution_dictionary(solutionFile)
    ilabel=header.index("Label")
    iid=header.index("EventId")
    ikaggleweight=header.index("KaggleWeight") # weight normalised wrt kaggle samples
    ikaggleset=header.index("KaggleSet") # which kaggle sample "t" training "b" public leaderboard "v" private ld "u" unused                       

    signalPublic=0.
    backgroundPublic=0.
    signalPrivate=0.
    backgroundPrivate=0.
                
    if check_submission(submissionFile):
        print submissionFile," is valid"

        
    with open(submissionFile, 'rb') as f:
        sub = csv.reader(f)
        iline=0 
        sub.next() # header
        iline+=1
        for row in sub:
            eventId=row[0]
            sol=solutionDict[eventId]
            kaggleweight=float(sol[ikaggleweight])
            label=sol[ilabel]
            kaggleset=sol[ikaggleset]
            #just to be sure
            if sol[iid] != eventId:
                print sol[iid],eventId
                exit()


            if row[2] == 's': # only events predicted to be signal are scored
                if label == 's':
                        if kaggleset=="b":
                                signalPublic += kaggleweight
                        elif kaggleset=="v":
                                signalPrivate += kaggleweight                            
                        else:
                            print "kaggleset=",usage
                elif label == 'b':
                        if kaggleset=="b":
                                backgroundPublic += kaggleweight
                        elif kaggleset=="v":
                                backgroundPrivate += kaggleweight                            
                else:
                    print "something wrong",label
                    exit()

    print "Public leaderboard: AMS = ",AMS(signalPublic, backgroundPublic),'signal = {0}, background = {1}'.format(signalPublic, backgroundPublic)
    print "Private leaderboard: AMS = ",AMS(signalPrivate, backgroundPrivate),'signal = {0}, background = {1}'.format(signalPrivate, backgroundPrivate)

    
#with simplest      
#Public leaderboard: AMS =  1.54450974337 signal = 461.228096209, background = 89012.844986
#Private leaderboard: AMS =  1.53518474743 signal = 457.142474838, background = 88508.8010881

#with original tmva (with TMVA 4.1.3 in Root 5.34/03)
#Public leaderboard: AMS =  3.24953916678 signal = 217.039443378, background = 4379.2523956
#Private leaderboard: AMS =  3.19956489456 signal = 212.848603705, background = 4345.089289


       
