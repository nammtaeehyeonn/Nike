import streamlit as st
import pandas as pd
# from googletrans import Translator

# # Translator 객체 생성
# translator = Translator()

# # 영어 문자열
# english_text = "Young lim"

# # 영어를 한글로 번역
# translated = translator.translate(english_text, src='en', dest='ko')

# # 결과 출력
# print("Original:", english_text)
# print("Translated:", translated.text)
import re

st.header("악덕사장 지현히씨🐷를 위한 재능기부")
st.divider()

if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
# if 'entryCheckExpanded' not in st.session_state:
#     st.session_state['entryCheckExpanded'] = True
# if 'fileUploadExpanded' not in st.session_state:
#     st.session_state['fileUploadExpanded'] = True

# Expander for 명단확인
with st.expander("1️⃣ **명단확인**", expanded=True):
    st.divider()
    entry = pd.read_excel("./entry.xlsx", engine='openpyxl')
    entry_editor = st.data_editor(entry)
    submitted = st.button("명단 확정")
    if submitted:
        entry_editor.to_excel('./entry2.xlsx', index=False)
        st.session_state['submitted'] = True
        # st.session_state['entryCheckExpanded'] = False
        st.rerun()

if st.session_state['submitted']:
    with st.expander("2️⃣ **파일 업로드**", expanded=True):
        uploaded_file = st.file_uploader(" ")
        if uploaded_file is not None:
            uploaded_df = pd.read_csv(uploaded_file)
            filtered_df = \
                uploaded_df[uploaded_df["경험 코멘트"].notna()].loc[:, ["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트"]]
            filtered_df[["등록 번호", "거래 번호"]] = filtered_df[["등록 번호", "거래 번호"]].astype(int)
            filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]] = \
                filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]].astype(str)
            
            st.write(filtered_df)
            names = entry_editor.iloc[:, -1]
            is_included_dict = dict()
            for cdx, comment_row in filtered_df.iterrows():
                comment = comment_row["경험 코멘트"]
                for edx, entry_row in entry_editor.iterrows():
                    name = entry_row['NAME']
                    entry_row_dict = dict()
                    is_included = False
                    if not (len(name) < 3):
                        if (name in comment) or (name[-2:] in comment):
                            is_included = True
                            # st.write(f"{cdx} : {comment_row.to_dict()} -> {edx} : {entry_row.to_dict()}")
                    else:
                        if (name in comment):
                            is_included = True
                            # st.write(f"{cdx} : {comment_row.to_dict()} -> {edx} : {entry_row.to_dict()}")
                            
                    if cdx not in is_included_dict:
                        is_included_dict[cdx] = {}
                    if "entry_datas" not in is_included_dict[cdx]:
                        is_included_dict[cdx]["entry_datas"] = []
                    is_included_dict[cdx].update(comment_row.to_dict())
                            
                    if is_included:
                        entry_row_dict["EDX"] = edx
                        entry_row_dict.update(entry_row.to_dict())
                        
                        is_included_dict[cdx]["entry_datas"].append(entry_row_dict)

            st.write(is_included_dict)
            
            filtered_data = []
            for key, value in is_included_dict.items():
                temp_dict = {k: v for k, v in value.items() if k != "entry_datas"}
                filtered_data.append(temp_dict)

            # Pandas 데이터프레임으로 변환
            df = pd.DataFrame(filtered_data)
            st.dataframe(df)
            



##################################################################################################
# st.session_state['submitted'] = False
# st.session_state['entryCheckExpanded'] = True
# st.session_state['fileUploadExpanded'] = True