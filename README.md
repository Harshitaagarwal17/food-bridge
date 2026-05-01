# FoodBridge 🍱
A smart food donation and distribution management system that connects donors, receivers, and administrators through a real-time workflow.

🌐 **Live Demo:** https://web-production-39984.up.railway.app

---

## Features
- Donors can register and list food donations with expiry tracking
- Receivers can browse available food and submit requests
- Admin dashboard with real-time analytics and zone-wise reports
- Automatic food expiry detection via MySQL Events and Triggers
- Audit logging for all status changes
- REST API backend with full CRUD support

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, Flask, REST APIs |
| Database | MySQL (3NF normalized schema) |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Railway |
| DB Features | Views, Triggers, Stored Procedures, Events, Functions |

## Database Design
- 6 tables: Zone, Donor, Receiver, FoodItem, Request, AuditLog
- Fully normalized to 3NF
- Stored procedures for donation matching and status updates
- Triggers for automatic audit logging
- `GetUrgencyLevel()` function for real-time expiry classification

## Getting Started (Local Setup)
1. Clone the repo
git clone https://github.com/Harshitaagarwal17/food-bridge.git
cd food-bridge
2. Install dependencies
pip install -r requirements.txt
3. Set up MySQL and run `schema.sql` then `sample_data.sql`
4. Run the app
python app.py
5. Open `http://localhost:5000`

## Pages
- `/` — Home
- `/donor` — Donor portal
- `/receiver` — Receiver portal  
- `/admin` — Admin dashboard
