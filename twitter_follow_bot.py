# -*- coding: utf-8 -*-

"""
Copyright 2014 Randal S. Olson
This file is part of the Twitter Follow Bot library.
The Twitter Follow Bot library is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option) any
later version.
The Twitter Follow Bot library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with the Twitter
Follow Bot library. If not, see http://www.gnu.org/licenses/.
"""

from twitter import Twitter, OAuth, TwitterHTTPError
import os
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# put your tokens, keys, secrets, and Twitter handle in the following variables
OAUTH_TOKEN = "" #add yours here
OAUTH_SECRET = "" #add yours here
CONSUMER_KEY = "" #add yours here
CONSUMER_SECRET = "" #add yours here
TWITTER_HANDLE = "" #add yours here

# put the full path and file name of the file you want to store your "already followed"
# list in
ALREADY_FOLLOWED_FILE = "already-followed.csv"

t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET,
            CONSUMER_KEY, CONSUMER_SECRET))

def send_dm(user, message):
    return t.direct_messages.new(user=user, text=message)

def search_tweets(q, count=100, result_type="recent"):
    """
        Returns a list of tweets matching a certain phrase (hashtag, word, etc.)
    """

    return t.search.tweets(q=q, result_type=result_type, count=count)


def auto_fav(q, count=100, result_type="recent"):
    """
        Favorites tweets that match a certain phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)

    for tweet in result["statuses"]:
        try:
            # don't favorite your own tweets
            if tweet["user"]["screen_name"] == TWITTER_HANDLE:
                continue

            result = t.favorites.create(_id=tweet["id"])
            logger.info("favorited: %s" % (result["text"].encode("utf-8")))
            print("favorited: %s" % (result["text"].encode("utf-8")))

        # when you have already favorited a tweet, this error is thrown
        except TwitterHTTPError as e:
            logger.info("error: %s" % (str(e)))
            print("error: %s" % (str(e)))


def auto_rt(q, count=100, result_type="recent"):
    """
        Retweets tweets that match a certain phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)

    for tweet in result["statuses"]:
        try:
            # don't retweet your own tweets
            if tweet["user"]["screen_name"] == TWITTER_HANDLE:
                continue

            result = t.statuses.retweet(id=tweet["id"])
            logger.info("retweeted: %s" % (result["text"].encode("utf-8")))
            print("retweeted: %s" % (result["text"].encode("utf-8")))

        # when you have already retweeted a tweet, this error is thrown
        except TwitterHTTPError as e:
            logger.info("error: %s" % (str(e)))
            print("error: %s" % (str(e)))


def get_do_not_follow_list():
    """
        Returns list of users the bot has already followed.
    """

    # make sure the "already followed" file exists
    if not os.path.isfile(ALREADY_FOLLOWED_FILE):
        with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
            out_file.write("")

        # read in the list of user IDs that the bot has already followed in the
        # past
    do_not_follow = set()
    dnf_list = []
    with open(ALREADY_FOLLOWED_FILE) as in_file:
        for line in in_file:
            dnf_list.append(int(line))

    do_not_follow.update(set(dnf_list))
    del dnf_list

    return do_not_follow


def auto_follow(q, count=100, result_type="recent"):
    """
        Follows anyone who tweets about a specific phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    do_not_follow = get_do_not_follow_list()

    for tweet in result["statuses"]:
        try:
            if (tweet["user"]["screen_name"] != TWITTER_HANDLE and
                    tweet["user"]["id"] not in following and
                    tweet["user"]["id"] not in do_not_follow):

                t.friendships.create(user_id=tweet["user"]["id"], follow=False)
                following.update(set([tweet["user"]["id"]]))

                print("followed %s" % (tweet["user"]["screen_name"]))

        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))

            # quit on error unless it's because someone blocked me
            if "blocked" not in str(e).lower():
                quit()


def auto_follow_followers_for_user(user_screen_name, count=100):
    """
        Follows the followers of a user
    """
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers_for_user = set(t.followers.ids(screen_name=user_screen_name)["ids"][:count]);
    do_not_follow = get_do_not_follow_list()

    for user_id in followers_for_user:
        try:
            if (user_id not in following and
                user_id not in do_not_follow):

                t.friendships.create(user_id=user_id, follow=False)
                print("followed %s" % user_id)

        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))

def auto_follow_followers():
    """
        Follows back everyone who's followed you
    """

    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)["ids"])

    not_following_back = followers - following

    for user_id in not_following_back:
        try:
            t.friendships.create(user_id=user_id, follow=False)
        except Exception as e:
            print("error: %s" % (str(e)))


def auto_unfollow_nonfollowers():
    """
        Unfollows everyone who hasn't followed you back
    """

    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)["ids"])

    # put user IDs here that you want to keep following even if they don't
    # follow you back
    users_keep_following = set([])

    not_following_back = following - followers

    # make sure the "already followed" file exists
    if not os.path.isfile(ALREADY_FOLLOWED_FILE):
        with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
            out_file.write("")

    # update the "already followed" file with users who didn't follow back
    already_followed = set(not_following_back)
    af_list = []
    with open(ALREADY_FOLLOWED_FILE) as in_file:
        for line in in_file:
            af_list.append(int(line))

    already_followed.update(set(af_list))
    del af_list

    with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
        for val in already_followed:
            out_file.write(str(val) + "\n")

    for user_id in not_following_back:
        if user_id not in users_keep_following:
            t.friendships.destroy(user_id=user_id)
            print("unfollowed %d" % (user_id))


def auto_mute_following():
    """
        Mutes everyone that you are following
    """
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    muted = set(t.mutes.users.ids(screen_name=TWITTER_HANDLE)["ids"])

    not_muted = following - muted

    # put user IDs of people you do not want to mute here
    users_keep_unmuted = set([])

    # mute all
    for user_id in not_muted:
        if user_id not in users_keep_unmuted:
            t.mutes.users.create(user_id=user_id)
            print("muted %d" % (user_id))


def auto_unmute():
    """
        Unmutes everyone that you have muted
    """
    muted = set(t.mutes.users.ids(screen_name=TWITTER_HANDLE)["ids"])

    # put user IDs of people you want to remain muted here
    users_keep_muted = set([])

    # mute all
    for user_id in muted:
        if user_id not in users_keep_muted:
            t.mutes.users.destroy(user_id=user_id)
            print("unmuted %d" % (user_id))


# Files required: list_index_start & follow_user_list
def auto_follow_list():
    """
        Follows back everyone who's followed you
    """

    g = open("list_index_start", "r+")
    start_idx = int(g.readline()) #0
    print("start index = %d" % start_idx)

    f = open("follow_user_list", "r")
    usernames = f.read().split(',')
    f.close()

    for index, screen_name in enumerate(usernames[start_idx:]):
        try:
            t.friendships.create(screen_name=screen_name, follow=True)
            time.sleep(20)
            logger.info("followed %s, index = %d" % (str(screen_name), start_idx+index))
            print("followed %s, index = %d" % (str(screen_name), start_idx+index))
        except Exception as e:
            logger.info("attempt to follow %s, index = %d" % (str(screen_name), start_idx+index))
            logger.info("error: %s" % (str(e)))
            print("attempt to follow %s, index = %d" % (str(screen_name), start_idx+index))
            print("error: %s" % (str(e)))

            g.seek(0)
            g.write(str(start_idx+index)) #write current index to start file
            g.truncate()

            errorstring = '\"errors\":[{\"code\":161'
            if errorstring in str(e):
                print("script stopped with error code 161")
                logger.info("script stopped with error code 161")
                g.close()
                break
