import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
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


all_members = [""] + [f"[{idx+1}] " + " - ".join(map(str, row)) for idx, row in entry_editor.iterrows()]

# if st.session_state['submitted']:
#     with st.expander("2️⃣ **파일 업로드**", expanded=True):
#         st.divider()
#         uploaded_file = st.file_uploader(" ")
#         if uploaded_file is not None:
st.write(" ")
st.write(" ")
# uploaded_df = pd.read_csv(uploaded_file)
uploaded_df = pd.read_csv("./설문조사 세부 정보 - 2023년 신규 설문조사 (2).csv")
filtered_df = \
    uploaded_df[uploaded_df["경험 코멘트"].notna()].loc[:, ["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트"]]
filtered_df[["등록 번호", "거래 번호"]] = filtered_df[["등록 번호", "거래 번호"]].astype(int)
filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]] = \
    filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]].astype(str)

filtered_df = filtered_df.sort_values(["거래 번호"])
for_df_dict = dict()
for col in filtered_df.columns:
    for_df_dict[col] = list(filtered_df[col].values)

for_df_dict['칭찬'] = [[] for i in range(len(filtered_df))]
dup_nums = find_duplicates(for_df_dict['거래 번호'])

for idx, (num, comment) in enumerate(zip(for_df_dict['거래 번호'], for_df_dict['경험 코멘트'])):
    is_included_list = []
    if num in dup_nums:
        is_included_list.append("거래번호 중복")
    else:
        for edx, entry_row in entry_editor.iterrows():
            member_data = f"[{edx}] " + " - ".join(entry_row.values)
            name = entry_row['NAME']
            if not (len(name) < 3):
                if (name in comment) or (name[-2:] in comment):
                    is_included_list.append(member_data)
            else:
                if (name in comment):
                    is_included_list.append(member_data)
    for_df_dict['칭찬'][idx] = is_included_list
            
data = pd.DataFrame(for_df_dict)
data['칭찬'] = data['칭찬'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else x)

gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_grid_options(
    autoSizeStrategy={
        "type": "fitGridWidth",  # 그리드 너비에 맞추는 전략
        "defaultMinWidth": 100,  # 기본 최소 너비
        "columnLimits": [
            {"colId": "조사 실행 날짜", "minWidth": 80, "maxWidth": 150},
            {"colId": "서비스 일자", "minWidth": 80, "maxWidth": 150},
            {"colId": "방문 시간", "minWidth": 80, "maxWidth": 150},
            {"colId": "등록 번호", "minWidth": 80, "maxWidth": 150},
            {"colId": "거래 번호", "minWidth": 80, "maxWidth": 150},
            {"colId": "경험 코멘트", "minWidth": 300},
            {"colId": "칭찬", "Width": 200}
        ]
    }
)
gb.configure_default_column(
    filterable=False,  # 필터 비활성화
    sorteable =False,
    cellStyle={'textAlign': 'center'},  # 셀 내용 중앙 정렬
    headerStyle={'textAlign': 'center'},  # 헤더 내용 중앙 정렬
    
    autoSizeColumns=True
)
gb.configure_column(
    "경험 코멘트",
    cellStyle={"white-space": "normal", "line-height": "1.5"},
    autoHeight=True,  # 높이를 내용에 맞게 조정
)
gb.configure_column("칭찬", 
                    editable=True, 
                    cellEditor='agSelectCellEditor', 
                    cellEditorParams={'values': all_members },
                    cellStyle={"white-space": "pre-wrap", "line-height": "1.5"},
                    autoHeight=True,  # 높이를 내용에 맞게 조정
                    ) 


grid_options = gb.build()

ag_data = AgGrid(
    data,
    gridOptions=grid_options,
    theme="alpine",  # 테마
    enable_enterprise_modules=False,
    height=600,  # 테이블 높이 (픽셀)
    allow_unsafe_jscode=True,  # HTML 사용 허용
)

modified_data = ag_data["data"]
# st.dataframe(modified_data, width=1500)

print(pd.DataFrame(modified_data))

modified_df = pd.DataFrame(modified_data)
confirm_btn = st.button("확정")
st_stop = False
if confirm_btn:
    for rdx, row in modified_df.iterrows():
        count_brackets = sum(s.count("[") for s in row['칭찬'])
        if count_brackets > 1:
            st_stop=True
            st.warning(f"{rdx}번 째 행의 칭찬글이 2개 이상이에요.")
    if st_stop:
        st.stop()
    else:
        st.success("GOOD!!!")
        
