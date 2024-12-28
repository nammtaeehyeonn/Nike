import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from collections import Counter
from datetime import datetime
import re
from io import StringIO

def find_duplicates(lst):
    counts = Counter(lst)
    return [item for item, count in counts.items() if count > 1]

def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

st.set_page_config(
    page_title="옥히나이키",
    page_icon="🚩",
    layout="wide"
)

st.header("나이키 칭찬글 선별 프로그램")
st.divider()

if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False
if 'uploaded_entry_action' not in st.session_state:
    st.session_state['uploaded_entry_action'] = False
if 'confirmed' not in st.session_state:
    st.session_state['confirmed'] = False
if 'alert_txt' not in st.session_state:
    st.session_state['alert_txt'] = ""
if 'all_members' not in st.session_state:
    st.session_state['all_members'] = []

team_sort_values = ["LEADERSHIP", "OPERATION", "STOCKROOM", "SALES1", "SALES2", "-"]

# 1️⃣ 명단 확인
with st.expander("1️⃣ **명단확인**", expanded=True):
    st.divider()
    # 엑셀 파일 읽기
    uploaded_entry = st.file_uploader(" ", key="uploaded_entry")
    try:
        if uploaded_entry != None:
            json_ver = pd.read_csv(uploaded_entry).to_json(force_ascii=False)
            entry = pd.read_json(StringIO(json_ver))[["TEAM", "ENGNAME", "NAME"]]
            entry["TEAM"] = pd.Categorical(entry["TEAM"], categories=team_sort_values, ordered=True)
            entry = entry.sort_values(by=["TEAM", "NAME"])
            # entry = pd.read_excel("./entry.xlsx", engine='openpyxl')
            # entry = read_data_from_db()
            entry.index = range(1, len(entry) + 1)  # 인덱스 재정렬
            # entry['SELECT'] = [True for _ in range(len(entry))]  # SELECT 컬럼 추가

            # 팀 선택 옵션 설정
            select_team_list = list(entry['TEAM'].unique())

            # 컬럼 레이아웃 설정
            col1, col2 = st.columns([0.85, 0.1], gap='large')

            # 데이터 편집 UI
            with col1:
                entry_editor = st.data_editor(
                    entry,
                    column_config={
                        "TEAM": st.column_config.SelectboxColumn(
                            "TEAM",
                            options=select_team_list,
                            required=True,
                            width='small',
                        ),
                        "ENGNAME" : st.column_config.TextColumn(
                            width='large'
                        ),
                        "NAME" : st.column_config.TextColumn(
                            width='small'
                        ),
                    },
                    use_container_width=True
                )

            c_1, c_2, _ = st.columns([0.2, 0.2, 0.6])     
            with c_1:
                submitted = st.button("명단 확정")  
                if submitted:
                    entry_editor['TEAM'] = pd.Categorical(
                        entry_editor['TEAM'],
                        categories=team_sort_values,
                        ordered=True
                    )

                    # TEAM 기준으로 정렬
                    # entry_editor = entry_editor.sort_values(['TEAM'])
                    # entry_editor = entry_editor.sort_values(by=["TEAM", "NAME"])
                    # entry_editor = entry_editor[entry_editor['SELECT']]
                    entry_editor.index = range(1, len(entry_editor) + 1)  # 인덱스 재정렬
                    # entry_editor.to_excel('./entry.xlsx', index=False)
                    st.session_state['submitted'] = True
                    # st.session_state['all_members'] = [""] + [f"[{idx}] " + " - ".join(map(str, row)) for idx, row in entry_editor[['TEAM', 'NAME']].iterrows()]
                    st.session_state['all_members'] = ["무명"] + [f"[{idx}] " + " - ".join(map(str, row)) for idx, row in entry_editor[['TEAM', 'NAME']].iterrows()]
                    # st.rerun()
                    
            with c_2:
                with st.popover("도움말"):
                    st.write("(1) 텍스트를 수정한 후 → 자판을 누른 후 Enter를 눌러야 정상 반영됩니다.")
    except:
        st.error("업로드된 명단파일의 양식이 일치하지 않습니다. \n\n파일을 다시 확인해주세요.")




