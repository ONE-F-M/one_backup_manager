import frappe
import os
from frappe.utils.backups import fetch_latest_backups

def get_latest_backup_files(with_files = 0):
    """fetches the last created file based on frappe's naming culture"""
    try:
        files = []
        last_backup = fetch_latest_backups()
        if not with_files:
            del last_backup['private']
            del last_backup['public']
        for each in last_backup:
            #Pick the file name with extension
            files.append(last_backup[each].split('/')[-1])
        backup_location =  os.getcwd()+"/"+frappe.utils.cstr(frappe.local.site)+'/private/backups/'

        return {"path":backup_location, 'files':files}
    except:
        frappe.msgprint('Error Fetch Latest Backup')
        frappe.log_error(title = "Error Fetching Latest Backup files",message= frappe.get_traceback())
