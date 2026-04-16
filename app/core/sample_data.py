from .. import crud, schemas, models
from sqlalchemy.orm import Session
from datetime import datetime

SAMPLE_INCIDENTS = [
    # Malware
    {"title": "Emotet Trojan Variant Spreading via Spam", "description": "A new variant of the Emotet trojan is being distributed through a widespread malspam campaign.", "severity": "High", "source": "Internal Research", "date": datetime(2023, 10, 26, 10, 0, 0), "category": "Malware"},
    {"title": "Ryuk Ransomware Attack on Healthcare Provider", "description": "A major healthcare provider has been hit by Ryuk ransomware, causing significant operational disruptions.", "severity": "High", "source": "News Outlet", "date": datetime(2023, 10, 25, 14, 30, 0), "category": "Malware"},
    {"title": "TrickBot Malware Uses New Evasion Techniques", "description": "The TrickBot banking trojan has been updated with new techniques to evade detection by security software.", "severity": "High", "source": "Threat Intel Report", "date": datetime(2023, 10, 24, 9, 15, 0), "category": "Malware"},
    {"title": "Mirai Botnet Variant Targeting IoT Devices", "description": "A new variant of the Mirai botnet is actively scanning for and infecting vulnerable IoT devices.", "severity": "Medium", "source": "Security Vendor", "date": datetime(2023, 10, 23, 11, 45, 0), "category": "Malware"},
    {"title": "Agent Tesla Infostealer Campaign Detected", "description": "A large-scale phishing campaign is distributing the Agent Tesla information stealer.", "severity": "High", "source": "Internal Research", "date": datetime(2023, 10, 22, 16, 0, 0), "category": "Malware"},

    # Phishing
    {"title": "Office 365 Credential Phishing Campaign", "description": "A sophisticated phishing campaign is targeting Office 365 users to steal their login credentials.", "severity": "Medium", "source": "User Report", "date": datetime(2023, 10, 26, 11, 0, 0), "category": "Phishing"},
    {"title": "Fake COVID-19 Vaccine Passport Phishing Site", "description": "A fake website is posing as a government portal to steal personal information under the guise of providing vaccine passports.", "severity": "Medium", "source": "News Outlet", "date": datetime(2023, 10, 25, 16, 0, 0), "category": "Phishing"},
    {"title": "CEO Fraud (BEC) Attempt Reported", "description": "An employee reported a Business Email Compromise (BEC) attempt where the attacker impersonated the CEO.", "severity": "High", "source": "Internal Alert", "date": datetime(2023, 10, 24, 13, 20, 0), "category": "Phishing"},
    {"title": "Smishing Attack Imitating a Major Bank", "description": "A widespread SMS phishing (smishing) campaign is tricking users into revealing their banking details.", "severity": "High", "source": "Security Vendor", "date": datetime(2023, 10, 23, 15, 10, 0), "category": "Phishing"},
    {"title": "LinkedIn Spear-Phishing Attack", "description": "Attackers are using highly personalized spear-phishing emails on LinkedIn to target specific employees.", "severity": "Medium", "source": "Threat Intel Report", "date": datetime(2023, 10, 22, 10, 5, 0), "category": "Phishing"},

    # Vulnerability
    {"title": "Critical RCE Vulnerability in Apache Struts", "description": "A critical remote code execution (RCE) vulnerability (CVE-2023-XXXX) has been discovered in Apache Struts.", "severity": "High", "source": "NVD", "date": datetime(2023, 10, 26, 9, 0, 0), "category": "Vulnerability"},
    {"title": "Zero-Day Exploit for Microsoft Exchange Server", "description": "A zero-day exploit is being actively used against on-premise Microsoft Exchange Servers.", "severity": "High", "source": "Microsoft", "date": datetime(2023, 10, 25, 18, 0, 0), "category": "Vulnerability"},
    {"title": "Log4j 'Log4Shell' Vulnerability Still Being Exploited", "description": "The Log4Shell vulnerability in the Log4j library continues to be a major target for attackers.", "severity": "High", "source": "Security Vendor", "date": datetime(2023, 10, 24, 17, 45, 0), "category": "Vulnerability"},
    {"title": "SQL Injection Flaw in Popular E-commerce Plugin", "description": "A SQL injection vulnerability has been found in a widely used e-commerce plugin for WordPress.", "severity": "High", "source": "Bug Bounty Hunter", "date": datetime(2023, 10, 23, 12, 30, 0), "category": "Vulnerability"},
    {"title": "Privilege Escalation Bug in Linux Kernel", "description": "A local privilege escalation vulnerability has been patched in the Linux kernel.", "severity": "Medium", "source": "Kernel.org", "date": datetime(2023, 10, 22, 14, 0, 0), "category": "Vulnerability"},
    # Today's Incidents
    {"title": "Active Ransomware Campaign Targeting Local Banks", "description": "A new wave of ransomware is specifically targeting regional financial institutions using spear-phishing.", "severity": "High", "source": "Internal Alert", "date": datetime.now(), "category": "Malware"},
    {"title": "Zero-Day Vulnerability in Popular PDF Reader", "description": "A critical zero-day has been discovered allowing remote code execution via specially crafted PDF files.", "severity": "High", "source": "Threat Intel Report", "date": datetime.now(), "category": "Vulnerability"},
    {"title": "Massive Credential Stuffing Attack on Cloud Providers", "description": "Multiple cloud service providers are reporting a spike in automated login attempts using leaked credentials.", "severity": "Medium", "source": "Security Vendor", "date": datetime.now(), "category": "Account Takeover"},
    {"title": "New Android Spyware Disguised as System Update", "description": "Mobile security researchers have identified a sophisticated spyware strain mimicking official system updates.", "severity": "High", "source": "Mobile Security Lab", "date": datetime.now(), "category": "Malware"}
]

