"""Generates a synthetic but realistic labeled dataset of government reports.

Run directly (``python data/generate_dataset.py``) to (re)build ``data/dataset.csv``.
The dataset feeds the TF-IDF + Logistic Regression classifier in ai_engine/classifier.py.
"""
import csv
import os
import random

random.seed(42)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "dataset.csv")

REGIONS = [
    "the capital district", "the northern province", "the coastal region",
    "the eastern governorate", "the western district", "the southern region",
    "the central metropolitan area", "the border province", "the industrial zone",
    "the rural district",
]

# Each category maps to a list of sentence templates. "{region}" is substituted.
TEMPLATES = {
    "Infrastructure": [
        "A major road collapse was reported in {region}, blocking traffic for over three hours and damaging nearby utility lines.",
        "The bridge connecting {region} to the main highway shows severe structural cracks and requires urgent inspection.",
        "Water supply pipelines in {region} have deteriorated, causing frequent leaks and pressure loss across residential blocks.",
        "Construction of the new public transit line in {region} is delayed due to funding shortages and contractor disputes.",
        "Streetlights across {region} have been non-functional for weeks, raising concerns about road safety at night.",
        "The drainage system in {region} failed during the recent storm, resulting in flooding of several main streets.",
        "An aging power grid in {region} is causing recurring outages that affect hospitals and schools.",
        "Public buildings in {region} require renovation after inspectors found violations of modern safety codes.",
        "The airport terminal expansion project in {region} is behind schedule due to material supply delays.",
        "Sewage infrastructure in {region} is overwhelmed, leading to overflow incidents near residential areas.",
    ],
    "Public Health": [
        "A rise in respiratory illness cases has been recorded in {region}, prompting concern from local clinics.",
        "The main hospital in {region} is reporting a shortage of essential medicines and vaccine supplies.",
        "Health inspectors identified unsanitary conditions in several food markets across {region}.",
        "An outbreak of waterborne disease was confirmed in {region} following contamination of the local water source.",
        "Maternal healthcare services in {region} are understaffed, leading to longer waiting times for patients.",
        "Public health officials launched a vaccination campaign in {region} after low immunization coverage was detected.",
        "Mental health support services remain limited in {region}, according to a recent community health survey.",
        "The emergency room in {region}'s central hospital is operating beyond capacity during peak hours.",
        "A new health awareness program was introduced in {region} to reduce chronic disease rates among adults.",
        "Nutrition assistance programs in {region} report increased demand from low-income families this quarter.",
    ],
    "Education": [
        "Several public schools in {region} lack sufficient classrooms, forcing double shifts for students.",
        "Teacher shortages in {region} have led to increased class sizes and reduced instructional quality.",
        "The Ministry of Education is reviewing curriculum standards after low test scores were reported in {region}.",
        "A new digital literacy initiative was launched in schools across {region} to close the technology gap.",
        "Dropout rates among secondary students in {region} have increased, correlating with rising transportation costs.",
        "School infrastructure in {region} requires urgent repair after inspectors found unsafe building conditions.",
        "Vocational training centers in {region} report strong enrollment growth among young adults seeking new skills.",
        "Access to higher education remains limited for students in {region} due to a lack of nearby universities.",
        "A scholarship program targeting underserved communities in {region} exceeded its enrollment targets this year.",
        "Reading proficiency among primary students in {region} has declined according to the latest assessment.",
    ],
    "Security": [
        "A rise in petty theft incidents has been recorded across {region} over the past month.",
        "Local police in {region} report increased response times due to a shortage of patrol vehicles.",
        "Community leaders in {region} have requested additional security cameras following recent break-ins.",
        "Border patrol units in {region} intercepted an attempt at illegal smuggling of goods.",
        "Cybersecurity incidents targeting municipal systems in {region} have prompted a full infrastructure audit.",
        "Public demonstrations in {region} required additional crowd-control measures from local authorities.",
        "A joint task force was formed to address organized crime activity reported in {region}.",
        "Emergency response coordination in {region} improved after the deployment of a new communications network.",
        "Reports of domestic disturbances in {region} have increased, prompting a review of support services.",
        "Security checkpoints in {region} were reinforced following a credible threat assessment.",
    ],
    "Economy": [
        "Small businesses in {region} report declining revenue due to rising operational costs.",
        "Unemployment figures in {region} have increased following the closure of a major manufacturing plant.",
        "A new investment fund was launched to support entrepreneurship and startups in {region}.",
        "Inflation has affected purchasing power for households in {region}, according to a recent economic survey.",
        "Export activity from {region}'s agricultural sector declined due to new trade regulations.",
        "The local chamber of commerce in {region} is requesting tax incentives to attract foreign investment.",
        "A microfinance initiative in {region} has helped hundreds of small merchants access working capital.",
        "Labor market analysis shows a skills mismatch between graduates and available jobs in {region}.",
        "Real estate prices in {region} have surged, raising affordability concerns among residents.",
        "Public-private partnerships in {region} are being explored to stimulate industrial growth.",
    ],
    "Environment": [
        "Air quality monitors in {region} recorded pollution levels exceeding national safety standards.",
        "Illegal deforestation activity was reported in the forested areas surrounding {region}.",
        "A coastal cleanup initiative in {region} removed several tons of plastic waste from public beaches.",
        "Groundwater contamination near industrial sites in {region} threatens local agricultural production.",
        "Renewable energy adoption in {region} is increasing following new solar subsidy programs.",
        "Waste management services in {region} are struggling to keep pace with rising urban population density.",
        "Wildlife conservation efforts in {region} have been hampered by habitat loss and illegal poaching.",
        "A prolonged drought in {region} has strained agricultural output and local water reserves.",
        "Industrial emissions from factories in {region} are under review following resident complaints.",
        "Recycling program participation in {region} has improved after a public awareness campaign.",
    ],
    "Corruption & Compliance": [
        "An internal audit uncovered irregularities in procurement contracts issued by the {region} municipal office.",
        "Whistleblower reports allege misuse of public funds within a development project in {region}.",
        "Compliance officers flagged discrepancies between reported and actual expenditures in {region}'s annual budget.",
        "An investigation was opened after bribery allegations surfaced involving a licensing office in {region}.",
        "Transparency reviews found inconsistent record-keeping practices among several departments in {region}.",
        "A conflict-of-interest complaint was filed against an official overseeing contracts in {region}.",
        "Anti-corruption authorities are examining a land allocation scheme reported in {region}.",
        "Financial oversight committees identified unauthorized payments linked to a vendor in {region}.",
        "A tip line received multiple reports of favoritism in hiring practices within {region}'s local government.",
        "Auditors recommended stronger internal controls after reviewing procurement files from {region}.",
    ],
    "Public Services": [
        "Citizens in {region} report long wait times when applying for identification documents.",
        "The customer service center in {region} is understaffed, leading to delays in permit processing.",
        "A new digital portal was launched to simplify public service requests for residents of {region}.",
        "Postal delivery delays have been reported across {region} for several consecutive weeks.",
        "Public transportation reliability in {region} has declined, frustrating daily commuters.",
        "Municipal offices in {region} are piloting an appointment system to reduce service backlogs.",
        "Residents of {region} have raised concerns about inconsistent garbage collection schedules.",
        "A satisfaction survey revealed declining trust in local administrative services within {region}.",
        "The one-stop government service center in {region} exceeded its target for same-day processing.",
        "Utility billing errors have affected numerous households across {region} this billing cycle.",
    ],
}


def build_rows():
    rows = []
    for category, templates in TEMPLATES.items():
        for template in templates:
            for region in REGIONS:
                text = template.format(region=region)
                rows.append({"text": text, "category": category})
    random.shuffle(rows)
    return rows


def main():
    rows = build_rows()
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["text", "category"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} labeled samples -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
