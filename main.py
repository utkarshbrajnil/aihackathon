from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from datetime import datetime

app = FastAPI()

# Load Excel files once at startup
hr_info_df = pd.read_excel("hr_info.xlsx")
plans_df = pd.read_excel("plans.xlsx")

# Convert date columns to datetime format
plans_df['START_DATE'] = pd.to_datetime(plans_df['START_DATE'], errors='coerce')
plans_df['END_DATE'] = pd.to_datetime(plans_df['END_DATE'], errors='coerce')

# Fiscal year mapping (update if more years are needed)
fiscal_year_ranges = {
    "2023": ("2022-06-01", "2023-05-31"),
    "2024": ("2023-06-01", "2024-05-31"),
    "2025": ("2024-06-01", "2025-05-31"),
}

@app.get("/get-plans")
def get_plans(
    email: str = Query(..., description="User's email"),
    fiscal_year: str = Query(..., description="Fiscal year to filter")
):
    # Step 1: Lookup email
    filtered_hr = hr_info_df[hr_info_df['EMAIL'] == email]
    if filtered_hr.empty:
        return {"message": "Email provided is not a valid salesrep"}

    job_code = filtered_hr.iloc[0]['JOB_CODE']

    # Step 2: Get fiscal year date range
    if fiscal_year not in fiscal_year_ranges:
        return {"message": "Fiscal year is not valid"}

    start_date_str, end_date_str = fiscal_year_ranges[fiscal_year]
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)

    # Step 3: Filter plans
    filtered_plans = plans_df[
        (plans_df['ATTRIBUTE13_CHAR'].fillna('').str.contains(fr'\b{job_code}\b')) &
        (plans_df['STATUS'].str.lower() == 'approved') &
        (plans_df['START_DATE'] >= start_date) &
        (plans_df['END_DATE'] <= end_date)
    ]
    if filtered_plans.empty:
        return {"message": "No plans found for the email and fiscal year"}
    plan_names = filtered_plans['PLAN_NAME'].dropna().tolist()
    return {"plan_names": plan_names}
