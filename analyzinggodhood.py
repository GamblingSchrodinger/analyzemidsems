import subprocess
import os
import time

input_folder = r"D:\exampdfs\extracted_text"
output_folder = r"D:\exampdfs\analysis_output"
model = "deepseek-r1:14b"
STOP_FILE = r"D:\exampdfs\STOP.txt"
MAX_ITERATIONS_PER_FILE = 5  # safety cap so it doesn't loop forever with no real improvement

os.makedirs(output_folder, exist_ok=True)

INITIAL_PROMPT = """You are helping a first-year engineering student prepare for a mid-sem exam tomorrow. Below is extracted text from a lecture slide deck or textbook chapter.

Do the following:
1. Summarize the key concepts and formulas in clear exam-focused language.
2. Identify every worked example or practice problem in the text, and solve it step-by-step showing full reasoning.
3. Flag the 3-5 most likely exam traps or common mistakes.
4. End with a bullet-point cheat sheet of the most important facts/formulas.

Material:
{content}
"""

REFINE_PROMPT = """Here is your previous analysis of exam material for a first-year engineering student:

---PREVIOUS ANALYSIS---
{previous}
---END PREVIOUS ANALYSIS---

Critically review your own work above. Find anything that is:
- Mathematically incorrect or imprecise
- Unclear or poorly explained for a first-year student
- Missing (an example you didn't solve, a formula you forgot, a trap you didn't mention)

Then produce an IMPROVED, COMPLETE version of the full analysis (not just a list of fixes — rewrite the whole thing better). If you genuinely find nothing to improve, say so explicitly at the very top with the line "NO FURTHER IMPROVEMENTS NEEDED" and then repeat the analysis unchanged.
"""

def check_stop():
    return os.path.exists(STOP_FILE)

def run_model(prompt):
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout

files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]
print(f"Found {len(files)} files to process.")
print(f"To stop at any time, create a file named STOP.txt at: {STOP_FILE}")

for i, filename in enumerate(files, 1):
    if check_stop():
        print("STOP file detected. Halting before starting next file.")
        break

    in_path = os.path.join(input_folder, filename)
    base_name = os.path.splitext(filename)[0]

    with open(in_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"[{i}/{len(files)}] {filename}: initial analysis...")
    current = run_model(INITIAL_PROMPT.format(content=content))

    out_path = os.path.join(output_folder, f"{base_name}_v1.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(current)
    print(f"  -> saved v1")

    for iteration in range(2, MAX_ITERATIONS_PER_FILE + 1):
        if check_stop():
            print("STOP file detected. Halting mid-refinement.")
            break

        print(f"[{i}/{len(files)}] {filename}: refinement pass {iteration}...")
        refined = run_model(REFINE_PROMPT.format(previous=current))

        out_path = os.path.join(output_folder, f"{base_name}_v{iteration}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(refined)
        print(f"  -> saved v{iteration}")

        if "NO FURTHER IMPROVEMENTS NEEDED" in refined[:200]:
            print(f"  Model says no further improvements needed. Stopping refinement for this file.")
            current = refined
            break

        current = refined

    # Save final version as the clean, no-suffix file for easy access
    final_path = os.path.join(output_folder, f"{base_name}_FINAL.txt")
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(current)

    if check_stop():
        break

print("Finished (or stopped).")