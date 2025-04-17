from __future__ import print_function

import io
import os.path 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']  # Request full Drive access

def download_file(service, file_id, file_name):
    """Downloads a file from Google Drive.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to download.
        file_name: Name to save the downloaded file as.
    """
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f'Download progress for {file_name}: {int(status.progress() * 100)}%')
        fh.seek(0)
        with open(file_name, 'wb') as f:
            f.write(fh.read())
        print(f'Downloaded "{file_name}"')
        return True
    except HttpError as error:
        print(f'An error occurred during download of {file_name}: {error}')
        return False

def find_and_download_file(service, filename_to_download):
    """Finds a file by name and downloads it."""
    try:
        # Call the Drive v3 API
        results = service.files().list(
            q=f"name='{filename_to_download}'",
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])

        if not items:
            print(f'No files found with the name "{filename_to_download}".')
            return

        for item in items:  # It's possible to have multiple files with the same name.
            print(f'Found file: {item["name"]} ({item["id"]})')
            download_file(service, item['id'], item['name'])  # Download each file found

    except HttpError as error:
        print(f'An error occurred: {error}')


def main():
    """Lists the names and IDs of the first 10 files and downloads them."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return

        print('Found files:')
        # for item in items:
        #     print(f'{item["name"]} ({item["id"]}) - Mime Type: {item["mimeType"]}')
        #     file_id = item['id']
        #     file_name = item['name']
        #     download_file(service, file_id, file_name)

        filename_to_download = input("Enter the name of the file to download: ")  # Get filename from user
        find_and_download_file(service, filename_to_download)

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
