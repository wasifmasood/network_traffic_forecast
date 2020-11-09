from workalendar.europe import Austria
import datetime
import codecs #to download and decode the information
import requests
import io
from dateutil.relativedelta import relativedelta
import pandas as pd
import datetime
import pytz
import numpy as np

def get_national_holidays(countary='Austria', year='2020'):
    cal = Austria()
    naitonal = pd.DataFrame(cal.holidays(year), columns =['ds', 'holiday']) 
    naitonal['lower_window'] = 0
    naitonal['upper_window'] = 1
    naitonal = naitonal[['holiday', 'ds', 'lower_window', 'upper_window']]
    return naitonal


def get_weather_hist(location='Vienna%2C%209%2C%20AT', start_date='2020-05-01', end_date=None, aggregate='24'):
    BaseURL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/'
    QueryKey = '&key=7AUK12563SY0CFLZYAJY10GSR'
    st_date = start_date
    searchfor = ['Snow', 'Rain']
    
    if end_date is None:
        end_date = (datetime.datetime.now() - relativedelta(days=3)).strftime("%Y-%m-%d")  
    QueryLocation = '&unitGroup=uk' + '&locations=' + location

    QueryDate = '&startDateTime=' + st_date + 'T00:00:00&endDateTime=' + end_date + 'T00:00:00' + '&contentType=csv'
    QueryTypeParams = 'history?goal=history&aggregateHours=' + aggregate + QueryDate 
    URL = BaseURL + QueryTypeParams + QueryLocation + QueryKey
    urlData = requests.get(URL).content
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))    
    #rawData['DateTime'] = pd.pandas.to_datetime(rawData['Date time'])
    rawData['DateTime'] = pd.pandas.to_datetime(rawData['Date time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    rawData['Pleasant'] = np.where(rawData.Temperature > 8, 1, 0)    
    rawData['Snow/Rain'] = np.where(rawData['Conditions'].str.contains('|'.join(searchfor)), 1, 0)
    return rawData[['DateTime', 'Temperature', 'Conditions', 'Pleasant', 'Snow/Rain']]


def is_weekend(ds):
    date = pd.to_datetime(ds)
    return (date.dayofweek < 5)


def convert_datetime_timezone(Date, tz1="Europe/London", tz2="Europe/Vienna"):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(Date,"%d/%m/%Y %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def get_matchdates():
    df_E0 = pd.read_csv('./data/matches/2019-2020/E0.csv')
    df_D1 = pd.read_csv('./data/matches/2019-2020/D1.csv')
    df_F1 = pd.read_csv('./data/matches/2019-2020/F1.csv')
    df_I1 = pd.read_csv('./data/matches/2019-2020/I1.csv')
    df_N1 = pd.read_csv('./data/matches/2019-2020/N1.csv')
    df_P1 = pd.read_csv('./data/matches/2019-2020/P1.csv')
    df_SP1 = pd.read_csv('./data/matches/2019-2020/SP1.csv')
    df_T1 = pd.read_csv('./data/matches/2019-2020/T1.csv')
    games_hist = pd.concat([df_E0, df_D1, df_F1, df_I1, df_N1, df_P1, df_SP1, df_T1])
    games_hist['Time'] = games_hist['Time'] + ':00'
    games_hist['DateTime'] = games_hist['Date'] + ' ' + games_hist['Time']
    games_hist = games_hist[['Date', 'Time', 'DateTime']]
    games_hist['DateTimeAdj'] = games_hist['DateTime'].apply(convert_datetime_timezone)
    games_hist['Date'] = pd.pandas.to_datetime(games_hist.Date)
    games_hist['DateTime'] = pd.pandas.to_datetime(games_hist.DateTime)
    games_hist = games_hist.sort_values(by='DateTime', ascending=True)
    games_hist = games_hist.drop_duplicates(subset=['DateTime'])
    return games_hist

