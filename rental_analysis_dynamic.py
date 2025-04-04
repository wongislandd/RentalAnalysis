#!/usr/bin/env python3
"""
Rental Analysis Calculator with Dynamic Expense Maps and Rent Increase

This script calculates the year-by-year details for your rental property investment.
It uses dynamic expense maps to compute:
  - Fixed monthly costs (HOA, Mortgage, Maintenance)
  - Additional monthly cash flows when occupied (based on Rental Rate, Tax Rate,
    Property Management Fee, and Random Fees)
  - Additional monthly costs when vacant (e.g., Utilities)
These are combined to determine a dynamically computed base annual cost.
The script then generates an amortization schedule for the loan and calculates cash flow metrics,
including tax benefits and “loss after principal” for either a single target year or a range of years.
It also factors in an annual rent increase (hardcoded inside the script).

Usage Examples:
    # For a single year (cash flow metrics only):
    $ python rental_analysis_dynamic.py --year 10

    # For a single year with detailed output (verbose mode):
    $ python rental_analysis_dynamic.py --year 10 --verbose

    # For a range of years (e.g., years 5 to 10):
    $ python rental_analysis_dynamic.py --year-range 5 10

    # To save verbose output for all 28 years in separate files and a summary file:
    $ python rental_analysis_dynamic.py --save-results

Note:
    The annual rent increase rate is hardcoded (default is 1% per year) in the script.
    To change it, modify the ANNUAL_RENT_INCREASE variable below.
"""

import argparse
import pandas as pd
import numpy as np
import os

# =============================================================================
# ADJUSTABLE PARAMETERS (Global Constants)
# =============================================================================

# Mortgage Details
LOAN_AMOUNT = 461698.00          # Total Loan Amount (new principal balance)
MONTHLY_PAYMENT_TOTAL = 3155.00  # Total monthly payment (Mortgage + Escrow)
MONTHLY_ESCROW = 593.92          # Monthly Escrow amount
ANNUAL_INTEREST_RATE = 0.05125   # Annual interest rate (e.g., 5.125%)
TERM_YEARS = 28                  # Loan term in years

# Annual Rent Increase (hardcoded; e.g., 0.01 = 1% per year)
ANNUAL_RENT_INCREASE = 0.01

# Expense Parameters (Dynamic Expense Maps)
FIXED_COSTS_PARAMS = {
    "annual_HOA": 1000.0,          # Annual HOA fee
    "mortgage": 3155.0,            # Monthly Mortgage payment (as positive; will be made negative)
    "annual_maintenance": 4000.0     # Annual Estimated Maintenance Cost
}
STARTING_RENTAL_RATE = 2700.0      # Starting gross monthly Rental Rate
OCCUPIED_EXPENSES_PARAMS = {
    "rental_rate": STARTING_RENTAL_RATE,  # Will be updated per year with rent increase
    "tax_rate": 0.35,              # Tax Rate for computing effective rental income
    "management_rate": 0.07,       # Property Management Rate (7%)
    "annual_random_fees": 2000.0   # Annual extra property management random fees
}
VACANT_EXPENSES_PARAMS = {
    "utilities": 100.0             # Utilities cost per month when vacant
}
VACANCY_MONTHS = 1.0             # Expected number of vacant months per year

# Tax & Other Constants
BASE_DEPRECIATION = 14938.18      # Annual Depreciation
BASE_ADDITIONAL_EXPENSES = 7800.00  # Annual Additional Expenses (e.g., management fees, maintenance)
TAX_RATE_EFFECTIVE = 0.35         # Effective Tax Rate (35%)

# =============================================================================
# Expense Calculation Functions
# =============================================================================

def compute_fixed_costs(params):
    hoa = -params["annual_HOA"] / 12
    mortgage = -params["mortgage"]
    maintenance = -params["annual_maintenance"] / 12
    return hoa + mortgage + maintenance

def compute_occupied_additional(params):
    rental_rate = params["rental_rate"]
    tax_rate = params["tax_rate"]
    management_rate = params["management_rate"]
    annual_random_fees = params["annual_random_fees"]
    effective_rental = rental_rate * (1 - tax_rate)
    management_fee = - rental_rate * management_rate
    random_fees = - annual_random_fees / 12
    return effective_rental + management_fee + random_fees

def compute_vacant_additional(params):
    utilities = params["utilities"]
    return -utilities

def compute_monthly_costs(fixed_params, occupied_params, vacant_params):
    fixed = compute_fixed_costs(fixed_params)
    occupied_additional = compute_occupied_additional(occupied_params)
    vacant_additional = compute_vacant_additional(vacant_params)
    monthly_when_occupied = fixed + occupied_additional
    monthly_when_vacant = fixed + vacant_additional
    return monthly_when_occupied, monthly_when_vacant

