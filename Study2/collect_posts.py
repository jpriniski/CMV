"""
Project: Attitude Change on Change My View (Study 2)
File: collect_posts.py
Description: Connect to the Reddit API and save Reddit data as a JSON file.      
Authors: J. Hunter Priniski & Zach Horne
run: python collect_posts.py
"""

import praw
import json
import datetime

#get_replies turns the Object returned by the Reddit API into a list of replies by ID. 
#This allows us to store the replies into a JSON object, and allows us to easily reconstruct
#the discussion tree if needed
def get_replies(comment):

	#Since replies are a Reddit Object, we need to access the comments attribute of the replies.
	replies= comment['_replies']._comments

	#We will append the replies to a list. 
	replies_list = []

	#We need to check if a comment as replies. 
	if len(replies) > 0:

		#If it does, we can iterate over the replie obejts and append the reply id to the list. 
		for reply in replies:
			replies_list.append(reply.id)
		#return the list of reply ids
		return replies_list
	#IF the comment has now replies, return an empty list.
	else:
		return []

#For some reason, the Reddit API doesn't like to provide you with all the comments in a discussion
#right away.  You must iterate over MoreComment Objects to get to some of the lower-level comments. 
#THis isn't a concern for discussions with few comments, but for large discussions, some of the comments
#are stored in MoreComment objects. get_comments, then iterates over the MoreComments objects
#and appends them to a list.  also, get_commetns removes useless REddit attributes that 
#prohibit us from saving the comments list to a JSON file. dont worry about loosing discussion network
#strucutre, we will save the ids of the replies in a replies attribute allowing us to reconstruct the network if needed
def get_comments(submission, metadata = True):

	#these are the fields (or attributes) we can save to a json object and store in local memory
	#ie. attibutes that are connections to more data in the APi need to be removed or transcribed into a string. 
	fields = ('_mod','subreddit_id', 'approved_at_utc', 'ups', 'mod_reason_by', 
	'banned_by', 'removal_reason', 'link_id', 'author_flair_type',
	'author_flair_template_id', 'likes', 'no_follow', 'user_reports', 
	'saved', 'id', 'banned_at_utc', 'mod_reason_title', 'gilded', 
	'archived', 'report_reasons', 'author', 'can_mod_post', 
	'send_replies', 'parent_id', 'score', 'approved_by',
	'downs', 'body', 'edited', 'author_flair_css_class', 
	'collapsed', 'author_flair_richtext', 'is_submitter', 
	'collapsed_reason', 'body_html', 'stickied', 'subreddit_type',
	'can_gild', 'author_flair_text_color', 'score_hidden', 
	'permalink', 'num_reports', 'name', 'created', 'author_flair_text',
	'created_utc', 'subreddit_name_prefixed', 'controversiality', 
	'depth', 'author_flair_background_color', 'mod_reports', 'mod_note', 
	'distinguished', '_fetched', '_info_params')

	#if the comment was deleted or removed, we don't want to save it. 
	REMOVE_COMMENTS = ['[deleted]', '[removed]', ]

	#this will become our list of comments
	comments = []

	#we unpack all of the MoreComments objects.  turning the 
	#returned discussion tree which is imcomplete into the complete discussion
	com = submission.comments.replace_more(limit=submission.num_comments)

	#we make our submission comments object iterable, this allows us to go over each comment
	#in the discussion
	com_tree = submission.comments[:]

	#while there are still more comments to be appended to our comment list, we will stay in this loop
	while com_tree:
		#our next comment will be popped off the tree
		comment = com_tree.pop(0)                    
		#if this comment as anny replies, we append them to our comment tree
		com_tree.extend(comment.replies)
		#append the comment's metadata to our list of comments
		comments.append(comment)


	#if we want all of the metadata the reddit api has to offer, we enter this branch
	if metadata is True:
		#we will make a list of dictionaries that contains all of the comment's metadata
		data_dicts = []
		#we iterate over each comment in our list of comments
		for comment in comments:
			#turn the comment object into a dictionary
			comment_dict = vars(comment)
			#access the body of the comment. 
			comment_body = comment_dict['body']

			#if the comment_body is not in our remove_comments list (that is it is not deleted of remove), we can save the data to our list of comment metadata
			if not(comment_body in REMOVE_COMMENTS):
				
				#write each desired field to the data_dict
				#Try and catch will continue on with the program if the Reddit API happens to not return one of our desired fields. 
				try:

					data_dict = {field:comment_dict[field] for field in fields}	
				
				except KeyError:
				
					continue

				#replace all of the reply objects with reply ids	
				data_dict['_replies'] = get_replies(comment_dict)
				#replace the author Reddit Object with the name of the author
				data_dict['author'] = vars(data_dict['author'])['name']
				#append our data to our list of datas
				data_dicts.append(data_dict)
	
		#return our list of data
		return data_dicts
	
	#if we only want comment text, we will enter this branch. this is boring tho. much more data available. so keep metadata true
	else:
		return comments

