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
# st.write(filtered_df)
names = entry_editor.iloc[:, -1]
is_included_dict = dict()
for cdx, comment_row in filtered_df.iterrows():
    comment = comment_row["경험 코멘트"]
    # for edx, entry_row in entry_editor.iterrows():
    for edx, entry_row in enumerate(all_members):
        if edx ==0:
            continue
        # name = entry_row['NAME']
        name = entry_row.split(" - ")[-1]
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
            # is_included_dict[cdx]["칭찬"] = []
            is_included_dict[cdx]["칭찬"] = ""
        is_included_dict[cdx].update(comment_row.to_dict())
                
        if is_included:
            # entry_row_dict["EDX"] = str(edx)
            # entry_row_dict.update(entry_row.to_dict())
            
            # is_included_dict[cdx]["칭찬"].append(entry_row_dict)
            # is_included_dict[cdx]["칭찬"].append(" \r ".join(list(entry_row_dict.values())))
            # is_included_dict[cdx]["칭찬"].append(entry_row + "\r")
            is_included_dict[cdx]["칭찬"] += f"{entry_row} / "
    try:
        if is_included_dict[cdx]["칭찬"][-3:] == " / ":
            is_included_dict[cdx]["칭찬"] = is_included_dict[cdx]["칭찬"][:-3]
    except:
        pass
# st.write(is_included_dict)


##### 표가 아니라 container, columns로 하나하나 출력하고 entry_datas를 muitiselect로 구성하고 세션키_n 으로 저장 한 후 세션에서 개수 체크해야할 듯
filtered_data = []
for key, value in is_included_dict.items():
    temp_dict = {k: v for k, v in value.items()}
    filtered_data.append(temp_dict)
print(is_included_dict)

df = pd.DataFrame(filtered_data)[["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트", "칭찬"]]
gb = GridOptionsBuilder.from_dataframe(df)

# gb.configure_column("경험 코멘트", 
#                     width=400, 
#                     minWidth=200, 
#                     maxWidth=800,
#                     # cellStyle={"white-space": "normal", "line-height": "1.5"},
#                     # autoHeight=True,  # 높이를 내용에 맞게 조정
#                     )
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
                    cellStyle={"white-space": "normal", "line-height": "1.5"},
                    autoHeight=True,  # 높이를 내용에 맞게 조정
                    ) 


grid_options = gb.build()

AgGrid(
    df,
    gridOptions=grid_options,
    theme="alpine",  # 테마
    enable_enterprise_modules=False,
    height=600,  # 테이블 높이 (픽셀)
    allow_unsafe_jscode=True,  # HTML 사용 허용
)

################################################################################################

# html_table = df.to_html(index=False, escape=False)

# # HTML 스타일 추가
# styled_html = f"""
# <style>
#     table {{
#         width: 80%;
#         border-collapse: collapse;
#     }}
#     th, td {{
#         border: 1px solid #ddd;
#         text-align: center;
#         padding: 8px;
#     }}
#     th {{
#         background-color: #f2f2f2;
#     }}
# </style>
# {html_table}
# """

# st.markdown(styled_html, unsafe_allow_html=True)
