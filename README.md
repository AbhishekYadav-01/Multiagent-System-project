# Multi-Agent System for Traffic Coordination

This project implements a sophisticated multi-agent system (MAS) to simulate and coordinate traffic flow at a bottleneck, such as students leaving a university complex. The system uses autonomous AI agents, powered by Large Language Models, that negotiate, cooperate, and adapt based on shared goals and past interactions. The entire simulation is visualized through a live, interactive web dashboard.

This project was developed as a comprehensive solution for the Multiagent Systems course assignment.

## ✨ Features

  * **Live Interactive Dashboard**: A web-based UI built with FastAPI and WebSockets to visualize the entire simulation in real-time.
  * **Dynamic Theming**: A clean, professional interface with a persistent Light/Dark mode switcher.
  * **Interactive Controls**: Users can define the number of agents (classrooms) and the number of consecutive episodes to run. A stop button allows for graceful termination of the simulation.
  * **Autonomous AI Agents**: Built with the **AutoGen** framework, agents have distinct roles (`BottleneckAgent`, `ClassroomAgent`) and personalities (`professor_flexibility`).
  * **Complex Negotiation Protocol**: Agents engage in dynamic negotiations, including proposals, counter-offers, acceptances, and rejections.
  * **Strategic Decision-Making**:
      * **Dynamic Proposals**: Agents adapt their proposals based on the severity of the traffic congestion.
      * **Intelligent Targeting**: Agents strategically choose negotiation partners based on prior commitments and a social reputation system.
  * **Stateful Memory**: The system saves the state of all commitments and agent reputations to a `commitments.json` file, allowing memory to persist across simulation runs.
  * **Reputation System**: Agents maintain a "trust" score for their peers. Successful deals improve reputation, while broken promises damage it, influencing future negotiations.
  * **NLP-Powered Parsing**: The system uses an LLM to reliably parse the natural language terms of a deal or counter-offer back into structured data.

## 🛠️ Technology Stack

  * **Backend**:

      * Python 3.11+
      * **AutoGen (`autogen-agentchat`)**: Framework for multi-agent conversations.
      * **FastAPI**: For building the web server and WebSocket endpoints.
      * **Uvicorn**: ASGI server to run the FastAPI application.
      * **LLM API**: Configured for Grok (via GroqCloud), but compatible with any OpenAI-style API.

  * **Frontend**:

      * HTML5
      * CSS3 (with CSS Variables for theming)
      * JavaScript (for WebSocket communication and DOM manipulation)
      * **Bootstrap 5**: For a responsive and clean UI layout.
      * **Font Awesome**: For professional icons.

## 📁 Project Structure

```
mas_visualization/
│
├── main.py                 # FastAPI server, WebSocket logic, and all agent/simulation code.
├── commitments.json        # Saved state file for agent memory (commitments & reputations).
├── requirements.txt        # Python dependencies for the project.
├── .env                    # Environment variables (API keys).
│
└── templates/
    └── index.html          # The single-page HTML file for the dashboard UI.
```

## 🚀 Setup and Installation

Follow these steps to set up and run the project locally.

### Prerequisites

  * Python 3.9+
  * Use OPENAI API key

### 1\. Clone the Repository

```bash
git clone <your-repository-url>
cd mas_visualization
```

### 2\. Create a Virtual Environment

It's highly recommended to use a virtual environment.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3\. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
fastapi
uvicorn[standard]
jinja2
python-dotenv
autogen-agentchat
autogen-ext-openai
python-multipart
```

Then, install the packages:

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

Create a file named `.env` in the root of the project directory and add your API key:

```env
OPENAI_API_KEY="your_api_key_here"
```

## ▶️ How to Run

1.  Make sure your virtual environment is activated.
2.  Run the FastAPI server using Uvicorn:
    ```bash
    uvicorn main:app --reload
    ```
3.  Open your web browser and navigate to **[http://127.0.0.1:8000](https://www.google.com/search?q=http://127.0.0.1:8000)**.

The `--reload` flag enables hot-reloading, so the server will automatically restart when you make changes to the code.

## 🕹️ How to Use the Dashboard

  * **Set Parameters**: Use the input fields in the "Simulation Controls" panel to set the desired number of classrooms (agents) and the number of episodes you want to run.
  * **Run Simulation**: Click the "Run Simulation(s)" button to start the process. The button will be disabled while the simulation is running.
  * **Stop Simulation**: Click the "Stop Simulation" button to gracefully cancel the ongoing simulation.
  * **Switch Themes**: Use the toggle in the top-right corner to switch between light and dark modes. Your preference will be saved for your next visit.
  * **Observe**: Watch the "Agent Status" grid, "Negotiation Visualizer," and "Live Log" to see the agents interact and coordinate in real-time.

## 🏛️ Code Architecture

  * **`main.py`**: The central file containing the entire backend.

      * **FastAPI App**: Sets up the web server, the root (`/`) endpoint for the dashboard, the WebSocket endpoint (`/ws`), and the simulation control endpoints (`/simulation/run`, `/simulation/stop`).
      * **Agent Classes**: `BottleneckAgent` and `ClassroomAgent` define the behavior, prompts, and capabilities of the AI agents.
      * **`MultiAgentTrafficSystem`**: The orchestrator class that manages the simulation lifecycle, including agent creation, state persistence (loading/saving `commitments.json`), and running negotiation episodes.

  * **`templates/index.html`**: The single-page frontend.

      * **HTML**: Defines the structure of the dashboard panels.
      * **CSS**: Contains all the styling, including the responsive layout and the light/dark themes.
      * **JavaScript**: Handles all client-side interactivity, including connecting to the WebSocket, processing incoming data, updating the UI in real-time, and sending requests to the server.
