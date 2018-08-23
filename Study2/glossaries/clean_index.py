"""  
Project Name: Attitude Change on Change My View (Study 2) 
Name: clean_index.py

Description of this script:
    Take messy index list of words (which are copied and pasted from pdfs of textbooks) and 
    remove exteraneous string content.   
                       
Authors: J. Hunter Priniski & Zachary Horne

"""
#REQUIRMENTS
import string

#Read in data copied from pdf and remove extra string content.  
def make_clean_index(directory):
	text_file = open(directory, "r")
	lines = text_file.read().split('\n')
	table1=str.maketrans("","",string.punctuation)
	table2=str.maketrans("","",string.digits) 
	new_lines = []
	for line in lines:
		line = line.lower()
		line = line.replace(",","")

		line = line.translate(table2)
		
		if "(" not in line:
			new_lines.append(line.strip())
	return new_lines

#We want to remove duplicates, however, casting a list to a set looses the list's ordering. 
#This function removes duplicates and perserves order. 
def remove_dups(dup_list):
    
    seen = []
    for x in dup_list:
    	if not (x in seen):
    		seen.append(x)
  
    return seen

def main():

	file = 'lists/american-government.txt'
	terms = make_clean_index(file)
	terms = remove_dups(terms)

	with open(file[:-4] + '-clean.txt', 'w') as the_file:
		
		for term in terms: 
			if len(term) > 1:
				the_file.write(term+'\n')



	


main()