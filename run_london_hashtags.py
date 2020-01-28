
import london_hashtags
import pandas as pd

path = 'data/hashtagCountsPerDayLondon.csv'
start_date = pd.to_datetime('01/01/2018')


self = london_hashtags.london_hashtags(path,start_date)
#self = london_hashtags(path,start_date)

list_size=100
num_increments=21

#dates with number of tweets less than 2.5 standard deviations below mean 
dates_to_remove = pd.to_datetime(['2018-05-21', '2018-05-22', '2018-08-09', '2018-11-30','2019-07-11', '2019-08-28', 
                '2019-08-29', '2019-08-31', '2019-09-11', '2019-09-12', '2019-09-13'])

# do you want to remove days with small sample sizes?
#self.graphically_choose_new_sample_size_cutoff()
self.remove_low_sample_days(dates_to_remove)

#is a powerlaw distribution ot lognormal positive the best fit?
self.powerlaw_or_positive_lognormal()

#set x ticks for date axes
list_of_years = ['2018','2019','2020']
self.date_ticks(list_of_years)


## needs to be made more general
#self.print_summary_stats()

turnover = self.derive_turnover_matrix(list_size,num_increments)
Nt = self.get_daily_sample_size()
daily_sample_size=self.get_daily_sample_size()
powerlaw_fit=self.get_powerlaw_fit()
daily_alpha,daily_sigma=self.get_daily_alpha()

self.summary_plot('plots/')
