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
```
This command displays the cash flow metrics for Year 10.

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

4. Generate results
```bash
python rental_analysis_dynamic.py --save-results
```

## Note:
The annual rent increase rate is hardcoded (default is 1% per year) in the script. To simulate a different rate, modify the ANNUAL_RENT_INCREASE variable in the source code.

## Configuration
- At the top of rental_analysis_dynamic.py, you will find a section labeled Adjustable Parameters. Here you can modify:
- Mortgage Details: Loan amount, monthly payment (Mortgage + Escrow), interest rate, and term.
- Expense Parameters: Fixed costs (e.g., HOA, maintenance), occupied expenses (e.g., rental rate, management fees), vacant expenses (e.g., utilities), and the number of vacancy months.
- Tax & Other Constants: Annual depreciation, additional expenses, and effective tax rate.
- Annual Rent Increase: Adjust the ANNUAL_RENT_INCREASE variable to set your desired rent growth rate.


# Year Range Sample Output (1-28):
| Year | Effective Rental Rate | Base Annual Cost | Annual Tax Refund | Annual Out-of-Pocket | Annual Loss After Principal |
|------|-----------------------|------------------|-------------------|----------------------|-----------------------------|
| 1    | 2700.00               | -27567.33       | 16181.10          | -11386.23            | -4146.81                    |
| 2    | 2727.00               | -27395.07       | 16048.15          | -11346.92            | -3727.64                    |
| 3    | 2754.27               | -27221.09       | 15908.22          | -11312.87            | -3293.80                    |
| 4    | 2781.81               | -27045.37       | 15760.95          | -11284.41            | -2844.57                    |
| 5    | 2809.63               | -26867.89       | 15605.96          | -11261.93            | -2379.24                    |
| 6    | 2837.73               | -26688.63       | 15442.83          | -11245.80            | -1897.03                    |
| 7    | 2866.10               | -26507.59       | 15271.14          | -11236.45            | -1397.14                    |
| 8    | 2894.77               | -26324.73       | 15090.44          | -11234.29            | -878.70                     |
| 9    | 2923.71               | -26140.04       | 14900.26          | -11239.78            | -340.82                     |
| 10   | 2952.95               | -25953.51       | 14700.10          | -11253.41            | 217.44                      |
| 11   | 2982.48               | -25765.11       | 14489.44          | -11275.67            | 797.06                      |
| 12   | 3012.30               | -25574.83       | 14267.73          | -11307.10            | 1399.10                     |
| 13   | 3042.43               | -25382.65       | 14034.38          | -11348.26            | 2024.65                     |
| 14   | 3072.85               | -25188.54       | 13788.79          | -11399.75            | 2674.86                     |
| 15   | 3103.58               | -24992.49       | 13530.31          | -11462.18            | 3350.94                     |
| 16   | 3134.62               | -24794.48       | 13258.27          | -11536.22            | 4054.16                     |
| 17   | 3165.96               | -24594.49       | 12971.95          | -11622.54            | 4785.88                     |
| 18   | 3197.62               | -24392.51       | 12670.61          | -11721.89            | 5547.50                     |
| 19   | 3229.60               | -24188.50       | 12353.46          | -11835.04            | 6340.50                     |
| 20   | 3261.89               | -23982.45       | 12019.67          | -11962.78            | 7166.45                     |
| 21   | 3294.51               | -23774.34       | 11668.36          | -12105.98            | 8026.98                     |
| 22   | 3327.46               | -23564.15       | 11298.62          | -12265.53            | 8923.83                     |
| 23   | 3360.73               | -23351.86       | 10909.48          | -12442.38            | 9858.81                     |
| 24   | 3394.34               | -23137.44       | 10499.92          | -12637.52            | 10833.84                    |
| 25   | 3428.28               | -22920.88       | 10068.87          | -12852.01            | 11850.92                    |
| 26   | 3462.57               | -22702.16       | 9615.21           | -13086.95            | 12912.17                    |
| 27   | 3497.19               | -22481.25       | 9137.74           | -13343.51            | 14019.81                    |
| 28   | 3532.16               | -22258.13       | 8635.21           | -13622.92            | 15176.19                    |




# Single Year Sample Output (Verbose):
## Rental Analysis Details for Year 1

### Mortgage Details
- **Monthly Payment (Principal+Interest):** $2561.08  
- **Monthly Escrow:** $593.92  
- **Total Monthly Payment:** $3155.00  

### Amortization (Yearly Totals)
- **Annual Interest Paid:** $23493.54  
- **Annual Principal Paid:** $7239.42  
- **Cumulative Principal Paid:** $7239.42  
- **Cumulative Interest Paid:** $23493.54  

### Dynamic Expense Calculations
- **Fixed Costs (per month):** $-3571.67  
- **Additional (Occupied):** $1399.33  
- **Additional (Vacant):** $-100.00  
- **Monthly When Occupied:** $-2172.33  
- **Monthly When Vacant:** $-3671.67  
- **Calculated Base Annual Cost:** $-27567.33  

### Cash Flow Metrics for the Year
- **Effective Rental Rate:** $2700.00  
- **Estimated Annual Tax Refund:** $16181.10  
- **Annual Out-of-Pocket After Tax Refund:** $-11386.23  
- **Annual Loss After Considering Principal:** $-4146.81  

### Assumptions
- **Vacancy Months per Year:** 1.0  
- **Annual Depreciation:** $14938.18  
- **Annual Additional Expenses:** $7800.00  
- **Tax Rate:** 35%
