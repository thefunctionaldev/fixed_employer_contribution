# Fixed Employer Contribution

Automate Indian statutory employer PF contributions (Employer EPF, EPS, EDLI, and Admin Charges) directly on Salary Slips in **Frappe HR + India Payroll** (v16).

---

## The Problem Solved

In standard Frappe HR + India Payroll, employee deductions for EPF and VPF are automated, but **Employer Contributions** (Employer EPF, EPS, EDLI, and Admin Charges) were left as fixed amounts on the Salary Structure or required manual calculation on every salary slip.

**Fixed Employer Contribution** completely automates this:
1. Calculates **PF Wages** from earned Basic and DA (taking payment days and Loss of Pay into account).
2. Calculates **EPS** (8.33% capped at ₹25,000 / ₹15,000 statutory ceiling).
3. Calculates **Employer EPF** (rounded 12% minus EPS, strictly following EPFO half-up rounding rules).
4. Calculates **EDLI** (0.5% capped at wage ceiling) and **EPF Admin Charges** (0.5% on PF wage).
5. Injects the 4 lines into the `Employer Contributions` table and updates total employer PF cost and credit on the draft Salary Slip.

---

## Prerequisites

- **Frappe** (v16+)
- **ERPNext** (v16+)
- **HRMS** (v16+)
- **India Payroll / India Compliance** (v16+)

---

## Installation

```bash
bench get-app https://github.com/thefunctionaldev/fixed_employer_contribution.git
bench --site <your-site> install-app fixed_employer_contribution
bench --site <your-site> migrate
```

---

## Configuration

### 1. Payroll Settings (`India Payroll` Tab)
Navigate to **Payroll Settings > India Payroll**:
- Check **Enable Employer PF Deduction**.
- Confirm or adjust statutory ceilings:
  - **PF Wage Ceiling**: `₹25,000` (revised statutory ceiling)
  - **Previous PF Wage Ceiling**: `₹15,000`
  - **EPS Eligibility Cut-off Date**: `2026-09-17`
  - **Rates**: Employer PF: `12%`, EPS: `8.33%`, EDLI: `0.5%`, Admin Charges: `0.5%`.
- Ensure the 4 employer contribution Salary Components are linked:
  - `Employer Provident Fund` (A/c 1)
  - `Employer Pension Scheme` (A/c 10)
  - `Employees Deposit Linked Insurance` (A/c 21)
  - `EPF Admin Charges` (A/c 2)

### 2. Salary Structure Assignment (`India Payroll` Tab)
- **EPS Eligible**: Check if the employee is eligible for the EPS pension diversion (default: Yes).
- **Contribute on Actual PF Wage**: Check if the employer contributes on the actual PF wage exceeding the ceiling under Para 26(6).
- **Para 26(6) Joint Declaration on File**: Check when the joint declaration is on file.

---

## License

MIT License. See [license.txt](license.txt) for details.
