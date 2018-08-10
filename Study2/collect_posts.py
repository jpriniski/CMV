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

def get_replies(comment):
	replies= comment['_replies']._comments
	replies_list = []

	if len(replies) > 0:
		for reply in replies:
			replies_list.append(reply.id)
		
		return replies_list

	else:
		return []


def get_comments(submission, metadata = True):
 
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

	REMOVE_COMMENTS = ['[deleted]', '[removed]', ]

	comments = []
	com = submission.comments.replace_more(limit=submission.num_comments)
	com_tree = submission.comments[:]

	while com_tree:
		comment = com_tree.pop(0)                    
		com_tree.extend(comment.replies)
		comments.append(comment)

	if metadata is True:
	
		data_dicts = []
	
		for comment in comments:
			comment_dict = vars(comment)
			comment_body = comment_dict['body']

			if not(comment_body in REMOVE_COMMENTS):
				data_dict = {field:comment_dict[field] for field in fields}		
				data_dict['_replies'] = get_replies(comment_dict)
				data_dict['author'] = vars(data_dict['author'])['name']
				data_dicts.append(data_dict)
	
		return data_dicts
	
	else:
		return comments


def main():

	reddit = praw.Reddit(client_id='',
                         client_secret='',
                         password='',
                         user_agent='',
                         username='')

    
	subreddit = reddit.subreddit('changemyview')

	list_of_posts = []
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

	for submission in subreddit.hot(limit = 15):
		print("Collecting data for %s" % submission.title[0:50])
		submission_dict = vars(submission)
		author = submission_dict['author']
		if not(author == None):
			data_dict = {field:submission_dict[field] for field in fields}
			data_dict['_comments'] = get_comments(submission, metadata = True)
			data_dict['author'] = vars(data_dict['author'])['name']
			list_of_posts.append(data_dict)
		
		#I want to find a better way to do this.  Maybe with a try and catch exception
		if author == None:
			print('Could not collect post data.')
	
	stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

	with open('data/'+ stamp +'_posts.json', 'w') as outfile:
		json.dump(list_of_posts, outfile)
		
	

main()