import subprocess
from flask import Flask, render_template, jsonify, request, send_file
import os
 
app = Flask(__name__)
 
# Function to run test script and capture output
def run_test_case():
    try:
        result = subprocess.run(
    ["python", "Automation_script.py"],
            capture_output=True, text=True, encoding="utf-8"
        )
        
        # Save output to a file for downloading
        output_file = "test_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)
 
        return {"status": "success", "output": result.stdout}
    
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
 
# Download Test Output
@app.route('/download_output', methods=['GET'])
def download_output():
    output_file = "test_output.txt"
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        return jsonify({"status": "error", "output": "File not found"}), 404
 
if __name__ == "__main__":
    app.run(debug=True)