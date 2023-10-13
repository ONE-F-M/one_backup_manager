import frappe
import os



def get_latest_files(with_files = 0):
    """fetches the last created file based on frappe's naming culture"""
    print(os.getcwd())
    backup_location =  os.getcwd()+"/"+frappe.utils.cstr(frappe.local.site)+'/private/backups/'
    if 'sites' in os.getcwd():
        print(os.getcwd())
        os.chdir(backup_location)
    else:
        os.chdir('sites')
        os.chdir(backup_location)
    files = os.listdir()
    files.sort(key=lambda x: os.path.getctime(os.path.join(x)))
    return {"path":backup_location,'files':files[-1:] if not with_files else files[-3:]}
        