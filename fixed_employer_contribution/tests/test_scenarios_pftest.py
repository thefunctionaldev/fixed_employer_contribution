import datetime
from decimal import Decimal
import json
import sys
import frappe
from frappe.utils import flt, getdate

EXPECTED_SCENARIOS = [
	{
		"scenario": 1,
		"pf_wage": 10000,
		"eps_member": "Y",
		"pf_wage_considered": 10000,
		"eps_wage": 10000,
		"employee_epf": 1200,
		"employer_eps": 833,
		"employer_epf": 367,
		"edli": 50,
		"admin": 50,
		"total_employer_cost": 1300,
		"total_ecr": 2500,
		"credited_to_pf_account": 1567,
	},
	{
		"scenario": 2,
		"pf_wage": 12000,
		"eps_member": "Y",
		"pf_wage_considered": 12000,
		"eps_wage": 12000,
		"employee_epf": 1440,
		"employer_eps": 1000,
		"employer_epf": 440,
		"edli": 60,
		"admin": 60,
		"total_employer_cost": 1560,
		"total_ecr": 3000,
		"credited_to_pf_account": 1880,
	},
	{
		"scenario": 3,
		"pf_wage": 15000,
		"eps_member": "Y",
		"pf_wage_considered": 15000,
		"eps_wage": 15000,
		"employee_epf": 1800,
		"employer_eps": 1250,
		"employer_epf": 550,
		"edli": 75,
		"admin": 75,
		"total_employer_cost": 1950,
		"total_ecr": 3750,
		"credited_to_pf_account": 2350,
	},
	{
		"scenario": 4,
		"pf_wage": 18000,
		"eps_member": "Y",
		"pf_wage_considered": 18000,
		"eps_wage": 18000,
		"employee_epf": 2160,
		"employer_eps": 1499,
		"employer_epf": 661,
		"edli": 90,
		"admin": 90,
		"total_employer_cost": 2340,
		"total_ecr": 4500,
		"credited_to_pf_account": 2821,
	},
	{
		"scenario": 5,
		"pf_wage": 20000,
		"eps_member": "Y",
		"pf_wage_considered": 20000,
		"eps_wage": 20000,
		"employee_epf": 2400,
		"employer_eps": 1666,
		"employer_epf": 734,
		"edli": 100,
		"admin": 100,
		"total_employer_cost": 2600,
		"total_ecr": 5000,
		"credited_to_pf_account": 3134,
	},
	{
		"scenario": 6,
		"pf_wage": 22000,
		"eps_member": "Y",
		"pf_wage_considered": 22000,
		"eps_wage": 22000,
		"employee_epf": 2640,
		"employer_eps": 1833,
		"employer_epf": 807,
		"edli": 110,
		"admin": 110,
		"total_employer_cost": 2860,
		"total_ecr": 5500,
		"credited_to_pf_account": 3447,
	},
	{
		"scenario": 7,
		"pf_wage": 25000,
		"eps_member": "Y",
		"pf_wage_considered": 25000,
		"eps_wage": 25000,
		"employee_epf": 3000,
		"employer_eps": 2083,
		"employer_epf": 917,
		"edli": 125,
		"admin": 125,
		"total_employer_cost": 3250,
		"total_ecr": 6250,
		"credited_to_pf_account": 3917,
	},
	{
		"scenario": 8,
		"pf_wage": 30000,
		"eps_member": "Y",
		"pf_wage_considered": 25000,
		"eps_wage": 25000,
		"employee_epf": 3000,
		"employer_eps": 2083,
		"employer_epf": 917,
		"edli": 125,
		"admin": 125,
		"total_employer_cost": 3250,
		"total_ecr": 6250,
		"credited_to_pf_account": 3917,
	},
	{
		"scenario": 9,
		"pf_wage": 30000,
		"eps_member": "N",
		"pf_wage_considered": 25000,
		"eps_wage": "-",
		"employee_epf": 3000,
		"employer_eps": "-",
		"employer_epf": 3000,
		"edli": 125,
		"admin": 125,
		"total_employer_cost": 3250,
		"total_ecr": 6250,
		"credited_to_pf_account": 6000,
	},
	{
		"scenario": 10,
		"pf_wage": 35000,
		"eps_member": "N",
		"pf_wage_considered": 25000,
		"eps_wage": "-",
		"employee_epf": 3000,
		"employer_eps": "-",
		"employer_epf": 3000,
		"edli": 125,
		"admin": 125,
		"total_employer_cost": 3250,
		"total_ecr": 6250,
		"credited_to_pf_account": 6000,
	},
	{
		"scenario": 11,
		"pf_wage": 50000,
		"eps_member": "N",
		"pf_wage_considered": 25000,
		"eps_wage": "-",
		"employee_epf": 3000,
		"employer_eps": "-",
		"employer_epf": 3000,
		"edli": 125,
		"admin": 125,
		"total_employer_cost": 3250,
		"total_ecr": 6250,
		"credited_to_pf_account": 6000,
	},
]


