## Description of this directory.

Reddit Change My View discussion data is divided into two folders:
- Study2/data (this folder)
- Study2/data/coded

The data as it is returned by the Reddit API (by running collect_posts.py) is saved in Study2/data.
Once that data's topic classification, evidence use, and detla awards are determined (by running discussion_analysis.py), the data will be additionally saved in Study2/data/coded. Seperating the datasets makes it easier to reproduce our work and do your own analyses on the Change My View discussion data.  

Note that if data in Study2/data is zipped, you must manually unzip it before running discussion_analysis.py.
