# Rental Analysis Calculator with Dynamic Expense Maps

This repository contains a Python script that calculates the year-by-year details for a rental property investment. The script uses dynamic expense maps to compute:

- **Fixed Monthly Costs** (e.g., HOA, Mortgage, Maintenance)
- **Additional Monthly Cash Flows When Occupied** (based on Rental Rate, Tax Rate, Property Management Fee, and Random Fees)
- **Additional Monthly Costs When Vacant** (e.g., Utilities)

These values are combined to determine a dynamically computed base annual cost. The script then generates a mortgage amortization schedule and calculates cash flow metrics (including tax benefits and “loss after principal”) for a specified year or range of years. Additionally, it factors in an annual rent increase (which is hardcoded by default).

## Features

- **Dynamic Expense Maps:** Easily adjust fixed costs, occupied expenses, and vacant expenses.
- **Mortgage Amortization Schedule:** Calculates the breakdown of principal and interest payments over the life of the loan.
- **Cash Flow Metrics:** Computes tax refunds, net out-of-pocket costs, and effective losses (or gains) after principal.
- **Rent Increase Factor:** Automatically applies an annual rent increase (default is 1% per year) to update rental income and expenses.
- **Flexible Output:** Run the script for a single target year or a range of years, with an option for detailed (verbose) output.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/rental-analysis-calculator.git
   cd rental-analysis-calculator
   ```

2. Ensure you have Python 3 installed.
  This script uses only standard Python libraries (e.g., argparse, pandas), so no additional packages are required apart from Pandas. To install Pandas, run:
   ```bash
    pip install pandas
   ```

## Usage
You can run the script from the command line. There are three main ways to call it:

1. Single Year (Cash Flow Metrics Only)
```bash
python rental_analysis_dynamic.py --year 10
This command displays the cash flow metrics for Year 10.
```

2. Single Year with Detailed Output (Verbose Mode)
```bash
python rental_analysis_dynamic.py --year 10 --verbose
```
This prints a detailed breakdown including mortgage details, amortization summary, dynamic expense calculations, and cash flow metrics for Year 10.

3. Range of Years
```bash
python rental_analysis_dynamic.py --year-range 5 10
```

This outputs a table of cash flow metrics for each year from 5 through 10, factoring in the annual rent increase.

## Note:
The annual rent increase rate is hardcoded (default is 1% per year) in the script. To simulate a different rate, modify the ANNUAL_RENT_INCREASE variable in the source code.

## Configuration
- At the top of rental_analysis_dynamic.py, you will find a section labeled Adjustable Parameters. Here you can modify:
- Mortgage Details: Loan amount, monthly payment (Mortgage + Escrow), interest rate, and term.
- Expense Parameters: Fixed costs (e.g., HOA, maintenance), occupied expenses (e.g., rental rate, management fees), vacant expenses (e.g., utilities), and the number of vacancy months.
- Tax & Other Constants: Annual depreciation, additional expenses, and effective tax rate.
- Annual Rent Increase: Adjust the ANNUAL_RENT_INCREASE variable to set your desired rent growth rate.
