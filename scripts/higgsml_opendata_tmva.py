"""
ATLAS Higgs Machine Learning Challenge 2014

Train TMVA BDT
Note that the TMVA benchmark on kaggle was obtained with TMVA 4.1.3 in Root 5.34/03.
Newer version may have different performances

Author D. Rousseau LAL

"""
# this script has 5 steps which need to be run sequentially
# the output of each step is saved in one or more file,
# so that each step can be run separately for easier debugging
# use the doXYZ flag to switch steps on/off

from ROOT import TFile,TTree,gStyle,TMVA,TCut,TH1F
import array
gStyle.SetOptStat(1111111)

import random,string,math,csv

debug=False
debug=True # if print some debugging printout

docsvtoroot=False    
dotraining=False     
doevaluate=False     
dothreshold=False    
dosubmission=False   # 

# uncomment the one you do not want
docsvtoroot=True # read csv file, convert into root file
dotraining=True # train on training file, save training in xml file
doevaluate=True # apply training on training and test files, output new root files with score variable
dothreshold=True # compute optimal threshold from score training file
dosubmission=True # generate csv file for kaggle submission, from optimal threshold and test score file

filenamecsv="atlas-higgs-challenge-2014-v2.csv"
treename="htautau"
picklename="threshold.p"


# convert the cvs file into a root file
# bit by bit conversion, except the "Label" which is converted into an int 1 for "s" 0 for "b"

if docsvtoroot:
    print " Step #1 : read csv file, convert into root file "
    pathtofile=""

    fullfilename=pathtofile+filenamecsv
    print "reading ",fullfilename
    allentries = list(csv.reader(open(fullfilename,"rb"), delimiter=','))

    # first line is the list of variables, put it aside
    header        = allentries.pop(0)
    if debug:
        print header

    output_name  = filenamecsv+'.root'
    output_file  = TFile(output_name, 'recreate')

    # create ttree
    tree = TTree(treename, treename)

    # mapping between name and field
    maps={}

    # mapping of variable name with type
    typemap={}

    # by default all variables are float
    for var in header:
        typemap [ var ] = "float"

    # create the new branches if any
    newvars= []
    # newvars= ["MyGreatNewVar"] 
    for var in newvars:
        maps [ var ] = array.array('f',[0.0])
        tree.Branch(var , maps[var],  '% s/F' % (var))  # assume all new vars are float

        
    # deal with some exception
    typemap["EventId"]="int" 
    typemap["PRI_jet_num"]="int"
    typemap["Label"]="int" # s/b will be converted to 1/0
    typemap["KaggleSet"]="int" # t b v u will be converted in 0 10 11 100


    if len(typemap)!=len(header): # we should not have added any variable
        print "typemap :", len(typemap), "header : ", len(header) # we should not have added any variable
        exit() # should not happen


    # create the tree branches
    for var in header:
        type=typemap[var]
        if type=="float":
            maps [ var ] = array.array('f',[0.0])
            tree.Branch(var , maps[var],  '% s/F' % (var))
        elif type=="int":
            maps [ var ] = array.array('i',[0])
            tree.Branch(var , maps[var],  '% s/I' % (var))

    if debug:
        tree.GetListOfBranches().Print()    

    # now fill the tree    
    ientry=0
    nvar=len(header)
    for entry in allentries:
        for ivar in range(nvar):
            varval=entry[ivar]
            varname=header[ivar]
            type=typemap[varname]

            # convert the character variables into int
            if varname=="Label":
                if varval=="s":
                    varval=1
                elif varval=="b":
                    varval=0
                else:
                    varval=-999
            if varname=="KaggleSet":
                if varval=="t":
                    varval=0
                elif varval=="b":
                    varval=10
                elif varval=="v":
                    varval=11
                elif varval=="u":
                    varval=100
                else:
                    varval=-999

            if type=="float":        
                maps [ varname ] [0]= float(varval)
            elif type=="int":
                maps [ varname ] [0]= int(varval)

            # now fill the new variables if any
            if len(newvars)!=0:
                maps["MyGreatNewVar"][0]=maps["PRI_lep_phi"][0]+1.213141 # some calculation


                
        tree.Fill()
        # if ientry>10:
        #    break
        ientry+=1
        if ientry % 10000 == 1:
            print "processing event ",ientry

    print ientry, " entries successfully written "
    # Save and close the output file (required for data to be written)    
    output_file.Write()
    output_file.Close()
    # cleanup this big object
    del allentries

