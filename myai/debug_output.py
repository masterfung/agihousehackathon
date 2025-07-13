#!/usr/bin/env python3
"""Debug browser-use output to see what's happening"""

import subprocess
import os

url = "https://www.opentable.com/s?dateTime=2025-07-16T19%3A00%3A00&covers=3&term=thai"
prompt = f"""Go to {url}

Just list 3 restaurant names you see:"""

env = os.environ.copy()

print("Running browser-use...")
result = subprocess.run([
    "poetry", "run", "browser-use",
    "--model", "gemini-2.5-flash-lite-preview-06-17",
    "--prompt", prompt
],
capture_output=True,
text=True,
timeout=30,
env=env
)

print(f"\n=== STDOUT ===")
print(result.stdout)
print(f"\n=== STDERR ===") 
print(result.stderr)
print(f"\n=== Return Code: {result.returncode} ===")