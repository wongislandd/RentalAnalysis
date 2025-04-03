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
"""

import argparse
import pandas as pd
import numpy as np

# ------------------------------
# Expense Calculation Functions
# ------------------------------

def compute_fixed_costs(params):
    """
    Fixed costs occur regardless of occupancy.
    Returns the sum of:
      HOA (annual fee/12), Mortgage (monthly, negative), Maintenance (annual/12)
    """
    hoa = -params["annual_HOA"] / 12
    mortgage = -params["mortgage"]  # monthly mortgage cost (negative)
    maintenance = -params["annual_maintenance"] / 12
    return hoa + mortgage + maintenance

def compute_occupied_additional(params):
    """
    Additional cash flow when occupied.
    Returns effective rental income (post-tax) plus negative fees.
    """
    rental_rate = params["rental_rate"]
    tax_rate = params["tax_rate"]
    management_rate = params["management_rate"]
    annual_random_fees = params["annual_random_fees"]

    effective_rental = rental_rate * (1 - tax_rate)  # e.g., 2700 * 0.65 = 1755
    management_fee = - rental_rate * management_rate   # e.g., -2700 * 0.07 = -189
    random_fees = - annual_random_fees / 12             # e.g., -2000/12 = -166.67
    return effective_rental + management_fee + random_fees

def compute_vacant_additional(params):
    """
    Additional costs when vacant.
    Returns the utilities cost as a negative number.
    """
    utilities = params["utilities"]
    return -utilities

def compute_monthly_costs(fixed_params, occupied_params, vacant_params):
    """
    Compute the monthly cash flow when occupied and when vacant.
    """
    fixed = compute_fixed_costs(fixed_params)
    occupied_additional = compute_occupied_additional(occupied_params)
    vacant_additional = compute_vacant_additional(vacant_params)
    monthly_when_occupied = fixed + occupied_additional
    monthly_when_vacant = fixed + vacant_additional
    return monthly_when_occupied, monthly_when_vacant

def compute_base_annual_cost(monthly_occupied, monthly_vacant, vacancy_months):
    """
    Base Annual Cost = (occupied months * monthly_when_occupied) +
                        (vacant months * monthly_when_vacant)
    """
    occupied_months = 12 - vacancy_months
    return occupied_months * monthly_occupied + vacancy_months * monthly_when_vacant

# ------------------------------
# Mortgage and Cash Flow Functions
# ------------------------------

def calculate_monthly_payment(principal, annual_interest_rate, term_years):
    """Calculate the monthly principal+interest payment using the amortization formula."""
    r = annual_interest_rate / 12
    n = term_years * 12
    payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return payment

def generate_amortization_schedule(principal, annual_interest_rate, term_years, monthly_payment):
    """Generate an amortization schedule (for principal+interest, excluding escrow)."""
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
    """Aggregate the monthly amortization schedule by year."""
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
    """
    Compute cash flow metrics for a given year:
      - Tax refund: tax_rate * (Interest Paid + Depreciation + Additional Expenses)
      - Net annual out-of-pocket cost: base_annual_cost + tax refund
      - Annual loss after considering principal: net out-of-pocket + Principal Paid
    """
    base_cost = constants["base_annual_cost"]
    depreciation = constants["depreciation"]
    additional_expenses = constants["additional_expenses"]
    tax_rate = constants["tax_rate"]

    tax_refund = tax_rate * (year_data["Interest Paid"] + depreciation + additional_expenses)
    net_out_of_pocket = base_cost + tax_refund
    loss_after_principal = net_out_of_pocket + year_data["Principal Paid"]
    return tax_refund, net_out_of_pocket, loss_after_principal

# ------------------------------
# Main Routine
# ------------------------------

def main():
    parser = argparse.ArgumentParser(description="Rental Analysis Calculator with Dynamic Expense Maps and Rent Increase")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--year", type=int, help="Target single year (1 to term) for details.")
    group.add_argument("--year-range", nargs=2, type=int, metavar=('START', 'END'),
                       help="Target range of years (inclusive) for details, e.g., --year-range 5 10.")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output (only applicable for single year output).")
    args = parser.parse_args()

    # Hardcoded annual rent increase rate (e.g., 1% per year)
    annual_rent_increase = 0.01

    # ----- Input Variables -----
    # Mortgage details:
    # New principal balance:
    loan_amount = 461698.00  # Total Loan Amount
    monthly_payment_total = 3155.00  # Total monthly payment (Mortgage + Escrow)
    monthly_escrow = 593.92  # Monthly Escrow
    monthly_pi = monthly_payment_total - monthly_escrow  # Payment toward principal+interest

    annual_interest_rate = 0.05125  # Annual interest rate (5.125%)
    term_years = 28

    # Expense parameters (dynamic maps)
    fixed_costs_params = {
        "annual_HOA": 1000.0,           # Annual HOA fee
        "mortgage": 3155.0,             # Monthly Mortgage payment (as positive; will be made negative)
        "annual_maintenance": 4000.0      # Annual Estimated Maintenance Cost
    }
    starting_rental_rate = 2700.0
    occupied_expenses_params = {
        "rental_rate": starting_rental_rate,  # Will be updated per year
        "tax_rate": 0.35,              # Tax Rate for computing effective rental income
        "management_rate": 0.07,       # Property Management Rate (7%)
        "annual_random_fees": 2000.0   # Annual extra property management random fees
    }
    vacant_expenses_params = {
        "utilities": 100.0             # Utilities cost per month when vacant
    }
    vacancy_months = 1.0  # Expected number of vacant months per year

    # ----- Mortgage Amortization Schedule -----
    schedule_df = generate_amortization_schedule(loan_amount, annual_interest_rate, term_years, monthly_pi)
    df_yearly = aggregate_yearly(schedule_df)

    # ----- Tax and Other Constants (from your sheet) -----
    base_depreciation = 14938.18      # Annual Depreciation
    base_additional_expenses = 7800.00  # Annual Additional Expenses
    tax_rate_effective = 0.35         # Effective Tax Rate: 35%

    # Prepare to collect results
    results = []

    # Determine target years
    if args.year:
        target_years = [args.year]
    else:
        start_year, end_year = args.year_range
        if start_year < 1 or end_year > term_years or start_year > end_year:
            print(f"Please provide a valid year range between 1 and {term_years}.")
            return
        target_years = list(range(start_year, end_year + 1))

    # For each target year, update the effective rental rate with the annual increase.
    for yr in target_years:
        effective_rental_rate = starting_rental_rate * ((1 + annual_rent_increase) ** (yr - 1))
        occ_params = occupied_expenses_params.copy()
        occ_params["rental_rate"] = effective_rental_rate

        monthly_when_occupied, monthly_when_vacant = compute_monthly_costs(fixed_costs_params, occ_params, vacant_expenses_params)
        base_annual_cost = compute_base_annual_cost(monthly_when_occupied, monthly_when_vacant, vacancy_months)

        year_data = df_yearly[df_yearly["Year"] == yr].iloc[0]
        constants = {
            "base_annual_cost": base_annual_cost,
            "depreciation": base_depreciation,
            "additional_expenses": base_additional_expenses,
            "tax_rate": tax_rate_effective
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

    results_df = pd.DataFrame(results).set_index("Year")

    # Output results
    if len(target_years) == 1 and args.verbose:
        yr = target_years[0]
        print(f"--- Rental Analysis Details for Year {yr} ---\n")
        print("Mortgage Details:")
        print(f"  Monthly Payment (Principal+Interest): ${monthly_pi:.2f}")
        print(f"  Monthly Escrow: ${monthly_escrow:.2f}")
        print(f"  Total Monthly Payment: ${monthly_payment_total:.2f}\n")
        year_data = df_yearly[df_yearly["Year"] == yr].iloc[0]
        print("Amortization (Yearly Totals):")
        print(f"  Annual Interest Paid: ${year_data['Interest Paid']:.2f}")
        print(f"  Annual Principal Paid: ${year_data['Principal Paid']:.2f}")
        print(f"  Cumulative Principal Paid: ${year_data['Cumulative Principal']:.2f}")
        print(f"  Cumulative Interest Paid: ${year_data['Cumulative Interest']:.2f}\n")
        print("Dynamic Expense Calculations:")
        print(f"  Fixed Costs (per month): ${compute_fixed_costs(fixed_costs_params):.2f}")
        print(f"  Additional (Occupied): ${compute_occupied_additional(occ_params):.2f}")
        print(f"  Additional (Vacant): ${compute_vacant_additional(vacant_expenses_params):.2f}")
        print(f"  Monthly When Occupied: ${monthly_when_occupied:.2f}")
        print(f"  Monthly When Vacant: ${monthly_when_vacant:.2f}")
        print(f"  Calculated Base Annual Cost: ${base_annual_cost:.2f}\n")
        print("Cash Flow Metrics for the Year:")
        print(f"  Effective Rental Rate: ${effective_rental_rate:.2f}")
        print(f"  Estimated Annual Tax Refund: ${tax_refund:.2f}")
        print(f"  Annual Out-of-Pocket After Tax Refund: ${net_out_of_pocket:.2f}")
        print(f"  Annual Loss After Considering Principal: ${loss_after_principal:.2f}\n")
        print("Assumptions:")
        print(f"  Vacancy Months per Year: {vacancy_months}")
        print(f"  Annual Depreciation: ${base_depreciation:.2f}")
        print(f"  Annual Additional Expenses: ${base_additional_expenses:.2f}")
        print(f"  Tax Rate: {tax_rate_effective * 100:.0f}%")
    else:
        print("--- Cash Flow Metrics ---")
        print(results_df.to_string(float_format="%.2f"))

if __name__ == "__main__":
    main()
