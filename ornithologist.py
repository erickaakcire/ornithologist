#!/usr/bin/python
# -*- coding: utf-8 -*-

# python2/3 interoperability
from __future__ import print_function

# argument parsing to take arguments from the command line
import argparse

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

import sys

#to do internet things
import requests
import urllib

# read relevant keys from config file
try:
    with open('ornithologist.conf', 'r') as config:
        c = config.readlines()
        assert len(c) == 5, """ornithologist.conf not in the right format. Need 'API key', 'API secret', 'Access token', 'Access token secret', and 'data output directory' each in a single line"""
        consumer_key = c[0].strip()
        consumer_secret = c[1].strip()
        access_token_key = c[2].strip()
        access_token_secret = c[3].strip()
        defaultDir = c[4].strip()
except OSError:
    print('Config file not found. Please refer to README.', file=sys.stderr)

# this is to make sure help instead of usage gets printed on error
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print('error: %s\n' % message, file=sys.stderr)
        self.print_help()
        sys.exit(2)

parser = ArgumentParser(description='retrieves Twitter data via the Twitter API for further analysis')
parser.add_argument('--term', dest='searchterm', help='search term, if it is more than one word use quotations e.g. "North Korea"',type=lambda s: unicode(s, 'utf8'), required=True)
parser.add_argument('--dir', dest='directory', default='', help='directory for output files')
parser.add_argument('--lang', dest='language', default='', help='e.g. en, nl (default: blank (all))')
parser.add_argument('--type', dest='resultType', default='recent', help='result type: options are recent, popular, mixed, see API documentation. (default: recent)')
parser.add_argument('--unshorten', dest='unshorten', default=False, help='To include the destination that links redirect to (unshortened links) in the linkList output file set this to True. Default is False because it takes a while to get this data.')
parser.add_argument('--iterations', dest='iterations', default=10, help='Each iteration (call to the API) gives up to 100 tweets. The current rate limit per 15 minutes for the search API is 180 calls (Twitter can change this at any time). Default is set to 10, which retrieves up to 1,000 tweets.')
parser.add_argument('--manmaxid', dest='manmaxid', default=None, help='If you already got results for your search and you want to go back further in time and get more tweets, put in the lowest tweet id from your current dataset here. Make sure to wait at least 15 minutes from collecting the intital dataset due to rate limits.')
parser.add_argument('--geo', dest='geo',default='', help='geocode lat,long,radius e.g. 37.781157,-122.398720,1mi')

args = parser.parse_args()
searchterm = urllib.quote(args.searchterm) #handle URL encoding
language = args.language
resultType = args.resultType
geo = args.geo
directory = args.directory
iterations = int(args.iterations)
manMaxId = args.manmaxid
unshorten = bool(args.unshorten)

# Twitter authentication, depends on ornithologist.conf, see README
api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token_key,
                      access_token_secret=access_token_secret)

status1 = api.GetSearch(term=searchterm, result_type="recent", include_entities=True, count=1, lang=language, geocode=geo)

if manMaxId == None:
    since = min(s.id for s in status1) # You may be over the rate limit, wait 15 minutes and try again
else:
    since = manMaxId

userList = []

iterate = 0
#Keep this under the rate limit, either 180 or 15 calls per 15 minutes
maxItems = iterations * 100
currentTime = datetime.utcnow()

#open and write a log of the data collection
sldFileName = defaultDir + "ornithologistLog.csv"
if os.path.isfile(sldFileName) is True:
    info = codecs.open(sldFileName, encoding='utf-8', mode='a')
    info.write ("\n" + searchterm + "\t" + language  + "\t" + str(currentTime) + " UTC" + '\t' + resultType + '\t' + str(maxItems))
else:
    info = codecs.open(sldFileName, encoding='utf-8', mode='w+')
    info.write("search term\tlanguage\tgathered\tresult type\tmax retrieved\n" + searchterm + "	" + language + "	" + str(currentTime) + " UTC" + '    ' + resultType + '\t' + str(maxItems))


