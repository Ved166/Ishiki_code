import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from services.email_analyzer import classify_risk


@dataclass
class URLRuleResult:
    rule_name: str
    score: int
    explanation: str
    triggered: bool = False
    trust_bonus: int = 0


@dataclass
class URLAnalysisResult:
    risk_score: int = 0
    classification: str = "Safe"
    triggered_rules: list = field(default_factory=list)
    all_rules: list = field(default_factory=list)


SUSPICIOUS_KEYWORDS = ["login", "verify", "secure", "update", "account", "signin", "banking"]
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def analyze_url(url: str) -> URLAnalysisResult:
    rules = []
    if not url or not url.strip():
        return URLAnalysisResult(classification="Safe", all_rules=[])

    raw = url.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw

    try:
        parsed = urlparse(raw)
    except Exception:
        return URLAnalysisResult(
            risk_score=50,
            classification="Suspicious",
            all_rules=[
                URLRuleResult("Invalid URL", 50, "Could not parse the URL.", True)
            ],
        )

    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    full_lower = raw.lower()
    score = 0

    # URL length
    length_triggered = len(raw) > 100
    rules.append(URLRuleResult(
        rule_name="URL Length",
        score=10,
        triggered=length_triggered,
        explanation=(
            f"URL is {len(raw)} characters. Very long URLs may hide malicious destinations."
            if length_triggered
            else f"URL length ({len(raw)} chars) is within normal range."
        ),
    ))
    if length_triggered:
        score += 10

    # IP address
    ip_triggered = bool(hostname and IP_PATTERN.match(hostname))
    rules.append(URLRuleResult(
        rule_name="IP Address Host",
        score=25,
        triggered=ip_triggered,
        explanation=(
            f"Host is an IP address ({hostname}) instead of a domain. Highly suspicious."
            if ip_triggered
            else "Host uses a domain name, not a raw IP."
        ),
    ))
    if ip_triggered:
        score += 25

    # Suspicious keywords
    kw_found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in full_lower]
    kw_triggered = len(kw_found) >= 2
    rules.append(URLRuleResult(
        rule_name="Suspicious Keywords",
        score=15,
        triggered=kw_triggered,
        explanation=(
            f"Multiple suspicious keywords: {', '.join(kw_found)}."
            if kw_triggered
            else (
                f"Keyword found: {kw_found[0]}." if kw_found
                else "Few or no phishing-related keywords in URL."
            )
        ),
    ))
    if kw_triggered:
        score += 15
    elif len(kw_found) == 1:
        score += 8

    # Excessive subdomains
    parts = hostname.split(".") if hostname else []
    sub_triggered = len(parts) > 4
    rules.append(URLRuleResult(
        rule_name="Excessive Subdomains",
        score=15,
        triggered=sub_triggered,
        explanation=(
            f"Domain has {len(parts) - 2} subdomains ({hostname}). May indicate domain spoofing."
            if sub_triggered
            else f"Subdomain count appears normal for {hostname}."
        ),
    ))
    if sub_triggered:
        score += 15

    # Hyphenated domain
    hyphen_triggered = hostname.count("-") >= 2
    rules.append(URLRuleResult(
        rule_name="Hyphenated Domain",
        score=10,
        triggered=hyphen_triggered,
        explanation=(
            f"Domain '{hostname}' has multiple hyphens, mimicking legitimate brands."
            if hyphen_triggered
            else "Domain hyphen usage appears normal."
        ),
    ))
    if hyphen_triggered:
        score += 10

    # HTTPS
    https_ok = parsed.scheme == "https"
    rules.append(URLRuleResult(
        rule_name="HTTPS Validation",
        score=0,
        triggered=not https_ok,
        trust_bonus=10 if https_ok else 0,
        explanation=(
            "HTTPS is enabled — increases trust (encryption in transit)."
            if https_ok
            else "No HTTPS — connection is not encrypted. Legitimate login pages use HTTPS."
        ),
    ))
    if not https_ok:
        score += 15

    score = max(0, min(score, 100))
    triggered = [r for r in rules if r.triggered]

    return URLAnalysisResult(
        risk_score=score,
        classification=classify_risk(score),
        triggered_rules=triggered,
        all_rules=rules,
    )
