# import pandas as pd
#
# from config import GOOGLE_SHEET_URL
#
# df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_URL}/export?format=csv")
#
# print(df.get("1. F. I. SH. (Pasportdagidek to'liq yozing)"))
#
# print(df.keys())
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_SHEET_URL, KEYS_PATH

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = KEYS_PATH

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of sheet
SAMPLE_SPREADSHEET_ID = GOOGLE_SHEET_URL

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()


def get_values_from_sheet():
    try:
        result = sheet.values().get(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range="sheet 1"
        ).execute()

        values = result.get("values", [])

        return values

    except HttpError as err:
        print(f"HTTP Error: {err}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