# train from training.csv.root
# output training in xml
# training is the most simple BDT in TMVA
# this is deliberate to leave room for improvements within TMVA

if dotraining:
    print " Step #2 : train on training file, save training in xml file"
    output_directory = 'higgsml_output'
    traintree_name = treename
    trainfilename=filenamecsv+".root" 


    trainfile = TFile.Open(trainfilename,"read")
    traintree = trainfile.Get(traintree_name)
    
    TMVA.Tools.Instance()
    
    
    # create the tmva output file, which will be full of details about the training
    fout = TFile("tmvatest.root","RECREATE")


    # use the default factory
    factory = TMVA.Factory("TMVAClassification", fout)                                



    # build the list of variables
    al=traintree.GetListOfBranches()
    varlist=[]
    for i in range(al.GetEntries()):
        varlist+=[al[i].GetName()]

        
    if debug:
        print "all variables of ",trainfile, " ", varlist
        print "now stripping EventId Weight and Label "

    # these variables should not be used for training
    mva_input_list=[e for e in varlist if not e in ['EventId','Weight','Label','KaggleSet','KaggleWeight']] 
    if debug:
        print "all input variables to BDT ", mva_input_list
    if len(mva_input_list)!=len(varlist)-5:
        raise Exception #  Something not understood in building mva_input_list

    # only use kaggle training set (arbitrary) KaggleSet==0    
    # signal selection    
    signalCut = TCut( "Label==1 && KaggleSet==0" ) 
    # background selection
    backgrCut = TCut( "Label==0 && KaggleSet==0" ) 

    # only one input tree
    factory.SetInputTrees(traintree, signalCut, backgrCut );
    

    n=0
    # declare all variables (all float except one int )
    for var in mva_input_list:
        if var=="PRI_jet_num":
            factory.AddVariable( var, var, "units", 'I' );
        else:
            factory.AddVariable( var, var, "units", 'D' );
        n +=1

    # specify weight. Can use KaggleWeight when using kaggle training set

    # if want to use the complete data set, then one should use variable Weight

    # if want to use another subset, then one should use variable
    # for signal event (Label==1)     : Weight*(Sum_(i all signal) Weight_i)) /(Sum_(i subset signal) Weight_i))
    # for background event (Label==0) : Weight*(Sum_(i all background) Weight_i)) /(Sum_(i subset background) Weight_i))
    # (KaggleWeight was computed like that for Kaggle subsets)     
    factory.SetWeightExpression("KaggleWeight");
    

 
    # SplitMode=block so that the order is respected.
    # usually TMVA split the input file in two, one for training, one for testing
    # but we want to use the full training.csv file for training, since the testing will be done from test.csv
    # TMVA way of doing this is to say we want just 1 signal and 1 background test event. ALl the others will be used for training
    factory.PrepareTrainingAndTestTree( signalCut, backgrCut,"nTrain_Signal=0:nTrain_Background=0:nTest_Signal=1:nTest_Background=1:SplitMode=Block")
    
    # use BDT out of the box, no attempt to fine tune
    method = factory.BookMethod(TMVA.Types.kBDT, "BDT")


    # launch the training
    factory.TrainAllMethods()
    # factory.TestAllMethods()
    # factory.EvaluateAllMethods()
    
    fout.Close()
    


# read in train and test file, apply scoring as described in weights directory
# write out new root tree with additional score file

