from nltk.corpus import wordnet
import wikipedia
import json

# read in each seperate glossary
bus = 'glossaries/grown/business-stats-clean-grown.txt'
stats= 'glossaries/grown/business-stats-clean-grown.txt'
econ = 'glossaries/grown/economics-terms-clean-grown.txt'
gov = 'glossaries/grown/american-government-clean-grown.txt'
	
bus_file = open(bus, "r")
bus_lines = bus_file.read().split('\n')

stats_file = open(stats, "r")
stats_lines = stats_file.read().split('\n')

econ_file = open(econ, "r")
econ_lines = econ_file.read().split('\n')

gov_file = open(gov, "r")
gov_lines = gov_file.read().split('\n')

# put all terms into a single corpus
corpus = bus_lines + stats_lines + econ_lines + gov_lines

# remove duplicate terms
corpus =set(corpus)

# add defintions for each term in our dictionary.
defintions = {}
count = 1
for word in corpus: 
	
	# will print some progress statements
	count+=1
	if count % 50 == 0:
		print('Count %4f percent complete' % ((count/len(corpus))*100)


	# will try to get Wikipedia summary data for 
	try:
		summary = wikipedia.summary(word)
		defintions.update({word:{'def':summary, 'source':'wiki'}})

	# if there is no wiki article for word, we will try to use wordnet to get a definition
	except:

		syns = wordnet.synsets(word)

		if len(syns) > 0:
			defintions.update({word:{'def':syns[0].definition(), 'source':'wordnet'}})
		else:
			#defintions.update({word:''})
			print('No defintion or wiki description found for %s ' % word)

with open('corpus.json','w') as out_file:
	json.dump(defintions, out_file)







