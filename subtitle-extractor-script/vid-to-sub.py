from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pytube import YouTube

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def check_creds():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
    return creds

def extract_subs_from_sheets(SAMPLE_SPREADSHEET_ID,SAMPLE_RANGE_NAME,creds):
    service = build('sheets', 'v4', credentials=creds)
    
    # # The ID and range of a sample spreadsheet.
    # SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    # SAMPLE_RANGE_NAME = 'Class Data!A2:E'

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('link, start','end')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s, %s' % (row[0], row[1],row[2]))
        # source = YouTube('https://www.youtube.com/watch?v=jHUewEWi9SE')

        # en_caption = source.captions.get_by_language_code('en')
        # en_caption_convert_to_srt = (en_caption.generate_srt_captions())
        # print(en_caption_convert_to_srt)

if __name__ == '__main__':
    creds = check_creds()
    extract_subs_from_sheets('1cQospZoRp0zMOMDp4xpHg8ACVvx1SL0Gw-O390AktYE','Sheet1!B2:D21',creds)


