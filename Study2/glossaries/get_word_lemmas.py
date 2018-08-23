"""  
Project Name: Attitude Change on Change My View (Study 2) 
Name: get_word_lemmas.py

Description of this script:
    get other tenses of a word in the word bank
                       
Authors: J. Hunter Priniski & Zachary Horne

"""
#REQUIRMENTS

from nltk.stem.wordnet import WordNetLemmatizer

def main():
	file = 'lists/american-government-clean.txt'
	
	text_file = open(file, "r")
	lines = text_file.read().split('\n')
	
	
	for word in lines:

		#we will add the verb, noun, and adjective lemmas of each word in word bank
		for w in ['v','n','a']:

			lemma = WordNetLemmatizer().lemmatize(word, w)
			
			if not (lemma in lines):
					lines.append(lemma)

	with open(file[:-4] + '-grown.txt', 'w') as the_file:
		
		for term in lines: 
			if len(term) > 1:
				the_file.write(term+'\n')
				
main()