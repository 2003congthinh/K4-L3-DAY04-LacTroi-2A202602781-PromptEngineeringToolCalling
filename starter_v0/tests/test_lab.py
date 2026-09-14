from __future__ import annotations

import json
import importlib
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import HelpdeskAgent
from chat import run_model_tool_loop
from providers.base import ModelResponse, ToolCall
from run_eval import evaluate_phase_b, load_cases, validate_expected_tools
from tools import TOOL_FUNCTIONS, load_tool_declarations
ticket_module = importlib.import_module("tools.create_ticket.tool")
external_search_module = importlib.import_module("tools.search_device_info.tool")


BASE_PATH = ROOT / "data" / "eval_base.json"
EXTENSION_PATH = ROOT / "data" / "eval_helpdesk_extension.json"
GROUP_PATH = ROOT / "data" / "eval_group.json"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"


class FakeProvider:
    def __init__(self, calls: list[ToolCall], text: str | None = None) -> None:
        self.calls = calls
        self.text = text

    def complete(self, messages, tools=None, **kwargs):
        return ModelResponse(text=self.text, tool_calls=self.calls)


class SequenceProvider:
    def __init__(self, responses: list[ModelResponse]) -> None:
        self.responses = list(responses)

    def complete(self, messages, tools=None, **kwargs):
        return self.responses.pop(0)


class FakeHTTPResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"results": [{
            "title": "Official support page",
            "url": "https://support.lenovo.com/example",
            "content": "Official driver and support information.",
            "score": 0.99,
        }]}


class LabStructureTests(unittest.TestCase):
    def test_json_and_yaml_load(self) -> None:
        for path in (BASE_PATH, EXTENSION_PATH, GROUP_PATH):
            json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(load_tool_declarations(TOOLS_PATH)), 5)

    def test_fixed_dataset_shape(self) -> None:
        base = json.loads(BASE_PATH.read_text(encoding="utf-8"))["cases"]
        extension = json.loads(EXTENSION_PATH.read_text(encoding="utf-8"))["cases"]
        group = json.loads(GROUP_PATH.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(base), 20)
        self.assertEqual(sum("query" in case for case in base), 14)
        self.assertEqual(sum("turns" in case for case in base), 6)
        self.assertEqual(len(extension), 10)
        self.assertEqual(group, [])
        self.assertEqual(len({case["id"] for case in base + extension}), 30)

    def test_every_expected_tool_is_declared_and_implemented(self) -> None:
        declarations = load_tool_declarations(TOOLS_PATH)
        for path in (BASE_PATH, EXTENSION_PATH):
            cases = load_cases(path, "B")
            validate_expected_tools(cases, declarations, path)

    def test_registry_and_tool_docs_match_declarations(self) -> None:
        declared = {item["name"] for item in load_tool_declarations(TOOLS_PATH)}
        self.assertEqual(declared, set(TOOL_FUNCTIONS))
        for name in declared:
            tool_doc = ROOT / "tools" / name / "TOOL.md"
            implementation = ROOT / "tools" / name / "tool.py"
            self.assertTrue(tool_doc.exists(), name)
            self.assertTrue(implementation.exists(), name)
            self.assertIn(f"name: {name}", tool_doc.read_text(encoding="utf-8"))

    def test_each_eval_case_scores_pass_for_its_expected_calls(self) -> None:
        for path in (BASE_PATH, EXTENSION_PATH):
            for case in load_cases(path, "B"):
                expected = case["expect"]
                calls = expected.get("tool_calls", [])
                result = evaluate_phase_b(case, calls, "mock response")
                self.assertTrue(result["passed"], f"{case['id']}: {result['failures']}")

    def test_expected_calls_execute_without_contract_error(self) -> None:
        for path in (BASE_PATH, EXTENSION_PATH):
            for case in load_cases(path, "B"):
                for call in case["expect"].get("tool_calls", []):
                    args = dict(call.get("args", {}))
                    if call["name"] == "clarify":
                        args.setdefault("question", "Synthetic test question")
                    elif call["name"] == "search_kb":
                        args.setdefault("query", case.get("query", "vpn"))
                    elif call["name"] == "policy":
                        args.setdefault("query", case.get("query", "ticket"))
                    elif call["name"] == "format_incident_report":
                        args.setdefault("findings", [{"label": "test", "detail": "ok"}])
                    elif call["name"] == "create_ticket":
                        args.setdefault("summary", "Synthetic validation ticket")
                        args["confirmed"] = False
                    if call["name"] == "search_device_info":
                        with mock.patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}), mock.patch.object(
                            external_search_module.requests, "post", return_value=FakeHTTPResponse()
                        ):
                            output = TOOL_FUNCTIONS[call["name"]](**args)
                    else:
                        output = TOOL_FUNCTIONS[call["name"]](**args)
                    self.assertIsInstance(output, dict, case["id"])
                    self.assertNotIn("error", output, case["id"])


