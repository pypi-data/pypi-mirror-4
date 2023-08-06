"""
	REQUIRED: PASTE YOUR TWITTER OAUTH CREDENTIALS INTO puttytat/credentials.txt 
	          OR USE -oauth OPTION TO USE A DIFFERENT FILE CONTAINING THE CREDENTIALS.
	
	Prints the most frequent hashtags found in tweets that contain any of the words 
	that are passed as arguments on the command line.  Prints the current count of 
	each hashtag.  
	
	Set the number of hashtags with the '-n' option.  The default is the 3 most 
	frequent hashtags.
	
	By default only real-time tweets are downloaded (using Twitter's Streaming API).  
	To search old tweets (using Twitter's REST API) use the '-past' flag.  Twitter 
	will permit about a week's worth of old tweets to be counted before breaking the 
	connection.
"""

__author__ = "Jonas Geduldig"
__date__ = "December 7, 2012"
__license__ = "MIT"

# unicode printing for Windows 
import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import argparse
import operator
import puttytat
import Tokenizer

OAUTH = None


def process_tweet(text, count, n):
	tokens = Tokenizer.Tokenizer.hashtags(text)
	for tok in tokens:
		if tok in count:
			count[tok] += 1
		else:
			count[tok] = 1
	count_list = sorted(count.iteritems(), key=operator.itemgetter(1), reverse=True)
	if len(count_list) > 0:
		print ' '.join('%s-%s' % i for i in count_list[:n])


def rank_hashtags_search(list, n):
	words = ' OR '.join(list)
	count = {}
	while True:
		tw = puttytat.TwitterRestPager(OAUTH)
		for item in tw.request('search/tweets', {'q': words}):
			if 'text' in item:
				process_tweet(item['text'], count, n)
			elif 'message' in item:
				if item['code'] == 131:
					continue # ignore internal server error
				elif item['code'] == 88:
					print>>sys.stderr, 'Suspend search until %s' % search.get_quota()['reset']
				raise Exception('Message from twiter: %s' % item['message'])


def rank_hashtags_stream(list, n):
	words = ','.join(list)
	count = {}
	while True:
		tw = puttytat.TwitterStream(OAUTH)
		try:
			while True:
				for item in tw.request('statuses/filter', {'track': words}):
					if 'text' in item:
						process_tweet(item['text'], count, n)
					elif 'disconnect' in item:
						raise Exception('Disconnect: %s' % item['disconnect'].get('reason'))
		except Exception, e:
			print>>sys.stderr, '*** MUST RECONNECT', e


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Hashtag ranker.')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-past', action='store_true', help='search historic tweets')
	parser.add_argument('-n', metavar='N', type=int, default=3, help='number of most frequest words displayed')
	parser.add_argument('words', metavar='W', type=str, nargs='+', help='word(s) to track')
	args = parser.parse_args()	

	OAUTH = puttytat.TwitterOauth.read_file(args.oauth)
	
	try:
		if args.past:
			rank_hashtags_search(args.words, args.n)
		else:
			rank_hashtags_stream(args.words, args.n)
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
	except Exception, e:
		print>>sys.stderr, '*** STOPPED', e
