import sys
import re
import os
import operator
from collections import defaultdict
from collections import Counter
import math
from time import time
from stemming.porter3 import stem
import nltk
from nltk.corpus import stopwords

newsobject1 = {}
newsobject2 = {}
newsobject3 = {}
newsobject4 = {}
TotalFileFor_Train = 600
TotalFileFor_Test = 20
vocabword = 50000
total_percent = 0
total_test = 0

header = ["X-Newsreader: ","Expires:","Version:","Last-modified:","Alt-atheism-archive-name:",
            "Archive-name:","Supersedes:","Summary:","From:","Subject:","Keywords:","Lines:","Distribution:",
            "Reply-To:","NNTP-Posting-Host:","Organization:"]


def removeStopwords(wordlist, stopwords):
    return [w for w in wordlist if w not in stopwords]

def parseinput(root,path,newsobject):
    if root not in newsobject.keys():
        dict1 = {}
        newsobject.setdefault(root,[]).append(dict1)

    f = file(path,"r")
    lines = f.readlines()
    for line in lines:
        if(line[0] == '>' or line[0] == '|'): #check for early message
            continue
        headerlist = re.findall(r"[\w']+:",line)
        if(len(headerlist) > 0):
            if headerlist[0] in header: #check for header
                continue
        wordlist = re.findall(r"[\w']+",line.lower())
        removeStopwords(wordlist,stopwords.words('english'))
        wordfreq = Counter(wordlist)
        for word in wordfreq:
            sword = stem(word)
            lst = newsobject[root]
            step = False
            for idx,item in enumerate(lst):
                if sword in item.keys():
                    count = item[sword]+wordfreq[word]
                    newsobject[root][idx][sword] = count;
                    dc = {}
                    dc[sword] = count
                    step = True
                    break
            if step:
                continue
            dc = {}
            dc[sword] = wordfreq[word]
            newsobject[root].append(dc)

def classify(files,path,newsobject):
    global classified
    global total
    global vocabword

    f = file(path,"r")
    lines = f.readlines()
    prob = {}
    for line in lines:
        if(line[0] == '>' or line[0] == '|'): #check for early message
            continue
        headerlist = re.findall(r"[\w']+:",line)
        if(len(headerlist) > 0):
            if headerlist[0] in header: #check for header
                continue
        wordlist = re.findall(r"[\w']+",line.lower())
        removeStopwords(wordlist,stopwords.words('english'))
        wordfreq = Counter(wordlist)
        dict2 = {}
        TotalCategory = len(newsobject)
        TotalWords = 0
        PC = 1.0/(float)(TotalCategory) #p(c) = 1/TotalCategory
        for key in newsobject.keys():
            list_item = newsobject[key]
            for item in list_item:
                for key in item.keys():
                    TotalWords += item[key] #calculate toatl words present in training set

        for word in wordfreq:
            sword = stem(word)
            TotalWords_allCategory = 0
            for key in newsobject.keys():
                prob.setdefault(key,[]).append(dict2)
                list_item = newsobject[key]
                for item in list_item:
                    if sword in item.keys():
                        TotalWords_allCategory += item[sword]

            for key in newsobject.keys():
                list_item = newsobject[key]
                for item in list_item:
                    if sword in item.keys():
                        PWC = item[sword] + 1/((float)(TotalWords_allCategory) + vocabword)  #p(w/c) = word in this category/total word in training set
                        PW = item[sword] + 1/(float)(TotalWords)  #p(w) = word in this category/frequecy of this word in all category
                        if PW != 0:
                            finalProbability = (PC*PWC)/(float)(PW) #p(c/w) =p(c)*p(w/c)/p(w)
                            tmpDict = {}
                            tmpDict[sword] = finalProbability
                            prob[key].append(tmpDict)
    postiprob = {}
    for key in prob.keys():
        tmp = 1.0
        lst = prob[key]
        for item in lst:
            for word in item.keys():
                if word:
                    tmp *= item[word]*10 #calculating postirior probability
        postiprob[key] = tmp
    maxVal = -1.0
    Targetcategory = ""
    for key in postiprob:
        if maxVal < postiprob[key]:
            maxVal = postiprob[key]
            Targetcategory = key

    return Targetcategory

def process_input (files,filepath) :
    global newsobject1
    global newsobject2
    global newsobject3
    global newsobject4

    bag = []

    res1 = classify(files, filepath, newsobject1)
    bag.append(res1)
    res2 = classify(files, filepath, newsobject2)
    bag.append(res2)
    res3 = classify(files, filepath, newsobject3)
    bag.append(res3)
    res4 = classify(files, filepath, newsobject4)
    bag.append(res4)

    bagfreq = Counter(bag)
    maxCount = 0
    res = ""
    for word in bagfreq:
        #if word == files:
         #   return word
        #else:
        if maxCount < bagfreq[word]:
            maxCount += bagfreq[word]
            res = word
    return res

def chkoutput():
    global total_percent
    global total_test
    total = 0
    classified = 0

    path = "/home/newton/bro/20news-bydate/20news-bydate-test/"
    dirs = os.listdir(path)
    for files in dirs:
        npath = path+"/"+files
        if(os.path.isfile(npath)):
            print npath," is not a directory"
            continue
        t0 = time()
        subfiles = os.listdir(npath)
        count = 0 #takes only TotalFileFor_Test file to Test system
        for subfile in subfiles:
            filepath = npath+"/"+subfile
            if(os.path.exists(filepath) and count < TotalFileFor_Test):
                if(os.path.isfile(filepath)):
                    res = process_input(files,filepath)
                    print files,"---------------->", res
                    total += 1
                    if res == files :
                        classified += 1

                    #print "classifing"
                else:
                    print filepath,"is not a file"
            else:
                print "Test Completed for ",files
                duration  = time()-t0
                print "time to classify ",files," is ",duration
                print "Percentage Accuracy = ", classified * 100/(float)(total)
                total_percent += classified/(float)(total)
                total_test += 1
                total = 0
                classified = 0
                break
            count+=1


def main():
    global newsobject1
    global newsobject2
    global newsobject3
    global newsobject4
    global total_percent
    global total_test

    print "...................Training................................"
    path = "/home/newton/bro/20news-bydate/20news-bydate-train/"
    dirs = os.listdir(path)
    val = 0;
    for files in dirs:
        npath = path+"/"+files
        if(os.path.isfile(npath)):
            print "not a directory"
            continue
        subfiles = os.listdir(npath)
        cnt = 0 #takes only TotalFileFor_Train file to train system
        for subfile in subfiles:
            filepath = npath+"/"+subfile
            if(os.path.exists(filepath) and cnt < TotalFileFor_Train):
                if(os.path.isfile(filepath)):
                    if cnt <= 150:
                        parseinput(files,filepath,newsobject1)
                    elif cnt <= 300:
                        parseinput(files,filepath,newsobject2)
                    elif cnt <= 450:
                        parseinput(files,filepath,newsobject3)
                    elif cnt <= 600:
                        parseinput(files,filepath,newsobject4)
                else:
                    "not a file"
            else:
                print "Training for ",files,"complete"
                break
            cnt += 1
        val += 1

    print "Training complete \n ..................Testing..................."
    t0 = time()
    chkoutput()
    duration = time()-t0
    print "total time to classify ",duration

    print "Average Percentage Acuuracy = ", total_percent*100/(float)(total_test)

if __name__ == '__main__':
    main()
