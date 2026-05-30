"""Seed database with modules, quizzes, badges, and default admin."""

from extensions import bcrypt, db
from models import Badge, Module, Question, Quiz, User
from services.gamification import BADGE_DEFINITIONS, ensure_badges_exist


MODULES = [
    {
        "title": "Introduction to Phishing",
        "description": "Learn what phishing is and how attackers operate.",
        "order_index": 1,
        "content": """
<h4>What is Phishing?</h4>
<p>Phishing is a social engineering attack where criminals impersonate trusted entities to steal credentials, money, or data.</p>
<h4>Types of Phishing</h4>
<ul>
<li><strong>Email phishing</strong> — Mass emails with malicious links</li>
<li><strong>Spear phishing</strong> — Targeted attacks on specific individuals</li>
<li><strong>Smishing</strong> — Phishing via SMS</li>
<li><strong>Vishing</strong> — Voice call scams</li>
</ul>
<h4>Real-World Examples</h4>
<p>Fake bank alerts, tax refund scams, and CEO fraud have cost organizations billions annually.</p>
""",
    },
    {
        "title": "Phishing Emails",
        "description": "Identify suspicious senders, links, and urgency tactics.",
        "order_index": 2,
        "content": """
<h4>Suspicious Senders</h4>
<p>Check the full email address — scammers use look-alike domains (paypa1.com vs paypal.com).</p>
<h4>Fake Links</h4>
<p>Hover over links before clicking. The displayed text may not match the actual URL.</p>
<h4>Attachments</h4>
<p>Unexpected .zip, .exe, or macro-enabled documents are high risk.</p>
<h4>Urgency Tactics</h4>
<p>Phrases like "act now" or "account suspended" pressure you to skip verification.</p>
""",
    },
    {
        "title": "Fake Websites",
        "description": "Inspect URLs, HTTPS, and domain spoofing.",
        "order_index": 3,
        "content": """
<h4>URL Inspection</h4>
<p>Read URLs character by character. Subdomains can mimic brand names.</p>
<h4>HTTPS</h4>
<p>HTTPS encrypts traffic but does not guarantee a site is legitimate.</p>
<h4>Domain Spoofing</h4>
<p>Attackers register similar domains: amaz0n-security.com</p>
<h4>Fake Login Pages</h4>
<p>Always navigate to sites directly or use bookmarks instead of email links.</p>
""",
    },
    {
        "title": "Social Engineering",
        "description": "Recognize manipulation through fear, authority, and rewards.",
        "order_index": 4,
        "content": """
<h4>Authority Attacks</h4>
<p>Impersonating CEOs, IT staff, or government agencies.</p>
<h4>Fear Tactics</h4>
<p>Threats of account closure, legal action, or security breaches.</p>
<h4>Curiosity Bait</h4>
<p>"You won't believe what I found" — entices clicks on malicious content.</p>
<h4>Reward Scams</h4>
<p>Fake prizes and gift cards to harvest personal information.</p>
""",
    },
    {
        "title": "Security Best Practices",
        "description": "Protect yourself with strong habits and reporting.",
        "order_index": 5,
        "content": """
<h4>Strong Passwords</h4>
<p>Use unique passwords and a password manager.</p>
<h4>MFA</h4>
<p>Enable multi-factor authentication on all important accounts.</p>
<h4>Safe Browsing</h4>
<p>Keep software updated and avoid unknown downloads.</p>
<h4>Reporting Phishing</h4>
<p>Report suspicious messages to your IT team or use ISHIKI's incident module.</p>
""",
    },
]


QUIZ_QUESTIONS = [
    {
        "title": "Phishing Fundamentals Quiz",
        "module_order": 1,
        "questions": [
            {
                "question": "What is the primary goal of most phishing attacks?",
                "type": "multiple_choice",
                "a": "Improve network speed",
                "b": "Steal credentials or sensitive data",
                "c": "Install antivirus software",
                "d": "Update your browser",
                "correct": "b",
            },
            {
                "question": "Spear phishing targets specific individuals.",
                "type": "true_false",
                "a": "True",
                "b": "False",
                "c": None,
                "d": None,
                "correct": "a",
            },
            {
                "question": "A CEO urgently requests a wire transfer via email. You should:",
                "type": "scenario",
                "a": "Transfer immediately",
                "b": "Verify through a known phone number",
                "c": "Reply with account details",
                "d": "Forward to colleagues",
                "correct": "b",
            },
        ],
    },
    {
        "title": "Email Security Quiz",
        "module_order": 2,
        "questions": [
            {
                "question": "Which is a red flag in an email?",
                "type": "multiple_choice",
                "a": "Personalized greeting from a known contact",
                "b": "Generic greeting and urgent action required",
                "c": "Newsletter you subscribed to",
                "d": "Order confirmation you placed",
                "correct": "b",
            },
            {
                "question": "Hovering over a link shows a different domain than expected — this is suspicious.",
                "type": "true_false",
                "a": "True",
                "b": "False",
                "c": None,
                "d": None,
                "correct": "a",
            },
        ],
    },
]


