import streamlit as st
import subprocess
import os
import pandas as pd

# Function to run test cases and capture output
def run_test_case():
    try:
        process = subprocess.Popen(
            ["python", "Automation_script.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        output_lines = []
        for line in iter(process.stdout.readline, ""):
            output_lines.append(line)

        # Capture errors if any
        errors = process.stderr.read()
        if errors:
            output_lines.append("\nErrors:\n" + errors)

        # Save output to a file (TXT)
        output_txt_file = "test_output.txt"
        with open(output_txt_file, "w", encoding="utf-8") as f:
            f.writelines(output_lines)

        # Save output to an Excel file
        output_excel_file = "test_output.xlsx"
        df = pd.DataFrame({"Test Output": output_lines})
        df.to_excel(output_excel_file, index=False)  # ✅ Removed 'encoding'

        return {"status": "success", "output": "".join(output_lines)}
    
    except Exception as e:
        return {"status": "error", "output": str(e)}

# Streamlit app
st.title("Test Case Runner")

if st.button("Run Test Cases"):
    result = run_test_case()
    st.subheader("Results:")
    st.text(result["output"])

if st.button("Download Output (TXT)"):
    output_file = "test_output.txt"
    if os.path.exists(output_file):
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download TXT",
                data=f,
                file_name="test_output.txt",
                mime="text/plain"
            )
    else:
        st.error("File not found")

if st.button("Download Output (Excel)"):
    output_file = "test_output.xlsx"
    if os.path.exists(output_file):
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Excel",
                data=f,
                file_name="test_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("File not found")