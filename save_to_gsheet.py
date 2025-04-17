
import gspread
import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def save_csv_to_sheet(csv_path, sheet_name, spreadsheet_name="가상염색 평가 결과"):
    # Streamlit secrets에서 서비스 계정 정보 불러오기
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)

    # Google 스프레드시트 열기
    spreadsheet = client.open(spreadsheet_name)

    # 워크시트 찾기 또는 새로 생성
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

    # CSV 불러와서 업로드
    df = pd.read_csv(csv_path)
    df = df.fillna("")
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