class ToolContractTests(unittest.TestCase):
    def test_local_data_tools(self) -> None:
        status = TOOL_FUNCTIONS["check_service_status"]("vpn", "production")
        self.assertEqual(status["status"], "degraded")
        device = TOOL_FUNCTIONS["inspect_device"]("lt-204", "vpn")
        self.assertIn("AUTH_TIMEOUT", device["diagnostics"]["vpn"])
        user = TOOL_FUNCTIONS["lookup_user"]("emp-1003")
        self.assertEqual(user["employee"]["assigned_assets"], ["DT-031"])
        kb = TOOL_FUNCTIONS["search_kb"]("Outlook Windows 11", "email", 1)
        self.assertEqual(kb["results"][0]["article_id"], "KB-EMAIL-002")
        policy = TOOL_FUNCTIONS["policy"]("xác nhận tạo ticket", "ticketing", 1)
        self.assertEqual(policy["results"][0]["policy_area"], "ticketing")

    def test_not_found_contracts(self) -> None:
        self.assertEqual(TOOL_FUNCTIONS["inspect_device"]("LT-999")["error"], "asset_not_found")
        self.assertEqual(TOOL_FUNCTIONS["lookup_user"]("EMP-9999")["error"], "employee_not_found")
        self.assertEqual(TOOL_FUNCTIONS["check_service_status"]("erp")["error"], "not_found")

    def test_external_device_search_uses_public_product_data_only(self) -> None:
        with mock.patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}), mock.patch.object(
            external_search_module.requests, "post", return_value=FakeHTTPResponse()
        ) as post:
            result = TOOL_FUNCTIONS["search_device_info"]("Lenovo", "ThinkPad T14 Gen 4", "drivers", 9)
        self.assertEqual(result["items"][0]["source"], "support.lenovo.com")
        request_body = post.call_args.kwargs["json"]
        self.assertEqual(request_body["max_results"], 5)
        self.assertEqual(request_body["include_domains"], ["support.lenovo.com", "psref.lenovo.com"])
        serialized = json.dumps(request_body).lower()
        self.assertNotIn("lt-204", serialized)
        self.assertNotIn("emp-", serialized)

    def test_external_device_search_requires_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            result = TOOL_FUNCTIONS["search_device_info"]("Lenovo", "ThinkPad T14 Gen 4", "specs")
        self.assertEqual(result["error"], "missing_api_key")

    def test_external_device_search_rejects_internal_identifier(self) -> None:
        with mock.patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}), mock.patch.object(
            external_search_module.requests, "post"
        ) as post:
            result = TOOL_FUNCTIONS["search_device_info"]("Lenovo", "ThinkPad T14 Gen 4 LT-204", "specs")
        self.assertEqual(result["error"], "restricted_internal_identifier")
        post.assert_not_called()

    def test_ticket_requires_confirmation_and_writes_only_after_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = ticket_module.TICKET_DIR
            ticket_module.TICKET_DIR = Path(temp_dir)
            try:
                before = TOOL_FUNCTIONS["create_ticket"]("VPN issue", "high", "LT-204", False)
                self.assertEqual(before["status"], "needs_confirmation")
                self.assertEqual(list(Path(temp_dir).iterdir()), [])
                after = TOOL_FUNCTIONS["create_ticket"]("VPN issue", "high", "LT-204", True)
                self.assertEqual(after["status"], "created")
                self.assertEqual(len(list(Path(temp_dir).glob("*.json"))), 1)
            finally:
                ticket_module.TICKET_DIR = original_dir

    def test_ticket_rejects_invalid_payload(self) -> None:
        self.assertEqual(TOOL_FUNCTIONS["create_ticket"]("", "high", confirmed=True)["error"], "missing_summary")
        self.assertEqual(TOOL_FUNCTIONS["create_ticket"]("Issue", "urgent", confirmed=True)["error"], "invalid_priority")

    def test_agent_executes_structured_calls(self) -> None:
        provider = FakeProvider([ToolCall("inspect_device", {"asset_id": "LT-204", "check": "vpn"})])
        agent = HelpdeskAgent(provider, system_prompt="test", tools=[])
        run = agent.run([{"role": "user", "content": "test"}])
        self.assertEqual(run.tool_calls[0].name, "inspect_device")
        self.assertIn("AUTH_TIMEOUT", run.tool_results[0]["result"]["diagnostics"]["vpn"])

    def test_chat_loop_pauses_on_clarification(self) -> None:
        provider = SequenceProvider([
            ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Mã máy là gì?", "response_type": "text"})])
        ])
        result = run_model_tool_loop(
            provider=provider,
            messages=[{"role": "user", "content": "Kiểm tra laptop của tôi"}],
            tools=[],
            model=None,
            max_tool_rounds=2,
        )
        self.assertEqual(result["status"], "waiting_for_user")
        self.assertEqual(result["assistant_text"], "Mã máy là gì?")


if __name__ == "__main__":
    unittest.main()
