import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import re

def find_duplicates(lst):
    counts = Counter(lst)
    return [item for item, count in counts.items() if count > 1]

st.set_page_config(
    page_title="옥히나이키",
    page_icon="🚩",
    layout="wide"
)

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
        st.divider()
        uploaded_file = st.file_uploader(" ")
        if uploaded_file is not None:
            st.write(" ")
            st.write(" ")
            uploaded_df = pd.read_csv(uploaded_file)
            filtered_df = \
                uploaded_df[uploaded_df["경험 코멘트"].notna()].loc[:, ["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트"]]
            filtered_df[["등록 번호", "거래 번호"]] = filtered_df[["등록 번호", "거래 번호"]].astype(int)
            filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]] = \
                filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]].astype(str)
            
            filtered_df = filtered_df.sort_values(["거래 번호"])
            # st.write(filtered_df)
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
                    if "칭찬" not in is_included_dict[cdx]:
                        is_included_dict[cdx]["칭찬"] = []
                    is_included_dict[cdx].update(comment_row.to_dict())
                            
                    if is_included:
                        entry_row_dict["EDX"] = str(edx)
                        entry_row_dict.update(entry_row.to_dict())
                        
                        # is_included_dict[cdx]["칭찬"].append(entry_row_dict)
                        is_included_dict[cdx]["칭찬"].append("/".join(list(entry_row_dict.values())))

            # st.write(is_included_dict)
            
            ##### 표가 아니라 container, columns로 하나하나 출력하고 entry_datas를 muitiselect로 구성하고 세션키_n 으로 저장 한 후 세션에서 개수 체크해야할 듯
            filtered_data = []
            for key, value in is_included_dict.items():
                temp_dict = {k: v for k, v in value.items()}
                filtered_data.append(temp_dict)

            # Pandas 데이터프레임으로 변환
            df = pd.DataFrame(filtered_data)[["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트", "칭찬"]]
            # df["칭찬"] = df["칭찬"].astype(str)
            
            duplicated_transaction_nums = find_duplicates(df["거래 번호"])
            # df.loc[df[len(df["칭찬"]) == 0], "칭찬"] = np.nan
            df.loc[df["거래 번호"].isin(duplicated_transaction_nums), "칭찬"] = "거래 번호 중복"
            
              
            
            
            df_col, _, _ = st.columns([0.7, 0.2, 0.1])
            with df_col:
                st.data_editor(df, use_container_width=True)
                



                
                
                
            # with vision_col:
            #     rows = [st.columns(7) for i in range(len(df))]
            #     for rdx, row in enumerate(rows):
            #         for cdx, col in enumerate(row):
            #             tile = col.container(border=True)
            #             tile.write(df.iloc[rdx, cdx])



##################################################################################################
# st.session_state['submitted'] = False
# st.session_state['entryCheckExpanded'] = True
# st.session_state['fileUploadExpanded'] = True
# 예제 데이터프레임 생성
# data = {
#     "Column 1": ["A", "B", "C", "D", "E", "F", "G", "H"],
#     "Column 2": [1, 2, 3, 4, 5, 6, 7, 8],
#     "Column 3": ["X", "Y", "Z", "W", "V", "U", "T", "S"],
#     "Column 4": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"],
#     "Column 5": [True, False, True, False, True, False, True, False],
#     "Column 6": ["😀", "😎", "🎉", "🔥", "💡", "💻", "📚", "🌟"],
# }
# df = pd.DataFrame(data)

# st.dataframe(df)

