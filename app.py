import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from collections import Counter
from datetime import datetime
import re

def find_duplicates(lst):
    counts = Counter(lst)
    return [item for item, count in counts.items() if count > 1]

st.set_page_config(
    page_title="옥히나이키",
    page_icon="🚩",
    layout="wide"
)

st.header("나이키 칭찬글 선별 프로그램")
st.divider()

if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'confirmed' not in st.session_state:
    st.session_state['confirmed'] = False
if 'alert_txt' not in st.session_state:
    st.session_state['alert_txt'] = ""
    
with st.expander("1️⃣ **명단확인**", expanded=True):
    st.divider()
    entry = pd.read_excel("./entry.xlsx", engine='openpyxl')
    entry.index = range(1, len(entry) + 1)
    col1, col2 = st.columns([0.6,0.4], gap='large', vertical_alignment='bottom')
    with col1:
        entry_editor = st.data_editor(entry, use_container_width=True)
    submitted = st.button("명단 확정")
    if submitted:
        entry_editor.to_excel('./entry.xlsx', index=False)
        st.session_state['submitted'] = True
        st.rerun()


all_members = [""] + [f"[{idx}] " + " - ".join(map(str, row)) for idx, row in entry_editor.iterrows()]

if st.session_state['submitted']:
    with st.expander("2️⃣ **파일 업로드 및 정성평가**", expanded=True):
        st.divider()
        uploaded_file = st.file_uploader(" ")
        if uploaded_file is not None:
            filename = uploaded_file.name
            today_date_yymmdd = datetime.now().strftime("%y%m%d")

            st.write(" ")
            with st.popover("도움말"):
                st.write("(1) 거래번호가 중복되는 칭찬글들은 붉은색으로 칠해지며 최종 집계에서 제외됩니다.")
                st.write("(2) 하나의 칭찬글에 2명 이상일 경우 회색바탕으로 칠해져있습니다.")
                st.write("&nbsp;&nbsp;&nbsp;&nbsp;(2-1) 하나의 칭찬글에는 한명의 데이터만 삽입되어야 최종 결과를 확인할 수 있습니다.")
                st.write("(3) 언급된 이름이 없을 경우에는 공백입니다.")
                st.write("(4) 최종 집계시에는 [거래번호중복], [공백]은 제외됩니다.")
            st.write(" ")
            
            uploaded_df = pd.read_csv(uploaded_file)

            filtered_df = uploaded_df[uploaded_df["경험 코멘트"].notna()].loc[:, ["조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트"]]
            filtered_df[["등록 번호", "거래 번호"]] = filtered_df[["등록 번호", "거래 번호"]].astype(int)
            filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]] = \
                filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]].astype(str)
            filtered_df = filtered_df.sort_values(["거래 번호"])
            filtered_df["번호"] = [i+1 for i in range(len(filtered_df))]
            filtered_df = filtered_df[["번호", "조사 실행 날짜", "서비스 일자", "방문 시간", "등록 번호", "거래 번호", "경험 코멘트"]]

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
                        {"colId": "번호", "minWidth": 60, "maxWidth": 100},
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
            cellstyle_jscode = JsCode("""
            function(params) {
                const baseStyle = {
                    'white-space': 'pre-wrap',
                    'line-height': '1.5'
                };
                if ((params.value.match(/\[/g) || []).length >= 2) {
                    baseStyle['backgroundColor'] = 'gray';
                    baseStyle['color'] = 'black';
                }
                if (params.value == "거래번호 중복"){
                    baseStyle['color'] = 'red';
                }
                return baseStyle;
            }
            """)
            gb.configure_column("칭찬", 
                                editable=True, 
                                cellEditor='agSelectCellEditor', 
                                cellEditorParams={'values': all_members },
                                cellStyle=cellstyle_jscode,
                                autoHeight=True,  # 높이를 내용에 맞게 조정
                                ) 


            grid_options = gb.build()

            ag_data = AgGrid(
                data,
                gridOptions=grid_options,
                theme="alpine",  # 테마
                enable_enterprise_modules=False,
                height=500,  # 테이블 높이 (픽셀)
                allow_unsafe_jscode=True,  # HTML 사용 허용
            )

            modified_data = ag_data["data"]

            modified_df = pd.DataFrame(modified_data)

            st.session_state["alert_bool"] = False
            for rdx, row in modified_df.iterrows():
                count_brackets = sum(s.count("[") for s in row['칭찬'])
                if count_brackets > 1:
                    st.session_state["alert_bool"] = True
                        
                    
            if not st.session_state["alert_bool"]:
                confirm_btn = st.button("확정")
                if confirm_btn:
                    st.session_state['confirmed'] = True
                    
    
if st.session_state['confirmed']:
    with st.expander("3️⃣ **최종결과 확인**", expanded=True):
        filtered_series = modified_df['칭찬'][(modified_df['칭찬'] != "거래번호 중복") & (modified_df['칭찬'] != "")]
        count_df = filtered_series.value_counts().reset_index()
        numbers = count_df["칭찬"].apply(lambda x: int(re.search(r"\[(\d+)\]", x).group(1)))
        counts = count_df["count"].tolist()
        final_entry = entry_editor.loc[numbers.tolist(), :]
        final_entry['칭찬'] = counts
        col1, col2 = st.columns([0.6,0.4], gap='large', vertical_alignment='bottom')
        with col1:
            st.dataframe(final_entry, use_container_width=True)
            
        with col2:
            def convert_df(df):
                return df.to_csv(index=False).encode("utf-8")

            csv = convert_df(final_entry)
            st.download_button(
                type="primary",
                label="최종결과 다운로드",
                data=csv,
                file_name=f"{today_date_yymmdd}_{filename}.csv",
                mime="text/csv",
            )