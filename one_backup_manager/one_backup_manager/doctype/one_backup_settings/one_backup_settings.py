# Copyright (c) 2023, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from one_backup_manager.utils.gdrive import GoogleDriveUploader
from frappe.utils.background_jobs import enqueue
from one_backup_manager.utils.utils import get_latest_backup_files
from frappe.utils import now

class OneBackupSettings(Document):
	def validate(self):
		if not self.enable_google_backups and self.enable_auto_backup_to_google_drive:
			self.enable_auto_backup_to_google_drive = False

@frappe.whitelist()
def auto_backup_to_gdrive():
	if frappe.db.get_single_value("One Backup Settings", "enable_auto_backup_to_google_drive"):
		create_backup()

@frappe.whitelist()
def create_backup():
	"""
		Starts the backup process in the background
	"""
	enqueue(
		method=new_backup,
		queue="long",
		timeout=6000,
		event="Uploading Backups to Google Drive",
		job_name="Uploading Backups to Google Drive",
		now=False
	)
	return True

def new_backup():
	'''
		Method to upload erp backup to google drive
	'''
	# Check if enabled google backup
	enable_google_backups = frappe.db.get_single_value("One Backup Settings", "enable_google_backups")
	if enable_google_backups:
		# Get latest backup files
		backup_with_files = frappe.db.get_single_value("One Backup Settings", "backup_with_files")
		# Get latset backup as a dict {'path': path to the file, 'files': list of name of the fiel with extension}
		file_details = get_latest_backup_files(with_files = backup_with_files)

		files = file_details.get('files')

		# init backup file folder name
		file_folder_name = ''

		if files and len(files) > 0:
			# Set a backup file folder name
			file_folder_name = files[0].split('-')[0]
		else:
			frappe.msgprint("No Backup files found to upload!", alert =1)
			return False

		gdrive = GoogleDriveUploader()
		parent_folder_ids = []

		# Create parent folder in google drive and set permission for the folder if backup folder name is defined
		if gdrive.settings_doc.backup_folder_name:
			parent_folder = gdrive.create_folder(gdrive.settings_doc.backup_folder_name, gdrive.settings_doc.shared_email_address)
			parent_folder_ids.append(parent_folder.get('id'))

		# Create folder for the backup in google drive and set permission for the folder
		file_folder = gdrive.create_folder(file_folder_name, gdrive.settings_doc.shared_email_address, parent_folder_ids)

		# Iterate backup files and create the file in google drive
		try:
			for file in files:
				# Create file in google dirve
				file_upload = gdrive.upload_file(file, [file_folder.get('id')], file_details.get('path'))
			# Create Google Drive Log in our system with the google drive link to the backup folder
			gdrive.create_log(1, url=file_folder.get('webViewLink'))

			# Notify the backup google drive upload details
			if gdrive.settings_doc.send_email_notifications_for_successful_backups:
				backup_doc.notify(success = True,message = f"Please note that the backup of {frappe.local.site} is successful")
			frappe.msgprint("Backup to Google Drive Complete", alert =1)
		except:
			# Create error log and notifications if any exception happened in the google drive upload
			frappe.log_error(message = frappe.get_traceback(),title="Error Uploading to Google Drive")
			gdrive.notify(success= False, message = "<p>Please see error log from google drive upload</p><br/>"+frappe.get_traceback())
			gdrive.create_log(0)
	else:
		frappe.msgprint(_("Enable Google Backups in One Backup Settings"))