def ensure_setup(company_name="PF Test Company"):
	if not frappe.db.exists("Company", company_name):
		c = frappe.new_doc("Company")
		c.company_name = company_name
		c.country = "India"
		c.default_currency = "INR"
		c.insert(ignore_permissions=True)

	frappe.db.set_value("Company", company_name, "default_holiday_list", "test")
	frappe.db.set_single_value("Payroll Settings", "employer_pf_wage_ceiling", 25000)
	frappe.db.set_single_value("Payroll Settings", "enable_employer_pf_deduction", 1)

	# Ensure Salary Structure
	struct_name = "PF_Test_Structure"
	if not frappe.db.exists("Salary Structure", struct_name):
		ss = frappe.new_doc("Salary Structure")
		ss.name = struct_name
		ss.salary_structure_name = struct_name
		ss.company = company_name
		ss.currency = "INR"
		ss.payroll_frequency = "Monthly"
		ss.append("earnings", {
			"salary_component": "Basic",
			"amount_based_on_formula": 1,
			"formula": "base",
			"idx": 1
		})
		ss.insert(ignore_permissions=True)
		ss.submit()

	frappe.db.commit()
	return company_name, struct_name


def get_or_create_employee(emp_id, first_name, joining_date="2026-01-01", company="PF Test Company"):
	if frappe.db.exists("Employee", emp_id):
		return frappe.get_doc("Employee", emp_id)

	emp = frappe.new_doc("Employee")
	emp.name = emp_id
	emp.employee = emp_id
	emp.first_name = first_name
	emp.gender = "Female" if "Female" in first_name else "Male"
	emp.date_of_birth = "1995-01-01"
	emp.date_of_joining = joining_date
	emp.company = company
	emp.holiday_list = "test"
	emp.insert(ignore_permissions=True)

	# Assign holiday list
	if not frappe.db.exists("Holiday List Assignment", {"assigned_to": emp.name}):
		hla = frappe.new_doc("Holiday List Assignment")
		hla.applicable_for = "Employee"
		hla.assigned_to = emp.name
		hla.holiday_list = "test"
		hla.from_date = "2026-01-01"
		hla.insert(ignore_permissions=True)
		hla.submit()

	frappe.db.commit()
	return emp


def create_assignment(employee, structure, wage, eps_eligible, from_date="2026-10-01", company="PF Test Company"):
	# Cancel existing assignments if any
	old_ssas = frappe.get_all("Salary Structure Assignment", filters={"employee": employee, "docstatus": 1})
	for s in old_ssas:
		doc = frappe.get_doc("Salary Structure Assignment", s.name)
		doc.cancel()

	ssa = frappe.new_doc("Salary Structure Assignment")
	ssa.employee = employee
	ssa.company = company
	ssa.currency = "INR"
	ssa.employment_state = "Karnataka"
	ssa.salary_structure = structure
	ssa.from_date = from_date
	ssa.epf_applicable = 1
	ssa.eps_eligible = 1 if eps_eligible == "Y" else 0
	ssa.contribute_on_actual_pf_wage = 0
	ssa.base = wage
	ssa.insert(ignore_permissions=True)
	ssa.submit()
	frappe.db.commit()
	return ssa


