ornithologist
=============

Ornithologist is a python script that retrieves Twitter data via the Twitter Search API for further analysis. I developed Ornithologist to provide students in my courses with a way to gather their own Twitter data to learn social media analysis.

Requires Python-Twitter https://github.com/bear/python-twitter and obtaining / filling in your own Twitter API credentials and directory for data output in a config file (example file included)

Ornithologist produces tab-delimited UTF-8 files with the resulting data and a directory with each tweet as a separate text file (often needed for natural language processing analysis):

ornithologistLog.csv* - 
Header row and one of data per search indicating the variables filled in and the time of the search (UTC)

tweets.csv - 
General purpose file with tweet-level data. See Twitter API documentation on status objects. 

users.csv - 
General purpose file with user-level data. See Twitter API documentation on user objects.

links.csv - Links found in tweets, use option --unshorten to get the destination link.

hashtags.csv - 
tweet ID and hashtag used in the tweet - one line per hashtag

mentions.csv - 
tweet ID and user name of the user mentioned in the tweet - one line per user

user2hashtagEdges.csv - 
Two mode network data (user = Source, hashtag= Target) ready to import to Gephi or other network analysis programs.

rtEdges.csv - 
Two mode network data (user = Source, retweeted user= Target).

userEdges.csv - 
Two mode network data (user = Source, user addressed= Target).

tweets/ - 
Directory with the text of each tweet as a separate text file, named as Tweet ID.csv. Suitable for NLP analysis applications.

Known Issues:
Check files for duplicates.

* Files are tab separated, csv extension used just to make it easier to find the files in some programs.