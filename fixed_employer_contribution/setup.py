import datetime
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from fixed_employer_contribution.custom_fields import get_custom_fields

EPF_WAGE_CEILING = 25_000
EPF_WAGE_CEILING_REVISED_ON = datetime.date(2026, 9, 17)
EPF_PREVIOUS_WAGE_CEILING = 15_000

DEFAULT_SETTINGS = {
	"employer_pf_wage_ceiling": EPF_WAGE_CEILING,
	"employer_pf_previous_wage_ceiling": EPF_PREVIOUS_WAGE_CEILING,
	"eps_eligibility_cutoff_date": EPF_WAGE_CEILING_REVISED_ON,
	"employer_pf_rate": 12,
	"employer_eps_rate": 8.33,
	"employer_edli_rate": 0.5,
	"employer_pf_admin_rate": 0.5,
}

DEFAULT_COMPONENTS = {
	"employee_pf_component": "Provident Fund",
	"employer_epf_component": "Employer Provident Fund",
	"employer_eps_component": "Employer Pension Scheme",
	"employer_edli_component": "Employees Deposit Linked Insurance",
	"employer_pf_admin_component": "EPF Admin Charges",
}


def after_install():
	after_migrate()
	set_employer_pf_defaults()


def after_migrate():
	create_custom_fields(get_custom_fields(), ignore_validate=True)
	set_employer_pf_defaults()


def before_uninstall():
	pass


def set_employer_pf_defaults():
	"""Fill empty Employer PF settings in Payroll Settings.
	Applied only to empty fields, so values a user has modified are never overwritten."""
	if not frappe.db:
		return

	stored = dict(frappe.db.sql("select field, value from `tabSingles` where doctype = 'Payroll Settings'"))
	values = {field: value for field, value in DEFAULT_SETTINGS.items() if not stored.get(field)}
	values.update(
		{
			field: component
			for field, component in DEFAULT_COMPONENTS.items()
			if not stored.get(field) and frappe.db.exists("Salary Component", component)
		}
	)

	if values:
		frappe.db.set_single_value("Payroll Settings", values)
		frappe.clear_document_cache("Payroll Settings", "Payroll Settings")
