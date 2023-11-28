# Copyright (c) 2023, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from one_backup_manager.utils.gdrive import GoogleDriveUploader
import os
import datetime
from one_fm.api.api import upload_file as upload_file_to_db
from pathlib import Path
import hashlib
import base64

class GDriveUpload(Document):
	@frappe.whitelist()
	def upload_to_google_drive(self):
		gdrive = GoogleDriveUploader()
		file_path = os.getcwd()+"/"+frappe.utils.cstr(frappe.local.site)+'/private/files/'
		file_name = frappe.db.get_value("File", {"file_url": self.file}, "file_name")

		parent_folder_ids = []

		if self.parent_folder_name:
			if self.share_file_only:
				parent_folder = gdrive.create_folder(self.parent_folder_name)
			else:
				parent_folder = gdrive.create_folder(self.parent_folder_name, self.share_with)
			parent_folder_ids.append(parent_folder.get('id'))

		if self.share_file_only:
			file_folder = gdrive.create_folder(self.file_folder_name, parent_folder_ids)
		else:
			file_folder = gdrive.create_folder(self.file_folder_name, self.share_with, parent_folder_ids)

		try:
			# Create file in google dirve
			file = gdrive.upload_file(file_name, [file_folder.get('id')], file_path, self.share_with)
			# Create Google Drive Log in our system with the google drive link to the file folder
			gdrive.create_log(1, url=file.get('webViewLink'))
			self.db_set("google_drive_link", file.get('webViewLink'))
			frappe.msgprint("Upload to Google Drive Complete", alert =1)
		except:
			# Create error log and notifications if any exception happened in the google drive upload
			frappe.log_error(message = frappe.get_traceback(),title="Error Uploading to Google Drive")
			gdrive.notify(success= False, message = "<p>Please see error log from google drive upload</p><br/>"+frappe.get_traceback())
			gdrive.create_log(0)

@frappe.whitelist()
def upload_to_gdrive(file_name: str = None, file: str = None, gdrive_folder: str = None, share_with: str = None):
	"""[summary]
		Args:
			file_name (str): Name of the file
			file (str): file
			gdrive_folder (str): Google drive folder name
			share_with (str): email id to share the file in google drive
		Returns:
			dict: {
				message (str): Brief message indicating the response,
				status_code (int): Status code of response.
				data (str): The url to the file,
				error (str): Any error handled.
			}
	"""

	if not file_name:
		return response("Bad Request", 400, None, "file_name required.")

	if not file:
		return response("Bad Request", 400, None, "file required.")

	if not gdrive_folder:
		return response("Bad Request", 400, None, "gdrive_folder required.")

	if not share_with:
		return response("Bad Request", 400, None, "share_with required.")

	if not isinstance(file_name, str):
		return response("Bad Request", 400, None, "file_name must be of type str")

	if not isinstance(gdrive_folder, str):
		return response("Bad Request", 400, None, "gdrive_folder must be of type str")

	try:
		file_ext = "." + file_name.split(".")[-1]
		content = base64.b64decode(file)
		file_name = hashlib.md5((file_name + str(datetime.datetime.now())).encode('utf-8')).hexdigest() + file_ext
		Path(frappe.utils.cstr(frappe.local.site)+f"/private/files/gdrive_upload").mkdir(parents=True, exist_ok=True)
		file_path = frappe.utils.cstr(frappe.local.site)+f"/private/files/gdrive_upload/{filename}"
		file_ = upload_file_to_db(doc, "attachments", filename, file_path, content, is_private=True)

		gdrive_upload = frappe.new_doc('GDrive Upload')
		gdrive_upload.file_folder_name = gdrive_folder
		gdrive_upload.share_with = share_with
		gdrive_upload.share_file_only = True
		gdrive_upload.file = file_.file_url
		gdrive_upload.save(ignore_permissions=True)
		gdrive_upload.upload_to_google_drive()
		return response("Success", 201, gdrive_upload.google_drive_link)

	except Exception as error:
		frappe.log_error(error, 'GDrive Upload API')
		return response("Internal Server Error", 500, None, error)
