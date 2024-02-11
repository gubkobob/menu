import os.path
import pickle
from typing import Any

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SAMPLE_RANGE_NAME = 'Test List!A2:E246'


class GoogleSheet:
    SPREADSHEET_ID = '1zVh6aMMqUVNotVQ8vTPV0wUOPHxHcW0wYc-Wo9PHyTo'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self):
        creds = None
        if os.path.exists('google_sheets/token.pickle'):
            with open('google_sheets/token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_sheets/credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('google_sheets/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def download(self, range_name: str = 'Test List!A1:G18') -> Any:
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get('values', [])
        return values


def main() -> None:
    gs = GoogleSheet()
    range = 'Test List!A1:G18'
    values = gs.download(range_name=range)
    for row in values:
        print(row)


if __name__ == '__main__':
    main()
