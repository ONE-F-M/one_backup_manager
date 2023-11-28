from . import __version__ as app_version

app_name = "one_backup_manager"
app_title = "One Backup Manager"
app_publisher = "ONE FM"
app_description = "Handles Backups of files to External File Storage"
app_email = "support@one-fm.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/one_backup_manager/css/one_backup_manager.css"
# app_include_js = "/assets/one_backup_manager/js/one_backup_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/one_backup_manager/css/one_backup_manager.css"
# web_include_js = "/assets/one_backup_manager/js/one_backup_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "one_backup_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "one_backup_manager.utils.jinja_methods",
#	"filters": "one_backup_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "one_backup_manager.install.before_install"
# after_install = "one_backup_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "one_backup_manager.uninstall.before_uninstall"
# after_uninstall = "one_backup_manager.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "one_backup_manager.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
#	"all": [
#		"one_backup_manager.tasks.all"
#	],
	"daily": [
		"one_backup_manager.one_backup_manager.doctype.one_backup_settings.one_backup_settings.auto_backup_to_gdrive"
	],
#	"hourly": [
#		"one_backup_manager.tasks.hourly"
#	],
#	"weekly": [
#		"one_backup_manager.tasks.weekly"
#	],
#	"monthly": [
#		"one_backup_manager.tasks.monthly"
#	],
}

# Testing
# -------

# before_tests = "one_backup_manager.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "one_backup_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "one_backup_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["one_backup_manager.utils.before_request"]
# after_request = ["one_backup_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["one_backup_manager.utils.before_job"]
# after_job = ["one_backup_manager.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"one_backup_manager.auth.validate"
# ]
