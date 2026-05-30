import re
from dataclasses import dataclass, field


@dataclass
class RuleResult:
    rule_name: str
    score: int
    explanation: str
    triggered: bool = False


@dataclass
class EmailAnalysisResult:
    risk_score: int = 0
    classification: str = "Safe"
    triggered_rules: list = field(default_factory=list)
    all_rules: list = field(default_factory=list)


URGENCY_KEYWORDS = [
    "urgent", "immediate action", "verify now", "act now",
    "account suspended", "limited time", "expires today",
    "within 24 hours", "respond immediately",
]

CREDENTIAL_KEYWORDS = [
    "password", "login", "otp", "bank account", "security code",
    "credentials", "pin", "ssn", "social security", "verify your account",
]

THREAT_KEYWORDS = [
    "account blocked", "legal action", "suspended", "penalty",
    "terminated", "unauthorized access", "frozen", "seized",
]

SHORT_URL_PATTERNS = [
    r"bit\.ly", r"tinyurl\.com", r"goo\.gl", r"t\.co", r"ow\.ly",
    r"is\.gd", r"buff\.ly", r"rebrand\.ly",
]

IP_URL_PATTERN = re.compile(
    r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    re.IGNORECASE,
)

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)


def _contains_any(text: str, keywords: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def _check_urgency(text: str) -> RuleResult:
    matches = _contains_any(text, URGENCY_KEYWORDS)
    triggered = len(matches) > 0
    return RuleResult(
        rule_name="Urgency Keywords",
        score=10,
        triggered=triggered,
        explanation=(
            f"Found urgency phrases: {', '.join(matches)}. "
            "Phishers create false deadlines to bypass careful thinking."
            if triggered
            else "No urgency manipulation detected."
        ),
    )


def _check_credentials(text: str) -> RuleResult:
    matches = _contains_any(text, CREDENTIAL_KEYWORDS)
    triggered = len(matches) > 0
    return RuleResult(
        rule_name="Credential Requests",
        score=15,
        triggered=triggered,
        explanation=(
            f"Requests sensitive information: {', '.join(matches)}. "
            "Legitimate services rarely ask for passwords via email."
            if triggered
            else "No credential harvesting language detected."
        ),
    )


def _check_threats(text: str) -> RuleResult:
    matches = _contains_any(text, THREAT_KEYWORDS)
    triggered = len(matches) > 0
    return RuleResult(
        rule_name="Threat Language",
        score=15,
        triggered=triggered,
        explanation=(
            f"Contains threatening language: {', '.join(matches)}. "
            "Fear tactics pressure victims into quick action."
            if triggered
            else "No threatening language detected."
        ),
    )


def _check_suspicious_links(text: str) -> RuleResult:
    urls = URL_PATTERN.findall(text)
    issues = []
    for url in urls:
        for pattern in SHORT_URL_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                issues.append(f"Shortened URL: {url[:60]}")
        if IP_URL_PATTERN.search(url):
            issues.append(f"IP-based URL: {url[:60]}")
    triggered = len(issues) > 0
    return RuleResult(
        rule_name="Suspicious Links",
        score=20,
        triggered=triggered,
        explanation=(
            "; ".join(issues) + ". Shortened and IP-based links hide true destinations."
            if triggered
            else "No obviously suspicious links detected."
        ),
    )


def _check_capitalization(text: str) -> RuleResult:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    caps_lines = [
        ln for ln in lines
        if len(ln) > 10 and sum(1 for c in ln if c.isupper()) / max(len([c for c in ln if c.isalpha()]), 1) > 0.7
    ]
    triggered = len(caps_lines) > 0
    preview = caps_lines[0][:80] if caps_lines else ""
    return RuleResult(
        rule_name="Excessive Capitalization",
        score=10,
        triggered=triggered,
        explanation=(
            f"ALL-CAPS shouting detected: \"{preview}...\". "
            "Used to grab attention and convey false urgency."
            if triggered
            else "No excessive capitalization detected."
        ),
    )


def _check_punctuation(text: str) -> RuleResult:
    excessive = re.findall(r"[!?]{2,}", text)
    triggered = len(excessive) >= 2
    return RuleResult(
        rule_name="Excessive Punctuation",
        score=5,
        triggered=triggered,
        explanation=(
            f"Multiple exclamation/question marks found ({len(excessive)} instances). "
            "Common in scam emails to create urgency."
            if triggered
            else "Punctuation usage appears normal."
        ),
    )


def classify_risk(score: int) -> str:
    if score <= 20:
        return "Safe"
    if score <= 50:
        return "Suspicious"
    return "High-Risk Phishing"


def analyze_email(content: str) -> EmailAnalysisResult:
    if not content or not content.strip():
        return EmailAnalysisResult(
            risk_score=0,
            classification="Safe",
            all_rules=[],
        )

    rules = [
        _check_urgency(content),
        _check_credentials(content),
        _check_threats(content),
        _check_suspicious_links(content),
        _check_capitalization(content),
        _check_punctuation(content),
    ]

    score = sum(r.score for r in rules if r.triggered)
    score = min(score, 100)
    triggered = [r for r in rules if r.triggered]

    return EmailAnalysisResult(
        risk_score=score,
        classification=classify_risk(score),
        triggered_rules=triggered,
        all_rules=rules,
    )
