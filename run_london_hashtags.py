
import london_hashtags

path = 'data/hashtagCountsPerDayLondon.csv'

list_size=100
num_increments=21

self = london_hashtags.london_hashtags(path)
self.print_summary_stats()


turnover = self.derive_turnover_matrix(list_size,num_increments)
Nt = self.get_daily_sample_size()
daily_sample_size=self.get_daily_sample_size()
powerlaw_fit=self.get_powerlaw_fit()
daily_alpha=self.get_daily_alpha()

self.summary_plot('plots/')
