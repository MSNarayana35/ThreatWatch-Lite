from ..models import Severity

CATEGORIES = {
    'Ransomware': ['ransomware', 'encrypt', 'decrypt', 'lockbit', 'conti'],
    'Phishing': ['phishing', 'credential', 'spoofing', 'impersonation'],
    'Malware': ['malware', 'trojan', 'virus', 'botnet', 'spyware'],
    'Data Breach': ['data breach', 'leak', 'exposed', 'database'],
    'Zero-Day': ['zero-day', '0-day', 'vulnerability', 'exploit'],
    'Cyber Attack': ['attack', 'cyberattack', 'hack']
}

SEVERITY_KEYWORDS = {
    Severity.HIGH: ['critical', 'zero-day', 'nation-state', 'widespread', 'emergency'],
    Severity.MEDIUM: ['vulnerability', 'exploit', 'breach', 'attack'],
    Severity.LOW: ['advisory', 'patch', 'update', 'potential']
}

def classify_incident(title: str, description: str) -> str:
    """Classifies an incident based on keywords in the title and description."""
    text = f"{title.lower()} {description.lower()}"
    for category, keywords in CATEGORIES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'General'

def score_severity(title: str, description: str) -> Severity:
    """Scores the severity of an incident based on keywords."""
    text = f"{title.lower()} {description.lower()}"
    for severity, keywords in SEVERITY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return severity
    return Severity.MEDIUM