EMAIL_SCENARIOS = [
    {
        "subject": "Your package is waiting",
        "from_addr": "noreply@fedex-tracking.com",
        "body": "Dear customer, your package could not be delivered. Click here to reschedule: http://bit.ly/pkg-reschedule",
        "is_phishing": True,
        "feedback": "Shortened URL + generic greeting + unexpected delivery notice = phishing.",
    },
    {
        "subject": "Team meeting notes",
        "from_addr": "sarah.jones@yourcompany.com",
        "body": "Hi team, attached are the notes from yesterday's standup. Let me know if you have questions.",
        "is_phishing": False,
        "feedback": "Internal sender, no urgency, no credential request — likely safe.",
    },
    {
        "subject": "URGENT: Verify your account NOW!!!",
        "from_addr": "security@paypa1-secure.com",
        "body": "Your account has been SUSPENDED. Enter your password immediately at http://192.168.1.50/login or face legal action.",
        "is_phishing": True,
        "feedback": "Urgency, typosquatting, IP URL, credential request, threat language.",
    },
]

WEB_SCENARIOS = [
    {
        "display_url": "https://www.paypal.com/signin",
        "actual_note": "Legitimate PayPal domain with HTTPS",
        "is_fake": False,
        "feedback": "Correct domain spelling, official TLD, HTTPS present.",
    },
    {
        "display_url": "https://paypal-secure-login.verify-account.com/signin",
        "actual_note": "Hyphenated subdomain spoofing",
        "is_fake": True,
        "feedback": "Excessive subdomains and hyphenated brand mimicry.",
    },
    {
        "display_url": "http://192.168.1.1/bank/login",
        "actual_note": "IP-based HTTP login page",
        "is_fake": True,
        "feedback": "Banks never use raw IP addresses for login pages.",
    },
]


def seed_database():
    ensure_badges_exist()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@ishiki.local",
            password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
            role="admin",
            xp=100,
        )
        db.session.add(admin)

    if not User.query.filter_by(username="demo").first():
        demo = User(
            username="demo",
            email="demo@ishiki.local",
            password_hash=bcrypt.generate_password_hash("demo1234").decode("utf-8"),
            role="user",
        )
        db.session.add(demo)

    for mod_data in MODULES:
        if not Module.query.filter_by(title=mod_data["title"]).first():
            db.session.add(Module(
                title=mod_data["title"],
                description=mod_data["description"],
                content=mod_data["content"],
                order_index=mod_data["order_index"],
            ))
    db.session.commit()

    for quiz_data in QUIZ_QUESTIONS:
        mod = Module.query.filter_by(order_index=quiz_data["module_order"]).first()
        if not Quiz.query.filter_by(title=quiz_data["title"]).first():
            quiz = Quiz(title=quiz_data["title"], module_id=mod.id if mod else None)
            db.session.add(quiz)
            db.session.flush()
            for q in quiz_data["questions"]:
                correct = q["correct"]
                if q["type"] == "true_false":
                    ans_map = {"a": "True", "b": "False"}
                    correct = ans_map.get(correct, correct)
                elif q["type"] == "multiple_choice":
                    ans_map = {"a": q["a"], "b": q["b"], "c": q["c"], "d": q["d"]}
                    correct = ans_map.get(correct, correct)
                db.session.add(Question(
                    quiz_id=quiz.id,
                    question=q["question"],
                    question_type=q["type"],
                    option_a=q["a"],
                    option_b=q["b"],
                    option_c=q["c"],
                    option_d=q["d"],
                    correct_answer=correct,
                ))
    db.session.commit()


def get_email_scenarios():
    return EMAIL_SCENARIOS


def get_web_scenarios():
    return WEB_SCENARIOS
