import pandas as pd

def append_df(spreadsheet, sheet_name, df, expected_headers):
    """
    Append a DataFrame to a Google Sheet using batch update (faster, avoids rate limits)
    
    Args:
        spreadsheet: gspread Spreadsheet object
        sheet_name: Name of the worksheet
        df: pandas DataFrame to append
        expected_headers: List of expected column headers
    """
    ws = spreadsheet.worksheet(sheet_name)
    
    # Ensure DataFrame columns match expected headers
    df = df[expected_headers]
    
    # Convert DataFrame to list of lists
    values = df.values.tolist()
    
    # Batch append all rows at once (single API call)
    if values:
        ws.append_rows(values, value_input_option='USER_ENTERED')
        print(f"  → Appended {len(values)} rows to '{sheet_name}'")
