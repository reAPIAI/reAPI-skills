---
name: reapi
description: "Call the public reAPI service to generate images and videos through asynchronous API tasks. Use when the user asks to use reAPI/reapi.ai, generate media with reAPI models, submit image or video generation jobs, poll task status, retrieve generated image_urls/video_urls, list example model payloads, or troubleshoot reAPI API responses. Requires a reAPI API key in REAPI_API_KEY or REAPI_KEY; default base URL is https://reapi.ai."
---

# reAPI

Use reAPI's public API to submit asynchronous image/video generation tasks and
poll for generated media URLs.

Default API base URL: `https://reapi.ai`.

## Security

This skill is safe to publish. Keep it that way:

- Do not add private repository paths, internal implementation details,
  deployment secrets, database URLs, or API keys.
- Treat all request examples as public API usage examples.
- Never paste a user's API key in the final answer.

## Configuration

Required:

- `REAPI_API_KEY` or `REAPI_KEY`: reAPI bearer token.

Get an API key:

1. Open `https://reapi.ai`.
2. Sign in or create an account.
3. Go to Dashboard -> API Keys.
4. Create a new key and copy it once.
5. Set it in the shell before using this skill:

```bash
export REAPI_API_KEY="rk_live_xxx"
```

Optional:

- `REAPI_BASE_URL`: override the API base URL. Defaults to `https://reapi.ai`.

If the API key is missing, ask the user to configure it. Do not ask them to paste
the key into chat unless there is no safer option. Direct them to
`https://reapi.ai` to create the key.

## Quick Start

Use the bundled script from this skill directory.

Check configuration:

```bash
python3 scripts/reapi.py config
```

List bundled model examples:

```bash
python3 scripts/reapi.py models
```

Print an example payload:

```bash
python3 scripts/reapi.py example gpt-image-2
```

Print a ready-to-run command for a model:

```bash
python3 scripts/reapi.py example gpt-image-2 --with-command
```

Submit an image task and wait for completion:

```bash
python3 scripts/reapi.py submit images \
  --wait \
  --json '{"model":"gpt-image-2","prompt":"a cute red panda eating bamboo","size":"1:1"}'
```

Submit a video task and wait for completion:

```bash
python3 scripts/reapi.py submit videos \
  --wait \
  --json '{"model":"doubao-seedance-2.0","prompt":"a cinematic red panda walking through bamboo","duration":5,"resolution":"720p"}'
```

Poll an existing task:

```bash
python3 scripts/reapi.py wait task_xxx
```

Get a task once:

```bash
python3 scripts/reapi.py get task_xxx
```

Submit by model id and let the CLI pick the endpoint from the bundled catalog:

```bash
python3 scripts/reapi.py submit-model gpt-image-2 \
  --wait \
  --json '{"prompt":"a cute red panda","size":"1:1"}'
```

## API Workflow

1. Submit to `/api/v1/images/generations` or `/api/v1/videos/generations`.
2. Read `id` from the response.
3. Poll `GET /api/v1/tasks/{id}` every 2-3 seconds.
4. On `status: "completed"`, return URLs from `output.image_urls`,
   or `output.video_urls`.
5. On `status: "failed"`, report `error.code` and `error.message`.

Polling does not consume credits. Submission requests consume credits based on
the selected model and parameters.

## Raw Curl

```bash
curl https://reapi.ai/api/v1/images/generations \
  -H "Authorization: Bearer $REAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"a cute red panda","size":"1:1"}'
```

```bash
curl https://reapi.ai/api/v1/tasks/task_xxx \
  -H "Authorization: Bearer $REAPI_API_KEY"
```

## Error Handling

reAPI errors use:

```json
{
  "error": {
    "code": 20002,
    "message": "Missing required parameter",
    "request_id": "req_xxx"
  }
}
```

Handling rules:

- `400`, `401`, `402`, `404`: fix the request or credentials.
- `429`: retry after the `Retry-After` header.
- `500`, `502`, `503`, `504`: for polling, retry with backoff when appropriate.
  For submission, avoid blind retries unless the user accepts the possibility of
  creating a second task.
- Completed HTTP polling with `status: "failed"` is a task failure; report the
  task's `error.code` and `error.message`.

## References

- `references/API.md`: public endpoint, task, auth, and response notes.
- `references/MODELS.md`: bundled model examples and common parameters.
- `references/models.json`: machine-readable examples used by the CLI.
- Public docs: `https://reapi.ai/docs`
