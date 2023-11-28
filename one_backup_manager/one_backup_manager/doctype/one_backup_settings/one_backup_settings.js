// Copyright (c) 2023, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('One Backup Settings', {
	refresh: function(frm) {
		if(frm.doc.enable_google_backups){
			frm.events.create_backup_button(frm)
		}
	},
	enable_google_backups: function(frm) {
		if(!frm.doc.enable_google_backups){
			frm.set_value('enable_auto_backup_to_google_drive', false);
		}
	},
	create_backup_button: function(frm) {
		frm.add_custom_button(__("Backup to Google Drive"),
			function(){
				if(frm.is_dirty()){
					frappe.throw(__('Please Save the Document and Continue!'))
				}
				else{
					frappe.confirm(
						"Are you sure you want to send the latest backup to Google Drive?",
						()=>{
							frappe.call({
								method:"one_backup_manager.one_backup_manager.doctype.one_backup_settings.one_backup_settings.create_backup",
								callback:function(r){
									frappe.show_alert("Backup to Google Drive Initiated")
								}
							});
						},
						()=>{
							// No
						}
					);
				}
			}
		);
	}
});