while iterate < iterations:
    iterate = iterate +1

    statuses = api.GetSearch(term=searchterm, result_type=resultType, include_entities=True, count=100, lang=language, geocode=geo, max_id=since)
    gathered = (len(statuses))
    print ('Gathering data, request ',iterate,' of up to ',iterations,' tweets gathered: ',gathered)

    if gathered == 0:
        print ('No more data available')
        break

    #to navigate the tweet timeline
    for s in statuses:
        if (since > s.id):
            since = s.id

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

            userFileName = defaultDir + searchterm + "/userEdges.csv"

            if not os.path.exists(os.path.dirname(userFileName)):
                os.makedirs(os.path.dirname(userFileName))
            if os.path.isfile(userFileName) is False:
                # open a file to write the to user network
                userNet = codecs.open(userFileName, encoding='utf-8', mode='w+')
                #Source is user, target is user mentioned
                userNet.write("Source\tTarget\ttweet id\ttweet")
            userNet = codecs.open(userFileName, encoding='utf-8', mode='a')
            userNet.write("\n" + unicode(s.user.screen_name) + "	" + unicode(toUserMatch.group(1)) + "\t" + unicode(s.id) + "\t" + unicode(strip))
        else:
            toUserList.append('')

        #get retweet user
        rtSearch = re.compile(r'RT @(\w*\b)', re.U)
        rtMatch = rtSearch.match(strip)
        rtList = []
        rtFileName = defaultDir + searchterm + "/rtEdges.csv"
        if rtMatch:
            rtList.append(rtMatch.group(1))

            if not os.path.exists(os.path.dirname(rtFileName)):
                os.makedirs(os.path.dirname(rtFileName))
            if os.path.isfile(rtFileName) is False:
                # open a file to write the RT network
                rt = codecs.open(rtFileName, encoding='utf-8', mode='w+')
                #Source is user, target is user retweeted
                rt.write("Source\tTarget\ttweet id\ttweet")

            rt = codecs.open(rtFileName, encoding='utf-8', mode='a')
            rt.write("\n" + unicode(s.user.screen_name) + "\t" + unicode(rtMatch.group(1)) + "\t" + unicode(s.id) + "\t" + unicode(strip))
        else:
            rtList.append('')

        #get all user mentions
        mentionList = re.findall(r'@(\w*\b)', strip, re.U)

        #get all hashtags
        hashtagList = re.findall(r'#\w*\b', strip, re.U)

        #get all links
        linkList = re.findall(r'https?://t\.co/[A-Za-z0-9]{10}', strip)

        #strip source field of HTML
        tweetSource= re.sub('<[^<]+?>', '', s.source)

        #read in the date 'Mon Sep 08 05:43:10 +0000 2014' as a date object and output as '20140908 05:43:10'
        dateObject = datetime.strptime(s.created_at, '%a %b %d %H:%M:%S +0000 %Y')
        unixDate = dateObject.strftime('%Y-%m-%d %H:%M:%S')

        tweetFileName = defaultDir + searchterm + "/tweets.csv"

        if not os.path.exists(os.path.dirname(tweetFileName)):
            os.makedirs(os.path.dirname(tweetFileName))

        if os.path.isfile(tweetFileName) is False:
            t = codecs.open(tweetFileName, encoding='utf-8', mode='w+')
            t.write("tweet id\tuser id\tuser name\ttime created\tretweets\tfavorites\ttweet source\tlanguage\twithheld from\ttweet\tto user\tretweet of\tlink")
        t = codecs.open(tweetFileName, encoding='utf-8', mode='a')
        # write one line of data to tweet file
        t.write("\n" + unicode(s.id) + "\t" + unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + unixDate + "\t" + unicode(s.retweet_count) + "\t" + str(s.favorite_count) + "\t" + unicode(tweetSource) + "\t" + unicode(s.lang) + "\t" + unicode(s.withheld_in_countries) + "\t" + unicode(strip) + "\t" + ', '.join(toUserList) + "\t" + ', '.join(rtList) + "\t" + "https://twitter.com/" + unicode(s.user.screen_name) + "/status/" + unicode(s.id))

        hashtagEdgeFileName = defaultDir + searchterm + "/user2hashtagEdges.csv"
        hashtagFileName = defaultDir + searchterm + "/hashtags.csv"
        mentionFileName = defaultDir + searchterm + "/mentions.csv"
        linkFileName = defaultDir + searchterm + "/links.csv"

        for h in hashtagList:
          if not os.path.exists(os.path.dirname(hashtagEdgeFileName)):
              os.makedirs(os.path.dirname(hashtagEdgeFileName))

          if os.path.isfile(hashtagEdgeFileName) is False:
            hash = codecs.open(hashtagEdgeFileName, encoding='utf-8', mode='w+')
            #Source is user and target is hashtag
            hash.write("Source\tTarget\ttweet id\ttweet")
          hash = codecs.open(hashtagEdgeFileName, encoding='utf-8', mode='a')
          hash.write("\n" + unicode(s.user.screen_name) + "\t" + unicode(h) + "\t" + unicode(s.id) + "\t" + unicode(strip))

          if not os.path.exists(os.path.dirname(hashtagFileName)):
              os.makedirs(os.path.dirname(hashtagFileName))
          if os.path.isfile(hashtagFileName) is False:
            hash = codecs.open(hashtagFileName, encoding='utf-8', mode='w+')
            hash.write("tweet id\thashtag")
          hash = codecs.open(hashtagFileName, encoding='utf-8', mode='a')
          hash.write("\n" + unicode(s.id) + "\t" + unicode(h))

        for m in mentionList:
          if not os.path.exists(os.path.dirname(mentionFileName)):
              os.makedirs(os.path.dirname(mentionFileName))

          if os.path.isfile(mentionFileName) is False:
            mention = codecs.open(mentionFileName, encoding='utf-8',mode='a')
            mention.write("tweet id\tuser name mentioned")
          mention = codecs.open(mentionFileName, encoding='utf-8',mode='a')
          mention.write("\n" + unicode(s.id) + "\t" + unicode(m))

        for l in linkList:
            #Unshorten links if flag is True
            if (unshorten):
                try:
                    shorten = requests.head(unicode(l), allow_redirects=True, timeout=.5)

                    #requests.exceptions.Timeout:
                    if shorten.status_code == requests.codes.ok:
                        if shorten.history:
                            unshort = shorten.url
                        else:
                            unshort = "no redirection"
                except:
                    unshort = "error or timeout"

                if not os.path.exists(os.path.dirname(linkFileName)):
                    os.makedirs(os.path.dirname(linkFileName))

                if os.path.isfile(linkFileName) is False:
                    linkFile = codecs.open(linkFileName, encoding='utf-8',mode='a')
                    linkFile.write("tweet id\tshort link\tunshortened link")
                linkFile = codecs.open(linkFileName, encoding='utf-8',mode='a')
                linkFile.write("\n" + unicode(s.id) + "\t" + unicode(l) + "\t" + unshort)
            else:
                if not os.path.exists(os.path.dirname(linkFileName)):
                    os.makedirs(os.path.dirname(linkFileName))

                if os.path.isfile(linkFileName) is False:
                    linkFile = codecs.open(linkFileName, encoding='utf-8',mode='a')
                    linkFile.write("tweet id\tshort link")
                linkFile = codecs.open(linkFileName, encoding='utf-8',mode='a')
                linkFile.write("\n" + unicode(s.id) + "\t" + unicode(l))

            #add users to the userList array
            for s in statuses:
                #take out any tabs or new lines in the user descriptions
                takeTabNewlinesDesc = re.compile(r'[\t\r\n]')
                stripDesc = takeTabNewlinesDesc.sub('', s.user.description)
                userList.append(unicode(s.user.id) + "\t" + unicode(s.user.screen_name) + "\t" + s.user.location + "\t" + str(s.user.time_zone) + "\t" + str(s.user.utc_offset) + "\t" + str(s.user.profile_image_url) + "\t" + stripDesc)

    # directory of each tweet as a file with ID as name for NLP (or whatever)
    for s in statuses:
        # create directory (if needed) and open a file to write each tweet to
        filename = defaultDir + searchterm + "/" + "tweets" + "/" + str(s.id) + ".txt"
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with codecs.open(filename, encoding='utf-8', mode="w+") as f:
            f.write(unicode(s.text))

userFileName = defaultDir + searchterm + "/users.csv"
if not os.path.exists(os.path.dirname(userFileName)):
    os.makedirs(os.path.dirname(userFileName))
u = codecs.open(userFileName, encoding='utf-8', mode='w+')
#deduplicate the user list before printing
userList = list(set(userList))
u.write("user id\tscreen name\tlocation\ttime zone\tutc offset\tprofile image URL\tdescription\n")
u.write('\n'.join(userList))

print("Done")
