import streamlit as st
import pandas as pd
import cv2
import pytesseract
import re

st.write("현히 안녕~")

jobs_config = ('-l eng --oem 3 --psm 6')
name_config = ('-l kor --oem 3 --psm 6')

image = cv2.imread("./image/KakaoTalk_20241119_200405350.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

j_x, j_y, j_w, j_h = 239, 247, 348, 1737
n_x, n_y, n_w, n_h = 372, 247, 422, 1737

# 이미지 자르기
jobs_cropped_image = gray[j_y:j_h, j_x:j_w]
name_cropped_image = gray[n_y:n_h, n_x:n_w]

jobs_text = pytesseract.image_to_string(jobs_cropped_image, config=jobs_config)
name_text = pytesseract.image_to_string(name_cropped_image, config=name_config)

cleaned_jobs_text = re.sub(r"[^\w\s가-힣]", "", jobs_text)
cleaned_jobs_text = re.sub(r'\bHEAD COACH\b', 'HEADCOACH', cleaned_jobs_text)
final_jobs = cleaned_jobs_text.replace('\n\x0c', '').replace('\n', ' ').split(' ')
cleaned_name_text = re.sub(r"[^\w\s가-힣]", "", name_text)
final_name = cleaned_name_text.replace('\n\x0c', '').replace('\n', ' ').split(' ')

# st.image(jobs_cropped_image)
st.write(final_jobs)
print(len(final_jobs))
# st.image(name_cropped_image)
st.write(final_name)
print(len(final_name))



uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
