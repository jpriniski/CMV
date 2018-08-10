
"""
Project: Attitude Change on Change My View (Study 2)

File: comment_analysis.py

Description: This code does the following three things: 
                    1)  calculate use of evidence in comment bodies.
                    2)  determine how many deltas are awarded to each comment.  
                    3)  classify discussions & comment's with respect to a 
                        pre-defined classification framework. 

Authors: J. Hunter Priniski & Zachary Horne
run: python discussion_analysis.py
"""

#REQUIREMENTS
import os
import praw
import pandas as pd
from datetime import datetime
import re
import nltk
import json
import itertools
import string

"""
Since we will be needing stemming capabilites in multiple functions, 
we will declare our SnowballStemmer object right away.  Stemming allows
us to turn different instances of a word (e.g., runner, running, run) into 
a single token (e.g., run).  Doing so will increase the accuracy of our
classification algorithim. 
"""
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english')

"""
We will save the CMV posts as a list of JSON objects.  Therefore, we need 
a method that reads in the JSON objects. 
"""
def json_reader(directory):
    
    with open(directory, 'r') as json_file:

        data = json.load(json_file)

    return data

"""
Phrase stemmer is a method built off of the NLTK SnowballStemmer.  
Phrase stemmer, unlike an out-of-the-box stemmer, will stem each 
token in a phrase and then concatenate the stemmed tokens to rebuild 
the stemmed phrase. Phrase stemming (as opposed to direct string 
stemming) is needed for our classification algorithim.  

EG) Phrase stemmer would phrase each word in the phrase 'beautiful rainbow skies'
as 'beautif rainbow skie'.  A typical stemmer would fail to stem such a phrase. 
"""
def phrase_stemmer(phrase):

    tokens = phrase.split()

    stemmed = [stemmer.stem(token) for token in tokens]

    return stemmed

"""
The method read_terms will allow us to easily read in a list of terms 
associated to given topic and stem the words directly.  Files are expected
to be of the following format: 
term1 \n
term2 \n
(and so on...)

Where the name of the file is the topic.  eg, a file for a topic on Politics 
would listed as politics.txt and could look something like this:
democrat \n
republican \n
president \n
congress
(and so on...)

We will also automatically stem terms in this list using a method called
phrase_stemmer. Phrase_stemmer is built upon NLTK's SnowballStemmer and 
will stem each individual token in a phrase. Stemming increases the 
classification acuracy of the algorithim.

This funciton will output the related terms to a topic as a list of lists. 
Therefore, while classifying, we will match each list of terms directly with 
subsets of the comment body.  This allows us to automatically search the text 
we are wich to classify for terms of variable length.   
"""
def read_terms(directory, stem = True):

    #Read in a file with the directory address provided in the method argument.  
    text_file = open(directory, "r")

    #Since topic lists are composed of a list of terms sperated by a new line,
    #we will split the string input at each new line character, where each line 
    #is an individual phrase relating to the larger topic.  
    lines = text_file.read().split('\n')
    
    #If we wish to stem the terms in our topic list (which we do!), 
    #we will enter this branch. 
    if stem is True:
        
        #We will iterate over every line in our read in file (which is list)
        #of words related to a given topic.  On each line, which is consequently
        #a single word or phrase relating to our topic, we will call the phrase_stemmer
        #function to stem each token in the phrase.  We will then make a list of phrase
        #stems for a given topic.  
        stemmed = [phrase_stemmer(line) for line in lines]

        #After stemming the words in our topic list, there is potential that 
        #we have duplicate terms in our stemmed topic list.  Since the data structure
        #of our topic terms is a list of lists, we need to sort the list by list
        #entry and remove duplicates via iterating over the sourted list.  Hence the 
        #line: list(stemmed for stemmed,_ in itertools.groupby(stemmed))
        stemmed.sort()
        
        return list(stemmed for stemmed,_ in itertools.groupby(stemmed))

    #After stemming the words in our topic list, there is potential that 
    #we have duplicate terms in our stemmed topic list.  Since the data structure
    #of our topic terms is a list of lists, we need to sort the list by list
    #entry and remove duplicates via iterating over the sourted list.  Hence the 
    #line: list(lines for lines,_ in itertools.groupby(list))
    lines.sort()
    
    return list(lines for lines,_ in itertools.groupby(list))


