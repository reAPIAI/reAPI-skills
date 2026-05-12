# reAPI Public API

Base URL:

```text
https://reapi.ai
```

Authentication:

```http
Authorization: Bearer <reapi-api-key>
```

Get an API key from `https://reapi.ai`:

1. Sign in or create an account.
2. Open Dashboard -> API Keys.
3. Create a new key.
4. Store it in `REAPI_API_KEY` or `REAPI_KEY`.

Do not commit or print keys.

## Submit Image Task

```http
POST /api/v1/images/generations
Content-Type: application/json
```

Example:

```json
{
  "model": "gpt-image-2",
  "prompt": "a cute red panda eating bamboo, photorealistic",
  "size": "1:1"
}
```

## Submit Video Task

```http
POST /api/v1/videos/generations
Content-Type: application/json
```

Example:

```json
{
  "model": "doubao-seedance-2.0",
  "prompt": "a cinematic red panda walking through bamboo",
  "duration": 5,
  "resolution": "720p"
}
```

## Submit Response

Submission returns immediately with a task:

```json
{
  "id": "task_xxx",
  "model": "gpt-image-2",
  "status": "processing",
  "created_at": 1735000000
}
```

## Poll Task

```http
GET /api/v1/tasks/{id}
```

Poll every 2-3 seconds. Polling does not consume credits.

Completed image output:

```json
{
  "id": "task_xxx",
  "model": "gpt-image-2",
  "status": "completed",
  "output": {
    "image_urls": ["https://cdn.reapi.ai/media/.../0.png"]
  },
  "error": null
}
```

Completed video output:

```json
{
  "id": "task_xxx",
  "model": "doubao-seedance-2.0",
  "status": "completed",
  "output": {
    "video_urls": ["https://cdn.reapi.ai/media/.../0.mp4"]
  },
  "error": null
}
```

Failed task:

```json
{
  "id": "task_xxx",
  "status": "failed",
  "output": null,
  "error": {
    "code": 80006,
    "message": "Request violates content policy"
  }
}
```

## Error Envelope

HTTP errors return:

```json
{
  "error": {
    "code": 20002,
    "message": "Missing required parameter",
    "request_id": "req_xxx"
  }
}
```

Common handling:

- `400`: invalid request parameters.
- `401`: missing, malformed, invalid, or revoked API key.
- `402`: insufficient credits.
- `404`: task not found or not owned by the API key's user.
- `429`: rate limited; use `Retry-After`.
- `5xx`: service or dependency issue. Retrying polling is safe. Avoid blind
  retries of submission requests unless the user accepts creating a second task.

## Public Docs

For current model-specific parameters and pricing, use:

```text
https://reapi.ai/docs
```
