from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pytube import YouTube
import datetime
import csv
import os
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def parse_subtitles(srt,ad_times):

    #convert all times to datetime objects
    for i in range(len(ad_times)):
        ad_times[i] = (datetime.datetime.strptime(ad_times[i][0],'%H:%M:%S'),datetime.datetime.strptime(ad_times[i][1],'%H:%M:%S'))
        
    lines = srt.splitlines()
    data = []
    tag = 'NA' #tag NA - Not Ad , A - Ad
    begin  = None
    end = None
    for i in range(len(lines)):
        if (i+1)%4 == 2:
            #timestamp detail
            begin,end = lines[i].split('-->')
            begin = datetime.datetime.strptime(begin.split(',')[0].strip(),'%H:%M:%S')
            end = datetime.datetime.strptime(end.split(',')[0].strip(),'%H:%M:%S')

            fl = 0
            for interval in ad_times:
                if (interval[0] >= begin and interval[0] < end) or (interval[1] > begin and interval[1] <= end) or (begin >= interval[0] and end <= interval[1]):
                    fl = 1
                    tag = 'A'
                    break
            if fl == 0:
                tag = 'NA'
                
        
        if (i+1)%4 == 3:
            data.append((begin.strftime('%H:%M:%S'),end.strftime('%H:%M:%S'),lines[i],tag))

    return data
        
def create_csv_dataset(filename,data):
    if not os.path.exists('Datasets'):
        os.makedirs('Datasets')

    with open('Datasets/'+filename,'w') as out:
        csv_out = csv.writer(out,delimiter='|')
        csv_out.writerow(['sub_begin_time','sub_end_time','text','class'])
        for row in data:
            csv_out.writerow(row)



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
            url = row[0]
            start_times = row[1].split(',')
            end_times = row[2].split(',')
            ad_times = [(start_times[i],end_times[i]) for i in range(len(start_times))]
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s, %s' % (row[0], row[1],row[2]))
            source = YouTube(url)
            en_caption = source.captions.get_by_language_code('en')
            srt = (en_caption.generate_srt_captions())
            dataset = parse_subtitles(srt,ad_times)
            create_csv_dataset(url.split('//')[1].split('/')[-1]+'.csv',dataset)
            
            

if __name__ == '__main__':
    creds = check_creds()
    extract_subs_from_sheets('1cQospZoRp0zMOMDp4xpHg8ACVvx1SL0Gw-O390AktYE','Sheet1!B2:D21',creds)


