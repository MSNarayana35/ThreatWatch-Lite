# ThreatWatch Lite

## Running the Application

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

Once the server is running, you can access the application at `http://localhost:8000`. – A Real-Time Cyber Threat Intelligence & Community Bounty Platform

ThreatWatch Lite is a user-friendly, visually premium, and real-world cybersecurity web application that functions as a lightweight Cyber Threat Intelligence (CTI) system. It aggregates, analyzes, and presents real-time cyber incident information from open-source intelligence (OSINT) sources.

## Core Objective

Create a platform that helps users stay informed about ongoing cyber threats, understand attack trends, and participate in educational cybersecurity bounties, all through a modern, premium-looking interface.

## Key Functional Modules

*   **Threat Feed Aggregation:** Collects cyber incident data from various public sources.
*   **Threat Classification & Intelligence:** Applies lightweight NLP to categorize incidents and assign severity scores.
*   **Interactive Dashboard:** A clean, modern UI with filters and visual analytics.
*   **Educational Bounties:** A dedicated section for cybersecurity-related challenges and a points-based leaderboard.

## Technology Stack

*   **Backend:** Python (FastAPI)
*   **Frontend:** HTML, CSS, JavaScript (with potential for React integration)
*   **Database:** SQLite
*   **Deployment:** Free and open-source tools.