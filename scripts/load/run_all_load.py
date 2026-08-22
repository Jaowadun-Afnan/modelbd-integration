
# run_all_load.py
import subprocess
print("🚀 Running Phase 5 Load...")
subprocess.run(["python", "load_to_oracle.py"], check=True)
print("✅ Load complete. Running verification...")
subprocess.run(["python", "verify_load.py"], check=True)