if st.session_state['submitted']:
    # entry_editor = entry_editor.iloc[:, :-1]
    with st.expander("2️⃣ **파일 업로드 및 정성평가**", expanded=True):
        st.divider()
        uploaded_file = st.file_uploader(" ", key="uploaded_file")
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
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                uploaded_df = uploaded_df.iloc[2:, :].fillna(0)
                filtered_df = uploaded_df[uploaded_df["경험 코멘트"].notna()].loc[:, ["조사 실행 날짜", "서비스 일자", "방문 시간",  "거래 번호", "경험 코멘트"]]
                filtered_df[["거래 번호"]] = filtered_df[["거래 번호"]].astype(int)
                filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]] = \
                    filtered_df[["조사 실행 날짜", "서비스 일자", "방문 시간", "경험 코멘트"]].astype(str)
                filtered_df = filtered_df.sort_values(["거래 번호"])
                filtered_df["번호"] = [i+1 for i in range(len(filtered_df))]
                filtered_df = filtered_df[["번호", "조사 실행 날짜", "서비스 일자", "방문 시간", "거래 번호", "경험 코멘트"]]
            except:
                st.error("업로드된 칭찬글 양식이 일치하지 않습니다. \n\n파일을 다시 확인해주세요.")
                st.stop()
            for_df_dict = dict()
            for col in filtered_df.columns:
                for_df_dict[col] = list(filtered_df[col].values)

            for_df_dict['칭찬'] = [[] for i in range(len(filtered_df))]
            dup_nums = find_duplicates(for_df_dict['거래 번호'])

            for idx, (num, comment) in enumerate(zip(for_df_dict['거래 번호'], for_df_dict['경험 코멘트'])):
                is_included_list = []
                comment = comment.lower()
                comment = re.sub(r'[^\w\s가-힣]', '', comment)
                if num in dup_nums:
                    is_included_list.append("거래번호 중복")
                else:
                    for edx, entry_row in entry_editor.iterrows():
                        member_data = f"[{edx}] " + " - ".join(entry_row[['TEAM', 'NAME']].values)
                        name = entry_row['NAME']
                        if not (len(name) < 3):
                            if (name in comment) or (name[-2:] in comment):
                                is_included_list.append(member_data)
                        else:
                            if (name in comment):
                                is_included_list.append(member_data)
                        
                        engname_list = [re.sub(r'[^\w\s가-힣]', '', engname.lower().strip()) for engname in entry_row['ENGNAME'].split(",")]
                        for engname in engname_list:
                            if engname in comment:
                                is_included_list.append(member_data)
                                break
                                
                        
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
                        # {"colId": "등록 번호", "minWidth": 80, "maxWidth": 150},
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
                if (params.value == "무명"){
                    baseStyle['color'] = 'blue';
                }
                return baseStyle;
            }
            """)
            gb.configure_column("칭찬", 
                                editable=True, 
                                cellEditor='agSelectCellEditor', 
                                cellEditorParams={'values': st.session_state['all_members'] },
                                cellStyle=cellstyle_jscode,
                                autoHeight=True,  # 높이를 내용에 맞게 조정
                                ) 


            grid_options = gb.build()

            st.session_state["alert_bool_1"] = False
            st.session_state["alert_bool_2"] = False
            with st.form("my_form", border=False):
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

                # # if not st.session_state["alert_bool"]:
                # if (not st.session_state["alert_bool_1"]) and (not st.session_state["alert_bool_2"]):
                #     confirm_btn = st.button("확정")
                #     if confirm_btn:
                #         st.session_state['confirmed'] = True
                        
                submitted = st.form_submit_button("확정")
                if submitted:
                    for rdx, row in modified_df.iterrows():
                        count_brackets = sum(s.count("[") for s in row['칭찬'])
                        if count_brackets > 1:
                            st.session_state["alert_bool_1"] = True
                            
                    if ("" in modified_df['칭찬'].unique()):
                        st.session_state["alert_bool_2"] = True
                        
                    if (not st.session_state["alert_bool_1"]) and (not st.session_state["alert_bool_2"]):
                        # st.write("submitted")    
                        st.session_state['confirmed'] = True
                    else:
                        # st.write("no!!")    
                        st.session_state['confirmed'] = False
                        if st.session_state["alert_bool_1"]:
                            st.info("중복 칭찬이 존재합니다.")
                        if st.session_state["alert_bool_2"]:
                            st.info("공란이 존재합니다.")
                        
        else:
            st.session_state['confirmed'] = False
            
            
if st.session_state['confirmed']:
    with st.expander("3️⃣ **최종결과 확인**", expanded=True):
        # filtered_series = modified_df['칭찬'][(modified_df['칭찬'] != "거래번호 중복") & (modified_df['칭찬'] != "")]
        filtered_series = modified_df['칭찬'][(modified_df['칭찬'] != "거래번호 중복")]
        # filtered_series = filtered_series.apply(lambda x : "무명" if not x else x)
        count_df = filtered_series.value_counts().reset_index()
        # numbers = count_df["칭찬"].apply(lambda x: int(re.search(r"\[(\d+)\]", x).group(1)))
        numbers = count_df["칭찬"].apply(
               lambda x: int(re.search(r"\[(\d+)\]", x).group(1)) if re.search(r"\[(\d+)\]", x) else 999
                )
        counts = count_df["count"].tolist()
        entry_editor.loc[999, entry_editor.columns] = ["-", "-", "무명"]
        final_entry = entry_editor.loc[numbers.tolist(), :]
        final_entry['칭찬'] = counts
        col1, col2 = st.columns([0.6,0.4], gap='large', vertical_alignment='bottom')
        with col1:
            st.dataframe(final_entry, use_container_width=True)
            
        with col2:
            csv = convert_df(final_entry)
            st.download_button(
                type="primary",
                label="최종결과 다운로드",
                data=csv,
                file_name=f"{today_date_yymmdd}_{filename}.csv",
                mime="text/csv",
            )
