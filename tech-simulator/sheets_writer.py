import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_or_create_worksheet(spreadsheet, title, headers, rows=1000, cols=20):
    """Get worksheet by title or create if missing"""
    try:
        ws = spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
        ws.append_row(headers)
    return ws

def append_df(spreadsheet, worksheet_title, df, headers):
    """Append DataFrame to worksheet"""
    ws = get_or_create_worksheet(spreadsheet, worksheet_title, headers)
    if df.empty:
        return
    for row in df.to_dict(orient="records"):
        ws.append_row(list(row.values()))
