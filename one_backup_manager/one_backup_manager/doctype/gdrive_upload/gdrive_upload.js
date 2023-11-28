// Copyright (c) 2023, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('GDrive Upload', {
	upload: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: 'upload_to_google_drive',
			callback: function(r) {
				frm.refresh();
			},
			freaze: true,
			freaze_message: __("Uploading to Google Drive!")
		})
	},
	view_in_gdrive: function(frm) {
		window.open(frm.doc.google_drive_link);
	}
});
