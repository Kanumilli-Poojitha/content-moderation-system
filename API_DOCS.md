# Content Moderation Service – API Documentation

## Base URL

http://localhost:8000


---

## Authentication

Currently, no authentication is required.  
Future versions may use API keys or JWT authentication.

---

## Content Submission API

### Endpoint
POST /api/v1/content/submit


### Description
Submits user-generated content for moderation.  
The request is rate-limited per user and processed asynchronously.

---

### Request Headers
Content-Type: application/json


---

### Request Body

```json
{
  "text": "string",
  "userId": "string"
}

Field	Type	Required	Description
text	string	Yes	Content to be moderated
userId	string	Yes	Unique user identifier
Success Response

Status Code: 202 Accepted

{
  "message": "Content accepted for moderation",
  "contentId": "uuid"
}

Error Responses
400 Bad Request
{
  "detail": "Invalid request body"
}

429 Too Many Requests
{
  "detail": "Rate limit exceeded"
}

Content Status API
Endpoint
GET /api/v1/content/{contentId}/status

Description

Returns the current moderation status of the submitted content.

Path Parameters
Parameter	Type	Description
contentId	UUID	ID of the content
Success Response

Status Code: 200 OK

{
  "contentId": "uuid",
  "status": "PENDING | APPROVED | REJECTED"
}

Error Responses
404 Not Found
{
  "detail": "Content not found"
}

Rate Limiting

Each user is limited to a fixed number of requests per minute.

Behavior:

Rate limiting is applied per userId

Excess requests return HTTP 429 Too Many Requests

Event Processing

When content is submitted:

API stores the content with status PENDING

Publishes a ContentSubmitted event to Redis

Moderation Processor consumes the event

Status is updated to APPROVED or REJECTED

Processing is asynchronous.

Example Workflow
1. Submit Content
POST /api/v1/content/submit

{
  "text": "Hello world",
  "userId": "user123"
}


Response:

{
  "message": "Content accepted for moderation",
  "contentId": "9f1a2c33-5f2a-4a12-b8d4-123456789abc"
}

2. Check Status
GET /api/v1/content/9f1a2c33-5f2a-4a12-b8d4-123456789abc/status


Response:

{
  "contentId": "9f1a2c33-5f2a-4a12-b8d4-123456789abc",
  "status": "APPROVED"
}

Error Codes Summary
Status Code	Meaning
200	Success
202	Accepted for processing
400	Bad Request
404	Not Found
429	Rate Limit Exceeded
500	Internal Server Error
Future Enhancements

Authentication & Authorization

Pagination for history endpoints

Webhooks for moderation results
ML-based moderation engine
Monitoring and logging

Contact
For questions or issues, please open a GitHub issue.