def compute_base_annual_cost(monthly_occupied, monthly_vacant, vacancy_months):
    occupied_months = 12 - vacancy_months
    return occupied_months * monthly_occupied + vacancy_months * monthly_when_vacant if False else \
           occupied_months * monthly_occupied + vacancy_months * monthly_vacant

# =============================================================================
# Mortgage and Cash Flow Functions
# =============================================================================

def calculate_monthly_payment(principal, annual_interest_rate, term_years):
    r = annual_interest_rate / 12
    n = term_years * 12
    payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return payment

def generate_amortization_schedule(principal, annual_interest_rate, term_years, monthly_payment):
    monthly_rate = annual_interest_rate / 12
    months = term_years * 12
    schedule = []
    remaining_balance = principal
    for month in range(1, months + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        if remaining_balance < 0:
            principal_payment += remaining_balance
            remaining_balance = 0
        schedule.append({
            "Month": month,
            "Year": (month - 1) // 12 + 1,
            "Interest Paid": interest_payment,
            "Principal Paid": principal_payment,
            "Remaining Balance": remaining_balance
        })
    return pd.DataFrame(schedule)

def aggregate_yearly(schedule_df):
    df_yearly = schedule_df.groupby("Year").agg({
        "Interest Paid": "sum",
        "Principal Paid": "sum"
    }).reset_index()
    df_yearly["Cumulative Principal"] = df_yearly["Principal Paid"].cumsum()
    df_yearly["Cumulative Interest"] = df_yearly["Interest Paid"].cumsum()
    df_yearly["Avg Monthly Interest"] = df_yearly["Interest Paid"] / 12
    df_yearly["Avg Monthly Principal"] = df_yearly["Principal Paid"] / 12
    return df_yearly.round(2)

def compute_annual_cash_flow(year_data, constants):
    base_cost = constants["base_annual_cost"]
    depreciation = constants["depreciation"]
    additional_expenses = constants["additional_expenses"]
    tax_rate = constants["tax_rate"]
    tax_refund = tax_rate * (year_data["Interest Paid"] + depreciation + additional_expenses)
    net_out_of_pocket = base_cost + tax_refund
    loss_after_principal = net_out_of_pocket + year_data["Principal Paid"]
    return tax_refund, net_out_of_pocket, loss_after_principal

# =============================================================================
# Analysis Function
# =============================================================================

def analyze_years(target_years):
    # Calculate monthly payment (principal+interest)
    monthly_pi = MONTHLY_PAYMENT_TOTAL - MONTHLY_ESCROW
    schedule_df = generate_amortization_schedule(LOAN_AMOUNT, ANNUAL_INTEREST_RATE, TERM_YEARS, monthly_pi)
    df_yearly = aggregate_yearly(schedule_df)
    results = []
    verbose_outputs = {}
    for yr in target_years:
        effective_rental_rate = STARTING_RENTAL_RATE * ((1 + ANNUAL_RENT_INCREASE) ** (yr - 1))
        occ_params = OCCUPIED_EXPENSES_PARAMS.copy()
        occ_params["rental_rate"] = effective_rental_rate
        monthly_when_occupied, monthly_when_vacant = compute_monthly_costs(FIXED_COSTS_PARAMS, occ_params, VACANT_EXPENSES_PARAMS)
        base_annual_cost = compute_base_annual_cost(monthly_when_occupied, monthly_when_vacant, VACANCY_MONTHS)
        year_data = df_yearly[df_yearly["Year"] == yr].iloc[0]
        constants = {
            "base_annual_cost": base_annual_cost,
            "depreciation": BASE_DEPRECIATION,
            "additional_expenses": BASE_ADDITIONAL_EXPENSES,
            "tax_rate": TAX_RATE_EFFECTIVE
        }
        tax_refund, net_out_of_pocket, loss_after_principal = compute_annual_cash_flow(year_data, constants)
        results.append({
            "Year": yr,
            "Effective Rental Rate": effective_rental_rate,
            "Base Annual Cost": base_annual_cost,
            "Annual Tax Refund": tax_refund,
            "Annual Out-of-Pocket": net_out_of_pocket,
            "Annual Loss After Principal": loss_after_principal
        })
        # Build verbose output for this year
        verbose_lines = []
        verbose_lines.append(f"--- Rental Analysis Details for Year {yr} ---\n")
        verbose_lines.append("Mortgage Details:")
        verbose_lines.append(f"  Monthly Payment (Principal+Interest): ${monthly_pi:.2f}")
        verbose_lines.append(f"  Monthly Escrow: ${MONTHLY_ESCROW:.2f}")
        verbose_lines.append(f"  Total Monthly Payment: ${MONTHLY_PAYMENT_TOTAL:.2f}\n")
        verbose_lines.append("Amortization (Yearly Totals):")
        verbose_lines.append(f"  Annual Interest Paid: ${year_data['Interest Paid']:.2f}")
        verbose_lines.append(f"  Annual Principal Paid: ${year_data['Principal Paid']:.2f}")
        verbose_lines.append(f"  Cumulative Principal Paid: ${year_data['Cumulative Principal']:.2f}")
        verbose_lines.append(f"  Cumulative Interest Paid: ${year_data['Cumulative Interest']:.2f}\n")
        verbose_lines.append("Dynamic Expense Calculations:")
        verbose_lines.append(f"  Fixed Costs (per month): ${compute_fixed_costs(FIXED_COSTS_PARAMS):.2f}")
        verbose_lines.append(f"  Additional (Occupied): ${compute_occupied_additional(occ_params):.2f}")
        verbose_lines.append(f"  Additional (Vacant): ${compute_vacant_additional(VACANT_EXPENSES_PARAMS):.2f}")
        verbose_lines.append(f"  Monthly When Occupied: ${monthly_when_occupied:.2f}")
        verbose_lines.append(f"  Monthly When Vacant: ${monthly_when_vacant:.2f}")
        verbose_lines.append(f"  Calculated Base Annual Cost: ${base_annual_cost:.2f}\n")
        verbose_lines.append("Cash Flow Metrics for the Year:")
        verbose_lines.append(f"  Effective Rental Rate: ${effective_rental_rate:.2f}")
        verbose_lines.append(f"  Estimated Annual Tax Refund: ${tax_refund:.2f}")
        verbose_lines.append(f"  Annual Out-of-Pocket After Tax Refund: ${net_out_of_pocket:.2f}")
        verbose_lines.append(f"  Annual Loss After Considering Principal: ${loss_after_principal:.2f}\n")
        verbose_lines.append("Assumptions:")
        verbose_lines.append(f"  Vacancy Months per Year: {VACANCY_MONTHS}")
        verbose_lines.append(f"  Annual Depreciation: ${BASE_DEPRECIATION:.2f}")
        verbose_lines.append(f"  Annual Additional Expenses: ${BASE_ADDITIONAL_EXPENSES:.2f}")
        verbose_lines.append(f"  Tax Rate: {TAX_RATE_EFFECTIVE * 100:.0f}%\n")
        verbose_lines.append("------------------------------------------------------------\n")
        verbose_outputs[yr] = "\n".join(verbose_lines)
    return results, verbose_outputs

# =============================================================================
# Main Routine
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Rental Analysis Calculator with Dynamic Expense Maps and Rent Increase")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--year", type=int, help="Target single year (1 to term) for details.")
    group.add_argument("--year-range", nargs=2, type=int, metavar=('START', 'END'),
                       help="Target range of years (inclusive) for details, e.g., --year-range 5 10.")
    group.add_argument("--save-results", action="store_true",
                       help="Save verbose output for years 1-28 in separate files and a summary table.")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output (only applicable for single year output).")
    args = parser.parse_args()

    # If --save-results is specified, we ignore any other year parameters and generate for all years.
    if args.save_results:
        target_years = list(range(1, TERM_YEARS + 1))
    elif args.year:
        target_years = [args.year]
    else:
        start_year, end_year = args.year_range
        if start_year < 1 or end_year > TERM_YEARS or start_year > end_year:
            print(f"Please provide a valid year range between 1 and {TERM_YEARS}.")
            return
        target_years = list(range(start_year, end_year + 1))

    results, verbose_outputs = analyze_years(target_years)
    results_df = pd.DataFrame(results).set_index("Year")

    if args.save_results:
        os.makedirs("results", exist_ok=True)
        # Save a separate verbose file for each year 1-28
        for yr in range(1, TERM_YEARS + 1):
            filename = os.path.join("results", f"year_{yr}.txt")
            with open(filename, "w") as f:
                f.write(verbose_outputs[yr])
        # Save summary table (non-verbose) for all years 1-28
        summary_filename = os.path.join("results", "summary.txt")
        with open(summary_filename, "w") as f:
            f.write(results_df.to_string(float_format="%.2f"))
        print("Verbose output for years 1-28 saved as individual files in the 'results' directory.")
        print("Summary table saved as 'results/summary.txt'.")
        return

    if len(target_years) == 1 and args.verbose:
        yr = target_years[0]
        print(verbose_outputs[yr])
    else:
        print("--- Cash Flow Metrics ---")
        print(results_df.to_string(float_format="%.2f"))

if __name__ == "__main__":
    main()