if doevaluate:
    print " Step #3 : apply training on training and test files, output new root files with score variable in addition"


    inputfilename=filenamecsv+".root"
    outputfilename=filenamecsv+"_score.root"


    new_variables_list = [
        'bdt',
        ]


    maps = {}

    inputfile = TFile.Open(inputfilename,"read")
    inputtree    = inputfile.Get(treename)

    # get the list of input variables
    al=inputtree.GetListOfBranches()
    varlist=[]
    for i in range(al.GetEntries()):
        varlist+=[al[i].GetName()]
    mva_input_list=[e for e in varlist if not e in ['EventId','Weight','Label','KaggleSet','KaggleWeight']]




    # create array to map variables to values
    for var in varlist:                
        maps [var ] = array.array('f',[0.0]) # all float, including possible integer (otherwise the reader chokes)          

    for var in new_variables_list: 
        if debug:
            print "adding ",var
        maps [var ] = array.array('f',[0.0])


    reader=TMVA.Reader()
    # Add to the reader the variables to be used for bdt evaluation (only that one)
    # Make sure variables are in the same order as for training

    for var in mva_input_list:                
        reader.AddVariable( var , maps[var]);            

    reader.BookMVA("BDT","weights/TMVAClassification_BDT.weights.xml")


    # Create the output file
    print "creating file ",outputfilename
    outputfile = TFile.Open(
        outputfilename, 
        'RECREATE'
        )

    # Clone the original chain (but don't copy any entries yet).
    outputtree = inputtree.CloneTree(0)

    # Create other derived branches in the new tree
    for var in new_variables_list:
            outputtree.Branch(var , maps[var],  '% s/F' % (var))

    if debug:
        print "List of branches for output tree"
        outputtree.GetListOfBranches().Print()


    # Loop over the original tree.
    max_index = inputtree.GetEntries()
    # max_index=min(max_index,10) ; # print "DR hack max event",max_index
    for i in xrange(0, max_index):
        if i % 10000==1:
            print " processing event ",i 

        # Now actually load the tree data.  This needs to be done before
        # doing any manual selections or calculations.
        inputtree.GetEntry(i)

        # copy the input tree variables into the arrays (might be a better way)
        # actually this is not be necessary for variables that are not used by BDT
        for var in varlist:
            exec ('maps["'+var+'"][0]=inputtree.'+var)

        # compute bdt scoree    
        maps['bdt'][0]=reader.EvaluateMVA("BDT")

        # Add this entry in the new tree
        outputtree.Fill()


    # Save the output file (required for data to be written)
    outputfile.Write()

    # Close the output file
    outputfile.Close()


# compute a threshold for the best AMS
# plot the different AMS
if dothreshold:
    print " Step #4 : compute optimal threshold from score training file"

    def amssimple(s,b):
        from math import sqrt
        if b==0:
            return 0
        return s/sqrt(float(b))

    def amsasimov(s,b):
        from math import sqrt,log
        if b==0:
            return 0

        return sqrt(2*((s+b)*log(1+float(s)/b)-s))

    def amsfinal(s,b):
        return amsasimov(s,b+10.)

    def printsig(s,b):
        return "ams simple=%.3f asimov=%.3f final=%.3f" % (amssimple(s,b),amsasimov(s,b),amsfinal(s,b))

    # function to return a vector of bin content of an histogram
    def getbins ( h):
        vals=[]
        vales=[]
        nbins=h.GetNbinsX()
        # copy the bins. Note that bin 0 is the underflow, bin nbins+1 is overflow    
        for i in range (0,nbins+2): 
            vals+=[h.GetBinContent(i)]
            vales+=[h.GetBinError(i)]            
        underflow=h.GetBinContent(0)
        overflow=h.GetBinContent(nbins+1)        
        if underflow>0:
            print " WARNING histo ", h.GetName(), " underflow non zero :",underflow," deliberate ?"
        if overflow>0:    
            print " WARNING histo ", h.GetName(), " overflow non zero :",overflow," deliberate ?"            
        return vals,vales    

    
    inputfilename= filenamecsv+"_score.root"
    inputfile = TFile.Open(inputfilename,"read")
    inputtree    = inputfile.Get(treename)

    nbins=1000
    scoremin=-1
    scoremax=1
    hsig=TH1F("hsig","signal bdt score",nbins,scoremin,scoremax)
    hbkg=TH1F("hbkg","background bdt score",nbins,scoremin,scoremax)    
    # accumulate sum of square weigths
    hsig.Sumw2()
    hbkg.Sumw2()    

    
    # fill histograms, using weight, only for training sample
    inputtree.Project("hsig","bdt","KaggleWeight*(Label==1 && KaggleSet==0)")
    inputtree.Project("hbkg","bdt","KaggleWeight*(Label==0 && KaggleSet==0)")    

    # copy into vectors
    vsig,ve=getbins(hsig)
    vbkg,ve=getbins(hbkg)    

    # prepare other vectors
    vsigint=[0]*(nbins+2)
    vbkgint=[0]*(nbins+2)
    vamsasimov=[0]*(nbins+2)
    vamsfinal=[0]*(nbins+2)
    vamssimple=[0]*(nbins+2)    

    # signal has higher values than background. So integrate histograms from the right
    sumsig=0
    sumbkg=0
    for i in range (nbins+1,-1,-1):
        sumsig+=vsig[i]
        vsigint[i]=sumsig
        sumbkg+=vbkg[i]
        vbkgint[i]=sumbkg
        vamsasimov[i]=amsasimov(sumsig,sumbkg)
        vamssimple[i]=amssimple(sumsig,sumbkg)
        vamsfinal[i]=amsfinal(sumsig,sumbkg)        

    hsigint=TH1F("hsigint","integrated signal vs bdt score",nbins,scoremin,scoremax)
    hbkgint=TH1F("hbkgint","integrated bkg vs bdt score",nbins,scoremin,scoremax)        
    hamsfinal=TH1F("hamsfinal","final ams vs bdt score",nbins,scoremin,scoremax)
    hamsasimov=TH1F("hamsasimov","asimov ams vs bdt score",nbins,scoremin,scoremax)
    hamssimple=TH1F("hamssimple","simple ams vs bdt score",nbins,scoremin,scoremax)

    # copy vectors into histogram
    for i in range(nbins+2):
        hsigint.SetBinContent(i,vsigint[i])
        hbkgint.SetBinContent(i,vbkgint[i])        
        hamsfinal.SetBinContent(i,vamsfinal[i])
        hamssimple.SetBinContent(i,vamssimple[i])
        hamsasimov.SetBinContent(i,vamsasimov[i])        

    # one nice plot    
    hamsfinal.SetLineColor(2)
    hamssimple.SetLineColor(3)   
    hamsfinal.Draw()
    hamssimple.Draw("same")
    hamsasimov.Draw("same")
   
    # determine the optimal value
    # Note that we determine the optimal value on the same data as used for the training.
    # There are many ways to do better
    bestamsfinal=max(vamsfinal)
    ibest=vamsfinal.index(bestamsfinal)
    threshold=hamsfinal.GetBinLowEdge(ibest+1)
    print "Best amsfinal ",bestamsfinal," for threshold :",threshold," ( ams simple =",vamssimple[ibest],", ams asimov=",vamsasimov[ibest],")"

    print " Writing out threshold value ",threshold, " in pickle file:",picklename
    import pickle
    pickle.dump(threshold,open (picklename,"wb"))


