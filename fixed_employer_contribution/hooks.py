app_name = "fixed_employer_contribution"
app_title = "Fixed Employer Contribution"
app_publisher = "thefunctionaldev"
app_description = "Automate Indian statutory employer PF contributions (EPF, EPS, EDLI, Admin Charges) on Salary Slips"
app_email = "thefunctionaldev@users.noreply.github.com"
app_license = "mit"

required_apps = ["frappe", "erpnext", "hrms"]

# Document Events
doc_events = {
	"Salary Structure Assignment": {
		"validate": [
			"fixed_employer_contribution.employer_pf.warn_if_eps_wage_above_ceiling",
			"fixed_employer_contribution.employer_pf.warn_if_joint_declaration_missing",
		],
	},
	"Salary Slip": {
		"validate": "fixed_employer_contribution.employer_pf.set_employer_pf_contributions",
	},
}

# Installation & Migrations
after_install = "fixed_employer_contribution.setup.after_install"
after_migrate = "fixed_employer_contribution.setup.after_migrate"
before_uninstall = "fixed_employer_contribution.setup.before_uninstall"

# Fixtures
fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
				"fieldname",
				"in",
				[
					"employer_pf_section",
					"enable_employer_pf_deduction",
					"employer_pf_wage_ceiling",
					"employer_pf_previous_wage_ceiling",
					"eps_eligibility_cutoff_date",
					"employer_pf_rates_cb",
					"employer_pf_rate",
					"employer_eps_rate",
					"employer_edli_rate",
					"employer_pf_admin_rate",
					"employer_pf_components_section",
					"employee_pf_component",
					"employer_epf_component",
					"employer_pf_components_cb",
					"employer_eps_component",
					"employer_edli_component",
					"employer_pf_admin_component",
					"eps_eligible",
					"joint_declaration_on_file",
					"pf_wage_considered",
					"employer_pf_totals_cb",
					"total_employer_pf_cost",
					"pf_credited_to_employee_account",
				],
			]
		],
	}
]
