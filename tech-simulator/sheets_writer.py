import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    return gspread.authorize(creds)

def write_df(sheet_id, sheet_name, df):
    client = get_client()
    sh = client.open_by_key(sheet_id)

    try:
        ws = sh.worksheet(sheet_name)
        ws.clear()
    except:
        ws = sh.add_worksheet(sheet_name, rows="1000", cols="20")

    ws.update([df.columns.tolist()] + df.values.tolist())

def append_df(sheet_id, sheet_name, df):
    client = get_client()
    ws = client.open_by_key(sheet_id).worksheet(sheet_name)
    ws.append_rows(df.values.tolist(), value_input_option="USER_ENTERED")
