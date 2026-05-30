from dataclasses import dataclass, field


@dataclass
class SocialEngineeringResult:
    detected_tactics: list = field(default_factory=list)
    threat_level: str = "Low"
    details: dict = field(default_factory=dict)


TACTICS = {
    "Fear": [
        "suspended", "blocked", "legal action", "terminated", "frozen",
        "unauthorized", "compromised", "breach", "arrest", "lawsuit",
    ],
    "Urgency": [
        "immediately", "today", "now", "urgent", "expires", "limited time",
        "act fast", "within 24 hours", "deadline",
    ],
    "Authority": [
        "ceo", "it department", "bank security team", "administrator",
        "irs", "fbi", "support team", "compliance officer", "hr department",
    ],
    "Reward": [
        "prize", "winner", "reward", "gift card", "lottery", "congratulations",
        "you have won", "free gift", "cash prize", "inheritance",
    ],
}


def _find_matches(text: str, keywords: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def analyze_social_engineering(text: str) -> SocialEngineeringResult:
    if not text or not text.strip():
        return SocialEngineeringResult()

    detected = []
    details = {}
    for tactic, keywords in TACTICS.items():
        matches = _find_matches(text, keywords)
        if matches:
            detected.append(tactic)
            details[tactic] = matches

    count = len(detected)
    if count >= 3:
        level = "High"
    elif count >= 2:
        level = "Medium"
    elif count >= 1:
        level = "Moderate"
    else:
        level = "Low"

    return SocialEngineeringResult(
        detected_tactics=detected,
        threat_level=level,
        details=details,
    )
