"""Rule-based decision-support layer that turns a classification result into
actionable guidance: risk level, recommendation text, suggested action and
decision priority. This complements the statistical classifier with domain
heuristics a government analyst would recognize.
"""

HIGH_RISK_TERMS = {
    "collapse", "outbreak", "corruption", "bribery", "smuggling", "contamination",
    "flooding", "shortage", "unsafe", "fraud", "crime", "threat", "drought",
    "poaching", "misuse", "irregularities",
}

MODERATE_RISK_TERMS = {
    "delay", "decline", "understaffed", "backlog", "complaint", "concern",
    "shortfall", "disruption", "inconsistent", "limited",
}

CATEGORY_ACTIONS = {
    "Infrastructure": "Dispatch a structural/engineering assessment team and schedule urgent maintenance works.",
    "Public Health": "Alert the regional health authority, verify medical supply chain and consider a rapid-response health team.",
    "Education": "Coordinate with the Ministry of Education to reallocate staffing/resources and audit facility conditions.",
    "Security": "Escalate to local law enforcement command and reinforce patrol or monitoring coverage in the area.",
    "Economy": "Refer to the economic policy unit for impact assessment and possible support measures for affected businesses.",
    "Environment": "Engage environmental protection authority for site inspection and enforcement of compliance standards.",
    "Corruption & Compliance": "Escalate immediately to the internal audit and anti-corruption unit for formal investigation.",
    "Public Services": "Review service delivery workflows with the relevant department and issue a citizen service improvement plan.",
}

CATEGORY_SUMMARY_LABEL = {
    "Infrastructure": "an infrastructure-related issue",
    "Public Health": "a public health concern",
    "Education": "an education sector issue",
    "Security": "a public security matter",
    "Economy": "an economic development issue",
    "Environment": "an environmental concern",
    "Corruption & Compliance": "a governance and compliance issue",
    "Public Services": "a public service delivery issue",
}


def _risk_from_keywords(keywords):
    lowered = {k.lower() for k in keywords}
    if lowered & HIGH_RISK_TERMS:
        return "High"
    if lowered & MODERATE_RISK_TERMS:
        return "Medium"
    return "Low"


def _combine_risk(priority: str, confidence: float, keyword_risk: str) -> str:
    priority_weight = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(priority, 2)
    keyword_weight = {"Low": 1, "Medium": 2, "High": 3}.get(keyword_risk, 1)
    confidence_weight = 2 if confidence >= 0.75 else (1 if confidence >= 0.5 else 0)

    score = priority_weight + keyword_weight + confidence_weight
    if score >= 8:
        return "Critical"
    if score >= 6:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def _decision_priority(risk_level: str, priority: str) -> str:
    order = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    combined = max(order.get(risk_level, 0), order.get(priority, 0))
    return {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}[combined]


def generate_summary(title: str, description: str, category: str) -> str:
    label = CATEGORY_SUMMARY_LABEL.get(category, "an issue requiring review")
    snippet = description.strip()
    if len(snippet) > 220:
        snippet = snippet[:217].rsplit(" ", 1)[0] + "..."
    return f'"{title}" has been classified as {label}. Summary: {snippet}'


def generate_recommendation(category: str, risk_level: str, confidence: float) -> str:
    confidence_pct = round(confidence * 100, 1)
    base = CATEGORY_ACTIONS.get(category, "Route the report to the relevant department for manual review.")
    urgency = {
        "Critical": "This requires immediate executive attention within 24 hours.",
        "High": "This should be prioritized for action within the current week.",
        "Medium": "This should be scheduled for review within the next reporting cycle.",
        "Low": "This can be handled through standard operating procedures.",
    }[risk_level]
    return (
        f"The AI model classified this report as '{category}' with {confidence_pct}% confidence. "
        f"{urgency} Recommended action: {base}"
    )


def analyze_report(title: str, description: str, priority: str, category: str,
                    confidence: float, keywords: list) -> dict:
    """Produce the full AI analysis payload for a submitted report."""
    keyword_risk = _risk_from_keywords(keywords)
    risk_level = _combine_risk(priority, confidence, keyword_risk)
    decision_priority = _decision_priority(risk_level, priority)

    return {
        "summary": generate_summary(title, description, category),
        "risk_level": risk_level,
        "decision_priority": decision_priority,
        "recommendation": generate_recommendation(category, risk_level, confidence),
        "suggested_action": CATEGORY_ACTIONS.get(
            category, "Route the report to the relevant department for manual review."
        ),
    }
