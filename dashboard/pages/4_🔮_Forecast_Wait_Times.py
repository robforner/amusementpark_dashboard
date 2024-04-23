import streamlit as st
import datetime
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from Homepage import dataset, attractions_aw, attendance_aw, entity_sched_aw, pred_results

st.set_page_config(page_title="Forecast Wait Times", page_icon="🔮")

attlist = attractions_aw['ATTRACTION'].values.tolist()

def select_ride_day(ride, date):
    out = pred_results.loc[(pred_results['ENTITY_DESCRIPTION_SHORT'] == str(ride)) & 
                                        (pred_results['WORK_DATE'] == date) & 
                                        (pred_results['OPEN_TIME'] > 0)].sort_values('DEB_TIME')

    return out

def select_ride_range(ride, start_date, end_date):
    out = pred_results.loc[(pred_results['ENTITY_DESCRIPTION_SHORT'] == str(ride)) & 
                                        (pred_results['WORK_DATE'] >= start_date) & 
                                        (pred_results['WORK_DATE'] <= end_date) & 
                                        (pred_results['OPEN_TIME'] > 0)].sort_values('DEB_TIME')
    
    out['TIME'] = out['DEB_TIME'].dt.time
    
    # PORCATA
    specified_date = pd.to_datetime('2023-01-01')
    out['time_string'] = out['TIME'].apply(lambda x: x.strftime('%H:%M:%S'))
    out['timedelta'] = pd.to_timedelta(out['time_string'])
    out['DATETIME'] = specified_date + out['timedelta']
    out.drop(columns=['timedelta'], inplace=True)
    # PORCATA

    out = out.groupby('DATETIME')[['prediction', 'WAIT_TIME_MAX']].mean().reset_index()

    return out

def guests_ride_day(date):
    out = pred_results.loc[(pred_results['WORK_DATE'] == date) & 
                      (pred_results['OPEN_TIME'] > 0)]
    
    out = out.groupby('ENTITY_DESCRIPTION_SHORT')[['WAIT_TIME_MAX', 'prediction']].mean().reset_index()

    return out


def guests_ride_range(start_date, end_date):
    out = pred_results.loc[(pred_results['WORK_DATE'] >= start_date) &
                      (pred_results['WORK_DATE'] <= end_date) & 
                      (pred_results['OPEN_TIME'] > 0)]
    
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT', 'WORK_DATE'])[['WAIT_TIME_MAX', 'prediction']].mean().reset_index() # Daily mean
    out = out.groupby(['ENTITY_DESCRIPTION_SHORT'])[['WAIT_TIME_MAX', 'prediction']].mean().reset_index()

    return out


st.markdown("# 🔮 Forecast Wait Times")
help = st.toggle('Help')
if help:
    st.markdown("Select visualization options from the sidebar on the left. If no options are visible visible please click on the arrow at the top left of the screen.")
st.sidebar.header("🔮 Forecast Wait Times")
st.markdown("<p style='text-align:center'><b>🟧 = Predicted Values <br> 🟩 = Actual Values </b></p>", unsafe_allow_html=True)

#### Single Ride Wait Times ####
with st.sidebar:
    st.markdown("## Single Ride Wait Times")
    help = st.toggle('Info', key=9954)
    if help:
        st.markdown("Visualize the forecasted wait time for a specific ride in a single day or in a range of days compared with the actual wait time.")
    ride = st.selectbox("Select a ride:", attlist)

    spec = st.checkbox('Specific Date')
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2022, 2, 2), min_value=datetime.date(2022, 2, 1), max_value=datetime.date(2022, 7, 26), key=3455)

    range = st.checkbox('Date Range', value=True)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2022, 2, 2), min_value=datetime.date(2022, 2, 2), max_value=datetime.date(2022, 7, 26))
        end_date = st.date_input('Select an end date', datetime.date(2022, 3, 2), min_value=datetime.date(2022, 2, 2), max_value=datetime.date(2022, 7, 26))

