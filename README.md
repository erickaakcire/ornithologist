ornithologist
=============

Python script that retrieves Twitter data via the Twitter API for further analysis

I developed Ornithologist to provide students in my Digital Research Methods course with a small sample of Twitter data on any topic of interest to them to do exercises on various forms of social media analysis. 

Ornothologist produces 6 tab-delimited UTF-8 files and one directory with up to 100 text files per query.

searchterm-fileName-searchLevelData.txt - 
Header row and one of data per search indicating the variables filled in and the time of the search (UTC)

searchterm-fileName-tweets.txt - 
General purpose file with tweet-level data. See Twitter API documentation on status objects. 

searchterm-fileName-hashtagEdges.txt - 
Two mode network data (user = Source, hashtag= Target) ready to import to Gephi or other network analysis programs.

searchterm-fileName-rtEdges.txt - 
Two mode network data (user = Source, retweeted user= Target).

searchterm-fileName-userEdges.txt - 
Two mode network data (user = Source, user addressed= Target).

searchterm-fileName-users.txt - 
General purpose file with user-level data. See Twitter API documentation on user objects.

searchterm-fileName-tweets/ - 
Directory with the text of each tweet as a separate text file, named as Tweet ID.txt. Suitable for NLP analysis applications.
