import frappe

def get_custom_fields():
	enabled = "eval:doc.enable_employer_pf_deduction"
	employer_contribution = '[["Salary Component", "type", "=", "Employer Contribution"]]'

	return {
		"Payroll Settings": [
			{
				"fieldname": "employer_pf_section",
				"label": "Employer PF Contribution",
				"fieldtype": "Section Break",
				"insert_after": "epf_establishment_code",
				"collapsible": 1,
				"collapsible_depends_on": enabled,
				"description": (
					"Employer EPF, EPS, EDLI and Admin Charges, added to the Employer Contributions table "
					"of each draft Salary Slip"
				),
			},
			{
				"fieldname": "enable_employer_pf_deduction",
				"label": "Enable Employer PF Deduction",
				"fieldtype": "Check",
				"insert_after": "employer_pf_section",
				"default": "0",
			},
			{
				"fieldname": "employer_pf_wage_ceiling",
				"label": "PF Wage Ceiling",
				"fieldtype": "Currency",
				"insert_after": "enable_employer_pf_deduction",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
				"description": "In force from the EPS Eligibility Cut-off Date",
			},
			{
				"fieldname": "employer_pf_previous_wage_ceiling",
				"label": "Previous PF Wage Ceiling",
				"fieldtype": "Currency",
				"insert_after": "employer_pf_wage_ceiling",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
				"description": (
					"In force before the cut-off date. A pay period that spans the date is split by days."
				),
			},
			{
				"fieldname": "eps_eligibility_cutoff_date",
				"label": "EPS Eligibility Cut-off Date",
				"fieldtype": "Date",
				"insert_after": "employer_pf_previous_wage_ceiling",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"description": "Transition date: the PF Wage Ceiling applies from this date",
			},
			{
				"fieldname": "employer_pf_rates_cb",
				"fieldtype": "Column Break",
				"insert_after": "eps_eligibility_cutoff_date",
			},
			{
				"fieldname": "employer_pf_rate",
				"label": "Employer EPF + EPS Share (%)",
				"fieldtype": "Percent",
				"insert_after": "employer_pf_rates_cb",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
			},
			{
				"fieldname": "employer_eps_rate",
				"label": "EPS Rate (%)",
				"fieldtype": "Percent",
				"insert_after": "employer_pf_rate",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
				"description": "On the PF wage capped at the ceiling; only for EPS Eligible employees",
			},
			{
				"fieldname": "employer_edli_rate",
				"label": "EDLI Rate (%)",
				"fieldtype": "Percent",
				"insert_after": "employer_eps_rate",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
			},
			{
				"fieldname": "employer_pf_admin_rate",
				"label": "Admin Charges Rate (%)",
				"fieldtype": "Percent",
				"insert_after": "employer_edli_rate",
				"depends_on": enabled,
				"mandatory_depends_on": enabled,
				"non_negative": 1,
			},
			{
				"fieldname": "employer_pf_components_section",
				"label": "Employer PF Components",
				"fieldtype": "Section Break",
				"insert_after": "employer_pf_admin_rate",
				"depends_on": enabled,
			},
			{
				"fieldname": "employee_pf_component",
				"label": "Employee PF Component",
				"fieldtype": "Link",
				"options": "Salary Component",
				"insert_after": "employer_pf_components_section",
				"mandatory_depends_on": enabled,
				"link_filters": '[["Salary Component", "type", "=", "Deduction"]]',
				"description": "Employer PF is calculated only on slips that deduct this component",
			},
			{
				"fieldname": "employer_epf_component",
				"label": "Employer EPF Component (A/c 1)",
				"fieldtype": "Link",
				"options": "Salary Component",
				"insert_after": "employee_pf_component",
				"mandatory_depends_on": enabled,
				"link_filters": employer_contribution,
			},
			{
				"fieldname": "employer_pf_components_cb",
				"fieldtype": "Column Break",
				"insert_after": "employer_epf_component",
			},
			{
				"fieldname": "employer_eps_component",
				"label": "Employer EPS Component (A/c 10)",
				"fieldtype": "Link",
				"options": "Salary Component",
				"insert_after": "employer_pf_components_cb",
				"mandatory_depends_on": enabled,
				"link_filters": employer_contribution,
			},
			{
				"fieldname": "employer_edli_component",
				"label": "EDLI Component (A/c 21)",
				"fieldtype": "Link",
				"options": "Salary Component",
				"insert_after": "employer_eps_component",
				"mandatory_depends_on": enabled,
				"link_filters": employer_contribution,
			},
			{
				"fieldname": "employer_pf_admin_component",
				"label": "EPF Admin Charges Component (A/c 2)",
				"fieldtype": "Link",
				"options": "Salary Component",
				"insert_after": "employer_edli_component",
				"mandatory_depends_on": enabled,
				"link_filters": employer_contribution,
			},
		],
		"Salary Structure Assignment": [
			{
				"fieldname": "eps_eligible",
				"label": "EPS Eligible",
				"fieldtype": "Check",
				"insert_after": "contribute_on_actual_pf_wage",
				"default": "1",
				"allow_on_submit": 1,
				"description": (
					"EPS (pension) member: the PF wage was within the ceiling on the date of joining or "
					"on the EPS Eligibility Cut-off Date. Members stay members if the wage later exceeds "
					"it. Never changed automatically."
				),
			},
			{
				"fieldname": "joint_declaration_on_file",
				"label": "Para 26(6) Joint Declaration on File",
				"fieldtype": "Check",
				"insert_after": "eps_eligible",
				"default": "0",
				"allow_on_submit": 1,
				"depends_on": "eval:doc.contribute_on_actual_pf_wage",
				"description": (
					"The joint employee and employer request to contribute on the actual PF wage, "
					"under Para 26(6) of the EPF Scheme, has been received"
				),
			},
		],
		"Salary Slip": [
			{
				"fieldname": "pf_wage_considered",
				"label": "PF Wage Considered",
				"fieldtype": "Currency",
				"options": "currency",
				"insert_after": "employer_contributions",
				"read_only": 1,
				"no_copy": 1,
				"depends_on": "eval:doc.total_employer_pf_cost",
				"description": (
					"PF wage on which EPF and Admin Charges are calculated: capped at the ceiling, or the "
					"actual wage with Contribute on Actual PF Wage. EPS and EDLI always use the capped wage."
				),
			},
			{
				"fieldname": "employer_pf_totals_cb",
				"fieldtype": "Column Break",
				"insert_after": "pf_wage_considered",
				"depends_on": "eval:doc.total_employer_pf_cost",
			},
			{
				"fieldname": "total_employer_pf_cost",
				"label": "Total Employer PF Cost",
				"fieldtype": "Currency",
				"options": "currency",
				"insert_after": "employer_pf_totals_cb",
				"read_only": 1,
				"no_copy": 1,
				"depends_on": "eval:doc.total_employer_pf_cost",
				"description": "Employer EPF + EPS + EDLI + Admin Charges",
			},
			{
				"fieldname": "pf_credited_to_employee_account",
				"label": "Credited to Employee PF Account",
				"fieldtype": "Currency",
				"options": "currency",
				"insert_after": "total_employer_pf_cost",
				"read_only": 1,
				"no_copy": 1,
				"depends_on": "eval:doc.total_employer_pf_cost",
				"description": "Employee 12% + Employer EPF",
			},
		],
	}
