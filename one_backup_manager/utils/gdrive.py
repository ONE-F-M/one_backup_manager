import frappe
from google.oauth2 import service_account
import os,io
from frappe.utils import cstr
from one_fm.processor import sendemail
from googleapiclient.discovery import build
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from one_backup_manager.utils.utils import get_latest_files

class GoogleDriveUploader():
    def __init__(self):
        self.settings_doc = frappe.get_doc("One Backup Settings")
        self.set_access_token()
        if not self.settings_doc.google_json_credentials:
            frappe.throw("Please set a credentials file in ONE Backup Settings")
    
    def set_access_token(self):
        SERVICE_ACCOUNT_FILE = os.getcwd()+"/"+cstr(frappe.local.site) + self.settings_doc.google_json_credentials
        
        SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = discovery.build('sheets', 'v4', credentials=self.credentials)
        self.drive_api = build('drive', 'v3', credentials=self.credentials)
        
        
    def notify(self,success = False,message = None):
        """Notify users of the outcome of the backup process"""
        recipient = self.settings_doc.shared_email_address
        success_value = "Successful" if success else "Failed"
        if not recipient:
            recipient = frappe.conf.error_report_email
            if not recipient:
                frappe.throw("No Email Recipient Set")
        print("SENDING MAIL O")
        sendemail(recipients=[recipient],subject = f"Backup {success_value}!",message = message )
    
    def upload_file(self,notify_success = False,with_files = False):
        files = get_latest_files(with_files = with_files)
        
        folder_name = self.settings_doc.backup_folder_name
        folder_exists = self.drive_api.files().list(q=f"name='{folder_name}'").execute()['files']
        if folder_exists:
            folder = folder_exists[0]
        else:
            folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
                }
            try:
                folder = self.drive_api.files().create(body=folder_metadata, fields="id").execute()
                permission = {'type': 'user','role': 'reader','emailAddress': self.settings_doc.shared_email_address}
                self.drive_api.permissions().create(fileId=folder.get('id'), body=permission).execute()
            except:
                print("FAILED CREATING FOLDER")
                frappe.log_error(message = frappe.get_traceback(),title="Error Creating Backup Folder")
        if files:
            try:
                for each in files.get('files'):
                    file_folder_metadata = {
                    "name": each.split('.')[0],
                    "mimeType": "application/vnd.google-apps.folder"
                        }
                    filefolder = self.drive_api.files().create(body=file_folder_metadata, fields="id").execute()
                    permission = {'type': 'user','role': 'reader','emailAddress': self.settings_doc.shared_email_address}
                    self.drive_api.permissions().create(fileId=filefolder.get('id'), body=permission).execute()
                    file_metadata = {
                        'name': each,
                        "parents": [filefolder.get('id')]
                    }
                    media = MediaFileUpload(files.get('path')+each, resumable=True)
                    file_upload = self.drive_api.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print("DONE UPLOADING")
                if self.settings_doc.send_email_notifications_for_successful_backups:
                    self.notify(success = True,message = f"Please note that the backup of {frappe.local.site} is successful")

            except:
                print("FAILED UPLOADING")
                frappe.log_error(message = frappe.get_traceback(),title="Error Creating Backup")
                self.notify(success= False,message = "<p>Please see error log from backup</p><br/>"+frappe.get_traceback())