def create_salary_slip(employee, structure, start_date="2026-10-01", end_date="2026-10-31", company="PF Test Company", **extra):
	# Cancel existing slips for this period if any
	old_slips = frappe.get_all("Salary Slip", filters={"employee": employee, "start_date": start_date, "end_date": end_date})
	for s in old_slips:
		doc = frappe.get_doc("Salary Slip", s.name)
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Salary Slip", s.name, force=True)

	slip = frappe.new_doc("Salary Slip")
	slip.employee = employee
	slip.company = company
	slip.salary_structure = structure
	slip.start_date = start_date
	slip.end_date = end_date
	slip.posting_date = end_date
	slip.payroll_frequency = "Monthly"
	for k, v in extra.items():
		setattr(slip, k, v)

	slip.insert(ignore_permissions=True)
	frappe.db.commit()
	return slip


def extract_actual_values(slip, eps_member):
	deductions = {r.salary_component: r.amount for r in slip.deductions}
	employer_contribs = {r.salary_component: r.amount for r in slip.employer_contributions}
	earnings = {r.salary_component: r.amount for r in slip.earnings}

	pf_wage = int(round(earnings.get("Basic", 0)))
	ee_epf = int(round(deductions.get("Provident Fund", 0)))
	er_eps = int(round(employer_contribs.get("Employer Pension Scheme", 0)))
	er_epf = int(round(employer_contribs.get("Employer Provident Fund", 0)))
	edli = int(round(employer_contribs.get("Employees Deposit Linked Insurance", 0)))
	admin = int(round(employer_contribs.get("EPF Admin Charges", 0)))

	pf_wage_considered = int(round(slip.pf_wage_considered or 0))
	eps_wage = pf_wage_considered if eps_member == "Y" else "-"
	er_eps_val = er_eps if eps_member == "Y" else "-"
	total_er = int(round(slip.total_employer_pf_cost or 0))
	total_ecr = ee_epf + total_er
	credited = int(round(slip.pf_credited_to_employee_account or 0))

	return {
		"pf_wage": pf_wage,
		"eps_member": eps_member,
		"pf_wage_considered": pf_wage_considered,
		"eps_wage": eps_wage,
		"employee_epf": ee_epf,
		"employer_eps": er_eps_val,
		"employer_epf": er_epf,
		"edli": edli,
		"admin": admin,
		"total_employer_cost": total_er,
		"total_ecr": total_ecr,
		"credited_to_pf_account": credited,
	}


def run_11_scenarios():
	company, structure = ensure_setup("PF Test Company")
	results = []

	for exp in EXPECTED_SCENARIOS:
		sc_num = exp["scenario"]
		emp_id = f"PF-SC-{sc_num:02d}"
		first_name = f"Scenario{sc_num}"
		emp = get_or_create_employee(emp_id, first_name, joining_date="2026-01-01", company=company)
		ssa = create_assignment(emp.name, structure, exp["pf_wage"], exp["eps_member"], company=company)
		slip = create_salary_slip(emp.name, structure, company=company)

		actual = extract_actual_values(slip, exp["eps_member"])

		# Compare against expected
		mismatches = []
		for field in [
			"pf_wage_considered", "eps_wage", "employee_epf", "employer_eps",
			"employer_epf", "edli", "admin", "total_employer_cost", "total_ecr", "credited_to_pf_account"
		]:
			if actual[field] != exp[field]:
				mismatches.append(f"{field}: expected {exp[field]} != actual {actual[field]}")

		passed = len(mismatches) == 0
		results.append({
			"scenario": sc_num,
			"expected": exp,
			"actual": actual,
			"passed": passed,
			"mismatches": mismatches,
		})

	return results


