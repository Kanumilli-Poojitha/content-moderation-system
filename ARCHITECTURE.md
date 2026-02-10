Architecture Overview – Content Moderation System
1. Introduction

This document describes the architecture and design decisions of the Content Moderation Service with Dynamic Rate Limiting and Asynchronous Event Processing.
The system is designed using a microservices and event-driven approach to ensure scalability, fault tolerance, and responsiveness.

The application consists of two main services:

API Service – handles content submission and status retrieval.

Moderation Processor Service – processes moderation events asynchronously.

Redis is used as a message broker and PostgreSQL as the persistent data store.

2. High-Level Architecture
Components

Client (Postman / Browser / Curl)

API Service (FastAPI)

Redis (Pub/Sub Message Queue)

Moderation Processor (Worker Service)

PostgreSQL Database

Architecture Diagram (Logical Flow)

Client
  |
  v
API Service (FastAPI)
  |
  |-- Save content (PENDING) --> PostgreSQL
  |
  |-- Publish event ---------> Redis (content-moderation-events)
                                |
                                v
                      Moderation Processor
                                |
                                v
                     Update status in PostgreSQL
                                |
                                v
                       Client queries status

3. API Service Design

The API Service is responsible for:

Validating incoming requests
Applying per-user rate limiting
Persisting content data
Publishing moderation events
Providing status retrieval endpoint

Endpoints

POST /api/v1/content/submit

GET /api/v1/content/{contentId}/status

Key Responsibilities

Input validation (non-empty text and userId)
Rate limiting using Token Bucket algorithm
Publishing ContentSubmitted events to Redis
Returning appropriate HTTP status codes

4. Rate Limiting Strategy

A Token Bucket style rate limiting algorithm is used:
Each userId has its own bucket
Configurable via environment variable (RATE_LIMIT_PER_MINUTE)
Prevents abuse and system overload
Returns HTTP 429 Too Many Requests when limit is exceeded

This approach allows bursts of traffic while still enforcing an average request rate.

5. Event-Driven Communication

Redis Pub/Sub is used for asynchronous messaging:
API Service publishes ContentSubmitted events
Moderation Processor subscribes to the same channel
Decouples request handling from moderation processing
Improves responsiveness and scalability

Event Payload Example
{
  "contentId": "uuid",
  "text": "some content",
  "userId": "user123"
}

6. Moderation Processor Design

The Moderation Processor:

Runs as a separate service

Subscribes to Redis events

Performs mock moderation logic

Updates moderation results in database

Moderation Logic

Rejects content if it contains the keyword "badword"

Otherwise randomly approves or rejects content (configurable logic)

7. Database Design

PostgreSQL is used for persistent storage.

Tables

content

id (UUID, primary key)

user_id (string)

text (text)

created_at (timestamp)

moderation_results

content_id (UUID, foreign key)

status (PENDING, APPROVED, REJECTED)

moderated_at (timestamp)

The content is initially stored with status PENDING and later updated by the Moderation Processor.

8. Error Handling & Reliability

API returns appropriate HTTP status codes:

400 – Invalid input
404 – Content not found
429 – Rate limit exceeded
500 – Internal server error
Moderation Processor logs errors

Docker health checks ensure services start in correct order

9. Testing Strategy

The project uses pytest with:

Unit tests for rate limiter
Unit tests for moderation logic
Integration tests for full workflow

This ensures correctness of both individual components and end-to-end flow.

10. Deployment Architecture

Docker and Docker Compose orchestrate:

API Service container
Moderation Processor container
Redis container
PostgreSQL container

Benefits

One-command startup (docker-compose up)
Environment consistency
Easy evaluation
Production-like setup

11. Design Trade-offs
Redis Pub/Sub vs Message Queue (RabbitMQ/Kafka)

Redis Pub/Sub chosen for simplicity
Suitable for demo and lightweight workloads
Easier setup for beginners
Mock Moderation vs ML Model
Simple keyword/random logic used
Keeps focus on system architecture
ML can be added later
Token Bucket Rate Limiting
Allows burst traffic
More flexible than fixed window limits

12. Future Improvements

Authentication using API keys or JWT
Retry mechanism in Moderation Processor
Dead-letter queue for failed events
Real ML-based moderation
Monitoring and metrics (Prometheus, Grafana)
Circuit breaker pattern

13. Conclusion

This architecture demonstrates:

Event-driven microservices design
Dynamic rate limiting
Asynchronous processing
Dockerized deployment
Clean separation of concerns

It provides a solid foundation for building a scalable and resilient content moderation platform.