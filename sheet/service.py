from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_SHEET_URL, KEYS_PATH


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = KEYS_PATH

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()


async def get_values_from_sheet():
    try:
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_URL,
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
