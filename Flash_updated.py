from flask import Flask, render_template, jsonify, request, send_file
import subprocess
import os
import pandas as pd
 
app = Flask(__name__)
 
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
 
# Home Page
@app.route('/')
def home():
    return render_template('index.html')
 
# Run Test API
@app.route('/run_test', methods=['GET'])
def run_test():
    result = run_test_case()
    return jsonify(result)
 
# Download Test Output (TXT)
@app.route('/download_output_txt', methods=['GET'])
def download_output_txt():
    output_file = "test_output.txt"
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        return jsonify({"status": "error", "output": "File not found"}), 404
 
# Download Test Output (Excel)
@app.route('/download_output', methods=['GET'])
def download_output():
    output_file = "test_output.txt"
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        return jsonify({"status": "error", "output": "File not found"}), 404   
 
if __name__ == "__main__":
    app.run(debug=True)
 