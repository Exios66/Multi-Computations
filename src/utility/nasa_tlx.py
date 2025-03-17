import os
import sys
import getpass
import matplotlib.pyplot as plt
from fpdf import FPDF

def get_input(prompt, min_val=0, max_val=100):
    """Get validated integer input between min_val and max_val"""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# Welcome message
print("\nNASA Task Load Index (NASA-TLX) Assessment\n")
participant_id = input("Enter Participant ID: ")
task_id = input("Enter Task ID: ")

# NASA-TLX Rating Scales (0-100)
ratings = {}
ratings["Mental Demand"] = get_input("Mental Demand (0-100): ")
ratings["Physical Demand"] = get_input("Physical Demand (0-100): ")
ratings["Temporal Demand"] = get_input("Temporal Demand (0-100): ")
ratings["Performance"] = get_input("Performance (0-100): ")
ratings["Effort"] = get_input("Effort (0-100): ")
ratings["Frustration"] = get_input("Frustration (0-100): ")

# Unweighted score calculation (average of 6 factors)
unweighted_score = sum(ratings.values()) / len(ratings)

# NASA-TLX Ranking Comparisons
print("\nNow, you will rank which factors contributed more to workload in 15 pairwise comparisons.\n")
comparisons = [
    ("Mental Demand", "Physical Demand"),
    ("Mental Demand", "Temporal Demand"),
    ("Mental Demand", "Performance"),
    ("Mental Demand", "Effort"),
    ("Mental Demand", "Frustration"),
    ("Physical Demand", "Temporal Demand"),
    ("Physical Demand", "Performance"),
    ("Physical Demand", "Effort"),
    ("Physical Demand", "Frustration"),
    ("Temporal Demand", "Performance"),
    ("Temporal Demand", "Frustration"),
    ("Temporal Demand", "Effort"),
    ("Performance", "Frustration"),
    ("Performance", "Effort"),
    ("Frustration", "Effort"),
]

rankings = {factor: 0 for factor in ratings.keys()}

for factor1, factor2 in comparisons:
    choice = None
    while choice not in [1, 2]:
        try:
            choice = int(input(f"Which is more important for workload? (1) {factor1} or (2) {factor2}: "))
            if choice == 1:
                rankings[factor1] += 1
            elif choice == 2:
                rankings[factor2] += 1
            else:
                print("Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter 1 or 2.")

# Weighted workload score calculation
weighted_score = sum((rankings[factor] / 15) * ratings[factor] for factor in ratings)

# Determine the Downloads directory
downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
pdf_path = os.path.join(downloads_dir, f"NASA_TLX_Report_{participant_id}.pdf")

# Generate Visualization
plt.figure(figsize=(8, 5))
plt.barh(list(ratings.keys()), list(ratings.values()), color='dodgerblue')
plt.xlabel("Score (0-100)")
plt.title(f"NASA-TLX Scores for Participant {participant_id}")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.savefig("nasa_tlx_scores.png", bbox_inches="tight")
plt.close()

# Create PDF Report
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", style='B', size=16)

pdf.cell(200, 10, "NASA Task Load Index (NASA-TLX) Report", ln=True, align='C')
pdf.ln(10)

# Participant Information
pdf.set_font("Arial", style='', size=12)
pdf.cell(200, 10, f"Participant ID: {participant_id}", ln=True, align='L')
pdf.cell(200, 10, f"Task ID: {task_id}", ln=True, align='L')
pdf.ln(5)

# Ratings Table
pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, "NASA-TLX Ratings (Scale: 0-100)", ln=True, align='L')

pdf.set_font("Arial", size=11)
pdf.cell(100, 8, "Factor", border=1)
pdf.cell(50, 8, "Rating", border=1, ln=True)

for factor, value in ratings.items():
    pdf.cell(100, 8, factor, border=1)
    pdf.cell(50, 8, str(value), border=1, ln=True)

pdf.ln(5)

# Workload Scores
pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, "NASA-TLX Workload Scores", ln=True, align='L')

pdf.set_font("Arial", size=11)
pdf.cell(200, 8, f"Unweighted Workload Score: {unweighted_score:.2f}", ln=True)
pdf.cell(200, 8, f"Weighted Workload Score: {weighted_score:.2f}", ln=True)
pdf.ln(5)

# Rankings Table
pdf.set_font("Arial", style='B', size=12)
pdf.cell(200, 10, "NASA-TLX Rankings", ln=True, align='L')

pdf.set_font("Arial", size=11)
pdf.cell(100, 8, "Factor", border=1)
pdf.cell(50, 8, "Weight (Times Selected)", border=1, ln=True)

for factor, value in rankings.items():
    pdf.cell(100, 8, factor, border=1)
    pdf.cell(50, 8, str(value), border=1, ln=True)

pdf.ln(10)

# Add Visualization
pdf.image("nasa_tlx_scores.png", x=30, w=150)

# Save PDF
pdf.output(pdf_path)

# Cleanup Image File
os.remove("nasa_tlx_scores.png")

print(f"\nNASA-TLX report has been successfully generated and saved to: {pdf_path}")