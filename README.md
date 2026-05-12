# reAPI Agent Skill

Agent skill for calling the public reAPI service at `https://reapi.ai` to
generate images and videos through asynchronous API tasks.

## Features

- Submit image generation tasks
- Submit video generation tasks
- Poll task status until completion
- List bundled model examples
- Print ready-to-edit JSON payloads
- Use only public reAPI endpoints and public documentation

## Requirements

- A reAPI account at `https://reapi.ai`
- A reAPI API key from Dashboard -> API Keys
- Python 3.10+ for the bundled CLI helper

## Get An API Key

1. Open `https://reapi.ai`.
2. Sign in or create an account.
3. Go to Dashboard -> API Keys.
4. Create a new key and copy it once.
5. Configure it before using the skill:

```bash
export REAPI_API_KEY="rk_live_xxx"
```

The skill also accepts `REAPI_KEY`. `REAPI_BASE_URL` is optional and defaults to
`https://reapi.ai`.

You can also create `skills/reapi/.env` based on `skills/reapi/.env.example`.
The CLI only reads `REAPI_*` values from `.env`.

## Claude Code Plugin

From Claude Code:

```bash
/plugin marketplace add https://github.com/reAPIAI/reAPI-skills.git
/plugin install reapi-skills
```

Restart Claude Code after installing.

## Usage

List bundled model examples:

```bash
cd skills/reapi
python3 scripts/reapi.py config
python3 scripts/reapi.py models
```

Print an example payload:

```bash
python3 scripts/reapi.py example gpt-image-2
```

Submit by model id and let the CLI choose the endpoint:

```bash
python3 scripts/reapi.py submit-model gpt-image-2 \
  --wait \
  --json '{"prompt":"a cute red panda","size":"1:1"}'
```

Submit an image task and wait:

```bash
python3 scripts/reapi.py submit images \
  --wait \
  --json '{"model":"gpt-image-2","prompt":"a cute red panda","size":"1:1"}'
```

Submit a video task and wait:

```bash
python3 scripts/reapi.py submit videos \
  --wait \
  --json '{"model":"doubao-seedance-2.0","prompt":"a cinematic red panda","duration":5,"resolution":"720p"}'
```

Poll an existing task:

```bash
python3 scripts/reapi.py wait task_xxx
```

## Structure

```text
skills/reapi/
├── .env.example
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── API.md
│   ├── MODELS.md
│   └── models.json
└── scripts/reapi.py
```

## Public Docs

Use `https://reapi.ai/docs` for the current model-specific parameter reference
and pricing.
