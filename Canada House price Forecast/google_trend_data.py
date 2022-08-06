import pandas as pd

from pytrends.request import TrendReq
pytrend = TrendReq()

from sklearn.decomposition import PCA
import statistics as stat
import numpy as np
import math
import time
import matplotlib.pyplot as plt
import random


#Collecting Google Search trend Data
class search_data_collect:

    def __init__(self, word_search, location):
        self.word_search = word_search
        self.location = location


    def extract_data(self):
        
        word_search = self.word_search
        geo_code_province = self.location

        #Creating an empty data frame to add search data
        df_search_main = pd.DataFrame()    
        row_length, col_length = df_search_main.shape 

        for geo_code_index in geo_code_province:
            
            #If the user have list of their own word search 
            #otherwise it uses the google search recomendation
            if isinstance(word_search, list) == True:
                search_queries = word_search

            else:
                #The initial word search
                pytrend.build_payload(kw_list=[word_search], timeframe='all', geo=geo_code_index)
                search_queries = pytrend.related_queries()[word_search]['top']['query'] #this gets the related serch words

                #the data for the initial search
                over_time_search = pytrend.interest_over_time()

                #Inserting data into dataframe
                df_search_main.insert(col_length, (geo_code_index +'_'+ word_search), over_time_search[word_search], True)
                row_length, col_length = df_search_main.shape
            

            #Loops through the search words
            for rel_query in search_queries:

                pytrend.build_payload(kw_list=[rel_query], timeframe='all', geo=geo_code_index)
                rel_query_over_time_search = pytrend.interest_over_time()

                #Inserting data into dataframe 
                df_search_main.insert(col_length, (geo_code_index +'_'+ rel_query), rel_query_over_time_search[rel_query], True)
                row_length, col_length = df_search_main.shape
                
                #Setting timer other wise google trend breaks
                #time.sleep(random.randrange(0, 10))#Adding random number because google trned no longer allows mass downloads


        return df_search_main[:], search_queries 