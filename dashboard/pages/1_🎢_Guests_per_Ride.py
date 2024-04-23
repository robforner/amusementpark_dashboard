import streamlit as st
import datetime
import pandas as pd
import altair as alt
from Homepage import dataset, attractions_aw, attendance_aw, entity_sched_aw

st.set_page_config(page_title="Guests per Ride", page_icon="🎢")

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

    out = out.groupby('DEB_TIME_HOUR')['GUEST_CARRIED'].mean().reset_index()

    return out

def guests_ride_day(date):
    out = dataset.loc[(dataset['WORK_DATE'] == str(date)) & 
                      (dataset['OPEN_TIME'] > 0)]
    
    out = out.groupby('ENTITY_DESCRIPTION_SHORT')['GUEST_CARRIED'].sum().reset_index()

    return out

def guests_ride_range(start_date, end_date):
    out = dataset.loc[(dataset['WORK_DATE'] >= str(start_date)) &
                      (dataset['WORK_DATE'] <= str(end_date)) & 
                      (dataset['OPEN_TIME'] > 0)]
    
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT', 'WORK_DATE'])['GUEST_CARRIED'].sum().reset_index()
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT'])['GUEST_CARRIED'].mean().reset_index()

    return out


st.markdown("# 🎢 Guests per Ride")
help = st.toggle('Help', value=True)
if help:
    st.markdown("Select visualization options from the sidebar on the left. If no options are visible visible please click on the arrow at the top left of the screen.")
st.sidebar.header("🎢 Guests per Ride")

#### Single Ride Guests ####
with st.sidebar:
    st.markdown("## Single Ride Guests")
    help = st.toggle('Info', key=7, value=True)
    if help:
        st.markdown("Visualize the number of guests who visited a specific ride in a single day or in a range of days.")
    ride = st.selectbox("Select a ride:", attlist)

    spec = st.checkbox('Specific Date', value=True)
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))

    range = st.checkbox('Date Range')
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2021, 7, 1), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))
        end_date = st.date_input('Select an end date', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))

if spec:
    st.divider()
    sel = select_ride_day(ride, date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(x = alt.X('DEB_TIME_HOUR:N').title('Time (hours)'))
    guests = chart.mark_bar(color='#e16e3d').encode(y = alt.Y('GUEST_CARRIED').title('Mean Number of Guests'))
    temp = chart.mark_line(color='yellow').encode(y = alt.Y('temp:Q').title('Temperature'))
    rain = chart.mark_circle(color='skyblue', size=100).encode(y = alt.Y('rain_1h:Q').title('Rainfall'))
    
    check_temp = st.checkbox('Overlay Temperature', value=True)
    check_rain = st.checkbox('Overlay Rain')
    if check_temp:
        chart = alt.layer(guests, temp).resolve_scale(y='independent')
    if check_rain:
        chart = alt.layer(guests, rain).resolve_scale(y='independent')
    if check_rain == False and check_temp == False: 
        chart = alt.layer(guests).resolve_scale(y='independent')
    if check_rain == True and check_temp == True: 
        chart = alt.layer(guests, temp, rain).resolve_scale(y='independent')
        
    st.markdown(f"<h4 style = 'text-align:center'> {ride} Guests on {date}</h4>", unsafe_allow_html=True) 
    st.altair_chart(chart, use_container_width=True)
    
if range:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> Mean {ride} Guests from {start_date} to {end_date}</h4>", unsafe_allow_html=True)
    sel = select_ride_range(ride, start_date, end_date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('DEB_TIME_HOUR:N').title('Time (hours)'), alt.Y('GUEST_CARRIED').title('Mean Number of Guests'))
    st.altair_chart(chart, use_container_width=True)


#### Mean Guests per Ride ####
with st.sidebar:
    st.markdown("## Mean Guests per Ride")
    help = st.toggle('Info', key=23, value=True)
    if help:
        st.markdown("Visualize the number of guests who visited each ride in a single day or in a range of days.")

    spec = st.checkbox('Specific Date', key=1, value=True)
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key= 1234)

    range = st.checkbox('Date Range', key=2)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2021, 7, 1), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key= 12474855)
        end_date = st.date_input('Select an end date', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26), key= 12345)

if spec:
    st.divider()
    st.markdown(f"<h4 style='text-align:center'> Guests per Ride on {date} </h4>", unsafe_allow_html=True) 

    sel = guests_ride_day(date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('ENTITY_DESCRIPTION_SHORT').title('Ride'), alt.Y('GUEST_CARRIED').title('Mean Number of Guests'))
    st.altair_chart(chart, use_container_width=True)

if range:
    st.divider()
    st.markdown(f"<h4 style='text-align:center'> Mean Guests per Ride from {start_date} to {end_date}</h4>", unsafe_allow_html=True)

    sel = guests_ride_range(start_date, end_date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('ENTITY_DESCRIPTION_SHORT').title('Ride'), alt.Y('GUEST_CARRIED').title('Mean Number of Guests'))
    st.altair_chart(chart, use_container_width=True)

