# Copyright (c) 2023, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from one_backup_manager.utils.gdrive import GoogleDriveUploader
from frappe.utils.background_jobs import enqueue

class OneBackupSettings(Document):
	pass
@frappe.whitelist()
def create_backup():
	"""
			Starts the backup process in the background
	"""
	enqueue(method=new_backup,queue="long",
				timeout=6000, event="Uploading Backups to Google Drive",
				job_name="Uploading Backups to Google Drive",
				now=False)
	return True

def new_backup():
    backup_doc = GoogleDriveUploader()
    backup_doc.upload_file()
    frappe.msgprint("Backup to Google Drive Complete",alert =1 )