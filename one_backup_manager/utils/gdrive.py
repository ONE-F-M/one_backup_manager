import frappe
from google.oauth2 import service_account
import os,io
from frappe.utils.user import get_system_managers
from datetime import datetime
from frappe.utils import cstr
from googleapiclient.discovery import build
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload

class GoogleDriveUploader():
    def __init__(self):
        self.settings_doc = frappe.get_doc("One Backup Settings")
        self.set_access_token()
        if not frappe.local.conf.google_service_account_credentials:
            frappe.throw("Please set a credentials file in Site Config")

    def set_access_token(self):
        SERVICE_ACCOUNT_FILE = os.getcwd()+"/"+cstr(frappe.local.site) + frappe.local.conf.google_service_account_credentials

        SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = discovery.build('sheets', 'v4', credentials=self.credentials)
        self.drive_api = build('drive', 'v3', credentials=self.credentials)


    def notify(self, success = False, message = None):
        """Notify users of the outcome of the backup process"""
        recipients = [self.settings_doc.shared_email_address]
        recipients+= get_system_managers(only_name=1)

        success_value = "Successful" if success else "Failed"
        subject = f"Google drive upload {success_value}!"

        if recipients and len(recipients) > 0:
            frappe.sendmail(recipients=recipients, subject=subject, message=message)

    def create_log(self,complete,url=None):
        """Create a  Backup Log to reflect the status of the upload"""
        data = frappe._dict({
            'date':frappe.utils.getdate(),
            'doctype':'Google Drive Log',
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

    def create_folder(self, folder_name, share_with=False, parents=[]):
        folder_exists = self.drive_api.files().list(q=f"name='{folder_name}'").execute()['files']
        if folder_exists:
            folder = folder_exists[0]
        else:
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parents and len(parents) > 0:
                folder_metadata['parents'] = parents
            try:
                folder = self.drive_api.files().create(body=folder_metadata, fields="id, webViewLink").execute()
                self.create_permission(folder.get('id'), share_with)
            except Exception as e:
                frappe.log_error(message = frappe.get_traceback(),title="Error Creating Google Drive Folder")
        return folder

    def upload_file(self, file_name_with_ext, parents, file_path, share_with=False):
        file_metadata = {
            'name': file_name_with_ext,
            "parents": parents
        }
        media = MediaFileUpload(file_path+file_name_with_ext, resumable=True)
        file = self.drive_api.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        self.create_permission(file.get('id'), share_with)
        return file

    def create_permission(self, file_id, share_with):
        if share_with:
            permission = {'type': 'user','role': 'writer','emailAddress': share_with}
            self.drive_api.permissions().create(fileId=file_id, body=permission).execute()
