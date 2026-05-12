#!/usr/bin/env python3
"""Small CLI for the public reAPI API.

Examples:
  python3 scripts/reapi.py config
  python3 scripts/reapi.py models
  python3 scripts/reapi.py example gpt-image-2
  python3 scripts/reapi.py submit images --wait \
    --json '{"model":"gpt-image-2","prompt":"a red panda"}'
  python3 scripts/reapi.py wait task_xxx
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://reapi.ai"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
SKILL_DIR = Path(__file__).resolve().parents[1]
MODELS_JSON = SKILL_DIR / "references" / "models.json"


def load_env_file() -> None:
    """Load REAPI_* values from .env without overriding existing env vars."""
    candidates = [Path.cwd() / ".env", SKILL_DIR / ".env"]
    for path in candidates:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key.startswith("REAPI_"):
                continue
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def env_api_key() -> str | None:
    return os.environ.get("REAPI_API_KEY") or os.environ.get("REAPI_KEY")


def normalize_base_url(raw: str | None) -> str:
    return (raw or os.environ.get("REAPI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def request_user_agent() -> str:
    return os.environ.get("REAPI_USER_AGENT") or DEFAULT_USER_AGENT


def load_models() -> list[dict[str, Any]]:
    try:
        data = json.loads(MODELS_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing model catalog: {MODELS_JSON}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid model catalog JSON: {exc}") from exc
    models = data.get("models")
    if not isinstance(models, list):
        raise SystemExit("Invalid model catalog: expected {\"models\": [...]}")
    return [m for m in models if isinstance(m, dict)]


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json and args.json_file:
        raise SystemExit("Use either --json or --json-file, not both")
    if args.json_file:
        text = Path(args.json_file).read_text(encoding="utf-8")
    elif args.json:
        text = args.json
    else:
        raise SystemExit("Missing payload. Pass --json or --json-file.")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON payload: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Payload must be a JSON object")
    return value


def request_json(
    method: str,
    url: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
) -> tuple[int, dict[str, str], Any]:
    body = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": request_user_agent(),
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            text = res.read().decode("utf-8")
            data = json.loads(text) if text else None
            return res.status, dict(res.headers.items()), data
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            data = json.loads(text) if text else {"error": {"message": text}}
        except json.JSONDecodeError:
            data = {"error": {"message": text}}
        return exc.code, dict(exc.headers.items()), data
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error calling reAPI: {exc}") from exc


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def require_api_key(args: argparse.Namespace) -> str:
    api_key = args.api_key or env_api_key()
    if not api_key:
        raise SystemExit(
            "Missing API key. Get one at https://reapi.ai -> Dashboard -> "
            "API Keys, then set REAPI_API_KEY."
        )
    return api_key


def endpoint_path(kind: str) -> str:
    if kind == "images":
        return "/api/v1/images/generations"
    if kind == "videos":
        return "/api/v1/videos/generations"
    raise SystemExit(f"Unsupported endpoint kind: {kind}")


def endpoint_for_model(model_id: str) -> str | None:
    for model in load_models():
        if model.get("id") == model_id:
            endpoint = model.get("endpoint")
            return endpoint if isinstance(endpoint, str) else None
    return None


def is_terminal(task: Any) -> bool:
    return isinstance(task, dict) and task.get("status") in {"completed", "failed"}


def wait_for_task(
    base_url: str,
    api_key: str,
    task_id: str,
    interval: float,
    timeout: float,
) -> Any:
    deadline = time.monotonic() + timeout
    last: Any = None
    while True:
        status, headers, data = request_json(
            "GET", f"{base_url}/api/v1/tasks/{task_id}", api_key
        )
        last = data
        if status == 429:
            retry_after = headers.get("Retry-After")
            sleep_for = float(retry_after) if retry_after else interval
            time.sleep(max(1.0, sleep_for))
            continue
        if status in {500, 502, 503, 504}:
            if time.monotonic() >= deadline:
                return data
            time.sleep(interval)
            continue
        if status != 200:
            return data
        if is_terminal(data):
            return data
        if time.monotonic() >= deadline:
            return {
                "status": "timeout",
                "message": f"Timed out waiting for task {task_id}",
                "last": last,
            }
        time.sleep(interval)


def cmd_submit(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = normalize_base_url(args.base_url)
    payload = load_payload(args)
    url = base_url + endpoint_path(args.kind)
    status, _headers, data = request_json(
        "POST", url, api_key, payload, idempotency_key=args.idempotency_key
    )
    if status < 200 or status >= 300:
        print_json(data)
        return 1
    if not args.wait:
        print_json(data)
        return 0
    if not isinstance(data, dict) or not isinstance(data.get("id"), str):
        print_json(data)
        return 1
    final = wait_for_task(
        base_url, api_key, data["id"], args.poll_interval, args.timeout
    )
    print_json(final)
    return 0 if isinstance(final, dict) and final.get("status") == "completed" else 1


def cmd_config(args: argparse.Namespace) -> int:
    api_key = args.api_key or env_api_key()
    base_url = normalize_base_url(args.base_url)
    result = {
        "base_url": base_url,
        "api_key": "set" if api_key else "missing",
        "docs": "https://reapi.ai/docs",
    }
    if not api_key:
        result["how_to_get_key"] = (
            "Open https://reapi.ai, sign in, go to Dashboard -> API Keys, "
            "create a key, then set REAPI_API_KEY."
        )
    print_json(result)
    return 0 if api_key else 1


def cmd_models(args: argparse.Namespace) -> int:
    models = load_models()
    if args.endpoint:
        models = [m for m in models if m.get("endpoint") == args.endpoint]
    if args.json:
        print_json({"models": models})
        return 0
    if not models:
        print("No models found.")
        return 0
    by_endpoint: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        endpoint = str(model.get("endpoint", "unknown"))
        by_endpoint.setdefault(endpoint, []).append(model)
    for endpoint in sorted(by_endpoint):
        print(f"\n[{endpoint}]")
        for model in sorted(by_endpoint[endpoint], key=lambda m: str(m.get("id", ""))):
            print(f"  {model.get('id')} - {model.get('description', '')}")
    print(f"\nTotal: {len(models)} model(s)")
    return 0


def cmd_example(args: argparse.Namespace) -> int:
    for model in load_models():
        if model.get("id") == args.model:
            example = model.get("example")
            if not isinstance(example, dict):
                raise SystemExit(f"No example payload for model: {args.model}")
            if args.with_command:
                endpoint = model.get("endpoint")
                if endpoint not in {"images", "videos"}:
                    raise SystemExit(f"Unsupported endpoint for model: {args.model}")
                payload = json.dumps(example, ensure_ascii=False)
                print(
                    "python3 scripts/reapi.py submit "
                    f"{shlex.quote(str(endpoint))} --wait --json {shlex.quote(payload)}"
                )
            else:
                print_json(example)
            return 0
    raise SystemExit(f"Unknown model: {args.model}. Run `reapi.py models`.")


def cmd_submit_model(args: argparse.Namespace) -> int:
    endpoint = endpoint_for_model(args.model)
    if endpoint not in {"images", "videos"}:
        raise SystemExit(f"Unknown or unsupported model: {args.model}")
    args.kind = endpoint
    payload = load_payload(args)
    if "model" in payload and payload["model"] != args.model:
        raise SystemExit("Payload model does not match submit-model argument")
    payload["model"] = args.model
    args.json = json.dumps(payload)
    args.json_file = None
    return cmd_submit(args)


def cmd_get(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = normalize_base_url(args.base_url)
    status, _headers, data = request_json(
        "GET", f"{base_url}/api/v1/tasks/{args.task_id}", api_key
    )
    print_json(data)
    return 0 if status == 200 else 1


def cmd_wait(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = normalize_base_url(args.base_url)
    final = wait_for_task(
        base_url, api_key, args.task_id, args.poll_interval, args.timeout
    )
    print_json(final)
    return 0 if isinstance(final, dict) and final.get("status") == "completed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call the public reAPI API")
    parser.add_argument("--api-key", help="reAPI API key; defaults to REAPI_API_KEY")
    parser.add_argument(
        "--base-url",
        help=f"API base URL; defaults to REAPI_BASE_URL or {DEFAULT_BASE_URL}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    config = sub.add_parser("config", help="Check reAPI configuration")
    config.set_defaults(func=cmd_config)

    models = sub.add_parser("models", help="List bundled model examples")
    models.add_argument("--endpoint", choices=["images", "videos"])
    models.add_argument("--json", action="store_true", help="Output as JSON")
    models.set_defaults(func=cmd_models)

    example = sub.add_parser("example", help="Print an example payload")
    example.add_argument("model")
    example.add_argument(
        "--with-command",
        action="store_true",
        help="Print a ready-to-run submit command instead of JSON",
    )
    example.set_defaults(func=cmd_example)

    submit = sub.add_parser("submit", help="Submit an image or video task")
    submit.add_argument("kind", choices=["images", "videos"])
    submit.add_argument("--json", help="Request payload JSON object")
    submit.add_argument("--json-file", help="Path to request payload JSON file")
    submit.add_argument("--idempotency-key", help="Optional Idempotency-Key header")
    submit.add_argument("--wait", action="store_true", help="Poll until terminal")
    submit.add_argument("--poll-interval", type=float, default=2.5)
    submit.add_argument("--timeout", type=float, default=600)
    submit.set_defaults(func=cmd_submit)

    submit_model = sub.add_parser(
        "submit-model", help="Submit by model id using its catalog endpoint"
    )
    submit_model.add_argument("model")
    submit_model.add_argument("--json", help="Request payload JSON object")
    submit_model.add_argument("--json-file", help="Path to request payload JSON file")
    submit_model.add_argument(
        "--idempotency-key", help="Optional Idempotency-Key header"
    )
    submit_model.add_argument("--wait", action="store_true", help="Poll until terminal")
    submit_model.add_argument("--poll-interval", type=float, default=2.5)
    submit_model.add_argument("--timeout", type=float, default=600)
    submit_model.set_defaults(func=cmd_submit_model)

    get = sub.add_parser("get", help="Get task status once")
    get.add_argument("task_id")
    get.set_defaults(func=cmd_get)

    wait = sub.add_parser("wait", help="Poll task until terminal")
    wait.add_argument("task_id")
    wait.add_argument("--poll-interval", type=float, default=2.5)
    wait.add_argument("--timeout", type=float, default=600)
    wait.set_defaults(func=cmd_wait)
    return parser


def main() -> int:
    load_env_file()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
