"""  
Project Name: Attitude Change on Change My View (Study 2) 
Name: discussion_analysis.py

Description of this script:
    
    This script does the following three things:

        1)  Classify discussions as related to pre-defined topics.
            (see the README.MD for more.)    
        2)   Signify how many deltas are awarded to each comment.
        3)  Determine the use of evidence in comments.     
                       
Authors: J. Hunter Priniski & Zachary Horne

Notes:

Before running this script, make sure all of the necessary directories and topic
lists are in the working directory. To run this script, direct the
terminal to the working directory, and type: python
discussion_analysis.py

Also, note that there is a FOOTNOTES section commented out at the
bottom of this script.  To allow for a detailed commenting of the code
while keep the script concise,  I will direct all detailed comments to
the FOOTNOTES section at the bottom of the  script.

The comment string #FN:i# will denote which footnote to read in
the list, where i stands for number i. Eg., ***FN:1*** is the first
footnote in the list.
"""

#REQUIREMENTS
import os
import praw
import re
import nltk
import json
import itertools
import string
from bs4 import BeautifulSoup

#Multiple methods requires word stemming, so we will declare it right away. 
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english')

#We save Reddit discussions as JSON objects. json_reader and json_writer are
#two functions making it easier to work with the data strucutre.  
def json_reader(directory):
    
    with open(directory, 'r') as json_file:

        data = json.load(json_file)

    return data

def json_writer(directory, data):

    with open(directory, 'w') as outfile:                 
    
            json.dump(data, outfile)

    return True 

"""
THE FOLLOWING METHODS 
    get_parent()
    get_delta_awards() 
    award_deltas()

ARE USED TO DENOTE THE NUMBER OF DELTAS AWARDED TO EACH COMMENT. 

get_parent will return the parent comment's metadata of a given comment
comments is the list of comments in a discussion, and current is the comment for which 
you wish to find the parent"""
def get_parent(comments, current):
    
    #parent_id is an attribute returned by the Reddit API.  So we first save this id to a new variable
    parent_id = current['parent_id']

    #We iterate over all the comments in the discussion
    for comment in comments:

        #If the parent_id is the name of the comment, then we have found the parent comment
        if parent_id in comment['name']:
            #Return this comment... it is the parent of current (as passed to the method)
            return comment 

    #if the parent is not in the discussion, then something BAD happened to this comment
    #and it died. ie, Reddit removed it from the discussion for some reason. 
    #If this is the case, we will reutnr None for this comment because it is dead. 
    return None

"""We want to select out each comment where a delta was awarded. We can then 
back track through the discussion tree to find which comment was awarded a delta. 
"""
def get_delta_awards(comments, as_id = False):

    #We will append all comments where a delta was awarded to this list 
    delta_awards = []

    #Iterate over every comment in our comment list
    for comment in comments:

        #DeltaBot awards deltas, so we need to look for comments where deltabot is the author
        if 'DeltaBot' in comment['author']:
    
            #DeltaBot does more than just award deltas.  
            #Since DeltaBot starts each delta awarding the same way: "Confirmed: 1 Delta awarded to",
            if ('confirmed: 1 delta awarded to' in comment['body'].lower()):
                #as_id will make the search quicker in the next method. 
                if as_id is True: 
                    delta_awards.append(comment['id'])

                #If we want to append the total comment meta_data, we will set as_id == False
                if as_id is False:
                    delta_awards.append(comment)

    #We will return all comments where the DeltaBot awarded a delta to a user
    return delta_awards

