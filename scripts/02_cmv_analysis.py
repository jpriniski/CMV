"""

Author: J. Hunter Priniski & Zachary Horne
Cognition, Computation, and Development Lab at ASU

cmv_analysis.py

This script will analyze rates of attitude change and evidence citation in ChangeMyView discussions on the website Reddit.

To run this script, enter the directory where this file is saved on the terminal and run: python cmv_analysis.py

"""

import os
import praw
import pandas as pd
from datetime import datetime
import re
import nltk
snow = nltk.stem.SnowballStemmer('english')

def get_comments(submission):
    
    comments = []
    #may be a more elegant solution than submission.num_comments
    com = submission.comments.replace_more(limit = submission.num_comments)
    com_tree = submission.comments[:]

    while com_tree:
        comment = com_tree.pop(0)                    
        com_tree.extend(comment.replies)
        comments.append(comment)
        
    return comments

def replace_sub_dicts(dic):

    for key, item in dic.items():
        if type(dic[key]) is dict:
            #we will turn the dictionary to a list of tuples, where the first element of each list is 
            #the item's key, while the second element is the value
            sub_lot = []
            for sub_key, sub_item in dic[key].items():
                sub_lot.append((sub_key,sub_item))
            dic[key] = sub_lot
    return dic

def make_comment_df(comments):
	
	data = pd.DataFrame(columns = vars(comments[0]).keys())

	for comment in comments:
		c = vars(comment)
		comment_df = pd.DataFrame(columns = c.keys())
		for key, item in c.items():
		
			if key is '_replies':
				comment_df[key] = c[key]._comments
			else:
				comment_df[key] = pd.Series(c[key])

		data = data.append(comment_df, ignore_index = True)

	data.columns = [c + '_comment' for c in list(data.columns) ]
	return data


def make_post_df(post):

	data = pd.DataFrame(columns = post.keys())

	for key, item in post.items():
		data[key] = pd.Series(post[key])

	data.columns = [c + '_post' for c in list(data.columns)]
	return data


"""Deltas are awarded via the DeltaBot.  Therefore, we will let the total number of deltas awarded in a discussion
be calcaulted by determining how many comments the DeltaBot has in each discussion. To do this, we will pass 
get_deltas(dataframe) the dataframe of each discussion.

"""

def get_deltas(dataframe):
    
    #return the number of deltas awarded in a discussion
    return len(dataframe[dataframe['author_comment'] == 'DeltaBot'])


"""
***
*** To determine use of evidence in disucssions, we will calculate the total number of hyperlinks in discussions, 
*** calculate the frequency and use of language representative of citing evidence. 
"""

"""
get_links will take a list of comments (passed as a column in a dataframe), and return a new column,
where row values are the links used in each comment. 

get_links(comments) should then be c-bound to the exisiting dataframe

"""
def get_links(comments):
    
    links = []
    total_links = []
    
    for comment in comments:
        comment = str(comment)
        
        extensions = ['http://', 'https://', '.com', '.org', '.gov', '.pdf', '.net', 'www.']
        
        comment_links = []   
        for word in comment.lower().split():
            if any(e in word for e in extensions) and not ('reddit.com' in word):
                comment_links.append(word)
    
        links.append(comment_links)
        total_links.append(len(comment_links))
        
    return links, total_links
    
"""
get_evid_lang will take a list of comments (passed as a column in a dataframe), and return a new column,
where row values are the evidence language used in each comment. 

get_evid_lang(comments) should then be c-bound to the exisiting dataframe

"""

def get_evid_lang(comments):
    
    evidence = []
    total_evidence = []
    
    for comment in comments:
        comment = str(comment)
        
        extensions = ['http://', 'https://', '.com', '.org', '.gov', 'pdf', '.net', 'www.']
        
        stems = ['data', 'stat', 'statist', 'figur', '%', 'percent', 'averag', 'number', 'amount', 
                 'thousand', 'million', 'billion', '$', '€', '¥', '£', 'dollar', 'evid', 'info', 
                 'testimoni', 'conclus', 'document', 'experi', 'experi', 'measur', 'measur', 'report', 
                 'result', 'census', 'figur', 'plot', 'graph', 'sum', 'total', 'decim', 'digit', 'fraction',
                 'numer', 'half', 'share', 'proport', 'capit', 'cash', 'properti', 'salari', 'wage', 'wealth', 
                 'financ', 'resourc', 'roll', 'treasuri', 'bank', 'deposit', 'exchang', 'safe', 'estim', 'price', 
                 'price', 'merchandis', 'retail', 'sale', 'cartel', 'invest', 'market', 'deposit', 'document', 
                 'indic', 'wit', 'affirm', 'corrobor', 'declar', 'good', 'ground', 'token', 'signific', 'probabl', 
                 'p valu', '<', '=', 'greater', 'equal', 'less', 'rang', 'devi', 'sd', 'mode',
                 'median']
        
        comment_evidence = [] 
        
        comment_stemmed = snow.stem(comment.lower())
        
        for word in comment_stemmed.split():
            if any(s == word for s in stems) and not any(e in word for e in extensions):
                comment_evidence.append(word)
    
        evidence.append(comment_evidence)
        total_evidence.append(len(comment_evidence))
        
    return evidence, total_evidence

def join_dfs(post, comments):
	new_post = pd.DataFrame()

	for row in range(len(comments)):
		new_post = new_post.append(post, ignore_index = True)

	return pd.concat([new_post, comments], axis = 1)


def main():


	reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='',
                     username='')

	
	subreddit = reddit.subreddit('changemyview')


	#if you have already collected some posts, and don't want them to be collected again, read in post ids from collected_posts.txt
	f  = open('collected_posts.txt', 'r')
	collected_posts = f.read().split('\n')
	f.close()

	df = pd.DataFrame()

	POST_TYPE = 'top'
	for post in subreddit.top(limit = 1000):
		
		
		if not(post.name in collected_posts):
			
			print("collecting %s data" % post.name)
			
			post2 = replace_sub_dicts(vars(post))
			post_df = make_post_df(post2)
			
			comments = get_comments(post)
			com_df = make_comment_df(comments)	
			com_df['Evidence_Lang_Use_com'], com_df['Total_Evidence_com'] = get_evid_lang(com_df['body_comment'])
			com_df['Links_Use_com'], com_df['Total_Links_com'] = get_links(com_df['body_comment'])
			
			post_df['Total_Deltas_post'] = get_deltas(com_df)
			post_df['Post_Type_post'] = POST_TYPE
			
			df = df.append(join_dfs(post_df, com_df))
			df.to_csv('08_top_posts.csv', na_rep = 'NA', index = False)

		else:

			print("%s already collected" % post.name)


main()























