def main():

	#this our where we input our credentials. you need to have these attributes filled out in order to collect data. 
	reddit = praw.Reddit(client_id='',
                         client_secret='',
                         password='',
                         user_agent='',
                         username='')

  	#connect directly to the subreddit. 
	subreddit = reddit.subreddit('changemyview')

	#we will be appending the data of each disscussion/post to this list
	list_of_posts = []
	#these are the fields (or attributes) we can save to a json object and store in local memory
	#ie. attibutes that are connections to more data in the APi need to be removed or transcribed into a string. 
	fields = ('approved_at_utc','selftext','user_reports','saved',
		'mod_reason_title','gilded','clicked','title','link_flair_richtext',
		'subreddit_name_prefixed','hidden','pwls','link_flair_css_class',
		'downs','parent_whitelist_status','hide_score','name','quarantine',
		'link_flair_text_color','author_flair_background_color','subreddit_type',
		'ups','domain','media_embed','author_flair_template_id','is_original_content',
		'secure_media','is_reddit_media_domain','is_meta','category','secure_media_embed',
		'link_flair_text','can_mod_post','score','approved_by','thumbnail','edited',
		'author_flair_css_class','author_flair_richtext','content_categories','is_self',
		'mod_note','created','link_flair_type','wls','banned_by','author_flair_type',
		'contest_mode','selftext_html','likes','suggested_sort','banned_at_utc',
		'view_count','archived','no_follow','is_crosspostable','pinned','over_18',
		'media_only','link_flair_template_id','can_gild','spoiler','locked',
		'author_flair_text','visited','num_reports','distinguished',
		'subreddit_id','mod_reason_by','removal_reason','link_flair_background_color','id',
		'report_reasons','author','num_crossposts','num_comments','send_replies','mod_reports',
		'author_flair_text_color','permalink','whitelist_status','stickied','url','subreddit_subscribers',
		'created_utc','media','is_video','_fetched','_info_params','comment_limit','comment_sort','_flair','_mod')

	#here we specify the type of post we want, the number of posts we want to collect, and then
	#iterate over them... collecting the data we need
	for submission in subreddit.top(limit = 30):


		print("Collecting data for %s" % submission.title[0:50])
		#turn the Reddit Object returned by the api into a dictionary.  This makes it easy to work with and we don't need to make additional api calls to see attributes of the data. 
		submission_dict = vars(submission)

		#get the author of the discussion
		author = submission_dict['author']

		#if the author is None, then the discussion was deleted.  We will skip over collecting the data. 
		if not(author == None):
			
			#create a dictionary of data that we wish to write to local memory
			#Try and catch will continue on with the program if the Reddit API happens to not return one of our desired fields. 
			try:
			
				data_dict = {field:submission_dict[field] for field in fields}
			
			except KeyError:
			
				continue

			#replace the CommentForest object with a list of comment metadata dictionaries
			data_dict['_comments'] = get_comments(submission, metadata = True)

			#Replace the author Reddit object with the name of the author
			data_dict['author'] = vars(data_dict['author'])['name']

			#append our data for the given discussion to our list of discussions
			list_of_posts.append(data_dict)
		
		#If the author is None, well, just print that we can't collect the data. 
		if author == None:
			print('Could not collect post data.')
	
	#we will save all of the discussion data to local memory, and time stamp the file for when we collected the data. 
	stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

	#Write the data into the data/ folder. 
	with open('data/'+ stamp +'_posts.json', 'w') as outfile:
		json.dump(list_of_posts, outfile)
		
main()