if spec:
    st.divider()
    sel = select_ride_day(ride, date)
    chart = alt.Chart(sel).encode(x = alt.X('DEB_TIME:T', axis=alt.Axis(format='%H:%M')).title('Time of day (hours)'))
    pred = chart.mark_line(color='#e16e3d').encode(y = alt.Y('prediction:Q').title('Predicted Wait Time'))
    act = chart.mark_line(color='green').encode(y = alt.Y('WAIT_TIME_MAX:Q').title('Actual Wait Time'))
    fig = (pred + act)
    st.markdown(f"<h4 style = 'text-align:center'> Forecasted vs. Predicted Wait Time for {ride} <br> {date} </h4>", unsafe_allow_html=True) 
    st.altair_chart(fig, use_container_width=True)

if range:
    st.divider()
    sel = select_ride_range(ride, start_date, end_date)
    chart = alt.Chart(sel).encode(x = alt.X('DATETIME:T', axis=alt.Axis(format='%H:%M')).title('Time of day (hours)'))
    pred = chart.mark_line(color='#e16e3d').encode(y = alt.Y('prediction:Q').title('Predicted Wait Time'))
    act = chart.mark_line(color='green').encode(y = alt.Y('WAIT_TIME_MAX:Q').title('Actual Wait Time'))
    fig = (pred + act)
    st.markdown(f"<h4 style = 'text-align:center'> Forecasted vs. Predicted Average Wait Time for {ride} <br> from {start_date} to {end_date} </h4>", unsafe_allow_html=True) 
    st.altair_chart(fig, use_container_width=True)


#### Mean Wait Times per Ride ####
with st.sidebar:
    st.markdown("## Wait Times per Ride")
    help = st.toggle('Info', key=5005)
    if help:
        st.markdown("Visualize the predicted average wait time for each ride in a single day or in a range of days compared with the actual average wait time.")

    spec = st.checkbox('Specific Date', key=1)
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2022, 2, 2), min_value=datetime.date(2022, 2, 1), max_value=datetime.date(2022, 7, 26))

    range = st.checkbox('Date Range', key=2, value=True)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2022, 2, 2), min_value=datetime.date(2022, 2, 1), max_value=datetime.date(2022, 7, 26))
        end_date = st.date_input('Select an end date', datetime.date(2022, 3, 2), min_value=datetime.date(2022, 2, 1), max_value=datetime.date(2022, 7, 26))

if spec:
    st.divider()

    sel = guests_ride_day(date)
    chart = alt.Chart(sel).encode(x = alt.X('ENTITY_DESCRIPTION_SHORT').title('Rides'))
    pred = chart.mark_circle(color='#e16e3d', size=100).encode(y = alt.Y('prediction:Q').title('Predicted Wait Time'))
    act = chart.mark_circle(color='green', size=100).encode(y = alt.Y('WAIT_TIME_MAX:Q').title('Actual Wait Time'))
    fig = (pred + act)
    st.markdown(f"<h4 style = 'text-align:center'> Forecasted vs. Predicted Average Wait Time <br> {date} </h4>", unsafe_allow_html=True) 
    st.altair_chart(fig, use_container_width=True)
if range:
    st.divider()

    sel = guests_ride_range(start_date, end_date)
    chart = alt.Chart(sel).encode(x = alt.X('ENTITY_DESCRIPTION_SHORT').title('Rides'))
    pred = chart.mark_circle(color='#e16e3d', size=100).encode(y = alt.Y('prediction:Q').title('Predicted Wait Time'))
    act = chart.mark_circle(color='green', size=100).encode(y = alt.Y('WAIT_TIME_MAX:Q').title('Actual Wait Time'))
    fig = (pred + act)
    st.markdown(f"<h4 style = 'text-align:center'> Forecasted vs. Predicted Average Wait Time <br> from {start_date} to {end_date}</h4>", unsafe_allow_html=True) 
    st.altair_chart(fig, use_container_width=True)
