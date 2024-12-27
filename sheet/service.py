# import pandas as pd
#
# from config import GOOGLE_SHEET_URL
#
# df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_URL}/export?format=csv")
#
# print(df.get("1. F. I. SH. (Pasportdagidek to'liq yozing)"))
#
# print(df.keys())
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import GOOGLE_SHEET_URL, KEYS_PATH

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = KEYS_PATH

creds = None
creds = creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = GOOGLE_SHEET_URL

service = build("sheets", "v4", credentials=creds)

sheet = service.spreadsheets()


def get_values_from_sheet():

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="sheet 1").execute()

    return result
