"""Offline provider checks: request/response mapping only, no network and no model quality."""
import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import providers
from src.providers import Provider

SCHEMA = [{"type": "function", "function": {"name": "search", "description": "Search the chapter",
                                            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}}}]
CHAT_REPLY = {"model": "m-1", "usage": {"prompt_tokens": 12, "completion_tokens": 3},
              "choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "content": None,
                           "tool_calls": [{"id": "c1", "type": "function",
                                           "function": {"name": "search", "arguments": '{"query": "iris"}'}}]}}]}


class ProviderTests(unittest.TestCase):
    def test_missing_key_and_unknown_provider_fail_loudly(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                Provider("gemini", "gemini-x")
            with self.assertRaises(ValueError):
                Provider("nope", "m")
            with self.assertRaises(ValueError):
                Provider("ollama", "")

    def test_chat_payload_and_normalized_result(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}, clear=True), \
                mock.patch.object(providers, "post_json", return_value=CHAT_REPLY) as post:
            r = Provider("gemini", "gemini-x").complete([{"role": "user", "content": "hi"}], SCHEMA)
        url, headers, payload = post.call_args.args
        self.assertEqual((payload["model"], payload["temperature"], payload["tools"]), ("gemini-x", 0.0, SCHEMA))
        self.assertEqual(headers, {"Authorization": "Bearer k"})
        self.assertEqual(r["calls"], [{"id": "c1", "name": "search", "arguments": '{"query": "iris"}'}])
        self.assertEqual(r["usage"], {"input_tokens": 12, "output_tokens": 3})
        self.assertEqual(r["finish"], "tool_calls")
        self.assertIn("latency_ms", r)

    def test_ollama_needs_no_key_and_uses_base_url(self):
        env = {"OLLAMA_BASE_URL": "http://127.0.0.1:9999/v1/"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(providers, "post_json", return_value=CHAT_REPLY) as post:
            Provider("ollama", "local-model").complete([{"role": "user", "content": "hi"}])
        url, headers, payload = post.call_args.args
        self.assertEqual(url, "http://127.0.0.1:9999/v1/chat/completions")
        self.assertEqual(headers, {})
        self.assertNotIn("tools", payload)

    def test_from_env_reads_provider_model_temperature(self):
        env = {"PROVIDER": "openai", "MODEL": "gpt-x", "TEMPERATURE": "0.2", "OPENAI_API_KEY": "k"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(Provider.from_env().info(), {"provider": "openai", "model": "gpt-x", "temperature": 0.2})

    def test_anthropic_tool_round_trip_mapping(self):
        reply = {"stop_reason": "tool_use", "usage": {"input_tokens": 7, "output_tokens": 2},
                 "content": [{"type": "tool_use", "id": "t1", "name": "search", "input": {"query": "iris"}}]}
        messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": "q"},
                    {"role": "assistant", "content": None, "tool_calls": CHAT_REPLY["choices"][0]["message"]["tool_calls"]},
                    {"role": "tool", "tool_call_id": "c1", "content": "[]"}]
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "k"}, clear=True), \
                mock.patch.object(providers, "post_json", return_value=reply) as post:
            r = Provider("anthropic", "m").complete(messages, SCHEMA)
        payload = post.call_args.args[2]
        self.assertEqual(payload["system"], "sys")
        self.assertEqual([m["role"] for m in payload["messages"]], ["user", "assistant", "user"])
        self.assertEqual(payload["messages"][2]["content"][0]["tool_use_id"], "c1")
        self.assertEqual((r["finish"], r["usage"]), ("tool_calls", {"input_tokens": 7, "output_tokens": 2}))
        self.assertEqual(json.loads(r["calls"][0]["arguments"]), {"query": "iris"})

    def test_post_json_retries_transient_errors_then_raises_without_body(self):
        err = lambda code: urllib.error.HTTPError("u", code, "x", {"Retry-After": "0"}, io.BytesIO(b"secret body"))
        ok = mock.MagicMock()
        ok.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        with mock.patch("urllib.request.urlopen", side_effect=[err(503), err(429), ok]):
            self.assertEqual(providers.post_json("http://example.invalid", {}, {}, timeout=1), {"ok": True})
        with mock.patch("urllib.request.urlopen", side_effect=err(401)):
            with self.assertRaises(RuntimeError) as ctx:
                providers.post_json("http://example.invalid", {}, {}, timeout=1)
        self.assertNotIn("secret", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
