"""Pure-Python rules (no AI needed) for grade and risk level."""


def grade_for(marks: float) -> str:
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    if marks >= 40: return "D"
    return "F"


def risk_for(marks: float, attendance: float) -> str:
    if marks < 40 or attendance < 60:
        return "High"
    if marks < 60 or attendance < 75:
        return "Medium"
    return "Low"