"""
This method sets the comment's data to the number of deltas it recieved 
and provides the info on the user who awarded the delta along with that user's reason for awarding that delta. 
"""
def award_deltas(comments):

    delta_awards = get_delta_awards(comments, as_id = True)

    #Iterate over each comment
    for comment in comments:
        #this will be the dictionary that houses our delta data for each comment. 
        #The values we save are the count (the # of deltas a given comment recieves)
        #and from (the author who awarded the comment a delta along with the reason they provide
        #for awarding the delta.)
        #We create an empty delta dictionary. Most comments (Since most comments don't recieve)
        #deltas, will have the empty delta dictionary. 
        delta = {   'count':0,
                    'from': {}
                }


        #Put the emtpy delta data dictionary into each commnent's metadata. 
        comment['Delta'] = delta

    #Iterate over comments again. 
    for comment in comments:    
        #If the comment was awarded a delta, then we will update the relevant Delta data. 
        if comment['id'] in delta_awards:

            #The comment where the delta is signified (that is, a user says "!delta")
            #is the parent of the DeltaBot's awarding of a Delta.  
            delta_sig = get_parent(comments, comment)

            #If the comment has no parent, there is nothing we can do. So we will just return.
            if delta_sig is None:
                return
            
            #the parent of the delta_sig reply is the DAC. so we will get the parent of the 
            #delta sig comment
            dac = get_parent(comments, delta_sig)

            #If the comment has no parent, there is nothing we can do. So we will just return. 
            if dac is None:
                return

            #We will update the delta count for this comment by 1. 
            dac['Delta']['count'] += 1

            #We will add the author and reason to the Delta's 'from' data. 
            dac['Delta']['from'].update({delta_sig['author']:delta_sig['body']})

"""
THE FOLLOWING METHODS
    phrase_stemmer
    read_terms
    prepare
    get_ngrams
    match
    classify_text

ARE USED TO PREPARE THE TEXT OF POST AND COMMENT FOR TEXTUAL ANALYSIS

phrase_stemmer stems each token in a list of words and re-concatnates the list of stemmed tokens.
To see how phrase_stemmer works differently than an out-of-the-box NLTK stemmer, see #FN:1#
"""
def phrase_stemmer(phrase):

    #Turn the string into a list of individual tokens (i.e., words)
    tokens = phrase.split()
    
    #Make a new list of stemmed tokens where each token is stemmed using the SnowBall stemmer
    stemmed = [stemmer.stem(token) for token in tokens]

    #Return the list of stemmed tokens. 
    return stemmed