#Talk about prepare text. 
def prepare(text):

    table=str.maketrans("","",string.punctuation) 
    
    text = text.lower()
    text = text.translate(table)
    text = text.split()

    content = [stemmer.stem(w) for w in text]
    
    text = " ".join(content)
    
    text = re.sub('\s+', text, ' ')

    #Turn string into a split list of tokens/
    text = text.split()
    
    #Remove all duplicates in out list. 
    text.sort()
    return list(text for text,_ in itertools.groupby(text))


"""
get_ngrams will turn a body of text into a list of n-tuples.  The n-tuples
represent n consecutive words, and are called ngrams.  For example, a 2-gram
representation of the sentence "I am happy." is [(I, am), (am, happy)].  This 
method requires text split into a list of tokens.  For eg, 'I am happy' needs
to be split into a list of the individual tokens: ["I", "am", "happy"]. The 
method can return tuples in a tuple data strucutre or as list. Since we are matching
individual words from a list of topic terms, we will generally return the tuples
as lists: it makes matching individuals words (tokens) more direct. 
"""
def get_ngrams(text, n, as_list = True):
    #If we only want a 1-gram representation, we will simply encode the
    #tokens of the split string (which are currently strings) into lists. 
    #The matching algorihtim expect to see lists of arbitrary length.  
    #For example, if n is 1: the split string ["I", "am", "happy"] will
    #become: [["I"], ["am"], ["happy"]]. 
    if n is 1:

        tokens_as_list = []                 #We will appending our tokens as strings in lists to this list
    
        for word in text:                   #Iterate over every word token in the text

            tokens_as_list.append([word])   #Append the string in a list to the tokens_as_list list
    
        return tokens_as_list               #Return our new 1-gram list of tokens
    
    else:                                                       #If we want a large n-gram representation we will need to construct the consecutive pairs of tokens.

        grams = list(zip(*[text[i:] for i in range(n)]))
        
        if as_list is True: 

            grams_list = []
    
            for gram in grams:

                grams_list.append(list(gram))

            return grams_list
    
        else:

            return grams

"""
The match method will match the text with respect to the terms in a given classification.
If there is a match in the text with a given topic classifiation term, then the
function returns True. If there is not a match, the method return False. 
"""
def match(text, terms):
    #We want to have a program that can match substrings of a text with 
    #terms of any length.  To do this, we need to find n-gram representations
    #of the text up to the number of tokens in the longest phrase in the topic
    #classifiaction list.  Below we find what the longest phrases in our topic
    #classification list of terms is. 
    largest_GRAM = max([len(x) for x in terms])

    #We will now match the words in our text we wish 
    #to classify with to every term in the dictionary.  Since some terms
    #in the dictionary list of terms are are phrases (they are phrases like 
    #"Make America Great Again" or "Donald Trump"), we need to iterate over
    #every possible n_gram representation up to the largest possible 
    #(as denoted in the largest_GRAM variable above).
    for i in range(1, largest_GRAM + 1):
        
        grams = get_ngrams(text, i)     #Get the n-gram representation of the text for value i
        
        for term in terms:              #Iterate over every term in our list of terms related to a given topic.
        
            if term in grams:           #If one of the terms is in the text, we return True
                
                return True
   
    return False                        #If there is no term in our topic list in the text, we return False


