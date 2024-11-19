import streamlit as st
import pandas as pd
import re

st.write("현히 안녕~")


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
