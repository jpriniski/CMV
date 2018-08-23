# Creating the word glossaries 

We use terms collected from the glossaries of four textbooks to construct our corpus of evidentiary words. Here, we describe the process of turning the raw glossaries (as collected from the textbooks) into a corpus of evidence language, and then describe the protocol for partitioning the words into sub-categories of more detailed evidence types. 

### Step 1: Gathering glossaries of terms
Terms were gathered from the glossaries in the following four books from [openstax.org](https://openstax.org/):

- [American Government]( https://openstax.org/details/books/american-government)
- [Principles of Economics]( https://openstax.org/details/books/principles-economics-2e)
- [Business Statistics](https://openstax.org/details/books/introductory-business-statistics)
- [Introductory Statistics](https://openstax.org/details/books/introductory-statistics)

The books were chosen because they best represent the breadth of evidentiary language commonly used in discussions on Change My View (and in everyday discussions for that manner.)  That is, textbooks on more techincal subject manner, like Quantum Physics or Calculus, for example, would contain terms not commonly used in such a setting. 

We copied the glossary content from each textbook into a seperate text file (a single text file for a single glossary.)  For example, here are the some terms at the head of the American Government gloassary:

|Term                                    | Page(s) |
|:--------------------------------------:|:-------:|
|AARP                                    | 234, 606|
|Abbot                                   | 55      |
|Abbott                                  | 537     |
|Abramoff                                | 395     |
|Abzug                                   | 422     |
|acquisitive model                       | 570     |
|(AIM)                                   | 192     |

### Step 2: Cleaning and preparing glossaries of terms
We then removed page numbers, commas, and terms in parentheses from the glossary in addition to casting strings to lower case. This resulted in the following *cleaned* glossary:
```
aarp
abbot
abbott
abramoff
abzug
acquisitive model
```
This cleaning is followed out by the following (slightly abstracted from its original form) Python method:
``` python
def make_clean_index(directory):

  # Read in text file
  text_file = open(directory, "r")
  
  #Split the text after each newline to create a Python list of terms
  lines = text_file.read().split('\n')
  
  # Create a mapping table that will map digits to empty strings
  table = str.maketrans("","",string.digits) 
	
  # We will appened our cleaned lines to the new_lines list
  new_lines = []
  for line in lines:
  
    # Cast the string to lower case
    line = line.lower()
    
    # Replace each comma with an empty string
    line = line.replace(",","")
    
    # Remove digits by using the mapper table from above
    line = line.translate(table)
    
    # We will not add terms enclosed in parentheses (since they are abbreviations of terms in the glossary)
    if "(" not in line:
    
      # Before appeneding our almost clean text line to the new_lines list, we will strip any additional trailing white space for good measure
      new_lines.append(line.strip())   
      
  return new_lines
```

We also did some additional cleaning for terms that were missed by the algorithim.  For example, changing words like 'type i error' to 'type one error'.


### Step 3: Adding lemmas
We used WordNet lemmatizer to add the noun, verb, and adjective forms of terms to our glossary.  

Some high-level python code details how we did this:

```python
# We will use the WordNetLemmatizer to lemmatize the words in our glossary
from nltk.stem.wordnet import WordNetLemmatizer

for word in glossary:

  # We will add the verb, noun, and adjective lemmas of each word in word bank.
  # 'v' stands for verb, 'n' stands for noun, and 'a' stands for adjective
  for w in ['v','n','a']:
    
    # Lemmatize the word. 
    lemma = WordNetLemmatizer().lemmatize(word, w)
    
    # If the word is no in our glossary, we will add it. 
    if not (lemma in glossary):
      glossary.append(lemma)          
```

### Step 4: Partitioning extended word glossaries into classes of evidence

We will use affinity propgation (Frey and Dueck, 2007) to cluster the words into classes of evidence type. To do this, we need to 






#### References

Frey, B.J. & Dueck, D. (2007). Clustering by Passing Messages Between Data Points. *Science*.






