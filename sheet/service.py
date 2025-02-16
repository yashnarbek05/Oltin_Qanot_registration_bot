from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_SHEET_URL, KEYS_PATH

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(KEYS_PATH, scopes=SCOPES)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()


async def get_values_from_sheet(sheet_name: str):
    try:
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_URL,
            range=f"{sheet_name}"
        ).execute()

        values = result.get("values", [])

        return values

    except HttpError as err:
        print(f"HTTP Error: {err}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


async def update_allowing(index: int, allowed: bool, sheet_name: str):
    # is_allowed = N row
    request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{sheet_name}!N{index + 1}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[allowed]]})
    response = request.execute()

    return response.get("updatedRows"), allowed


async def update_given(index: int, given: bool, sheet_name: str):
    # is_given   = M row

    request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{sheet_name}!M{index + 1}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[given]]})
    response = request.execute()

    return response.get("updatedRows"), given


async def write_volunteer_id(index: int, sheet_name: str, vol_id: int):
    # volunteer_id   = O row

    request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{sheet_name}!O{index + 1}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[vol_id]]})
    response = request.execute()

    return response.get("updatedRows"), vol_id