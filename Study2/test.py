"""  
Project Name: Attitude Change on Change My View (Study 2) 
Name: test.py

Description of this script:
    
    This script runs a series of tests over the dataset to make 
    sure that the data was collected and analyzed properly.  
                       
Authors: J. Hunter Priniski & Zachary Horne

To check the tests, run: python test.py
"""

import json
import random

# We will use json_reader to read in our JSON object. 
def json_reader(directory):
    
    with open(directory, 'r') as json_file:

        data = json.load(json_file)

    return data

def main():
	
	# Read in data. If you are testing for a new data set, input the directory to the file here. 
	data = json_reader('data/coded/20180815182030_posts.json')

	# TEST 1. Right number of discussions. 
	if len(data) == 29:
		PASS_1 = True
	else:
		PASS_1 = False

	print("TEST 1: proper number of discussions.  %r" % PASS_1) 
	
	# Test 2. Every discussion has a topic. 
	PASS_2 = True
	for post in data:
		if not('topic' in post.keys()):
			PASS_2 = False
	
	print("TEST 2: Every discussion has a topic classification. %r" % PASS_2) 


	# Test 3. Every comment has evidence classification.

	PASS_3 = True

	for post in data:
		for comment in post['_comments']:
			if not ('evidence_use' in comment.keys()): 
				PASS_3 = False

	print("TEST 3: Every comment has a evidence use classification.  %r" % PASS_3)


	# Test 4. Every comment has evidence classification.

	PASS_4 = True

	for post in data:
		for comment in post['_comments']:
			if not ('Delta' in comment.keys()): 
				PASS_4 = False

	print("TEST 3: Every comment has a delta attribute.  %r" % PASS_4)

	# View the delta count in 10 random post. Not a formal test, but just to make sure things look alright.  
	print("10 random delta attributes. They will mostly be 0.")

	for i in range(10):
		random_post_num = random.randint(0,len(data)-1)
		post = data[random_post_num]

		random_com_num = random.randint(0,len(post['_comments'])-1)

		delta = post['_comments'][random_com_num]['Delta']
		print(delta)

		# If you want to see comments that received more than 1 delta, uncomment the code below. 
		# Note, you may have to set range value higher. 
		#if delta['count'] > 1:
		#		print(delta)
	
	# Get a sense of how many deltas were awarded in the dataset. 
	for post in data:
		num_delta = 0
		for comment in post['_comments']:
			num_delta += comment['Delta']['count']
			
		print("%d deltas was awarded in discussion %s" % (num_delta, post['title'][0:75]))

	# Check the data qualitatively. uncomment code below to compare DACs to an actual discussion.
	# Our script says that the discussion with the title CMV: The universe indifferent to suffering, god is not there
	# (link found here: https://www.reddit.com/r/changemyview/search?q=flair_name%3A%22Deltas(s)%20from%20OP%22&restrict_sr=1)
	# has 80 deltas.  This is high, so let's double check (by clicking on the link) to make sure that this is the case. 

	# print every DAC for discussion above. 
	#for post in data:
	#		if "CMV: The universe indifferent to suffering, god is not there".lower() in post['title'].lower():
	#		for comment in post['_comments']:
	#			if comment['Delta']['count'] > 0:
	#				print(comment['body'])
	#				print('\n was awarded this many deltas:\n')
	#				print(comment['Delta']['count'])

main()