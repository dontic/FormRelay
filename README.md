# FormRelay

A Django REST framework API to manage the forms on your websites. Waitlists, newsletter signups, and contact forms.

## API Endpoints

### Create Subscriber

```
POST /api/subscribers/
```

Public endpoint (no authentication required) that creates a new subscriber in a given audience. The audience is automatically created if it doesn't already exist. The source domain is recorded from the request's `Origin` or `Referer` header.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `audience` | object | Yes | The audience to subscribe to. |
| `audience.name` | string | Yes | Name of the audience. |
| `audience.audience_type` | string | Yes | One of `waitlist`, `newsletter`, or `contact_form`. |
| `email` | string | Yes | Subscriber's email address. |
| `first_name` | string | No | Subscriber's first name. |
| `last_name` | string | No | Subscriber's last name. |
| `phone` | string | No | Subscriber's phone number. |
| `message` | string | No | Free-text message (useful for contact forms). |
| `custom_data` | object | No | Arbitrary JSON for any extra fields. |

#### Example Request

```json
{
  "audience": {
    "name": "Beta Waitlist",
    "audience_type": "waitlist"
  },
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Doe"
}
```

#### Responses

**`201 Created`** — Subscriber was successfully created.

```json
{
  "id": 1,
  "audience": {
    "name": "Beta Waitlist",
    "audience_type": "waitlist"
  },
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone": "",
  "message": "",
  "custom_data": {},
  "source": null,
  "created_at": "2026-02-23T12:00:00Z"
}
```

**`409 Conflict`** — A subscriber with the same email already exists in this audience.

```json
{
  "detail": "A subscriber with email 'jane@example.com' already exists in this audience."
}
```

**`400 Bad Request`** — Validation failed (missing required fields, invalid email, etc.).
