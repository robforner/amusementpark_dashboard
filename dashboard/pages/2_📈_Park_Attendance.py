import streamlit as st
import datetime
import pandas as pd
from Homepage import dataset, attractions_aw, attendance_aw, entity_sched_aw
import calendar
import altair as alt

st.set_page_config(page_title="Park Attendance", page_icon="📈")

def att_day(date):
    out = attendance_aw.loc[(attendance_aw['WORK_DATE'] == str(date))].reset_index(drop=True)
    number = out.at[0, 'ATTENDANCE']
    w_cond = dataset.loc[(dataset['WORK_DATE'] == str(date))].reset_index(drop=True).at[0, 'weather_description']
    min_temp = dataset.loc[(dataset['WORK_DATE'] == str(date))].reset_index(drop=True).at[0, 'temp_min']
    max_temp = dataset.loc[(dataset['WORK_DATE'] == str(date))].reset_index(drop=True).at[0, 'temp_max']
    
    return number, w_cond, max_temp, min_temp

def att_range(start_date, end_date):
    out = attendance_aw.loc[(attendance_aw['WORK_DATE'] >= str(start_date)) & 
                      (attendance_aw['WORK_DATE'] <= str(end_date))].reset_index(drop=True)

    return out



st.markdown("# 📈 Park Attendance")
help = st.toggle('Help')
if help:
    st.markdown("Select visualization options from the sidebar on the left. If no options are visible visible please click on the arrow at the top left of the screen.")

st.sidebar.header("📈 Park Attendance")
with st.sidebar:
    help = st.toggle('Info', key=2)
    if help:
        text = st.markdown("Visualize the attendance of PortAventura World for single day or for a range of days.")
    
    spec = st.checkbox('Specific Date', value=True)
    if spec:
        date = st.date_input('Select a date to look into', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))
    
    range = st.checkbox('Date Range', value=True)
    if range:
        start_date = st.date_input('Select a start date', datetime.date(2021, 7, 1), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))
        end_date = st.date_input('Select an end date', datetime.date(2021, 7, 26), min_value=datetime.date(2018, 6, 1), max_value=datetime.date(2022, 7, 26))
        show_table = st.checkbox('Show Table')


if spec:
    st.divider()
    number, w_cond, max_temp, min_temp = att_day(date)
    st.markdown(f"### Attendance on {date.day} {calendar.month_name[date.month]} {date.year} was :green[{number}] people.")
    st.markdown(f"Weather conditions: :orange[{w_cond}]")
    st.markdown(f":blue[Minimum temperature registered: :blue[{min_temp}]]")
    st.markdown(f":red[Maximum temperature registered: :red[{max_temp}]]")

if range:
    st.divider()
    st.markdown(f"<h4 style = 'text-align:center'> Park Attendance Graph <br> from {start_date} to {end_date}</h4>", unsafe_allow_html=True)

    sel = att_range(start_date, end_date)
    chart = alt.Chart(sel).mark_bar(color='#e16e3d').encode(alt.X('WORK_DATE:N').title('Date'), alt.Y('ATTENDANCE').title('Attendance'))
    st.altair_chart(chart, use_container_width=True)

    if show_table:
        st.divider()
        st.markdown(f"<h4 style = 'text-align:center'> Park Attendance Table <br> from {start_date} to {end_date}</h4>", unsafe_allow_html=True)
        st.dataframe(sel[['WORK_DATE', 'ATTENDANCE']], use_container_width=True, hide_index=True)