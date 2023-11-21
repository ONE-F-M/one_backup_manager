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
		frappe.throw("DDDDDD")
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
	backup_with_files = frappe.db.get_single_value("One Backup Settings", "backup_with_files")
	files = get_latest_backup_files(with_files = backup_with_files)
	file_name = 'backup-{0}'.format(now())
	first_file = files.get('files')[0]
	if first_file:
		file_name = first_file.split('-')[0]
	backup_doc = GoogleDriveUploader()
	backup_doc.upload_file(files, file_name)
	frappe.msgprint("Backup to Google Drive Complete", alert =1)
