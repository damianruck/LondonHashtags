import numpy as np
import matplotlib.pyplot as plt
import powerlaw
import os
import pandas as pd
import statsmodels.api as sm


class london_hashtags:
    def __init__(self,path):
        df = pd.read_csv(path)#,nrows=200000)
        df['date'] = pd.to_datetime(df['date'])
        self.data = df
        
    def print_summary_stats(self):
        print('# hashtag-days:',len(self.data.index))
        print('date range:',self.data['date'].min(),self.data['date'].max())

        s=self.data.groupby(['hashtag'],as_index=False).agg({'count':'sum'}).sort_values('count',ascending=False)
        s.index=range(1,len(s.index)+1)

        sorted_unique_dates = pd.Series(np.sort(self.data['date'].unique()))

        diff=sorted_unique_dates.diff()
        u=pd.Series(diff.unique()).dropna()
        #only two different gap lengths betwen measurements (1 and 2 days)

        print('maximum number of days between measurements:', u.iloc[1]/u.iloc[0])
        print('number of occassions maximum gap occurs:', len(diff[diff==u.iloc[1]]))

        missing_dates = sorted_unique_dates[np.where(diff==u.iloc[1])[0]]

        #sorted_unique_dates[sorted_unique_dates.isin(missing_dates - pd.Timedelta(1,'d'))]
        print('missing dates are: ', [m - pd.Timedelta(1,'d') for m in missing_dates])
        
        
    def derive_turnover_matrix(self,list_size=100,num_increments=21):
        
        #add list features as attributes
        self.list_size = list_size
        self.num_increments = num_increments
        
        def nlargestGroup(df,list_size):
            return (df.nlargest(list_size,'count').
                    assign(rank = lambda df: df['count'].rank(method='first',ascending = False)))

        def turnover(df):
            return len(df[~df['hashtag_today'].isin(df['hashtag_yesterday'])].index)

        def today_yesterday_merge(df):
            return (df.merge(df, left_on=['date','rank'], right_on=['yesterday','rank'], 
                  suffixes = ('_today','_yesterday'),how='inner'))

        def get_turnover_matrix(df,list_size,num_increments):
            turnover_df = pd.DataFrame()
            
            for ls in np.linspace(1,list_size,num_increments,dtype='int'): 
                turnover_df[ls]=df[df['rank'] <= ls].groupby('date_today').apply(turnover)
            
            return turnover_df
        
        self.turnover_matrix=(
            self.data.groupby('date',as_index=False).apply(nlargestGroup,list_size).
            assign(yesterday = lambda df: df['date']-pd.Timedelta(1,'d')).
            pipe(today_yesterday_merge).
            pipe(get_turnover_matrix,list_size,num_increments)
        ) 
        
        return self.turnover_matrix
    
    def get_daily_sample_size(self): 
        self.daily_sample_size = self.data.groupby('date').agg({'count':'count'})
        return self.daily_sample_size
    
    def get_powerlaw_fit(self): 
        
        #hashtag counts over all dates
        self.all_time_rankings = (self.data.groupby('hashtag').agg({'count':'sum'})['count'].
                                sort_values(ascending = False))
        
        # fit power law 
        self.powerlaw_fit=powerlaw.Fit(self.all_time_rankings,verbose=False)
        self.alpha = self.powerlaw_fit.alpha #power law exponent
        
        return self.all_time_rankings
    
    def get_daily_alpha(self):

        def calculate_daily_powerlaw(df):
            return powerlaw.Fit(df['count'],verbose=False).alpha

        #calculate the power law exponent for each day
        self.daily_alpha = self.data.groupby('date').apply(calculate_daily_powerlaw)

        return self.daily_alpha
    
    
    ### indivual methods for the plots ####
    
    def plotaxis_turnover_by_listsize(self,ax):
    
        if hasattr(self,'turnover_matrix') == False:
            #set list size and increments to default
            list_size=100
            num_increments=21
            self.derive_turnover_matrix(list_size,num_increments)


        list_vec = self.turnover_matrix.columns
        mean = self.turnover_matrix.mean()
        error = self.turnover_matrix.std()

        #f, ax = plt.subplots()

        ax.plot(list_vec,mean)
        ax.fill_between(list_vec,mean-error,mean+error,alpha=0.5)
        ax.set_xlabel('list size',fontsize=16)
        ax.set_ylabel('turnover',fontsize=16)

        return ax

    def plotaxis_turnover_by_time(self,ax):

        if hasattr(self,'turnover_matrix') == False:
            #set list size and increments to default
            list_size=100
            num_increments=21
            self.derive_turnover_matrix(list_size,num_increments)

        #HARD WIRED DATE TICKS
        ticks_to_use = pd.Series([pd.to_datetime('2017'),pd.to_datetime('2018'),
                                  pd.to_datetime('2019'),pd.to_datetime('2020')])

        labels = ticks_to_use.dt.year

        ax.plot(self.turnover_matrix[self.list_size],alpha=0.7)

        # Now set the ticks and labels
        ax.set_xticks(ticks_to_use)
        ax.set_xticklabels(labels)

        ax.set_xlabel('year',fontsize=16)
        ax.set_ylabel('turnover (top ' + str(self.list_size) + ')',fontsize=16)

        return ax

    def plotaxis_sample_size(self,ax):

        if hasattr(self,'daily_sample_size') == False:
            self.get_daily_sample_size()

        #HARD WIRED DATE TICKS
        ticks_to_use = pd.Series([pd.to_datetime('2017'),pd.to_datetime('2018'),
                                  pd.to_datetime('2019'),pd.to_datetime('2020')])

        labels = ticks_to_use.dt.year

        ax.plot(self.daily_sample_size.index,self.daily_sample_size,'-')
        ax.set_ylabel('sample size',fontsize=16)
        ax.set_xlabel('year',fontsize=16)
        ax.set_xticks(ticks_to_use)
        ax.set_xticklabels(labels)

        return ax

    def plotaxis_turnover_by_sample_size(self,ax):

        if hasattr(self,'daily_sample_size') == False:
            self.get_daily_sample_size()

        if hasattr(self,'turnover_matrix') == False:
            #set list size and increments to default
            list_size=100
            num_increments=21
            self.derive_turnover_matrix(list_size,num_increments)

        x=self.turnover_matrix[self.list_size]
        y=self.daily_sample_size.loc[self.turnover_matrix.index,'count']

        lowess = sm.nonparametric.lowess(endog=y, exog=x, frac=0.9)    
        xfit,yfit = list(zip(*lowess))

        ax.plot(x,y,'o',alpha=0.7,label='_legend_')
        ax.plot(xfit,yfit,'-',c='darkred',lw=4,alpha=0.7,label='LOESS fit')
        ax.set_ylabel('sample size',fontsize=16)
        ax.set_xlabel('turnover (top 100)',fontsize=16)
        ax.legend(fontsize=14)

        return ax

    def plotaxis_powerlaw(self,ax):

        if hasattr(self,'powerlaw_fit') == False:
            self.get_powerlaw_fit()

        def predicted_y(x,fit):
            yfit = x**-fit.alpha
            yfit = yfit/sum(yfit)
            return yfit

        # power law histogram of hashtags
        x,y = self.powerlaw_fit.pdf()
        x = x[:-1] + np.diff(x)/2
        y = y/sum(y) #normlize probability density

        #power law line of best fit
        yfit = predicted_y(x,self.powerlaw_fit)

        ax.loglog(x,y,'s',lw=3,label='data hist')
        ax.loglog(x,yfit,'--',lw=2,c='darkred',label=r'power law fit ($\alpha$= ' + str(np.round(self.alpha,2)) + ')')

        ax.set_xlabel('hashtag frequency',fontsize=16)
        ax.set_ylabel('probability',fontsize=16)

        ax.legend(fontsize=14)

        return ax

    def plotaxis_daily_powerlawalpha(self,ax):

        if hasattr(self,'daily_alpha') == False:
            self.get_daily_alpha()

        date_marks = pd.to_datetime(pd.Series(['2017','2018','2019','2020']))
        date_labels = date_marks.dt.year

        ax.plot(self.daily_alpha)

        ax.set_xticks(date_marks)
        ax.set_xticklabels(date_labels)
        ax.set_ylabel(r'$\alpha$',fontsize=20,rotation=0)
        ax.set_xlabel('year',fontsize=16)

        return ax
    
    def summary_plot(self,save_directory):
        print(save_directory)

        plt.style.use('tableau-colorblind10')

        f, ax = plt.subplots(3,2,figsize=[13,9])

        self.plotaxis_turnover_by_listsize(ax[0,0])
        self.plotaxis_turnover_by_time(ax[0,1])
        self.plotaxis_sample_size(ax[1,0])
        self.plotaxis_turnover_by_sample_size(ax[1,1])
        self.plotaxis_powerlaw(ax[2,0])
        self.plotaxis_daily_powerlawalpha(ax[2,1])
        plt.tight_layout()

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        plt.savefig(save_directory+'summary_plots.pdf')
    ###end plots ######
