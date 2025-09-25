# Multiagent Traffic Bottleneck Coordination (Autogen-AgentChat)

**MAS — Multiagent Systems Course**
Traffic coordination demo using the `autogen-agentchat` framework and a Gemini model client.

---

## Overview

This repository contains a simple multiagent simulation demonstrating how classroom agents can coordinate student exit times at a physical bottleneck (e.g., a corridor or stairwell). The system uses conversational agents to:

* Monitor bottleneck capacity (BottleneckAgent)
* Assess classroom situations (ClassroomAgent)
* Negotiate commitments to shift exit times (PROPOSE / ACCEPT / REJECT)
* Execute and track commitments

The code is written to be minimally invasive and demonstrates:

* async/await workflow for agent calls
* tool-enabled agents (small helper functions)
* a single, shared `model_client` used across agents (closed once after everything finishes)

---

## Features

* Simulated bottleneck monitoring with structured traffic updates
* Classroom assessments that consider student counts and professor flexibility
* A negotiation protocol (PROPOSE / ACCEPT / REJECT) and commitment objects
* Demonstration of agent tool usage (monitoring and student-count estimation)
* Minimal, easy-to-read code intended for coursework / demo purposes

---

## Files

* `autogen_agent.py` — main script containing the full multiagent implementation (agents, run loop, tool demos).
* `.env` — (not included) file to store `GEMINI_API_KEY`.
* `README.md` — this file.

---

## Prerequisites

* Python 3.10+ (or at least 3.8+, but modern async features recommended)
* Internet access (to call the remote model API)
* Access/permission to the Gemini model you intend to use (model availability varies by account/project)

Python packages:

* `autogen_agentchat` (your project dependency)
* `autogen_ext` (model client extension used in the script)
* `python-dotenv` (for `.env` support)
* Any other packages used by your local `autogen_*` implementation

> Install dependencies with a `requirements.txt` or your preferred package manager. Example (adjust package names to your environment):

```text
autogen_agentchat
autogen_ext
python-dotenv
```

Install with pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration (.env)

Create a `.env` file in the project root with your model API key:

```
GEMINI_API_KEY=your_real_api_key_here
```

The script expects `load_dotenv()` at startup and obtains the key via `os.getenv('GEMINI_API_KEY')`.

**Important:** Model names and access vary by provider and project. The example script uses:

```python
model="gemini-2.5-flash"
```

If you receive a `404`/`model not found` error, either:

* your project does not have access to that model version, or
* you must use a different model name/version that your account can call.

---

## How to run

Assuming your environment is set up and `.env` is present:

```bash
source .venv/bin/activate
python3 autogen_agent.py
```

You should see console output for:

1. Traffic monitoring phase (Agent B broadcast)
2. Situation assessment phase (each classroom)
3. Negotiation & commitment creation / execution
4. Tool demonstration block (monitor & estimate tools)

When finished, the script closes the shared `model_client` exactly once (in `main()`), so subsequent calls will not fail due to closed resources.

---

## Output example (what to expect)

* Structured JSON-like traffic update printed by Agent B.
* Short assessment messages from each classroom agent.
* A negotiation PROPOSE/REJECT/ACCEPT flow between two classroom agents.
* A final summary of coordinated student exits (timestamps and counts).
* Tool demo prints for the enhanced agents, or an error message if the client could not connect.

---

## Troubleshooting

### 1. `Error code: 404 - Publisher Model ... not found`

**Cause:** The model name used (e.g., `gemini-1.5-flash-002`, `gemini-2.5-flash`) is not available to your account/project, or the model version has been retired.

**Fixes:**

* Verify the model name is correct and available to your account/project.
* Check provider docs or console (Vertex AI / your cloud provider) for the correct model names and versions.
* Use a model your project has access to (set `model=` accordingly).

### 2. `Connection error` in the tool demo

**Cause:** The `model_client` was closed prematurely (or network/credential issues).

**Fixes:**

* Ensure `model_client.close()` is called **once**, after all agent work completes. The posted script calls `await model_client.close()` in `main()` `finally:` — that is the recommended approach.
* Confirm that your `.env` file contains `GEMINI_API_KEY` and that it is loaded at startup.
* Verify stable internet and that the API endpoint is reachable.

### 3. Missing or invalid `GEMINI_API_KEY`

**Symptoms:** Authorization errors, inability to connect, or immediate failures.

**Fixes:**

* Double-check `.env` and ensure `GEMINI_API_KEY` is set.
* Ensure `load_dotenv()` is executed before `OpenAIChatCompletionClient` is constructed (the provided script does this at the top).
* If your API uses a different env var name, update `os.getenv('GEMINI_API_KEY')` to match.

### 4. Slow or inconsistent responses

* The script uses remote model calls; latency depends on the provider and internet connection.
* For offline testing, mock the `AssistantAgent` or `model_client` responses.

---

## Architecture & Design Notes

* `BottleneckAgent` — monitors and periodically broadcasts a structured traffic state.
* `ClassroomAgent` — each represents one classroom, can assess its situation and propose or evaluate commitments.
* `Commitment` dataclass — records negotiated agreements between classrooms.
* `MultiAgentTrafficSystem` — orchestrates an episode (monitor → assess → negotiate → execute).
* Tools: small async functions (`monitor_bottleneck`, `estimate_students`) are exposed to agents in the enhanced demo.

Concurrency is handled via `asyncio` and all agent interactions use async `run()` calls from the `autogen_agentchat` API.

---

## Customization Points

* **Number of classrooms:** change `for i in range(1, 6)` to any number.
* **Initial bottleneck capacity:** set it in `TrafficState(capacity=...)`.
* **Professor flexibility distribution:** currently `random.choice(["high","medium","low"])`; replace with deterministic values if needed.
* **Model & client parameters:** switch `model` in `OpenAIChatCompletionClient(...)` to any supported model accessible to your account.

---

## Contribution

This is an educational / demo project. Feel free to:

* Add logging instead of prints.
* Add unit tests or mocks for the agent client.
* Add a visualization for exit timings and simulated congestion.

---

## License

Use freely for coursework and learning. If you incorporate this into a larger project or public repo, add an appropriate open-source license.

---

## Contact / Support

If you hit an error you can’t fix:

* Paste the full trace / console output.
* Confirm the `.env` contents (don’t share your key publicly).
* Confirm which model name/version you are trying to call and whether your account/project has access.

---

Enjoy experimenting — and if you want, I can:

* produce a `requirements.txt` tuned to your environment, or
* add unit tests / mocks so you can run the simulation offline.
