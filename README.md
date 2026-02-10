# Content Moderation Service with Dynamic Rate Limiting and Asynchronous Event Processing

## 📌 Project Overview

This project implements a scalable backend content moderation system using an event-driven architecture.  
The system provides an API for submitting user-generated content, applies per-user rate limiting, and processes moderation asynchronously using a message queue.

Two main services are implemented:
- **API Service**: Accepts content submissions, enforces rate limiting, stores data, and publishes moderation events.
- **Moderation Processor Service**: Consumes events from the message queue and simulates moderation logic (APPROVED/REJECTED).

The application is fully containerized using Docker and orchestrated with Docker Compose.

---

## 🏗 Architecture Overview

**Flow:**

1. Client sends content to API Service (`POST /api/v1/content/submit`)
2. API validates input and applies rate limiting
3. Content is stored in PostgreSQL with status `PENDING`
4. API publishes a `ContentSubmitted` event to Redis Pub/Sub
5. Moderation Processor consumes the event and processes content
6. Moderation result is stored in PostgreSQL
7. Client retrieves status using `GET /api/v1/content/{contentId}/status`

**Components:**
- FastAPI (API Service)
- PostgreSQL (Database)
- Redis (Message Queue)
- Python Worker (Moderation Processor)
- Docker & Docker Compose

---

## 📂 Project Structure

content-moderation-system/
├── src/
│ ├── api/
│ └── processor/
├── docker/
│ └── init.sql
├── tests/
├── docker-compose.yml
├── .env.example
├── README.md
├── API_DOCS.md
└── docs/
└── postman_collection.json

---

## ⚙️ Setup & Run Instructions

### Prerequisites
- Docker
- Docker Compose
- Python 3.10+
- Postman (optional for testing)

---

### 1️⃣ Clone Repository

```bash
git clone https://github.com/<your-username>/content-moderation-system.git
cd content-moderation-system

2️⃣ Start Services
docker-compose up --build


All services will start:

API: http://localhost:8000

PostgreSQL

Redis

Moderation Processor

3️⃣ Run Tests

In a new terminal:

python -m pytest


Expected output:

4 passed in X.XXs

🔌 API Endpoints
POST /api/v1/content/submit

Request Body:

{
  "text": "string",
  "userId": "string"
}


Responses:

202 Accepted → Content accepted

400 Bad Request → Invalid input

429 Too Many Requests → Rate limit exceeded

GET /api/v1/content/{contentId}/status

Response:

{
  "contentId": "uuid",
  "status": "PENDING | APPROVED | REJECTED"
}


Errors:
404 Not Found → Content not found

🧪 Testing

Unit tests for rate limiting logic
Unit tests for moderation logic
Integration tests for end-to-end workflow
Postman collection included in docs/postman_collection.json

🐳 Docker Compose Services

api
processor
database (PostgreSQL)
redis
Health checks ensure correct startup order.

🔐 Environment Variables

See .env.example:

DATABASE_URL=
REDIS_URL=
RATE_LIMIT_PER_MINUTE=

📑 API Documentation

Detailed API documentation is available in:

API_DOCS.md

## 📸 API Testing Screenshots

### Submit Content (Success)
![Submit Success](screenshots/submit_success.png)


### Get Content Status (Approved)
![Status Approved](screenshots/status_approved.png)

### Get Content Status (Rejected)
![Status Rejected](screenshots/rejected.png)

### Invalid Input
![Invalid Input](screenshots/invalid_input.png)

### Rate Limit Exceeded
![Rate Limit](screenshots/rate_limit.png)

### Content Not Found
![Not Found](screenshots/not_found.png)

### Pytest Results
![Pytest](screenshots/pytest_passed.png)


✅ Features Implemented

Dynamic per-user rate limiting (Token Bucket style)
Event-driven architecture using Redis Pub/Sub
Asynchronous moderation processing
Persistent storage with PostgreSQL
Dockerized microservices
Unit & integration testing
Error handling and validation

🚀 Future Improvements

Authentication (API Key / JWT)
Real ML-based moderation logic
Retry mechanism in processor
Circuit breaker
Monitoring & metrics

👩‍💻 Author
Poojitha