"""
read_terms directly reads in a list of terms associated with an individual topic. 
See #FN2# for more details. 
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

        #We will remove dublicates by sorting the list and then removing any repeated values. 
        stemmed.sort()
        
        return list(stemmed for stemmed,_ in itertools.groupby(stemmed))

    #If we don't want to stem the words in out topic list, we will not enter the 
    #branch above.  
    #We will remove dublicates by sorting the list and then removing any repeated values. 
    lines.sort()
    
    return list(lines for lines,_ in itertools.groupby(list))

#prepare will remove all puncuation, cast all text to lower case, and split the strings into tokens. . 
def prepare(text):

    #Make a translation table where we map punctuation marks to empty strings. 
    table=str.maketrans("","",string.punctuation) 
    #Case the text to lower case. 
    text = text.lower()

    #Remove all puncuation in the text string
    text = text.translate(table)

    #Split the text string into word tokens. 
    text = text.split()

    #Stem each token. 
    content = [stemmer.stem(w) for w in text]
    
    #Rejoin the text
    text = " ".join(content)
    ###***###***###***LOOKDOWNLOOKDOWN
    #Check this, there seems to be some redundant code in here. 
    #Remove any dangling whitespace
    text = re.sub('\s+', text, ' ')

    #Turn string into a split list of tokens/
    text = text.split()
    
    #Remove all duplicates in out list. 
    text.sort()
    return list(text for text,_ in itertools.groupby(text))

"""
get_ngrams will turn a body of text into a list of n-tuples.  More details in #FN:3#
"""
def get_ngrams(text, n, as_list = True):
    
    #If n=1, we only want a list of words embedded in a list. 
    if n is 1:

        #We want a list of tokens as strings in lists 
        tokens_as_list = []                 
        
        #Iterate over every word token in the text
        for word in text:                   
            
            #Append the string in a list to the tokens_as_list list
            tokens_as_list.append([word])   
        
        #Return our new 1-gram list of tokens
        return tokens_as_list               
    
    #If we want a large n-gram representation we will need to construct the consecutive pairs of tokens.
    else:                                                       
        #Pair each word with the next n words in the text. This is what makes an n-gram representation of a text.
        grams = list(zip(*[text[i:] for i in range(n)]))
        
        #If we want our n_grams as lists, we set as_list as True. 
        if as_list is True: 

            grams_list = []
    
            for gram in grams:
                #Cast each gram as a list. 
                grams_list.append(list(gram))

            return grams_list

        #If we want our n_grams as tuples, we set as_list <- False. 
        else:
            return grams

"""
The match method will match the text with respect to the terms in a given classification.
If there is a match in the text with a given topic classifiation term, then the
function returns True. If there is not a match, the method return False. 
"""
def match(text, terms):
    matches = []
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

        #Get the n-gram representation of the text for value i
        grams = get_ngrams(text, i)     
        #Iterate over every term in our list of terms related to a given topic.
        for term in terms:              
            #If one of the terms is in the text, we return True
            if term in grams:           
                matches.append(term)
    #If there is no term in our topic list in the text, we return False
    
    return len(matches) > 0, matches

"""
classify_text will classify a piece of text (in our case a discussion title and selftext or the body of a comment)
and return the topics that the piece of text relates to. 
"""
def classify_text(text, topics):
    
    #Create a empty dictionary, we will add our classifications to this dictionary as we iterate over every topic
    classifications = {} 

    #Prepare the text (i.e., remove whitespace, puncuation, stem, and tokenize)
    prepared_text = prepare(text)
    
    #We will iterate the dictionary of topics. That is, iterate each topic, then iterate over each word in the topic list. 
    
    for key, val in topics.items():

        #See if there is a match with the prepared text and any of the words in the topic list. 
        #text_match is boolean value
        text_match, matches = match(prepared_text, val)

        #If there is a match with the text and one of the values in the list
        #of terms associated with a topic, we will set the topic value equal to 1.
        #This means that the text does relate to the topic.  
        
        classifications[key] = {'match':text_match, 'terms':matches}
        
        #if a classification model wishes to classify a text if it contains a digit, 
        #then the classifiaction key (topic name) needs to contain numbers in it. 
        #Therefore, if 'number' is in the topic name, we will also search the string
        #for use of a digit.  
        if 'number' in key.lower():
            if any(char.isdigit() for char in text):
                classifications[key]['match'] = True
                digits = [char for char in text if char.isdigit()]
                classifications[key]['terms'] = classifications[key]['terms'].append(digits)

    #We will return out list of topic classifications for the given text. 
    return classifications

def get_links(comments):

    for comment in comments:
        html_doc = comment['body_html']
        soup = BeautifulSoup(html_doc, 'html.parser')
        link_list_tag = soup.findAll('a', attrs={'href': re.compile("^https?://")})
        link_list_str = []

        for link in link_list_tag:
            link_list_str.append(str(link))

        comment['links'] = link_list_str

#This is the main method.  This is where the script starts and essentially runs from.
def main():    

    #Load in our topics. See #FN4# for details. 
    topics = {
        'gender' : read_terms('topics/gender.txt'),
        'hot_topics' : read_terms('topics/hot_topics.txt'),
        'lgbt' : read_terms('topics/lgbt.txt'),
        'moral' : read_terms('topics/moral.txt'),
        'politics' : read_terms('topics/politics.txt'),
        'race' : read_terms('topics/race.txt'),
        'religion' : read_terms('topics/religion.txt')
    }

    #Load in our evidence language. See #FN5# for details.
    evidence = {
        'data' : read_terms('evidence-language/data.txt'),
        'economics' : read_terms('evidence-language/economics.txt'),
        'evidence' : read_terms('evidence-language/evidence.txt'),
        'numbers' : read_terms('evidence-language/numbers.txt'),
        'stats' : read_terms('evidence-language/stats.txt'),
        'values' : read_terms('evidence-language/values.txt'),
        'explanations': read_terms('evidence-language/explanatory.txt')
    }

    #Encode our directory where our discussion data is as a directory object.
    #Since we may have multiple files in our data directory (this would occur if we collected
    #data on more than one occasion, as I generally do), we want to iterate over each
    #data file and execute the same code on each file.  
    directory = os.fsencode('data')     

    #Iterate over files in our data folder.
    for file in os.listdir(directory): 

        #Get a string representation of a file in our folder
        filename = os.fsdecode(file)    

        #If the file ends in .json, it's a data file we want to classify
        if filename.endswith(".json"):  
            
            #Read in our CMV data as a list of JSON objects
            data = json_reader('data/' + filename)  
             
            #Iterate over each discussion in our dataset.
            for post in data:   

                #We will classify each discussion with respect to the title and selftext.
                #Therefore, we will concatenate these two strings for classification.
                title = post['title']
                body = post['selftext']
                
                #Firstly, we will classify each post with respect to the topic. 
                #The topic attribute in the post JSON object will denote what the discussion's classification is. 
                post['topic'] = classify_text(title + ' ' + body, topics)
                
                get_links(post['_comments'])

                #Secondly, we will first denote how many deltas each comment recieved
                award_deltas(post['_comments'])

                #Thirdly, we will calculate use of evidence
                #Pull out all of the comments in the discussion. 
                post_comments = post['_comments']

                #Iterate over every comment in the list of comments. 
                for comment in post_comments:

                    #Create an atribute in the comment JSON obbject that specifies the types of evidence used in the comment body.
                    comment['evidence_use'] = classify_text(comment['body'], evidence)
        
            #Write our discussion JSON objects to a new file in the directory /coded. 
            written = json_writer('data/coded/'+ filename, data)
            
            #If data is succesfully written to file, json_writer return True.
            #We print a success message to confirm our data is saved. 
            if written:
                print("Data succesfully written to file %s" % filename)

main()


"""                         ***FOOTNOTES***