SAMPLE_CTF_CHALLENGES = [
    {
        "title": "Basic Web Exploitation",
        "description": "Find the flag hidden in this simple web application. Hint: Inspect the source code.",
        "points": 100,
        "flag": "CTF{WEB_BASICS}",
        "hint": "View Page Source (Ctrl+U) might reveal something.",
        "resources": [
            "/ctf/scenario/web-basics"
        ]
    },
    {
        "title": "Code Breaker",
        "description": "Crack the vault PIN code by analyzing the client-side logic.",
        "points": 150,
        "flag": "CTF{RE_EASY}",
        "hint": "Use Chrome DevTools Console or Sources tab.",
        "resources": [
            "/ctf/scenario/code-breaker"
        ]
    },
    {
        "title": "Log Analysis",
        "description": "Analyze the server logs to find the intruder's trace.",
        "points": 200,
        "flag": "CTF{PCAP_ANALYSIS}",
        "hint": "Look for POST requests or suspicious parameters.",
        "resources": [
            "/ctf/scenario/log-analysis"
        ]
    },
    {
        "title": "Cookie Monster",
        "description": "The admin panel is locked. Can you trick the browser into thinking you are the admin?",
        "points": 100,
        "flag": "CTF{COOKIES_ARE_TASTY}",
        "hint": "Check your browser cookies (DevTools -> Application -> Cookies).",
        "resources": [
            "/ctf/scenario/cookie-monster"
        ]
    },
    {
        "title": "SQL Injection Basic",
        "description": "Bypass the login screen using a classic SQL injection vulnerability.",
        "points": 150,
        "flag": "CTF{SQLI_MASTER}",
        "hint": "Try using ' OR '1'='1 in the username field.",
        "resources": [
            "/ctf/scenario/sqli-basic"
        ]
    },
    {
        "title": "Hidden in Plain Sight",
        "description": "Sometimes secrets are just hidden from view via CSS.",
        "points": 100,
        "flag": "CTF{HIDDEN_ELEMENTS}",
        "hint": "Inspect the DOM for hidden elements (display: none).",
        "resources": [
            "/ctf/scenario/hidden-element"
        ]
    },
    {
        "title": "Base64 Basic",
        "description": "The flag is encoded. Can you decode it?",
        "points": 100,
        "flag": "CTF{BASE64_IS_NOT_ENCRYPTION}",
        "hint": "The string looks like alphanumeric soup ending with '='.",
        "resources": [
            "/ctf/scenario/base64-basic"
        ]
    },
    {
        "title": "Robots Protocol",
        "description": "Check the robots.txt file for disallowed paths.",
        "points": 100,
        "flag": "CTF{ROBOTS_RULE}",
        "hint": "Visit /ctf/scenario/robots/robots.txt",
        "resources": [
            "/ctf/scenario/robots"
        ]
    },
    {
        "title": "Header Hunter",
        "description": "The flag is hidden in the HTTP response headers.",
        "points": 150,
        "flag": "CTF{HEADERS_TELL_TALES}",
        "hint": "Check the Network tab in DevTools for the response headers of the main page.",
        "resources": [
            "/ctf/scenario/header-hunter"
        ]
    },
    {
        "title": "Comment Section",
        "description": "Developers often leave sensitive info in comments.",
        "points": 100,
        "flag": "CTF{COMMENTS_ARE_LEAKY}",
        "hint": "Read the HTML comments carefully.",
        "resources": [
            "/ctf/scenario/comments"
        ]
    },
    {
        "title": "Hex Decoder",
        "description": "The flag is encoded as a hex string. Decode it.",
        "points": 100,
        "flag": "CTF{HEX_CHALLENGE}",
        "hint": "Each pair of characters represents a byte in hexadecimal.",
        "resources": [
            "/ctf/scenario/hex-basic"
        ]
    },
    {
        "title": "ROT13 Cipher",
        "description": "A classic substitution cipher hides the flag.",
        "points": 150,
        "flag": "CTF{ROT13_IS_FUN}",
        "hint": "Rotate letters by 13 positions in the alphabet.",
        "resources": [
            "/ctf/scenario/rot13-basic"
        ]
    },
    {
        "title": "XOR Mystery",
        "description": "Recover the flag from an XOR-encoded string.",
        "points": 200,
        "flag": "CTF{XOR_CHALLENGE}",
        "hint": "Single-byte XOR with a short key can often be brute forced.",
        "resources": [
            "/ctf/scenario/xor-basic"
        ]
    },
    {
        "title": "Console Debug",
        "description": "The flag is only printed in the browser console.",
        "points": 100,
        "flag": "CTF{CONSOLE_LOG}",
        "hint": "Open DevTools and check the Console tab.",
        "resources": [
            "/ctf/scenario/console-debug"
        ]
    },
    {
        "title": "Local Storage Secrets",
        "description": "Secrets are sometimes stored in local storage.",
        "points": 150,
        "flag": "CTF{LOCAL_STORAGE}",
        "hint": "Inspect localStorage entries for this site.",
        "resources": [
            "/ctf/scenario/local-storage"
        ]
    },
    {
        "title": "Layered Encoding",
        "description": "The flag has been encoded in multiple layers.",
        "points": 200,
        "flag": "CTF{LAYERED_ENCODE}",
        "hint": "Try decoding step by step instead of all at once.",
        "resources": [
            "/ctf/scenario/layered-encoding"
        ]
    },
    {
        "title": "JS Variable Leak",
        "description": "The flag is stored in a JavaScript variable in the page source.",
        "points": 100,
        "flag": "CTF{JS_LEAK}",
        "hint": "Inspect inline scripts and look for suspicious variables.",
        "resources": [
            "/ctf/scenario/js-leak"
        ]
    },
    {
        "title": "Meta Tag Secret",
        "description": "Important metadata is sometimes placed in the HTML head.",
        "points": 100,
        "flag": "CTF{META_TAG_SECRET}",
        "hint": "View source and inspect meta tags at the top of the page.",
        "resources": [
            "/ctf/scenario/meta-flag"
        ]
    },
    {
        "title": "Query Debug Mode",
        "description": "The application exposes extra information when debug mode is enabled.",
        "points": 100,
        "flag": "CTF{QUERY_DEBUG}",
        "hint": "Try adding a debug parameter to the URL.",
        "resources": [
            "/ctf/scenario/query-debug"
        ]
    },
    {
        "title": "Hidden Form Field",
        "description": "Forms can contain hidden fields that never appear in the UI.",
        "points": 100,
        "flag": "CTF{HIDDEN_FORM_FIELD}",
        "hint": "Inspect the form markup and list of inputs.",
        "resources": [
            "/ctf/scenario/hidden-form"
        ]
    },
    {
        "title": "Double Base64",
        "description": "The flag has been encoded twice using Base64.",
        "points": 150,
        "flag": "CTF{DOUBLE_BASE64}",
        "hint": "Decode, then decode again.",
        "resources": [
            "/ctf/scenario/double-base64"
        ]
    },
    {
        "title": "Obfuscated Script",
        "description": "The flag is built from character codes inside a script.",
        "points": 150,
        "flag": "CTF{OBFUSCATED_JS}",
        "hint": "Look for String.fromCharCode or similar patterns.",
        "resources": [
            "/ctf/scenario/obfus-script"
        ]
    },
    {
        "title": "Caesar Shift",
        "description": "A simple Caesar cipher hides the flag with a fixed shift.",
        "points": 150,
        "flag": "CTF{CAESAR_SHIFT}",
        "hint": "Rotate letters by a small number of positions.",
        "resources": [
            "/ctf/scenario/caesar-shift"
        ]
    },
    {
        "title": "Substitution Cipher",
        "description": "Each letter has been substituted using a custom mapping.",
        "points": 200,
        "flag": "CTF{SUBSTITUTION_CIPHER}",
        "hint": "A mapping between plaintext and ciphertext letters is available.",
        "resources": [
            "/ctf/scenario/substitution"
        ]
    },
    {
        "title": "RSA Puzzle",
        "description": "Public key parameters and ciphertext are provided for analysis.",
        "points": 200,
        "flag": "CTF{RSA_PUZZLE}",
        "hint": "This is a toy example, not real 2048-bit crypto.",
        "resources": [
            "/ctf/scenario/rsa-puzzle"
        ]
    },
    {
        "title": "Log Correlation",
        "description": "Multiple log streams must be correlated to recover the flag.",
        "points": 200,
        "flag": "CTF{LOG_CORRELATION}",
        "hint": "Look for matching IDs across different log lines.",
        "resources": [
            "/ctf/scenario/log-correlation"
        ]
    }
]

