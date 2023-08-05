#!/usr/bin/env python

# Author: Alberto Lumbreras
# A script to get a followers network. A mutation of a code written by Edd Dumbill. http://twitter.com/edd

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth
from xml.sax.saxutils import escape
import tweepy
import auth
import time
import datetime
import pickle
import os
import getopt
import sys

global api_calls

user = ""
whitelist = [] # put here possible followers that you don't want to track 
api_calls = 0


try:                                
    opts, args = getopt.getopt(sys.argv[1:], "u:", ["user="]) 
except getopt.GetoptError:           
    print "Wrong parameters"                          
    sys.exit(2)

for opt, arg in opts:
    if opt in ['-u', '--user']:
        user = arg
        print "Analyzing user:", user

def all_followers(api, screen_name):
    """ Return followers as User objects """
    global api_calls

    print "API: all_followers of ", screen_name
    followers = []
    print "getting cursor..."
    try:
        follower_cursors = tweepy.Cursor(api.followers, id=screen_name)
    except Excepction as e:
        print "Excepction: user profile is probably closed"
        print e
        return []
    api_calls +=1
    c = 0
    for f in follower_cursors.items():
        followers.append(f)
        c +=1
        if c%10 == 0:
            print "10 cursors ...", datetime.datetime.now()
            sleep_if_near_limit()
        if c%2000 == 0: #limit number of Cursors / followers
            break
    print ("%d followers retrieved" % c)
    print "end of All_followers. API calls:", api_calls
    return followers

def sleep_if_near_limit():
    limit_status = api.rate_limit_status() #esto enlentece. Quitarlo o no hacerlo tan frecuente
    seconds_to_reset = limit_status['reset_time_in_seconds'] - time.time()
    if limit_status['remaining_hits'] < 25:
        print "**sleeping " + str(seconds_to_reset) + " secs. to avoid reaching rate limit..."
        time.sleep(seconds_to_reset)
        time.sleep(60)

##########################

# Main
api = auth.get_api()

print "Getting main User..."
me = api.get_user(user)
api_calls +=1
print "Getting followers of main User..."
my_friends = all_followers(api, me.screen_name)
friend_ids = {}

# Load already tracked followers tracked
if os.path.exists('followers.pickle'):
    print "Opening pickle file..." 
    pfile = open('followers.pickle', 'r')
    friend_ids = pickle.load(pfile)
    print(friend_ids.keys())
    pfile.close()

print "followers loaded from pickle file:", friend_ids.keys()
friend_ids[me.id] = my_friends

print("Enumerating %d followers" % len(my_friends))
count = len(my_friends)

try:
    for u in my_friends:
        print "******Followers left:", count
        limit_status = api.rate_limit_status()
        seconds_to_reset = limit_status['reset_time_in_seconds'] - time.time()
        print "API Remaining hits:", limit_status['remaining_hits']
        print "API seconds to reset:", seconds_to_reset
        sleep_if_near_limit()
        count -=1
        if not friend_ids.has_key(u.id) or u.screen_name in whitelist:
            print("Finding followers of %s" % (u.screen_name))
            try:
                # friend_ids[u.id] = all_followers(api, u.screen_name) # TODO llamar a la de ids
                friend_ids[u.id] = api.friends_ids(u.screen_name)
            except Exception as e:
                print "****Exception", e
                friend_ids[u.id] = []
            print "Number of followers:", len(friend_ids[u.id])
            
            # find intersections. Followers that follow each other.                                   
            common_friends = []
            for f in my_friends:
                for ff in  friend_ids[u.id]:
                    if str(f.id) == str(ff):
                        common_friends.append(f)
            print u.screen_name + " is also followed by:"
            names = [c.screen_name for c in common_friends]
            print names

        else:
            print("Already loaded followers of %s" % u.screen_name)

    # Store followers tracked. We might use them in the future when analyzing other user
    # print "Saving followers lists to pickle file...", datetime.datetime.now() 
    # print "Size of dict:", len(friend_ids)
    # pfile = open('followers.pickle', 'w')
    # pickle.dump(friend_ids, pfile)
    # print("Saved followers to pickle")
    # pfile.close()


except TwitterError:
    print("Got Twitter HTTP Error")
except Exception as e:
    print "**** Exception no reconocida:"
    print e

finally:
    pfile = open('followers.pickle', 'w')
    pickle.dump(friend_ids, pfile)
    print("Saved followers to pickle")
    pfile.close()


######################### DRAW GRAPH
print "Writing graph..."
out = open("graph.graphml", "w")
out.write("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
  http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">

  <key id="name" for="node" attr.name="name" attr.type="string" />

  <graph edgedefault="directed">
""")

out.write("<node id='%d'><data key='name'>%s</data></node>\n" % (me.id, escape(me.screen_name)))
# making a set of the friends as Twitter read process sometimes includes dupes
friends_set=set([(x.id,x.screen_name) for x in my_friends])
for (f_id, f_name) in friends_set:
    out.write("<node id='%d'><data key='name'>%s</data></node>\n" % (f_id, escape(f_name)))

edge_id = 0
my_fids = set(friend_ids[me.id])
written = {}
for u in my_friends:
    if written.has_key(u.id):
        break
    else:
        written[u.id] = True
        print ("<!-- followers of %s -->\n" % escape(u.screen_name))
        out.write("<!-- followers of %s -->\n" % escape(u.screen_name))
        # write an edge for my relationship to them
        out.write("<edge id='edge%d' source='%d' target='%d' />\n" % (edge_id, u.id, me.id))
        edge_id = edge_id + 1
        # now write edges for each of their connections within my follower network
        # find intersections. Followers that follow each other.
        common_friends = []
        try:
            for f in my_fids:
                for ff in  friend_ids[u.id]:
                    # if this friend of mine also follows thos other friend of mine (common followers)
                    if str(f.id) == str(ff):
                        common_friends.append(f)
        except Exception as e:
            print "Exception while writing the graph"
            print e
            continue
        print u.screen_name + " is also followed by:"
        names = [c.screen_name for c in common_friends]
        print names

        for c in common_friends:
            out.write("<edge id='edge%d' source='%d' target='%d' />\n" % (edge_id, c.id, u.id))
            edge_id = edge_id + 1

out.write("""</graph></graphml>""")
out.close()
