"""LLM providers behind one interface (ported from Day 4 providers.py). No agent loop here.

    provider = Provider.from_env()            # reads PROVIDER, MODEL, TEMPERATURE (+ API key)
    r = provider.complete(messages, schemas)  # Chat Completions-format messages and tool schemas
    r -> {message, calls, finish, usage: {input_tokens, output_tokens}, latency_ms, retries, model}

Changes vs Day 4: `ollama` (local, no key), temperature (default 0 for reproducible runs),
normalized token usage and latency for time/cost reporting, retry also on transient 5xx.
Standard library only.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

# name -> (API key env var or None, default endpoint, request timeout in seconds)
CONFIG = {
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", 60),
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions", 60),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1/chat/completions", 60),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/messages", 60),
    # Ollama's OpenAI-compatible endpoint; override with OLLAMA_BASE_URL. Local models are slower.
    "ollama": (None, "http://localhost:11434/v1/chat/completions", 300),
}
RETRY_STATUS = {429, 500, 502, 503, 504}


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], *, timeout: float,
              retries: int = 4, on_retry: Any = None) -> dict[str, Any]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Rate limit or transient server error: same request again with backoff (Retry-After if given).
            if exc.code in RETRY_STATUS and attempt < retries:
                wait = exc.headers.get("Retry-After") if exc.headers else None
                seconds = float(wait) if wait and wait.isdigit() else 5 * 2 ** attempt  # 5, 10, 20, 40 s
                if on_retry:
                    on_retry({"status": exc.code, "wait_s": seconds})
                time.sleep(seconds)
                continue
            # Do not print response bodies: they may contain account or request data.
            raise RuntimeError(f"provider returned HTTP {exc.code}; check model, key and quota") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"cannot reach provider: {exc.reason}") from exc
    raise AssertionError("unreachable")


def normalize_usage(usage: dict[str, Any]) -> dict[str, int]:
    """OpenAI-style (prompt/completion_tokens) or Anthropic-style (input/output_tokens) -> one shape."""
    return {"input_tokens": int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0),
            "output_tokens": int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0)}


class Provider:
    """complete(messages, schemas) -> {message, calls, finish, usage, latency_ms, model}.

    messages use the Chat Completions format (system/user/assistant/tool). Append the returned
    `message` unchanged; a tool result is {role: "tool", tool_call_id, content: JSON string}.
    """

    def __init__(self, name: str, model: str, *, temperature: float = 0.0) -> None:
        if name not in CONFIG:
            raise ValueError(f"unknown provider {name!r}; choose one of {sorted(CONFIG)}")
        if not model:
            raise ValueError("set MODEL to a model that supports tool calling")
        self.name, self.model, self.temperature = name, model, temperature
        key_name, self.url, self.timeout = CONFIG[name]
        if name == "ollama":
            self.url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/") + "/chat/completions"
        self.key = os.getenv(key_name) if key_name else None
        if key_name and not self.key:
            raise ValueError(f"{key_name} is not set; add it to .env (see .env.example)")

    @classmethod
    def from_env(cls) -> "Provider":
        return cls(os.getenv("PROVIDER", ""), os.getenv("MODEL", ""),
                   temperature=float(os.getenv("TEMPERATURE", "0")))

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.model, "temperature": self.temperature}

    def complete(self, messages: list[dict[str, Any]], schemas: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        start = time.perf_counter()
        self._retries: list[dict[str, Any]] = []
        result = self._anthropic(messages, schemas or []) if self.name == "anthropic" else self._chat(messages, schemas or [])
        result["latency_ms"] = round((time.perf_counter() - start) * 1000, 1)
        result["retries"] = self._retries  # HTTP 429/5xx retries inside this call (time is included above)
        return result

    def _chat(self, messages: list[dict[str, Any]], schemas: list[dict[str, Any]]) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": self.temperature}
        if schemas:
            payload["tools"] = schemas
        headers = {"Authorization": f"Bearer {self.key}"} if self.key else {}
        data = post_json(self.url, headers, payload, timeout=self.timeout, on_retry=self._retries.append)
        choice = data["choices"][0]
        message = choice["message"]
        calls = [{"id": c["id"], "name": c["function"]["name"], "arguments": c["function"]["arguments"]}
                 for c in message.get("tool_calls") or []]
        return {"message": message, "calls": calls, "finish": choice.get("finish_reason"),
                "usage": normalize_usage(data.get("usage") or {}), "model": data.get("model", self.model)}

    def _anthropic(self, messages: list[dict[str, Any]], schemas: list[dict[str, Any]]) -> dict[str, Any]:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        native: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "system":
                continue
            if m["role"] == "assistant":
                blocks = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": m["content"]})
                for call in m.get("tool_calls") or []:
                    blocks.append({"type": "tool_use", "id": call["id"], "name": call["function"]["name"],
                                   "input": json.loads(call["function"]["arguments"])})
                native.append({"role": "assistant", "content": blocks})
            elif m["role"] == "tool":
                block = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}
                if native and native[-1]["role"] == "user" and isinstance(native[-1]["content"], list):
                    native[-1]["content"].append(block)
                else:
                    native.append({"role": "user", "content": [block]})
            else:
                native.append({"role": "user", "content": m["content"]})
        tools = [{"name": x["function"]["name"], "description": x["function"]["description"],
                  "input_schema": x["function"]["parameters"]} for x in schemas]
        payload: dict[str, Any] = {"model": self.model, "max_tokens": 1024, "system": system,
                                   "messages": native, "temperature": self.temperature}
        if tools:
            payload["tools"] = tools
        data = post_json(self.url, {"x-api-key": self.key, "anthropic-version": "2023-06-01"}, payload,
                         timeout=self.timeout, on_retry=self._retries.append)
        blocks = data["content"]
        calls = [{"id": b["id"], "name": b["name"], "arguments": json.dumps(b["input"], ensure_ascii=False)}
                 for b in blocks if b["type"] == "tool_use"]
        text = "\n".join(b["text"] for b in blocks if b["type"] == "text")
        message: dict[str, Any] = {"role": "assistant", "content": text or None}
        if calls:
            message["tool_calls"] = [{"id": c["id"], "type": "function",
                                      "function": {"name": c["name"], "arguments": c["arguments"]}} for c in calls]
        reason = {"end_turn": "stop", "tool_use": "tool_calls", "max_tokens": "length"}.get(
            data.get("stop_reason"), data.get("stop_reason"))
        return {"message": message, "calls": calls, "finish": reason,
                "usage": normalize_usage(data.get("usage") or {}), "model": data.get("model", self.model)}
