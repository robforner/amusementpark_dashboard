import streamlit as st
import datetime
import pandas as pd
from Homepage import dataset, attractions_aw, attendance_aw, entity_sched_aw
import altair as alt

st.set_page_config(page_title="Past Wait Times", page_icon="⏪️")

attlist = attractions_aw['ATTRACTION'].values.tolist()

def select_ride_day(ride, date):
    out = dataset.loc[(dataset['ENTITY_DESCRIPTION_SHORT'] == str(ride)) & 
                                        (dataset['WORK_DATE'] == str(date)) & 
                                        (dataset['OPEN_TIME'] > 0)].sort_values('DEB_TIME')

    return out

def select_ride_range(ride, start_date, end_date):
    out = dataset.loc[(dataset['ENTITY_DESCRIPTION_SHORT'] == str(ride)) & 
                                        (dataset['WORK_DATE'] >= str(start_date)) & 
                                        (dataset['WORK_DATE'] <= str(end_date)) & 
                                        (dataset['OPEN_TIME'] > 0)].sort_values('DEB_TIME')
    
    out['TIME'] = out['DEB_TIME'].dt.time
    
    # PORCATA
    specified_date = pd.to_datetime('2023-01-01')
    out['time_string'] = out['TIME'].apply(lambda x: x.strftime('%H:%M:%S'))
    out['timedelta'] = pd.to_timedelta(out['time_string'])
    out['DATETIME'] = specified_date + out['timedelta']
    out.drop(columns=['timedelta'], inplace=True)
    # PORCATA

    out = out.groupby('DATETIME')['WAIT_TIME_MAX'].mean().reset_index()

    return out

def guests_ride_day(date):
    out = dataset.loc[(dataset['WORK_DATE'] == str(date)) & 
                      (dataset['OPEN_TIME'] > 0)]
    
    out = out.groupby('ENTITY_DESCRIPTION_SHORT')['WAIT_TIME_MAX'].mean().reset_index()

    return out

def guests_ride_range(start_date, end_date):
    out = dataset.loc[(dataset['WORK_DATE'] >= str(start_date)) &
                      (dataset['WORK_DATE'] <= str(end_date)) & 
                      (dataset['OPEN_TIME'] > 0)]
    
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT', 'WORK_DATE'])['WAIT_TIME_MAX'].mean().reset_index() # Daily mean
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT'])['WAIT_TIME_MAX'].mean().reset_index()

    return out


st.markdown("# ⏪️ Past Wait Times")
help = st.toggle('Help')
if help:
    st.markdown("Select visualization options from the sidebar on the left. If no options are visible visible please click on the arrow at the top left of the screen.")
st.sidebar.header("⏪️ Past Wait Times")

#### Single Ride Wait Times ####
with st.sidebar:
    st.markdown("## Single Ride Wait Times")
    help = st.toggle('Info', key=1)
    if help:
        st.markdown("Visualize the wait time specific ride in a single day or in a range of days.")
    ride = st.selectbox("Select a ride:", attlist)

    spec = st.checkbox('Specific Date')
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=86594)

    range = st.checkbox('Date Range', value=True)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2021, 7, 1), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=58493)
        end_date = st.date_input('Select an end date', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=78549)

if spec:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> {ride} Wait Times on {date} </h4>", unsafe_allow_html=True) 
    sel = select_ride_day(ride, date)
    chart = alt.Chart(sel).mark_line(color='#e16e3d').encode(alt.X('DEB_TIME:T', axis=alt.Axis(format='%H:%M')).title('Time'), alt.Y('WAIT_TIME_MAX').title('Wait Time'))
    st.altair_chart(chart, use_container_width=True)

if range:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> Average {ride} Wait Times <br> from {start_date} to {end_date} </h4>", unsafe_allow_html=True) 
    sel = select_ride_range(ride, start_date, end_date)
    chart = alt.Chart(sel).mark_line(color='#e16e3d').encode(alt.X('DATETIME:T', axis=alt.Axis(format='%H:%M')).title('Time'), alt.Y('WAIT_TIME_MAX').title('Wait Time'))
    st.altair_chart(chart, use_container_width=True)


#### Mean Wait Times per Ride ####
with st.sidebar:
    st.markdown("## Wait Times per Ride")
    help = st.toggle('Info', key=2)
    if help:
        st.markdown("Visualize the average wait time for each ride in a single day or in a range of days.")

    spec = st.checkbox('Specific Date', key=5)
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=4323)

    range = st.checkbox('Date Range', key=7, value=True)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2021, 7, 1), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=432)
        end_date = st.date_input('Select an end date', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key=76543)

if spec:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> Average Wait Time per Ride <br> {date} </h4>", unsafe_allow_html=True) 

    sel = guests_ride_day(date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('ENTITY_DESCRIPTION_SHORT:N').title('Rides'), alt.Y('WAIT_TIME_MAX').title('Average Wait Time'))
    st.altair_chart(chart, use_container_width=True)

if range:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> Average Wait Time per Ride <br> from {start_date} to {end_date} </h4>", unsafe_allow_html=True) 

    sel = guests_ride_range(start_date, end_date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('ENTITY_DESCRIPTION_SHORT:N').title('Rides'), alt.Y('WAIT_TIME_MAX').title('Average Wait Time'))
    st.altair_chart(chart, use_container_width=True)
