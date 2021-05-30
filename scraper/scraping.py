import pandas as pd
import snscrape.modules.twitter as sntwitter

# Creating list to append tweet data to
tweets_list1 = []

# Using TwitterSearchScraper to scrape data and append tweets to list
for i, tweet in enumerate(sntwitter.TwitterSearchScraper('from:jack').get_items()):
    if i > 2:
        break
    print(dir(tweet))
    print(tweet.__dict__)
    print(tweet.conversationId)
    # print(tweet.verified)
    tweets_list1.append([tweet.date, tweet.id, tweet.content, tweet.user.username])

# Creating a dataframe from the tweets list above
# tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
print(tweets_list1[0])
