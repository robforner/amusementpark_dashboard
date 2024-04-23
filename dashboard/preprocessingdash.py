import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

@st.cache_data 
def load_datasets():
    attendance = pd.read_csv('data/attendance.csv')
    link_attraction_park = pd.read_csv('data/link_attraction_park.csv', sep=';')
    entity_schedule = pd.read_csv('data/entity_schedule.csv')
    waiting_times = pd.read_csv('data/waiting_times.csv')
    weather_data = pd.read_csv('data/weather_data.csv')
    pred_results = pd.read_csv('data/prediction_result_6months.csv')
    return attendance,link_attraction_park, entity_schedule, waiting_times, weather_data, pred_results

@st.cache_data 
def preprocessing(attendance, link_attraction_park, entity_schedule, waiting_times, weather_data, pred_results):
    
    # Removing attendance data related to Tivoli Gardens and dropping negative values, since they have been classified as mis-inputs
    attendance_aw = attendance.drop(attendance[attendance['FACILITY_NAME'] == 'Tivoli Gardens'].index).reset_index(drop=True)
    attendance_aw = attendance_aw[attendance_aw['attendance'] >= 0]
    attendance_aw.sort_values('USAGE_DATE', inplace=True)
    attendance_aw.rename(columns={'attendance':'ATTENDANCE', 'USAGE_DATE':'WORK_DATE'}, inplace=True)

    # Removing Tivoli Garden Attractions
    attractions_aw = link_attraction_park.drop(link_attraction_park[link_attraction_park['PARK'] == 'Tivoli Gardens'].index).reset_index(drop=True)

    # Removing Tivoli Gardens entity schedules along with its attractions
    entity_sched_aw = entity_schedule.drop(entity_schedule[entity_schedule['ENTITY_DESCRIPTION_SHORT'] == 'Tivoli Gardens'].index)
    entity_sched_aw = entity_sched_aw[entity_schedule['ENTITY_DESCRIPTION_SHORT'].isin(attractions_aw['ATTRACTION'])].reset_index(drop=True)

    # Removing Tivoli Gardens attractions from waiting_times
    waiting_times_aw = waiting_times[waiting_times['ENTITY_DESCRIPTION_SHORT'].isin(attractions_aw['ATTRACTION'])].reset_index(drop=True)
    waiting_times_aw['DEB_TIME'] = pd.to_datetime(waiting_times_aw['DEB_TIME'])

    # Selecting Appropriate Weather Data (from start of available park data)
    cols_todrop = ['timezone', 'city_name', 'lat', 'lon', 'weather_icon', 'dt', 'visibility', 'sea_level', 'grnd_level', 'snow_3h']
    weather_data['dt_iso'] = weather_data['dt_iso'].str.replace('+0000 UTC', '', regex=False)
    weather_data['dt_iso'] = pd.to_datetime(weather_data['dt_iso'])
    weather_data_aw = weather_data.drop(weather_data[weather_data['dt_iso'] < '2018-06-01'].index).drop(columns=cols_todrop).reset_index(drop=True)

    # simulated weather conditions every 15 minutes to have data for each collection
    weather_data_aw = weather_data_aw.loc[weather_data_aw.index.repeat(4)].reset_index(drop=True)
    if 'dt_iso' in weather_data_aw.columns:
        weather_data_aw['dt_iso'] += pd.to_timedelta((weather_data_aw.groupby('dt_iso').cumcount() * 15), unit='min')
    weather_data_aw = weather_data_aw.rename(columns={'dt_iso':'DEB_TIME'})

    # Merging waiting_times_aw and weather_data_aw
    waitweather = pd.merge(waiting_times_aw, weather_data_aw, on='DEB_TIME', how='inner')

    # Since we want to base ourselves on normal operations we just select days where no fermetures happened
    fermeture_days = entity_sched_aw[entity_sched_aw['REF_CLOSING_DESCRIPTION'].notnull()].reset_index(drop=True)
    fermeture_days = fermeture_days.drop(columns=['ENTITY_TYPE', 'DEB_TIME', 'FIN_TIME', 'UPDATE_TIME'])

    # Since our objective is to predict wait times in normal conditions, we remove wait times for rides with fermetures
    merged_df = pd.merge(waitweather, fermeture_days[['ENTITY_DESCRIPTION_SHORT', 'WORK_DATE']], on=['ENTITY_DESCRIPTION_SHORT', 'WORK_DATE'], how='left', indicator=True)
    waitweather_noferm = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])

    # Merging attendance data to the dataset to obtain our final dataset
    dataset = pd.merge(waitweather_noferm, attendance_aw[['WORK_DATE', 'ATTENDANCE']], on=['WORK_DATE'], how='left')

    # Handling null values in weather putting 0 into nan, as nan is in place of a zero quantity (e.g., rain millimeters if it's sunny)
    w_nullcols = ['wind_gust', 'rain_1h', 'rain_3h', 'snow_1h']
    dataset[w_nullcols] = dataset[w_nullcols].fillna(0)

    # Dropping other null values in attendance
    dataset.dropna(inplace=True)

    # Preprocessing pred_results
    pred_results.drop(columns='Unnamed: 0', inplace=True)
    pred_results['DEB_TIME'] = pd.to_datetime(pred_results['DEB_TIME'])
    pred_results['WORK_DATE'] = pred_results['DEB_TIME'].dt.date
    pred_results = pd.merge(pred_results, dataset[['ENTITY_DESCRIPTION_SHORT', 'DEB_TIME', 'OPEN_TIME']], on=['ENTITY_DESCRIPTION_SHORT', 'DEB_TIME'], how='left')


    return dataset, attractions_aw, attendance_aw, entity_sched_aw, pred_results
