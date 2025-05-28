from typing import Optional
from fastapi import FastAPI, HTTPException, Query
import pandas as pd

app = FastAPI()

# Load Excel files once at startup
hr_info_df = pd.read_excel("hr_info.xlsx")
plans_df = pd.read_excel("plans.xlsx")

@app.get("/get-plans")
def get_plans(
    email: str = Query(..., description="User's email"),
    fiscal_year: str = Query(..., description="Fiscal year to filter")
):
    # Step 1: Lookup email
    filtered_hr = hr_info_df[hr_info_df['EMAIL'] == email]
    if filtered_hr.empty:
        raise HTTPException(status_code=404, detail="Email not found in HR data.")

    job_code = filtered_hr.iloc[0]['JOB_CODE']
    print(job_code)

    # Step 2: Match job_code in comma-separated attribute13_char and fiscal_year
    filtered_plans = plans_df[
        plans_df['ATTRIBUTE13_CHAR'].fillna('').str.contains(fr'\b{job_code}\b')
    ]

    print(filtered_plans)
    plan_names = filtered_plans['PLAN_NAME'].dropna().tolist()
    print(plan_names)
    return {"plan_names": plan_names}
