#!/usr/bin/python
# Ornothologist produces 6 tab-delimited UTF-8 files and one directory per query.
# See README.md for details.
# By: Ericka Menchen-Trevino http://www.ericka.cc/

# Variables to fill in
searchterm = "" #must be URL encoded
fileName = "" #for file name to append, e.g. student name
language = "" #e.g. "en", "nl", None is ""
before = "" # get tweets before this date YYYY-MM-DD, "" for "now"
resultType = "recent" #options are recent, popular or mixed, see API documentation

# using this python module to access the Twitter API https://github.com/bear/python-twitter
import twitter

#to handle UTF-8
import codecs

#to process tweet text
import re

#to get timestamp
from datetime import tzinfo, datetime

# to be able to create directories
import os

# Twitter authentication
api = twitter.Api(consumer_key='',
                      consumer_secret='',
                      access_token_key='',
                      access_token_secret='')

#do the actual search
statuses = api.GetSearch(term=searchterm, result_type=resultType, include_entities=True, count=100, lang=language, until=before)

currentTime = datetime.utcnow()

#open and write a file with search-level data
sldFileName = searchterm + "-" + fileName + "-searchLevelData.txt"
if os.path.isfile(sldFileName) is True:
  info = codecs.open(sldFileName, encoding='utf-8', mode='a')
  info.write ("\n" + searchterm + "\t" + language  + "\t" + fileName + "\t" + before + "\t" + str(currentTime) + " UTC" + '\t' + resultType)
else:
  info = codecs.open(sldFileName, encoding='utf-8', mode='w+')
  info.write("search term\tlanguage\tfile name\tbefore\tgathered\tresult type\n" + searchterm + "\t" + language  + "\t" + fileName + "\t" + before + "\t" + str(currentTime) + " UTC" + '\t' + resultType)

#loop through each result
for s in statuses:
  #take out any tabs or new lines in the tweets
  takeTabNewlines = re.compile(r'[\t\r\n]')
  strip = takeTabNewlines.sub('', s.text)
  
  #get tweets to users (user begins the tweet)
  toUserSearch = re.compile(r'@(\w*\b)', re.U)
  toUserMatch = toUserSearch.match(strip)
  toUserList = []
  if toUserMatch:
    toUserList.append(toUserMatch.group(1))
    
    userFileName = searchterm + "-" + fileName + "-userEdges.txt"
    
    if os.path.isfile(userFileName) is True:
      userNet = codecs.open(userFileName, encoding='utf-8', mode='a')
      userNet.write(unicode(s.user.screen_name) + "\t" + unicode(toUserMatch.group(1)) + "\t" + unicode(s.id) + "\n")
    else:
      # open a file to write the to user network
      userNet = codecs.open(userFileName, encoding='utf-8', mode='w+')
      #Source is user, target is user mentioned
      userNet.write("Source\tTarget\ttweet id\n")
  else:
    toUserList.append('')
  
  #get retweet user
  rtSearch = re.compile(r'RT @(\w*\b)', re.U)
  rtMatch = rtSearch.match(strip)
  rtList = []
  rtFileName = searchterm + "-" + fileName + "-rtEdges.txt"
  if rtMatch:
    rtList.append(rtMatch.group(1))
    if os.path.isfile(rtFileName) is True:
      rt = codecs.open(rtFileName, encoding='utf-8', mode='a')
      rt.write(unicode(s.user.screen_name) + "\t" + unicode(rtMatch.group(1)) + "\t" + unicode(s.id) + "\n")
    else:
      # open a file to write the RT network
      rt = codecs.open(rtFileName, encoding='utf-8', mode='w+')
      #Source is user, target is user retweeted
      rt.write("Source\tTarget\ttweet id\n")
      rt.write(unicode(s.user.screen_name) + "\t" + unicode(rtMatch.group(1)) + "\t" + unicode(s.id) + "\n")
  else:
    rtList.append('')
  
  #get all user mentions
  mentionList = re.findall(r'@(\w*\b)', strip)
  
  #get all hashtags
  hashtagList = re.findall(r'#\w*\b', strip)
  
  #get all links
  linkList = re.findall(r'https?://[\w\./]*\b', strip)
  
  #strip source of HTML
  tweetSource= re.sub('<[^<]+?>', '', s.source)
  
  #read in the date 'Mon Sep 08 05:43:10 +0000 2014' as a date object and output as '20140908 05:43:10'
  dateObject = datetime.strptime(s.created_at, '%a %b %d %H:%M:%S +0000 %Y')
  unixDate = dateObject.strftime('%Y-%m-%d %H:%M:%S')
  
  tweetFileName = searchterm + "-" + fileName + "-tweets.txt"
    
  if os.path.isfile(tweetFileName) is True:
    #open a file to write the tweet-level data
    t = codecs.open(tweetFileName, encoding='utf-8', mode='a')
    # write one line of data to tweet file
    t.write(unicode(currentTime) + "\t" + unicode(s.id) + "\t" + unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + unixDate + "\t" + unicode(s.retweet_count) + "\t" + str(s.favorite_count) + "\t" + unicode(tweetSource) + "\t" + unicode(s.lang) + "\t" + unicode(s.withheld_in_countries) + "\t" + unicode(strip) + "\t" + ', '.join(toUserList) + "\t" + ', '.join(rtList) + "\t" + ', '.join(mentionList) + "\t" + ', '.join(hashtagList) + "\t" + ', '.join(linkList) + "\n")
  else:
    t = codecs.open(tweetFileName, encoding='utf-8', mode='w+')
    # Write the header row
    t.write("gathered\ttweet id\tuser id\tuser name\ttime created\tretweets\tfavorites\ttweet source\tlanguage\twithheld from\ttweet\tto user\tretweet of\tall user mentions\thashtags\tlinks\n")
    # write one line of data to tweet file
    t.write(unicode(currentTime) + "\t" + unicode(s.id) + "\t" + unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + unixDate + "\t" + unicode(s.retweet_count) + "\t" + str(s.favorite_count) + "\t" + unicode(tweetSource) + "\t" + unicode(s.lang) + "\t" + unicode(s.withheld_in_countries) + "\t" + unicode(strip) + "\t" + ', '.join(toUserList) + "\t" + ', '.join(rtList) + "\t" + ', '.join(mentionList) + "\t" + ', '.join(hashtagList) + "\t" + ', '.join(linkList) + "\n")
  
  hashtagFileName = searchterm + "-" + fileName + "-hashtagEdges.txt"
  
  for h in hashtagList:
    if os.path.isfile(hashtagFileName) is True:
      #open a file to write the hashtag-level data
      hash = codecs.open(hashtagFileName, encoding='utf-8', mode='a')
      hash.write(unicode(s.user.screen_name) + "\t" + unicode(h) + "\t" + unicode(s.id) + "\n")
    else:
      #open a file to write the hashtag-level data
      hash = codecs.open(hashtagFileName, encoding='utf-8', mode='w+')
      #Source is user and target is hashtag
      hash.write("Source\tTarget\ttweet id\n")
      hash.write(unicode(s.user.screen_name) + "\t" + unicode(h) + "\t" + unicode(s.id) + "\n")

