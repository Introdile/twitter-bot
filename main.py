import tweepy
import markovify
import glob,os,re,datetime,time
from os import environ
import threading,random

# this all essentially logs the script into your twitter account
CONSUMER_KEY = environ.get('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = environ.get('TWITTER_CONSUMER_SECRET')
ACCESS_KEY = environ.get('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_SECRET = environ.get('TWITTER_ACCESS_SECRET')

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)

api = tweepy.API(auth)

hour_in_seconds = 60.0*60.0

# SETTINGS 

# the twitter @ of your bot account. if you dont set this right, it wont reply to replies
my_handle = 'your_bot_accounts_handle'

# the accounts the bot pulls tweets from, must be in quotes and comma seperate
# only up to 6 accounts by default
# !! ASK FOR PERMISSION IF YOU WANT TO ADD ACCOUNTS OTHER THAN ONES YOU OWN !!
source_accounts = ['your_account_1','your_account_2']

# words to filter out
# Add words between the parenthesis, seperated by | with no spaces
# An example swear filter would look like '\b(fuck|fucking|shit|damn)\b'
# This should only find whole words, so putting 'fuck' in wont find 'fucking' or 'fucks'
exclude_words = r'\b()\b'

# what to replace filtered words with
# I recommend either leaving this blank or adding a single word
replace_word = ""

# the chance the bot will reply to a tweet
# above put 1-10 here, 1 is a 10% chance and 10 is a 100% chance
reply_chance = 7
# if you want to set it to 0, you should just set can_reply to False and set up a scheduler

# how many hours between each corpus rebuild
corpus_rebuild_time = 8.0

# how many hours between each tweet
tweet_time = 1.0

# if the bot can reply or not
# if you turn this off, you'll have to set up a scheduler on heroku
can_reply = True
# remember to capitalize True or False when you set this

# END SETTINGS

# This watches the bot's mentions
class streamListener(tweepy.StreamListener):
    def __init__(self,api):
        self.api = api

    def on_status(self,status):
        print("{}: {}".format(status.author.screen_name,status.text))
        newStatus = generate_random_sentence()

        # There's a ~60% chance that the bot will reply to a tweet
        if random.randint(0,9) < reply_chance:
            try:
                api.update_status('@{} {}'.format(status.user.screen_name,newStatus),in_reply_to_status_id=status.id)
                print('{} to {}: {}'.format(my_handle,status.user.screen_name,newStatus))
            except tweepy.TweepError as e:
                print(e.reason)
        else:
            print("I'm not going to reply to this one. :)")
    
    def on_timeout(self):
        print("Timeout... :(")
        return True

def markov_tweet(sched=True):
    newStatus = generate_random_sentence()
    try:
        # Tweets the random sentence!
        #api.update_status(newStatus)
        print('{}: {}'.format(my_handle,newStatus))
    except tweepy.TweepError as e:
        # If there's an error, it'll push it to the log
        print(e.reason)
    
    if sched == True:
        # Schedules this to occur again after the given time
        t = threading.Timer(hour_in_seconds * tweet_time,markov_tweet)
        t.daemon = True
        t.start()

def build_corpus(sched=True):

    os.chdir('corpus/')
    for user in source_accounts:
        last_id = -1
        # checks if a lastid file exists and if so, it losts the last tweet id it scanned
        if os.path.isfile('./{}_lastid.txt'.format(source_accounts.index(user))):
            fid = open("./{}_lastid.txt".format(source_accounts.index(user)),"r")
            last_id = fid.readline()
            print(last_id)
            fid.close()
        
        source_tweets, first_id, was_ended = get_tweets(api,user,int(last_id))

        if last_id == -1 or last_id != -1 and was_ended == False:
            # if the file is new or the last tweet it scanned was deleted, it rewrites the whole corpus
            f = open("{}_tweets.txt".format(source_accounts.index(user)),"w",encoding='utf-8')

            for tweets in source_tweets:
                f.write(tweets + "\n")
            
            print("{user}\'s tweets written to {num}_tweets.txt".format(user=user,num=source_accounts.index(user)))
            f.close()
        else:
            # if there were new tweets since the last rebuild, it adds those lines to the corpus instead
            if len(source_tweets) > 0:
                new_tweets = ""
                for tweets in source_tweets:
                    new_tweets = new_tweets + tweets + "\n"

                print("{user}\'s tweets preappended to {num}_tweets.txt".format(user=user,num=source_accounts.index(user)))
                preappend_file("{}_tweets.txt".format(source_accounts.index(user)),new_tweets)
            else: print("No new tweets for {}!".format(user))
            # if there's no new tweets it just doesn't, fuck it
        
        # adds the last tweet id scanned in to the account's lastid file
        fid = open("{}_lastid.txt".format(source_accounts.index(user)),"w")
        fid.write(str(first_id))
        fid.close()
        print("Wrote {} to {}_lastid.txt".format(first_id,source_accounts.index(user)))

    os.chdir('..')

    # schedules this function to run again after the given time
    if sched == True:
        t = threading.Timer(hour_in_seconds * corpus_rebuild_time,build_corpus)
        t.daemon = True
        t.start()

def filter_text(text):
    text = re.sub(r'(\#|@|(http))\S+', '', text) # Removes hashtags, @'s, and urls
    text = re.sub(r'([0-9]+\s|[0-9]+:\s|[0-9]+\))','', text) # Removes numbers (such as '1 ','5: ','42) ') from the beginning of text
    text = re.sub(r'^\s+','',text) # Removes whitespace from the beginning of text
    text = re.sub(exclude_words,replace_word,text) # Replaces excluded words with the replace word
    return text

def get_tweets(api,user,end_id = -1):
    # Grabs tweets from the user specified
    grabbed_tweets = []
    print("Grabbing tweets for {}!".format(user))
    first_id = None
    end = False
    # Iterates through pages of a user's timeline
    for page in tweepy.Cursor(api.user_timeline,id=user,tweet_mode='extended').pages():
        for tweet in page:
            if first_id == None: first_id = tweet.id
            if tweet.id == end_id:
                end = True
                break
            # Filters out retweets, which always begin with "RT" at the beginning
            if not re.search(r'^RT',tweet.full_text):
                this_text = filter_text(tweet.full_text)
                grabbed_tweets.append(this_text)
        
        if end == True:
            print("{} new tweets!".format(str(len(grabbed_tweets))))
            break

        print("{} tweets found so far...".format(str(len(grabbed_tweets))))

    print("{}: {} tweets".format(user,str(len(grabbed_tweets))))
    return grabbed_tweets,first_id,end

def choose_random_files():
    # Gets all corpus files from the corpus directory
    tweet_files = []
    ##tweet_files = glob.glob("corpus/*_tweets.txt")
    for i in range(len(source_accounts)):
        tweet_files.append("corpus/{}_tweets.txt".format(i))
    
    rand = random.randint(1,len(tweet_files))

    random_files = []
    # Grabs files for the amount of random files chosen, 
    # removing files already chosen to prevent duplicates
    for i in range(rand):
        i = i
        rfile = random.choice(tweet_files)
        random_files.append(rfile)
        tweet_files.remove(rfile)
    
    return random_files

def generate_random_sentence(length = 240,files=None):
    source_files = []
    # You can choose specific files when calling this function, if you want
    if files == None:
        source_files = choose_random_files()
    else:
        source_files = files
    
    # Combines all the lines in each file chosen into a string, for use with the markovify library
    if source_files is not None:
        text = ''
        for sf in source_files:
            with open(sf,encoding='utf-8') as f:
                text += f.read()
        
        # Generates a sentence using markovify's generic markov chain model
        # i dont know how to make my own so this will have to do :(
        text_model = markovify.NewlineText(text)
        return text_model.make_short_sentence(length)

def preappend_file(original_file,text):
    # adds lines to the beginning of a file
    # sets the original content aside, adds the new lines, then readds the original
    with open(original_file, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(text.rstrip('\r\n') + '\n' + content)

if __name__ == "__main__":
    if can_reply == True:
        now = datetime.datetime.now()
        time_till_next_hour = 60.0 - now.minute

        # Schedules the two main function to run at the turn of the hour
        t = threading.Timer(time_till_next_hour * 60.0,build_corpus)
        t.daemon = True
        t.start()

        t = threading.Timer(time_till_next_hour * 60.0,markov_tweet)
        t.daemon = True
        t.start()

        print("Starting stream!")
        # This keeps the script running, hopefully forever!
        while True:
            try:
                # Sets up watching the mentions
                tweetStream = tweepy.Stream(auth=api.auth,listener=streamListener(api))
                tweetStream.filter(track=['@{}'.format(my_handle)])

            except Exception as e:
                # If an error is thrown, such as hitting twitter's rate limit, it'll wait a while before starting again
                print("Something happend!: {}".format(e))
                time.sleep(60)
                continue
    else:
        now = datetime.datetime.now()

        # Rebuilds the corpus depending on what you set the rebuild time too
        # This will rebuild every 24 hours if the rebuild time is set above 24 (theoretically)
        build_corpus(False)
        markov_tweet(False)