# create kaggle submission file (just for reference)
# ranks all entries according to score
# given a threshold, label entries "s" or "b"
if dosubmission:
    print " Step #5 : generate csv file for kaggle submission, from optimal threshold and test score file"
    import pickle
    threshold=pickle.load( open( picklename, "rb" ) )
    print " Reading out threshold value ",threshold, " from pickle file:",picklename    

    inputfilename=filenamecsv+"_score.root"
    submissionfilename="submission_tmva.csv"

    inputfile = TFile.Open(inputfilename,"read")
    inputtree    = inputfile.Get(treename)


    print  "Loop once to load the EventId, bdt score pairs"
    max_index = inputtree.GetEntries()
    testentries=[]
    for i in xrange(0, max_index):
        if i % 100000==1:
            print " processing event ",i 
        inputtree.GetEntry(i)
        # only consider event from the public and private dataset
        if inputtree.KaggleSet not in [10,11]:
            continue
        testentries+=[(inputtree.EventId,inputtree.bdt)]

    # sort on the bdt,
    print "sort on the bdt score"
    testsorted=sorted(testentries,key=lambda entry: entry[1])

    # then build a map key Id, value rank
    testdict={}
    r=1 # kaggle ask to start at 1
    for e in testsorted:
        if r % 100000==1:
            print " sorting event ",r 

        testdict[e[0]]=r
        r+=1

        
    print "size of dict",len(testdict)
    if len(testdict)!=len(testsorted):
        print " ERROR ! Size of input file : ",len(testsorted), " size of map : ",len(testdict), " Should be equal. Maybe identical values ? " 
        raise Exception # should not happen


    outputfile=open(submissionfilename,"w")
    outputfile.write("EventId,RankOrder,Class\n")

    print  "Loop again to write the submission file",submissionfilename
    for i in xrange(0, max_index):
        if i % 100000==1:
            print " processing event ",i 
                
        inputtree.GetEntry(i)
        if inputtree.KaggleSet not in [10,11]:
            continue

        rank=testdict[inputtree.EventId]
        if rank>550000:
            print "large rank: ",rank, " for event ",i, " ",inputtree.EventId
            exit() # should not happen
        
        # compute label 
        slabel="b"
        if inputtree.bdt>threshold:
            slabel="s"
            
        outputfile.write(str(inputtree.EventId)+",")
        outputfile.write(str(rank)+",")
        outputfile.write(slabel)            
        outputfile.write("\n")

    outputfile.close()
    print "All done!"
    # delete big objects
    del testentries
    del testdict
    del testsorted
