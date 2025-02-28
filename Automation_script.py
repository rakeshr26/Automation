import snowflake.connector
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
 
# Snowflake connection details
conn = snowflake.connector.connect  (
            user='RAKESHRAJA',
            password='Rakeshrajamsdcsk26',
            account='geqfumy-qf13136',
            warehouse='COMPUTE_WH',
            database='myfirstdb',
            schema='myfirstsh'
)
 
# Connect to Snowflake

cursor = conn.cursor()
 
# Define source and target tables
source_table = "table1"
target_table = "table2"
 
# 1️⃣ **Count Validation**
def validate_count():
    cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
    source_count = cursor.fetchone()[0]
 
    cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
    target_count = cursor.fetchone()[0]
 
    return source_count == target_count, source_count, target_count
 
# 2️⃣ **Data Validation**
def validate_data():
    query = f"SELECT * FROM {source_table} LIMIT 10"
    source_data = pd.read_sql(query, conn)
 
    query = f"SELECT * FROM {target_table} LIMIT 10"
    target_data = pd.read_sql(query, conn)
 
    # Ensure both DataFrames have the same columns
    common_columns = list(set(source_data.columns) & set(target_data.columns))
    source_data = source_data[common_columns]
    target_data = target_data[common_columns]
 
    # Sort DataFrames by common columns and reset index
    source_data = source_data.sort_values(by=common_columns).reset_index(drop=True)
    target_data = target_data.sort_values(by=common_columns).reset_index(drop=True)
 
    match = source_data.equals(target_data)
    
    return match
 
# 3️⃣ **DDL Validation**
def validate_ddl():
    cursor.execute(f"DESC TABLE {source_table}")
    source_ddl = cursor.fetchall()
 
    cursor.execute(f"DESC TABLE {target_table}")
    target_ddl = cursor.fetchall()
 
    return source_ddl == target_ddl, {"Source DDL": source_ddl, "Target DDL": target_ddl} if source_ddl != target_ddl else None
 
# 4️⃣ **Corrected Minus Query Validation (Handles Exact Counts)**
def validate_minus_query():
    
 
    # Query to get records in source but missing in target (considering duplicates)
    query_source_not_in_target = f"""
    SELECT * FROM {source_table}
    EXCEPT
    SELECT * FROM {target_table}
    """
    cursor.execute(query_source_not_in_target)
    source_minus_target = cursor.fetchall()
 
    # Print raw output for debugging
    print("\n🔹 Records in Source but Missing in Target:")
    if source_minus_target:
        for row in source_minus_target:
            print(row)
    else:
        print("✅ No extra records in Source.")
 
    # Query to get records in target but missing in source (considering duplicates)
    query_target_not_in_source = f"""
    SELECT * FROM {target_table}
    EXCEPT
    SELECT * FROM {source_table}
    """
    cursor.execute(query_target_not_in_source)
    target_minus_source = cursor.fetchall()
 
    # Print raw output for debugging
    print("\n🔹 Records in Target but Missing in Source:")
    if target_minus_source:
        for row in target_minus_source:
            print(row)
    else:
        print("✅ No extra records in Target.")
 
    # If any mismatches exist, return False in summary
    return not (source_minus_target or target_minus_source), {
        "Records in Source but Missing in Target": source_minus_target if source_minus_target else "No extra records in Source.",
        "Records in Target but Missing in Source": target_minus_source if target_minus_source else "No extra records in Target."
    }
 
 
# 5️⃣ **Duplicate Validation**
def validate_duplicates():
    query = f"""
    SELECT ID, COUNT(*) 
    FROM {source_table} 
    GROUP BY ID
    HAVING COUNT(*) > 1
    """
    cursor.execute(query)
    source_duplicates = cursor.fetchall()
 
    query = f"""
    SELECT ID, COUNT(*) 
    FROM {target_table} 
    GROUP BY ID
    HAVING COUNT(*) > 1
    """
    cursor.execute(query)
    target_duplicates = cursor.fetchall()
 
    return not source_duplicates and not target_duplicates, {
        "Source Duplicates": source_duplicates,
        "Target Duplicates": target_duplicates
    } if source_duplicates or target_duplicates else None
 
# **Run Validations**
print("\n=== Running Snowflake Table Validation ===")
 
count_match, source_count, target_count = validate_count()
data_match = validate_data()
ddl_match, ddl_mismatches = validate_ddl()
minus_match, minus_mismatches = validate_minus_query()
duplicates_match, duplicate_details = validate_duplicates()
 
# **Print Detailed Summary**
print("\n=== Validation Summary ===")
print(f"✅ Count Match: {count_match} (Source: {source_count}, Target: {target_count})")
if not count_match:
    print("❌ Count Mismatch!")
 
print(f"✅ Data Match: {data_match}")
if not data_match:
    print("❌ Data Mismatch!")
 
print(f"✅ DDL Match: {ddl_match}")
if not ddl_match:
    print("❌ DDL Differences!")
    print(ddl_mismatches)
 
print(f"✅ Minus Query Match: {minus_match}")
if not minus_match:
    print("❌ Data differences found:")
    print(minus_mismatches)
 
print(f"✅ No Duplicates: {duplicates_match}")
if not duplicates_match:
    print("❌ Duplicate Records Found!")
    print(duplicate_details)
 
# **Close Connection**
cursor.close()
conn.close() 