
import pandas as pd
import numpy as np
import statistics as stat
from statsmodels.tsa.stattools import adfuller
from obspy.signal.detrend import polynomial
from statsmodels.tsa.seasonal import STL
from tsmoothie.smoother import ExponentialSmoother, KalmanSmoother



def Deseasonalize_STL(df):
    # This function deseasonalizes the variables
    # Input is a the data frame of Google trends and a set of seasonal dummies
    deseasonalized = pd.DataFrame(index = df.index)

    for columns in df:
        # Create model object
        stl = STL(df[columns], period = 12)
        
        # Estimate the model
        fit = stl.fit()
        # Add the seasonal and trend components  
        deas_temp = fit._trend + fit._resid
        deseasonalized = deseasonalized.merge(deas_temp.to_frame(), left_index=True, right_index=True)
        
    deseasonalized.columns = df.columns.values    
    return deseasonalized

def Detrend(df,significance,lags = 0):
    # This function detrends or first differences the Google data
    # Input is a the data frame of Google trends and a significance level: '1%', '5%' or '10%'
    Outputdf = pd.DataFrame(np.nan, index = df.index, columns = df.columns )
    
    for columns in df:
        # ADF test with a constant
        test_c = adfuller(df[columns], regression ='c', autolag='AIC', maxlag = lags)
        # ADF test with a constant and linear trend
        test_ct = adfuller(df[columns], regression ='ct', autolag='AIC', maxlag = lags)

    
        # here we test if test stat is lower than critical value
        if test_c[0]<=test_c[4][significance]:
            residuals_temp = df[columns]
        elif test_ct[0]<=test_ct[4][significance]:
            residuals_temp = polynomial(df[columns], order=1)
        else:
            residuals_temp = polynomial(df[columns], order=2)

        Outputdf[columns] = residuals_temp

    # We remove NaN caused by first differencing
    Outputdf = Outputdf.fillna(method='backfill') 
    
    return Outputdf  


def ExpSmoother(df, window = 20, alpha = 0.5):
    result = pd.DataFrame(np.nan, index = df.index, columns = df.columns)
    
    smoother = ExponentialSmoother(window_len = window, alpha = alpha)
    
    for i in range(0,len(df.columns)):
        smooth = smoother.smooth(df.iloc[:,i])
        result.iloc[:window,i] = df.iloc[:window,i]
        result.iloc[window:,i] = smooth.smooth_data    
    return result


def KalSmoother(df, level = 0.8):
    
    result = pd.DataFrame(np.nan, index = df.index, columns = df.columns)
                          
    smoother = KalmanSmoother(component='level',component_noise={'level':level})                      
    
    for i in range(0,len(df.columns)):
        
        smooth = smoother.smooth(df.iloc[:,i])
        
        result.iloc[:,i] = np.transpose(smooth.smooth_data)
    
    return result


def Median_decomp(df):
    
    #Demeaning
    for values in df.columns.values:
        u = stat.mean(df[values])
        std = stat.stdev(df[values])

        df[values] = (((df[values] - u)/std) +10)

    #This on is with base year
    df = df.apply(lambda x: np.floor(((x)/x.iloc[0] * 100)))

    #calculating the median
    arr = []
    for x in df.T.columns.values:    
        arr.append(stat.median(df.T[x]))

    #Putting the array in dataframe
    df_index = pd.DataFrame({'index':arr})
    df_index = df_index.set_index(pd.Index(df.T.columns.values[:]))

    return df_index

def data_prep(df,var_lagg_values):
    for var in var_lagg_values:

        lagg_value = var_lagg_values[var]

        df[var] = df[var].shift(periods=-lagg_value)
        
    df_processed = df.dropna()

    return df_processed
