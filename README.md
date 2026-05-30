<<<<<<< HEAD
# ISHIKI – Rule-Based Phishing Awareness & Detection Platform

ISHIKI is a cybersecurity training web application that educates users about phishing attacks and analyzes suspicious emails and URLs using a **transparent, rule-based detection engine**.

## Features

- **User Authentication** — Registration, login, logout, forgot password, profile management (BCrypt hashing)
- **Dashboard** — XP, badges, quiz scores, analysis history, Chart.js progress charts
- **Learning Modules** — 5 modules covering phishing fundamentals through best practices
- **Email Analyzer** — Rule-based scoring with detailed explanations per triggered rule
- **URL Analyzer** — Length, IP hosts, keywords, subdomains, hyphens, HTTPS checks
- **Social Engineering Detector** — Fear, urgency, authority, reward tactics
- **Interactive Simulations** — Email and website phishing scenarios
- **Quiz System** — Multiple choice, true/false, scenario questions with timer and review
- **Gamification** — XP, badges, leaderboard
- **Incident Reporting** — Users report suspicious activity; admins review
- **Admin Panel** — User, module, quiz, and report management with analytics

## Tech Stack

- Python 3.10+
- Flask, SQLAlchemy, Flask-Login, Flask-Bcrypt
- **SQLite**
- Bootstrap 5, Chart.js, JavaScript

## Database

ISHIKI uses a **relational database** accessed through **SQLAlchemy** (Python ORM).


SQLite stores everything in a single local file — no separate database server to install. Tables include `users`, `modules`, `quizzes`, `questions`, `results`, `reports`, `badges`, `user_badges`, `module_progress`, `analysis_history`, `activities`, and `simulation_attempts`.



## Quick Start

```bash
cd ISHIKI
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**

### Default Accounts

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | Admin |
| demo     | demo1234  | User  |

## MySQL Configuration

Set environment variable before running:

```bash
export DATABASE_URL="mysql+pymysql://user:password@localhost/ishiki"
pip install pymysql
python app.py
```

## Project Structure

```
ISHIKI/
├── app.py                 # Entry point
├── ishiki.db              # SQLite database (auto-created)
├── factory.py             # Application factory
├── config.py
├── extensions.py
├── seed.py                # Initial data
├── models/                # SQLAlchemy models
├── services/              # Detection engines & gamification
├── routes/                # Flask blueprints
├── templates/             # Jinja2 HTML templates
├── static/                # CSS & JavaScript
└── requirements.txt
```

## Detection Rules (Email)

| Rule                    | Score |
|-------------------------|-------|
| Urgency keywords        | +10   |
| Credential requests     | +15   |
| Threat language         | +15   |
| Suspicious links        | +20   |
| Excessive capitalization| +10   |
| Excessive punctuation   | +5    |

**Classification:** 0–20 Safe | 21–50 Suspicious | 51–100 High-Risk Phishing

## License

Educational project — use freely for learning purposes.
=======
# Ishiki_code
>>>>>>> 3c5ef70449a0c167edd5767c77f79801d66facd3
