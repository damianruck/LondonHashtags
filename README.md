# Popularity of Twitter Hashtags in London since 2017

Possible modelling using the Neutral (random copying) model??

## London_hashtag Python library

Calculates and plots the following for Twitter hashtag popularity in London:

* Zipfs Law frequency distribution 
* Turnover in top ranked list vs list length
* Turnover in top ranked list vs time
* Total daily sampled hashtag vs time
* Turnover in top ranked list vs Total daily sampled hashtag
* Power law exponent (&alpha;) vs time

Looks for statsical signitures of social learning in the data, including right skewed (possibly powerlaw) frequency distribution and linear-ish turnover profile (turnover in top ranked lists of increasing size).  


# Things to do
* test if power law distribution is best explanation for frequency distribution of hashtags (test against other skewed distributions, such as lognormal)
* Correct for the dependence of turnover in the top 100 list on sample size.
* Identify days with low hashtag sample sizes
* Heaps Law (need Tweet data)
* Begin time series in January 2018 due for gradually rolled out changes on Twitter in late 2017. 
