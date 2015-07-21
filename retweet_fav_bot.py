import time
from twitter_follow_bot import auto_fav, auto_rt

# run 15 times a day (once per hour) starting 6AM PST, total of 3*1*15= 45 favorites a day
for x in range(0, 2):
    auto_fav('keyword1', count=1) #add your own keywords
    auto_rt('keyword1', count=1, result_type="recent")
    time.sleep(60)
    auto_fav('keyword2', count=1) #add your own keywords
    auto_rt('keyword2', count=1, result_type="recent")
    time.sleep(60)
    #add more if necessary
