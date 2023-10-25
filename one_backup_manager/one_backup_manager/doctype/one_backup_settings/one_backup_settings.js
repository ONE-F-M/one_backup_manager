// Copyright (c) 2023, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('One Backup Settings', {
	refresh: function(frm) {
		frm.add_custom_button("Backup to Google Drive",function(){
			frappe.confirm("Are you sure you want to send the latest backup to Google Drive?",()=>{
				frappe.call({
					method:"one_backup_manager.one_backup_manager.doctype.one_backup_settings.one_backup_settings.create_backup",
					callback:function(r){
						frappe.show_alert("Backup to Google Drive Initiated")
					}
				})
			},
			()=>{
				;
			})
			
		})
	}
});
