
import csv, sqlite3
import pandas as pd


con = sqlite3.connect("spacex_sql.db")
cur = con.cursor()

df = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv"
)
df.to_sql("SPACEXTBL", con, if_exists="replace", index=False, method="multi")

cur.execute("DROP TABLE IF EXISTS SPACEXTABLE;")
con.commit()
cur.execute("CREATE TABLE SPACEXTABLE AS SELECT * FROM SPACEXTBL WHERE Date IS NOT NULL")
con.commit()

print("Database ready. Running all 10 tasks...\n")

def run(title, sql):
    print(f"{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    result = pd.read_sql_query(sql, con)
    print(result.to_string(index=False))
    print()
    return result

# ── Task 1: Unique launch sites ───────────────────────────────────────────────
run(
    "Task 1 — Unique Launch Sites",
    'SELECT DISTINCT "Launch_Site" FROM SPACEXTABLE;'
)

# ── Task 2: Sites beginning with 'CCA' (5 records) ───────────────────────────
run(
    "Task 2 — 5 Records Where Launch Site Begins with 'CCA'",
    '''SELECT * FROM SPACEXTABLE
       WHERE "Launch_Site" LIKE 'CCA%'
       LIMIT 5;'''
)

# ── Task 3: Total payload mass by NASA CRS ────────────────────────────────────
run(
    "Task 3 — Total Payload Mass Carried by NASA (CRS)",
    '''SELECT SUM("PAYLOAD_MASS__KG_") AS Total_Payload_Mass_kg
       FROM SPACEXTABLE
       WHERE Customer = 'NASA (CRS)';'''
)

# ── Task 4: Average payload — F9 v1.1 ─────────────────────────────────────────
run(
    "Task 4 — Average Payload Mass by Booster Version F9 v1.1",
    '''SELECT AVG("PAYLOAD_MASS__KG_") AS Avg_Payload_Mass_kg
       FROM SPACEXTABLE
       WHERE "Booster_Version" = 'F9 v1.1';'''
)

# ── Task 5: First successful ground pad landing ───────────────────────────────
run(
    "Task 5 — Date of First Successful Ground Pad Landing",
    '''SELECT MIN(Date) AS First_Ground_Pad_Success
       FROM SPACEXTABLE
       WHERE "Landing_Outcome" = 'Success (ground pad)';'''
)

# ── Task 6: Drone ship success with payload 4000–6000 kg ─────────────────────
run(
    "Task 6 — Boosters: Drone Ship Success & Payload 4000–6000 kg",
    '''SELECT "Booster_Version", "PAYLOAD_MASS__KG_", "Landing_Outcome"
       FROM SPACEXTABLE
       WHERE "Landing_Outcome" = 'Success (drone ship)'
         AND "PAYLOAD_MASS__KG_" > 4000
         AND "PAYLOAD_MASS__KG_" < 6000;'''
)

# ── Task 7: Total successful & failure mission outcomes ───────────────────────
run(
    "Task 7 — Total Successful and Failure Mission Outcomes",
    '''SELECT "Mission_Outcome", COUNT(*) AS Count
       FROM SPACEXTABLE
       GROUP BY "Mission_Outcome";'''
)

# ── Task 8: Boosters with maximum payload mass (subquery) ────────────────────
run(
    "Task 8 — Booster Versions Carrying Maximum Payload Mass",
    '''SELECT "Booster_Version", "PAYLOAD_MASS__KG_"
       FROM SPACEXTABLE
       WHERE "PAYLOAD_MASS__KG_" = (
           SELECT MAX("PAYLOAD_MASS__KG_") FROM SPACEXTABLE
       );'''
)

# ── Task 9: 2015 drone ship failures with month names ───────────────────────
run(
    "Task 9 — 2015 Drone Ship Failures (Month, Booster, Site)",
    '''SELECT
           CASE substr(Date, 6, 2)
               WHEN '01' THEN 'January'   WHEN '02' THEN 'February'
               WHEN '03' THEN 'March'     WHEN '04' THEN 'April'
               WHEN '05' THEN 'May'       WHEN '06' THEN 'June'
               WHEN '07' THEN 'July'      WHEN '08' THEN 'August'
               WHEN '09' THEN 'September' WHEN '10' THEN 'October'
               WHEN '11' THEN 'November'  WHEN '12' THEN 'December'
           END AS Month,
           "Booster_Version",
           "Launch_Site",
           "Landing_Outcome"
       FROM SPACEXTABLE
       WHERE "Landing_Outcome" = 'Failure (drone ship)'
         AND substr(Date, 1, 4) = '2015';'''
)

# ── Task 10: Rank landing outcomes between 2010-06-04 and 2017-03-20 ─────────
run(
    "Task 10 — Landing Outcome Counts (2010-06-04 to 2017-03-20, Descending)",
    '''SELECT "Landing_Outcome", COUNT(*) AS Count
       FROM SPACEXTABLE
       WHERE Date BETWEEN '2010-06-04' AND '2017-03-20'
       GROUP BY "Landing_Outcome"
       ORDER BY Count DESC;'''
)

con.close()
print("✅ All 10 tasks completed successfully!")
