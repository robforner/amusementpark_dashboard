# streamlit run "dashboard/Homepage.py"

import streamlit as st
from preprocessingdash import preprocessing, load_datasets

st.set_page_config(page_title="Homepage", page_icon="🏠")
# Import Datasets
attendance,link_attraction_park, entity_schedule, waiting_times, weather_data, pred_results_orig = load_datasets()

dataset, attractions_aw, attendance_aw, entity_sched_aw, pred_results = preprocessing(attendance,link_attraction_park, entity_schedule, waiting_times, weather_data, pred_results_orig)

st.markdown("""<style>
a:link {
  color: orange;
  background-color: transparent;
  text-decoration: none;
}

a:visited {
  color: orange;
  background-color: transparent;
  text-decoration: underline;
}
            
a:hover {
  color: orange;
  background-color: transparent;
  text-decoration: underline;
}

a:active {
  color: orange;
  background-color: transparent;
  text-decoration: underline;
}""", unsafe_allow_html=True)

st.sidebar.header('🏠 Homepage')
with st.sidebar:
    st.markdown("Select one of the pages above to start visualizing the data related to waiting times at :orange[PortAventura World]!")

st.markdown('<h1 style = "text-align:center">Data Visualization Tool <a href="https://www.portaventuraworld.com/en">PortAventura World</a></h1>', unsafe_allow_html=True)
st.markdown(' ')
st.markdown('<h3 style = "text-align:center">Group 11</h3>', unsafe_allow_html=True)
st.markdown(' ')
st.markdown(' ')
st.markdown(' ')

col1, col2, col3 = st.columns([0.2, 0.9, 0.2])
with col2:
    st.image('dashboard/images/home.png', use_column_width='always')