def run_edge_cases():
	company, structure = ensure_setup("PF Test Company")
	edge_results = {}

	# Edge Case a: PF Wage = 25,001, EPS = Y (just above cap)
	emp_a = get_or_create_employee("PF-EDGE-A", "EdgeA", joining_date="2026-01-01", company=company)
	create_assignment(emp_a.name, structure, 25001, "Y", company=company)
	slip_a = create_salary_slip(emp_a.name, structure, company=company)
	edge_results["a"] = extract_actual_values(slip_a, "Y")

	# Edge Case b: PF Wage = 24,999, EPS = Y (just below cap)
	emp_b = get_or_create_employee("PF-EDGE-B", "EdgeB", joining_date="2026-01-01", company=company)
	create_assignment(emp_b.name, structure, 24999, "Y", company=company)
	slip_b = create_salary_slip(emp_b.name, structure, company=company)
	edge_results["b"] = extract_actual_values(slip_b, "Y")

	# Edge Case c: Employee EPS = Y whose wage later rises from 20,000 to 30,000 via a new SSA
	emp_c = get_or_create_employee("PF-EDGE-C", "EdgeC", joining_date="2026-01-01", company=company)
	create_assignment(emp_c.name, structure, 20000, "Y", from_date="2026-01-01", company=company)
	create_assignment(emp_c.name, structure, 30000, "Y", from_date="2026-10-01", company=company)
	slip_c = create_salary_slip(emp_c.name, structure, company=company)
	edge_results["c"] = extract_actual_values(slip_c, "Y")

	# Edge Case d: Changing EPS Member from Y to N on existing assignment and regenerating slip
	emp_d = get_or_create_employee("PF-EDGE-D", "EdgeD", joining_date="2026-01-01", company=company)
	ssa_d = create_assignment(emp_d.name, structure, 30000, "Y", company=company)
	slip_d1 = create_salary_slip(emp_d.name, structure, company=company)
	val_d1 = extract_actual_values(slip_d1, "Y")

	# Now change SSA to eps_eligible = 0
	frappe.db.set_value("Salary Structure Assignment", ssa_d.name, "eps_eligible", 0)
	frappe.db.commit()
	slip_d2 = create_salary_slip(emp_d.name, structure, company=company)
	val_d2 = extract_actual_values(slip_d2, "N")
	edge_results["d"] = {"before_Y": val_d1, "after_N": val_d2}

	# Edge Case e: Re-saving, cancelling and re-creating the same Salary Slip
	emp_e = get_or_create_employee("PF-EDGE-E", "EdgeE", joining_date="2026-01-01", company=company)
	create_assignment(emp_e.name, structure, 25000, "Y", company=company)
	slip_e = create_salary_slip(emp_e.name, structure, company=company)
	rows_orig = [(r.salary_component, r.amount) for r in slip_e.employer_contributions]

	# Re-save
	slip_e.save()
	rows_resaved = [(r.salary_component, r.amount) for r in slip_e.employer_contributions]

	# Submit, cancel, re-create
	slip_e.submit()
	slip_e.cancel()
	slip_e_new = create_salary_slip(emp_e.name, structure, company=company)
	rows_recreated = [(r.salary_component, r.amount) for r in slip_e_new.employer_contributions]

	edge_results["e"] = {
		"orig_rows": len(rows_orig),
		"resaved_rows": len(rows_resaved),
		"recreated_rows": len(rows_recreated),
		"values_identical": (rows_orig == rows_resaved == rows_recreated),
		"rows": rows_orig,
	}

	# Edge Case f: Partial month (15 days LOP) for PF Wage = 20,000
	emp_f = get_or_create_employee("PF-EDGE-F", "EdgeF", joining_date="2026-01-01", company=company)
	create_assignment(emp_f.name, structure, 20000, "Y", company=company)
	slip_f = create_salary_slip(emp_f.name, structure, company=company)
	# Apply 15 days LOP so payment days is 15
	slip_f.payment_days = 15.0
	slip_f.leave_without_pay = 15.0
	slip_f.calculate_net_pay()
	slip_f.save()
	frappe.db.commit()

	edge_results["f"] = {
		"payment_days": slip_f.payment_days,
		"total_working_days": slip_f.total_working_days,
		"earned_basic": [r.amount for r in slip_f.earnings if r.salary_component == "Basic"],
		"values": extract_actual_values(slip_f, "Y"),
	}

	return edge_results


def run_all_tests():
	scenarios = run_11_scenarios()
	edges = run_edge_cases()
	output = {
		"scenarios": scenarios,
		"edge_cases": edges,
	}
	print(json.dumps(output, indent=2, default=str))
	return output


if __name__ == "__main__":
	run_all_tests()