t.close()  #save the tweet-level data file
hash.close() #save the hashtag-level data file

userFileName = searchterm + "-" + fileName + "-users.txt"

if os.path.isfile(userFileName) is True:
  u = codecs.open(userFileName, encoding='utf-8', mode='a')
  #loop through each result
  userList = []
  for s in statuses:
    #take out any tabs or new lines in the user descriptions
    takeTabNewlinesDesc = re.compile(r'[\t\r\n]')
    stripDesc = takeTabNewlinesDesc.sub('', s.user.description)
    userList.append(unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + s.user.location + "\t" + str(s.user.time_zone) + "\t" + str(s.user.utc_offset) + "\t" + str(s.user.profile_image_url) + "\t" + stripDesc)
  #deduplicate the user list before printing
  userList = list(set(userList))
  u.write('\n'.join(userList))
else:
  #open a file to write the user-level data to
  u = codecs.open(userFileName, encoding='utf-8', mode='w+')
  #write the header row to the file
  u.write("user id\tscreen name\tlocation\ttime zone\tutc offset\tprofile image URL\tdescription\n")
  #loop through each result
  userList = []
  for s in statuses:
    #take out any tabs or new lines in the user descriptions
    takeTabNewlinesDesc = re.compile(r'[\t\r\n]')
    stripDesc = takeTabNewlinesDesc.sub('', s.user.description)
    userList.append(unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + s.user.location + "\t" + str(s.user.time_zone) + "\t" + str(s.user.utc_offset) + "\t" + str(s.user.profile_image_url) + "\t" + stripDesc)
  #deduplicate the user list before printing
  userList = list(set(userList))
  u.write('\n'.join(userList))

u.close()

# directory of each tweet as a file with ID as name for NLP

for s in statuses:
  # create directory (if needed) and open a file to write each tweet to
  filename = searchterm + "-" + fileName + "-" + "tweets" + "/" + str(s.id) + ".txt"
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  with codecs.open(filename, encoding='utf-8', mode="w+") as f:
    f.write(unicode(s.text))
f.close()