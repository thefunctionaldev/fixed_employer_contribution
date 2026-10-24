import frappe
from fixed_employer_contribution.setup import set_employer_pf_defaults


def execute():
	set_employer_pf_defaults()