def populate_incidents(db: Session):
    if db.query(models.Incident).count() == 0:
        for incident_data in SAMPLE_INCIDENTS:
            incident = schemas.IncidentCreate(**incident_data)
            crud.create_incident(db, incident)
        print("Sample incidents have been populated.")

def populate_ctf_challenges(db: Session):
    desired_by_title = {c["title"]: c for c in SAMPLE_CTF_CHALLENGES}
    
    # 1. Update existing challenges
    mapping = {
        "Reverse Engineering 101": "Code Breaker",
        "Network Forensics": "Log Analysis"
    }
    
    existing_challenges = db.query(models.CTFChallenge).all()
    existing_titles = set()
    
    updated = 0
    for challenge in existing_challenges:
        # Handle renames
        if challenge.title in mapping:
            challenge.title = mapping[challenge.title]
            
        existing_titles.add(challenge.title)
        
        desired = desired_by_title.get(challenge.title)
        if not desired:
            continue
            
        desired_resources = ", ".join(desired["resources"]) if isinstance(desired["resources"], list) else desired["resources"]
        if (
            challenge.description != desired["description"]
            or challenge.resources != desired_resources
            or challenge.hint != desired["hint"]
            or challenge.flag != desired["flag"]
            or challenge.points != desired["points"]
        ):
            challenge.description = desired["description"]
            challenge.resources = desired_resources
            challenge.hint = desired["hint"]
            challenge.flag = desired["flag"]
            challenge.points = desired["points"]
            updated += 1

    # 2. Add new challenges
    for challenge_data in SAMPLE_CTF_CHALLENGES:
        if challenge_data["title"] not in existing_titles:
            challenge_payload = challenge_data.copy()
            if isinstance(challenge_payload.get("resources"), list):
                challenge_payload["resources"] = ", ".join(challenge_payload["resources"])
            challenge = schemas.CTFChallengeCreate(**challenge_payload)
            crud.create_ctf_challenge(db=db, challenge=challenge)
            print(f"Added new challenge: {challenge_data['title']}")
            
    if updated:
        db.commit()
        print("Sample CTF challenges have been updated.")