"""
CHANGE LANGUAGE TO BE GENERIC
classify_text will take an text and see if there is a match with the a word in a
topic list provided.  This method is general: it will classify any text with respect
to any list of topics. The function will return a dictionary of topics matched
to boolean values.  i.e., a dictionary of topics and a 1 or 0 value denoting 
if that text is classified by that topic.  For example, if this method returns the 
following dictionary of topic classifiations for a given text: 

{
    "politics": 0,
    "gender":   1,
    "moral":    0
}
it is said that the text relates to gender issues and not moral or political topics.
"""
def classify_text(text, topics):

    classifications = {} #Create a empty dictionary, we will add our classifications to this dictionary as we iterate over every topic

    prepared_text = prepare(text)
    
    for key, val in topics.items():

        text_match = match(prepared_text, val)

        #If there is a match with the text and one of the values in the list
        #of terms associated with a topic, we will set the topic value equal to 1
        if text_match is True:

            classifications[key] = 1

        #If there is not a match with the text and one of the values in the list
        #of terms associated with a topic, we will set the topic value equal to 0
        if text_match is False:

            classifications[key] = 0

    return classifications

def main():    

    #We will be classifying posts with repsect to the following topics: 
    #gender, hot topics, lgbt, morality, politics, race, and religion.
    #Here we read in the terms associated with each topic from the provided
    #directory. The function will automatically stem the terms in the list
    #unless told otherwise. The topics will be saved as a dictioanry and 
    #where a topic name (the dict key) is associated to the topic's terms 
    #(the dict values).  To access the terms associated with a 
    #topic, for example, to see LGBT terms, you would call, topics['lgbt'].
    topics = {
        'gender' : read_terms('topics/gender.txt'),
        'hot_topics' : read_terms('topics/hot_topics.txt'),
        'lgbt' : read_terms('topics/lgbt.txt'),
        'moral' : read_terms('topics/moral.txt'),
        'politics' : read_terms('topics/politics.txt'),
        'race' : read_terms('topics/race.txt'),
        'religion' : read_terms('topics/religion.txt')
    }

    #We will be classifying comments with repsect to the their use of the following
    #types of evidence use: 
    #data, economics, evidence, numbers, stats, and values.
    #Here we read in the terms associated with each topic from the provided
    #directory. The function will automatically stem the terms in the list
    #unless told otherwise. The topics will be saved as a dictioanry and 
    #where a topic name (the dict key) is associated to the topic's terms 
    #(the dict values).  To access the terms associated with a 
    #evidence use type, for example, to see data terms, you would call, evidence['data'].
    evidence = {
        'data' : read_terms('evidence-language/data.txt'),
        'economics' : read_terms('evidence-language/economics.txt'),
        'evidence' : read_terms('evidence-language/evidence.txt'),
        'numbers' : read_terms('evidence-language/numbers.txt'),
        'stats' : read_terms('evidence-language/stats.txt'),
        'values' : read_terms('evidence-language/values.txt'),
    }

    directory = os.fsencode('data')     #Encode our directory string as a directory object
    
    for file in os.listdir(directory):  #Iterate over files in our data folder.

        filename = os.fsdecode(file)    #Get a string representation of a file in our folder

        if filename.endswith(".json"):  #If the file ends in .json, it's a data file we want to classify
            
            data = json_reader('data/' + filename)  #Read in our CMV data as a list of JSON objects
             
            for post in data:   #Iterate over each discussion in our dataset individually.

                #We will classify each discussion with respect to the title and selftext.
                #Therefore, we will concatenate these two strings for classification.
                title = post['title']
                body = post['selftext']
                
                #We will make a new attribute in each discussions JSON object named
                #topic.  Topic will be a dict of the topics and boolean value
                #denoting if a discussion is related to that topic.  
                post['topic'] = classify_text(title + ' ' + body, topics)
            
                #Now that we classified the posts, we need to classify the comments with
                #respect to their use of evidence based language. 
                post_comments = post['_comments']

                for comment in post_comments: 
                
                    comment['evidence_use'] = classify_text(comment['body'], evidence)
                    
            with open('data/coded/'+ filename, 'w') as outfile: #Write our classifed discussions to a new file in the directory /coded/
                
                json.dump(data, outfile)

main()