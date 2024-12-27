import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Setup credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/jsonfile.json", scope)
client = gspread.authorize(creds)

# Open sheet by URL or title
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/your-sheet-id")

# Select worksheet
worksheet = spreadsheet.worksheet("Sheet1")

# Get data
data = worksheet.get_all_records()

# Convert to DataFrame
df = pd.DataFrame(data)
print(df.head())
