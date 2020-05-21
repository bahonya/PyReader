from __future__ import print_function
import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class Drive:
    def __init__(self):
        self.service = None

    
    def auth(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
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

        self.service = build('drive', 'v3', credentials=creds)

    def list_books(self):
        """Function to list all pdf, fb2, epub files from Google Drive"""
        results = []
        page_token = None

        while True:
            try:
                param = {}

                if page_token:
                    param['pageToken'] = page_token
                """mimeTypes:
                pdf = application/pdf
                fb2 = text/xml
                epub = application/epub+zip"""
                files = self.service.files().list(q="mimeType='application/pdf' or mimeType='text/xml' or mimeType='application/epub+zip'",
                                                 fields="nextPageToken, files(id, name)",
                                                 **param).execute()
                # append the files from the current result page to our list
                results.extend(files.get('files'))
                # Google Drive API shows our files in multiple pages when the number of files exceed 100
                page_token = files.get('nextPageToken')

                if not page_token:
                    break

            except errors.HttpError as error:
                print(f'An error has occurred: {error}')
                break
        # output the file metadata to console
        for file in results:
            print(file)
        return results
    
    def clean_trash_bin(self):
        """Deletes trash bin that remains after deleting files"""
        self.service.files().emptyTrash().execute()
    
    def search_file(self, mime_type, file_name):
        """Search for file and return search response"""
        page_token = None
        while True:
            response = self.service.files().list(q=f"mimeType='{mime_type}' and name = '{file_name}'",
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name)',
                                                  pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                return response.get('files', [])
                break         
    
    def download_file(self, file_id, file_name):
        """Download a Drive file's content to the local filesystem."""
        file_id = '19q-GsRKT43GyDvUn8Gv0loF4I2hC0otL'
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))
        with open(file_name, "wb") as binary:
            binary.write(fh.getvalue())
            binary.close()
    
    def create_folder(self):
        """Create folder to store .json file with progress details"""
        file_metadata = {
            'name': 'PyReader',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata,
                                            fields='id').execute()
        print ('Folder ID: %s' % file.get('id'))
        return file.get('id')
    
    def get_progress_folder(self):
        """Search and return folder's id or create and return folder's id. At first clean trash bin, deleted files still remain in drive"""
        self.clean_trash_bin()
        results = self.search_file('application/vnd.google-apps.folder', 'PyReader')
        if len(results) == 1:
            return results[0]['id']
        elif len(results) == 0:
            return self.create_folder()
        else:
            raise DriveMultipleFoldersException('You have multiple PyReader folders in your Google Drive')
            
#    def get_progress_file(self):
#        """Search and return progress file's id or create and return progress file's id. At first clean trash bin, deleted files still remain in #drive"""
#        self.clean_trash_bin()
#        results = self.search_file('application/json', 'progress')
#        if len(results) == 1:
#            return results[0]['id']
#        elif len(results) == 0
#            return self.create_fo
#        else:
#            raise DriveMultipleFoldersException('You have multiple PyReader folders in your Google Drive')
    
    def upload_file(self, folder):
        """Upload .json file containing progress data"""
        file_metadata = {
        'name': 'progress.json',
        'parents': [folder],
        }
        media = MediaFileUpload('progress.json',
                                mimetype='application/json',
                                resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print ('File ID: ' + file.get('id'))
        return file.get('id')
        
    def update_file(self, file_id):
        """Update .json file containing progress data"""
        # First retrieve the file from the API.
        file = self.service.files().get(fileId=file_id).execute()
        # File's new content.
        media = MediaFileUpload('progress.json',
                                mimetype='application/json',
                                resumable=True)
        # Send the request to the API.
        updated_file = self.service.files().update(fileId=file_id,
                                                   media_body=media).execute()
        return updated_file
    

                
        
                

        
    
#folder_id = '1lRouiNLHVdicNJez8z8SpSyS1Qt0lRNe'    
#drive = Drive()
#drive.auth()
#drive.list_books()
#folder_id = drive.create_folder()
#progress_id = drive.upload_file(folder_id)
#drive.update_file('16zaQB5BGxLT8eG0-SqmI7kE1mQVJHboq')
#folder = drive.get_progress_folder()
#print(folder)
#drive.clean_trash_bin()

#drive.insert_file('progress.json', 'test', x, '*/*', 'progress.json')

#drive.download_file('19q-GsRKT43GyDvUn8Gv0loF4I2hC0otL')