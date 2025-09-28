# Multi-Agent Traffic Coordination System

This project simulates a multi-agent system designed to manage and coordinate access to a shared, limited resource (a traffic bottleneck). The system uses cooperative agents that negotiate with each other to stagger their access times, effectively preventing congestion.

The implementation uses the modern `autogen-agentchat` framework for agent creation and interaction.

-----

## System Architecture

The system is composed of two types of agents:

  * **Bottleneck Agent:** A central agent that monitors the traffic capacity of the bottleneck and broadcasts real-time status updates (e.g., capacity, estimated congestion) to all other agents.
  * **Classroom Agents:** Agents representing individual groups that need to use the bottleneck. Each agent:
      * Receives status updates from the Bottleneck Agent.
      * Assesses its own state (e.g., number of students).
      * Negotiates with other Classroom Agents to deconflict exit times by creating commitments.

-----

## Core Logic & Features

  * **Dynamic Environment Simulation:** The system simulates a changing traffic environment, with the Bottleneck Agent providing live updates.
  * **Negotiation Protocol:** Agents can `PROPOSE`, `ACCEPT`, or `REJECT` commitments. A commitment involves one agent adjusting its schedule in exchange for a future obligation from another.
  * **Commitment History:** Agents track past agreements (`Commitment` objects), which can influence future negotiation rounds.
  * **Tool-Enabled Agents:** The simulation includes a demonstration of enhanced agents that can use asynchronous tools to perform actions like monitoring traffic or estimating student counts.

-----

## Setup and Installation

### 1\. Prerequisites

  * Python 3.9+
  * An API Key from a compatible LLM provider (the code is configured for Gemini).

### 2\. Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install autogen-agentchat autogen-ext python-dotenv
    ```

### 3\. Configuration

1.  Create a file named `.env` in the root directory of the project.
2.  Add your API key to the `.env` file:
    ```
    GEMINI_API_KEY='YOUR_API_KEY_HERE'
    ```

-----

## How to Run the Simulation

Execute the main Python script from your terminal:

```bash
python your_script_name.py
```

The console will display the step-by-step simulation output, including:

1.  The initial traffic update from the Bottleneck Agent.
2.  Assessments from each Classroom Agent.
3.  A demonstration of the negotiation phase.
4.  The final coordinated exit plan.
5.  A demonstration of tool usage by enhanced agents.
