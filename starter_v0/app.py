from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop
from versioning import build_artifact_version

ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(
    page_title="Northstar IT Helpdesk Agent",
    page_icon="🛠️",
    layout="wide",
)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #0b1220;
                --panel: rgba(15, 23, 42, 0.9);
                --panel-soft: rgba(30, 41, 59, 0.9);
                --accent: #38bdf8;
                --accent-2: #22c55e;
                --accent-3: #f59e0b;
                --text: #e2e8f0;
                --muted: #94a3b8;
                --border: rgba(148, 163, 184, 0.25);
                --shadow: 0 18px 40px rgba(15, 23, 42, 0.28);
            }

            .stApp {
                background: linear-gradient(135deg, #020817 0%, #0f172a 35%, #111827 100%);
                color: var(--text);
            }

            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }

            [data-testid="stSidebar"] > div {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.86));
                border-right: 1px solid var(--border);
            }

            .metric-card {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(17, 24, 39, 0.95));
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow);
                height: 100%;
            }

            .metric-title {
                color: var(--muted);
                font-size: 0.78rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.55rem;
            }

            .metric-value {
                font-size: 1.6rem;
                font-weight: 700;
                color: white;
            }

            .artifact-badge {
                display: inline-block;
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #bae6fd;
                padding: 0.45rem 0.8rem;
                border-radius: 999px;
                font-weight: 600;
                font-size: 0.8rem;
                margin-top: 0.5rem;
            }

            .glass-panel {
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow);
            }

            .helpdesk-header {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 0.25rem;
            }

            .subtle-copy {
                color: var(--muted);
                font-size: 0.96rem;
            }

            .user-message > div:first-child {
                background: linear-gradient(130deg, #0ea5e9 0%, #2563eb 100%);
                border-radius: 18px 18px 18px 6px;
                color: white;
                padding: 0.9rem 1rem;
                box-shadow: var(--shadow);
            }

            .assistant-message > div:first-child {
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid var(--border);
                border-radius: 18px 18px 6px 18px;
                color: var(--text);
                padding: 0.9rem 1rem;
                box-shadow: var(--shadow);
            }

            .stChatInput textarea {
                border-radius: 16px;
                border: 1px solid rgba(56, 189, 248, 0.4);
                background: rgba(15, 23, 42, 0.8);
                color: white;
            }

            .stExpander {
                border: 1px solid var(--border);
                border-radius: 12px;
                background: rgba(15, 23, 42, 0.65);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_decls = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_decls)

artifact_ver = build_artifact_version("v3", SYSTEM_PROMPT_PATH, TOOLS_PATH)

with st.sidebar:
    st.markdown("### 🧭 Northstar Labs")
    st.markdown("#### IT Helpdesk Agent")
    st.markdown(f"<div class='artifact-badge'>Artifact Version: {artifact_ver.artifact_version}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### Included capabilities")
    st.markdown("- VPN, email, Wi‑Fi and printing checks")
    st.markdown("- Device diagnostics and inventory review")
    st.markdown("- Employee lookup and access validation")
    st.markdown("- Policy and knowledge base retrieval")
    st.markdown("- Incident report generation and ticket creation")
    st.markdown("---")
    st.markdown("#### Safety guardrails")
    st.markdown("- No guessing of IDs or credentials")
    st.markdown("- Explicit confirmation before write actions")
    st.markdown("- Internal data stays inside the security boundary")
    st.markdown("- External search only uses public manufacturer/model info")

st.markdown("<div class='helpdesk-header'>🛠️ IT Helpdesk Agent</div>", unsafe_allow_html=True)
st.caption("Evidence-based support assistant for service desk operations, diagnostics, and controlled follow-up actions.")

metric_cols = st.columns(4)
with metric_cols[0]:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-title'>Service Checks</div>
            <div class='metric-value'>VPN / SSO / Wi‑Fi</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_cols[1]:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-title'>Device Review</div>
            <div class='metric-value'>Asset + diagnostics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_cols[2]:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-title'>Knowledge</div>
            <div class='metric-value'>KB + policy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_cols[3]:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-title'>Actions</div>
            <div class='metric-value'>Ticket + report</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(
        """
        <div class='glass-panel'>
            <div class='subtle-copy'>Start with a helpdesk request such as: “Check the VPN status,” “Investigate asset LT-204,” or “Create a ticket for a Wi‑Fi issue.”</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools" in msg and msg["tools"]:
            with st.expander("🔍 Tool calling trace"):
                st.json(msg["tools"])

if prompt := st.chat_input("Describe the IT issue or request..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    provider = make_provider("openrouter")
    chat_history = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        chat_history.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing request and selecting the right tool..."):
            result = run_model_tool_loop(
                provider=provider,
                messages=chat_history,
                tools=openai_tools,
                model=None,
                max_tool_rounds=4,
            )
            reply = result["assistant_text"]
            tool_events = result.get("tool_events", [])
            st.markdown(reply)
            if tool_events:
                with st.expander("🔍 Tool calling trace"):
                    st.json(tool_events)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "tools": tool_events,
    })