#FN1#
Phrase stemmer is a method built off of the NLTK SnowballStemmer.
Phrase stemmer, unlike an out-of-the-box stemmer, will stem each
token in a phrase and then concatenate the stemmed tokens to rebuild
a phrase of stemmed tokens. Phrase stemming (as opposed to direct string
stemming) is needed for our classification algorithim.

EG) Phrase stemmer would phrase each word in the phrase 'beautiful
rainbow skies' as 'beautif rainbow skie'.  A typical stemmer would
fail to stem such a phrase.

#FN2#
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

#FN:3#
The n-tuples represent n consecutive words, and are called ngrams.  For example, a 2-gram
representation of the sentence "I am happy." is [(I, am), (am, happy)].  This 
method requires text split into a list of tokens.  For eg, 'I am happy' needs
to be split into a list of the individual tokens: ["I", "am", "happy"]. The 
method can return tuples in a tuple data strucutre or as list. Since we are matching
individual words from a list of topic terms, we will generally return the tuples
as lists: it makes matching individuals words (tokens) more direct. 

If we only want a 1-gram representation, we will simply encode the
tokens of the split string (which are currently strings) into lists. 
The matching algorihtim expect to see lists of arbitrary length.  
For example, if n is 1: the split string ["I", "am", "happy"] will
become: [["I"], ["am"], ["happy"]]. 

#FN:4#
We will be classifying posts with repsect to the following topics: 
gender, hot topics, lgbt, morality, politics, race, and religion.

#FN:5#
We will be classifying comments with repsect to the their use of the following
types of evidence use: data, economics, evidence, numbers, stats, and values.
"""
