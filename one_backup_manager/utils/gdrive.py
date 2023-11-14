import frappe
from google.oauth2 import service_account
import os,io
from frappe.utils.user import get_system_managers
from datetime import datetime
from frappe.utils import cstr
from googleapiclient.discovery import build
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload
from one_backup_manager.utils.utils import get_latest_files

class GoogleDriveUploader():
    def __init__(self):
        self.settings_doc = frappe.get_doc("One Backup Settings")
        self.set_access_token()
        if not frappe.local.conf.google_drive_json_credentials:
            frappe.throw("Please set a credentials file in Site Config")

    def set_access_token(self):
        SERVICE_ACCOUNT_FILE = os.getcwd()+"/"+cstr(frappe.local.site) + frappe.local.conf.google_service_account_credentials

        SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = discovery.build('sheets', 'v4', credentials=self.credentials)
        self.drive_api = build('drive', 'v3', credentials=self.credentials)


    def notify(self,success = False,message = None):
        """Notify users of the outcome of the backup process"""
        recipient = [self.settings_doc.shared_email_address]
        recipient+=get_system_managers(only_name=1)


        success_value = "Successful" if success else "Failed"
        subject = f"Backup {success_value}!"
        if not recipient:
            recipient = frappe.conf.error_report_email
            if not recipient:
                frappe.throw("No Email Recipient Set")

        frappe.sendmail(recipients=recipient,subject = subject,message = message)

    def fetch_folder_id(self):
        """Fetch the folder ID of the drive used for backups, If one does not exist then create one"""
        folder_name = self.settings_doc.backup_folder_name
        if folder_name:
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
                    permission = {'type': 'user','role': 'writer','emailAddress': self.settings_doc.shared_email_address}
                    self.drive_api.permissions().create(fileId=folder.get('id'), body=permission).execute()
                except:

                    frappe.log_error(message = frappe.get_traceback(),title="Error Creating Backup Folder")
            return folder

    def  validate_limit(self,parent_folder_id =None):
        if not parent_folder_id:
            parent_folder_id = self.fetch_folder_id()
        if  self.settings_doc.enable_google_backups:
            limit = self.settings_doc.number_of_backups
            if not limit:
                limit = 3
            #list the folder in the root backup location

            sub_folders = self.drive_api.files().list(q=f"'{parent_folder_id.get('id')}' in parents and mimeType = 'application/vnd.google-apps.folder'",orderBy="createdTime desc").execute()['files']

            if len(sub_folders) > (limit-1):
                removed_folders = sub_folders[(limit-1):]
                for folder in removed_folders:
                    self.drive_api.files().delete(fileId=folder['id']).execute()


    def create_log(self,complete,url=None):
        """Create a  Backup Log to reflect the status of the upload"""
        data = frappe._dict({
            'date':frappe.utils.getdate(),
            'doctype':'Backup Log',
            'status':'Completed' if complete else "Failed"
        })
        if not complete:
            data.error_message = frappe.get_traceback()
        log_doc = frappe.get_doc(data)
        if complete:
            log_doc.uploaded_files = self.settings_doc.backup_with_files
            log_doc.route = url

        log_doc.insert()
        frappe.db.commit()


    def upload_file(self):
        if not self.settings_doc.enable_google_backups:
            return
        files = get_latest_files(with_files = self.settings_doc.backup_with_files)
        folder = self.fetch_folder_id()
        first_file = files.get('files')[0]
        file_folder_metadata = {
                    "name": first_file.split('-')[0],
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [folder.get('id')]
                        }
        self.validate_limit(parent_folder_id = folder)
        filefolder = self.drive_api.files().create(body=file_folder_metadata, fields="id,webViewLink").execute()
        permission = {'type': 'user','role': 'writer','emailAddress': self.settings_doc.shared_email_address}
        self.drive_api.permissions().create(fileId=filefolder.get('id'), body=permission).execute()
        if files:
            try:
                for each in files.get('files'):
                    file_metadata = {
                        'name': each,
                        "parents": [filefolder.get('id')]
                    }
                    media = MediaFileUpload(files.get('path')+each, resumable=True)
                    file_upload = self.drive_api.files().create(body=file_metadata, media_body=media, fields='id').execute()


                self.create_log(1,url =filefolder.get('webViewLink'))
                if self.settings_doc.send_email_notifications_for_successful_backups:
                    self.notify(success = True,message = f"Please note that the backup of {frappe.local.site} is successful")

            except:

                frappe.log_error(message = frappe.get_traceback(),title="Error Creating Backup")
                self.notify(success= False,message = "<p>Please see error log from backup</p><br/>"+frappe.get_traceback())
                self.create_log(0)
