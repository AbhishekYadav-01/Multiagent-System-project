# main.py

import fastapi
import asyncio
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os

from fastapi import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

# Assuming autogen_agentchat and dotenv are installed
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

# Model client configuration (copy from your other file)
model_client = OpenAIChatCompletionClient(
    model="gemini-2.5-flash",
    api_key=os.getenv('GEMINI_API_KEY')
)

simulation_task: Optional[asyncio.Task] = None

# Create the FastAPI app object
app = fastapi.FastAPI()

# Point to the 'templates' directory for HTML files
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    This function runs when a user goes to the main page ('/').
    It renders and returns the index.html file.
    """
    return templates.TemplateResponse("index.html", {"request": request})




class ConnectionManager:
    def __init__(self):
        self.active_connections: List[fastapi.WebSocket] = []

    async def connect(self, websocket: fastapi.WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: fastapi.WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# In main.py, after the root ("/") endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except fastapi.WebSocketDisconnect:
        manager.disconnect(websocket)
        
        
@dataclass
class Commitment:
    """Represents a commitment between agents"""
    debtor: str
    creditor: str
    time_adjustment: int  # minutes (positive = early, negative = late)
    future_obligation: str
    created_at: datetime
    episode: str  # e.g., "Monday_11AM"
    status: str = "pending" # <--- ADD THIS LINE

@dataclass
class TrafficState:
    """Current traffic state at bottleneck"""
    capacity: int  # students per minute
    estimated_total_students: int
    current_congestion: float
    timestamp: datetime

class BottleneckAgent:
    """Agent B - Monitors bottleneck point and coordinates traffic"""

    def __init__(self, name="BottleneckAgent"):
        self.name = name
        self.agent = AssistantAgent(
            name=name,
            model_client=model_client,
            system_message="""You are the Bottleneck Monitoring Agent (Agent B). 
            Your responsibilities:
            1. Monitor traffic capacity at the bottleneck point
            2. Estimate total students in classrooms
            3. Broadcast capacity information to classroom agents
            4. Track overall system performance

            You should send regular updates about:
            - Current bottleneck capacity (students/minute)
            - Estimated total students
            - Congestion warnings

            Format your messages as structured data when possible."""
        )

        self.traffic_state = TrafficState(
            capacity=50,  # students per minute
            estimated_total_students=0,
            current_congestion=0.0,
            timestamp=datetime.now()
        )

    async def broadcast_traffic_state(self) -> str:
        """Broadcast current traffic state to all classroom agents"""
        # Simulate monitoring the bottleneck
        self.traffic_state.estimated_total_students = random.randint(200, 300)
        self.traffic_state.current_congestion = random.uniform(0.1, 0.9)
        self.traffic_state.timestamp = datetime.now()

        message = f"""
        TRAFFIC_UPDATE:
        Bottleneck Capacity: {self.traffic_state.capacity} students/minute
        Estimated Total Students: {self.traffic_state.estimated_total_students}
        Current Congestion Level: {self.traffic_state.current_congestion:.2f}
        Timestamp: {self.traffic_state.timestamp}

        Classroom agents, please coordinate your exit times to avoid congestion.
        """

        # Use the new autogen-agentchat API
        response = await self.agent.run(task=f"Broadcast this traffic update: {message}")
        return str(response.messages[-1].content)

class ClassroomAgent:
    """Classroom Agent - Manages individual classroom and negotiates commitments"""

    def __init__(self, classroom_id: str, all_agent_names: List[str]):
        self.classroom_id = classroom_id
        self.name = f"ClassroomAgent_{classroom_id}"
        self.agent = AssistantAgent(
            name=self.name,
            model_client=model_client,
            system_message=f"""You are Classroom Agent {classroom_id}. 
            Your responsibilities:
            1. Monitor attendance in your classroom
            2. Receive traffic updates from the Bottleneck Agent
            3. Negotiate commitments with other classroom agents
            4. Coordinate student exit times to prevent congestion
            5. Track and honor previous commitments

            Negotiation protocol:
            - PROPOSE: Offer time adjustments with future obligations
            - ACCEPT: Agree to proposed commitments  
            - REJECT: Decline proposals with reasons
            - BROADCAST: Announce successful deals to all agents

            You must consider:
            - Current student count in your classroom: {random.randint(30, 80)}
            - Available bottleneck capacity
            - Previous commitments made
            - Professor's flexibility for lecture duration changes

            Format: When negotiating, use structured messages like:
            PROPOSE: [Target Agent] - [Time Adjustment] - [Future Obligation]
            """
        )

        self.student_count = random.randint(30, 80)
        self.commitments_made = []
        self.commitments_received = []
        self.reputation_scores = {name: 10 for name in all_agent_names if name != self.name}
        self.violation_count = 0
        self.professor_flexibility = random.choice(["high", "medium", "low"])
    
    async def receive_broadcast(self, broadcast_message: str):
        """Receives and acknowledges a broadcast message from the system."""
        print(f"[{self.name}] Broadcast Received: {broadcast_message}")

    # In ClassroomAgent
    async def propose_commitment(self, target_agent: str, congestion_level: float) -> str:
        # Determine adjustment based on congestion
        if congestion_level > 0.7: adjustment = -4
        elif congestion_level > 0.4: adjustment = -2
        else: adjustment = -1
        
        future_obligation = f"you ({target_agent}) can receive a favorable time adjustment in a future episode."

        proposal_task = f"""
        You are {self.name}. You need to make a coordination proposal to {target_agent}.
        The congestion is significant, so you have decided on a time adjustment of {adjustment} minutes.

        1. Write a clear, natural language proposal message.
        2. Append the exact terms of the deal in a JSON block at the end.

        Example:
        PROPOSE: I'd like to propose an early exit...
        ```json
        {{
            "debtor": "{self.name}",
            "creditor": "{target_agent}",
            "time_adjustment": {adjustment},
            "future_obligation": "{future_obligation}"
        }}
        ```
        """
        response = await self.agent.run(task=proposal_task)
        return str(response.messages[-1].content)

    def create_commitment(self, debtor: str, creditor: str, time_adjustment: int, 
                         future_obligation: str) -> Commitment:
        """Create a new commitment object"""
        return Commitment(
            debtor=debtor,
            creditor=creditor,
            time_adjustment=time_adjustment,
            future_obligation=future_obligation,
            created_at=datetime.now(),
            episode="Monday_11AM"
        )
        
    async def assess_situation(self, traffic_update: str) -> str:
        """Assess current situation based on traffic update and past commitments."""
        
        # --- NEW LOGIC TO CHECK FOR OBLIGATIONS ---
        # Find commitments where this agent is the debtor (owes a favor)
        my_obligations = []
        for commitment in self.commitments_received:
            # Note: In our current setup, the agent who receives the commitment is the creditor.
            # Let's adjust this. A better way is to check the commitments made by others to this agent.
            # For simplicity, let's assume the `commitments_received` list tracks what is owed TO this agent.
            # And `commitments_made` tracks what this agent owes.
            pass # We will check commitments_made instead.

        my_debts = [c for c in self.commitments_made if c.status == "pending"]
        
        obligations_summary = "None"
        if my_debts:
            obligations_summary = ""
            for debt in my_debts:
                obligations_summary += (
                    f"- You owe {debt.creditor}: '{debt.future_obligation}' "
                    f"from episode {debt.episode}.\n"
                )
        # ------------------------------------------

        assessment_task = f"""
        You are {self.name}. Assess the current situation and decide on a coordination strategy.

        **Current Traffic State:**
        {traffic_update}

        **Your Classroom Status:**
        - Student count: {self.student_count}
        - Professor flexibility: {self.professor_flexibility}

        **Your Outstanding Obligations:**
        {obligations_summary}

        **Your Task:**
        1. Analyze the traffic state and your classroom status.
        2. Review your outstanding obligations. If you owe another agent a favor, you **must** prioritize fulfilling that promise in your strategy.
        3. Propose a clear course of action. For example: "High congestion. I will propose a -3 minute adjustment to ClassroomAgent_C2 to honor my previous commitment." or "Low congestion. No action needed."
        """

        response = await self.agent.run(task=assessment_task)
        return str(response.messages[-1].content)
    
# In ClassroomAgent
    async def parse_commitment_from_text(self, text: str, **kwargs) -> Optional[Dict]:
        # This method now just needs to extract the JSON, which is much more reliable.
        try:
            json_str = text[text.find('{'):text.rfind('}')+1]
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            print(f"[{self.name}] ERROR: Failed to find or parse JSON block in the proposal text.")
            return None
        
    async def evaluate_proposal(self, proposal: str, proposing_agent_name: str) -> str:
        """Evaluates a proposal based on professor_flexibility and decides to accept, reject, or counter."""
        
        evaluation_task = f"""
        You are {self.name}. You have received a coordination proposal from {proposing_agent_name}.
        Your professor's flexibility for changing lecture duration is '{self.professor_flexibility}'.

        **Received Proposal:**
        "{proposal}"

        **Your Task:**
        Evaluate this proposal based on your flexibility:
        - If your flexibility is 'high', you are likely to ACCEPT.
        - If your flexibility is 'medium', you might accept or reject.
        - If your flexibility is 'low', you are likely to REJECT the proposal, especially if it asks you to shorten your lecture. You should make a COUNTER-OFFER instead (e.g., offer to extend your lecture so they can leave early).

        Your final response MUST start with one of three keywords: ACCEPT, REJECT, or COUNTER.
        - ACCEPT: "I accept your proposal..."
        - REJECT: "I reject your proposal because..."
        - COUNTER: "I cannot accept your proposal. Instead, I make a counter-offer: ..."
        """
        
        response = await self.agent.run(task=evaluation_task)
        return str(response.messages[-1].content)

class MultiAgentTrafficSystem:
    """Main system orchestrating all agents"""

    def __init__(self):
        self.bottleneck_agent = BottleneckAgent()
        agent_names = [f"ClassroomAgent_C{i}" for i in range(1, 6)]
        self.classroom_agents = [ClassroomAgent(f"C{i}", agent_names) for i in range(1, 6)]
        self.load_commitments_from_file()

    async def run_coordination_episode(self, num_classrooms: int):
            """
            Runs one full episode of the simulation and yields JSON updates for each step.
            This is the main simulation async generator.
            """
            # Helper to format messages for streaming
            def format_update(msg_type, data):
                return json.dumps({"type": msg_type, "data": data}) + "\n"

            # --- INITIALIZATION ---
            agent_names = [f"ClassroomAgent_C{i}" for i in range(1, num_classrooms + 1)]
            self.classroom_agents = [ClassroomAgent(f"C{i}", agent_names) for i in range(1, num_classrooms + 1)]
            self.load_commitments_from_file()

            yield format_update("log", f"Starting new simulation with {num_classrooms} classrooms.")
            
            initial_states = [{
                "name": agent.name, "students": agent.student_count,
                "flexibility": agent.professor_flexibility, "reputation": agent.reputation_scores
            } for agent in self.classroom_agents]
            yield format_update("agent_setup", initial_states)

            try:
                # --- STEP 1: TRAFFIC MONITORING ---
                yield format_update("log", "1. TRAFFIC MONITORING PHASE")
                traffic_update = await self.bottleneck_agent.broadcast_traffic_state()
                yield format_update("bottleneck_update", {
                    "message": traffic_update,
                    "congestion": round(self.bottleneck_agent.traffic_state.current_congestion, 2),
                    "capacity": self.bottleneck_agent.traffic_state.capacity
                })

                # --- STEP 2: SITUATION ASSESSMENT ---
                yield format_update("log", "2. SITUATION ASSESSMENT PHASE")
                for agent in self.classroom_agents:
                    assessment = await agent.assess_situation(traffic_update)
                    yield format_update("assessment_update", {"name": agent.name, "assessment": assessment})
                    await asyncio.sleep(2);

                # --- STEP 3: DYNAMIC NEGOTIATION ---
                yield format_update("log", "3. DYNAMIC NEGOTIATION PHASE")
                agents_by_pressure = sorted(self.classroom_agents, key=lambda a: a.student_count, reverse=True)
                initiator = agents_by_pressure[0]
                target = self.select_negotiation_target(initiator)
                if not target:
                    yield format_update("log", "Not enough agents to negotiate."); return

                yield format_update("negotiation_start", {"initiator": initiator.name, "target": target.name})
                proposal = await initiator.propose_commitment(target.name, self.bottleneck_agent.traffic_state.current_congestion)
                yield format_update("negotiation_proposal", {"from": initiator.name, "to": target.name, "proposal": proposal})
                evaluation = await target.evaluate_proposal(proposal, initiator.name)
                yield format_update("negotiation_response", {"from": target.name, "to": initiator.name, "response": evaluation})

                # --- STEP 4: COMMITMENT EXECUTION ---
                yield format_update("log", "4. COMMITMENT EXECUTION")
                
                agent_map = {agent.name: agent for agent in self.classroom_agents}

                def update_reputations(agent1_name, agent2_name, outcome: str):
                    # Helper function to update reputation scores
                    agent1 = agent_map[agent1_name]
                    agent2 = agent_map[agent2_name]
                    if outcome == 'success':
                        agent1.reputation_scores[agent2.name] = min(15, agent1.reputation_scores.get(agent2.name, 10) + 1)
                        agent2.reputation_scores[agent1.name] = min(15, agent2.reputation_scores.get(agent1.name, 10) + 1)
                    elif outcome == 'violation':
                        # Only the initiator's opinion of the violator is damaged
                        agent1.reputation_scores[agent2.name] = max(0, agent1.reputation_scores.get(agent2.name, 10) - 5)

                async def check_for_violation(violator, initiator):
                    # Async generator to check for and yield violation updates
                    for commitment in violator.commitments_made:
                        if commitment.creditor == initiator.name and commitment.status == "pending":
                            commitment.status = "violated"
                            violator.violation_count += 1
                            update_reputations(initiator.name, violator.name, 'violation')
                            yield format_update("violation_update", {
                                "violator": violator.name, "initiator": initiator.name,
                                "new_reputation": initiator.reputation_scores[violator.name]
                            })

                if evaluation.strip().upper().startswith("ACCEPT"):
                    parsed_terms = await initiator.parse_commitment_from_text(proposal)
                    if parsed_terms:
                        yield format_update("log", "✅ Deal ACCEPTED. Creating commitment...")
                        commitment = initiator.create_commitment(**parsed_terms)
                        agent_map[commitment.debtor].commitments_made.append(commitment)
                        agent_map[commitment.creditor].commitments_received.append(commitment)
                        update_reputations(initiator.name, target.name, 'success')
                        yield format_update("reputation_update", {"agents": [initiator.name, target.name], "new_scores": {initiator.name: initiator.reputation_scores, target.name: target.reputation_scores}})
                        async for update in self.broadcast_commitment(commitment): yield update
                
                elif evaluation.strip().upper().startswith("COUNTER"):
                    yield format_update("log", f"🔵 Deal Countered. [{initiator.name}] is evaluating...")
                    async for update in check_for_violation(target, initiator): yield update
                    
                    counter_evaluation = await initiator.evaluate_proposal(evaluation, target.name)
                    yield format_update("negotiation_response", {"from": initiator.name, "to": target.name, "response": counter_evaluation})

                    if counter_evaluation.strip().upper().startswith("ACCEPT"):
                        parsed_terms = await target.parse_commitment_from_text(evaluation)
                        if parsed_terms:
                            yield format_update("log", "✅ Counter-offer ACCEPTED. Creating commitment...")
                            commitment = target.create_commitment(**parsed_terms)
                            agent_map[parsed_terms['debtor']].commitments_made.append(commitment)
                            agent_map[parsed_terms['creditor']].commitments_received.append(commitment)
                            update_reputations(initiator.name, target.name, 'success')
                            yield format_update("reputation_update", {"agents": [initiator.name, target.name], "new_scores": {initiator.name: initiator.reputation_scores, target.name: target.reputation_scores}})
                            async for update in self.broadcast_commitment(commitment): yield update
                    else:
                        yield format_update("log", "❌ Counter-offer REJECTED. Negotiation failed.")
                
                else: # REJECT
                    yield format_update("log", "❌ Deal REJECTED. No coordination achieved.")
                    async for update in check_for_violation(target, initiator): yield update

                yield format_update("log", "5. COORDINATED STUDENT EXITS")

            except Exception as e:
                yield format_update("error", f"Error in coordination episode: {e}")
            finally:
                self.save_commitments_to_file()
                yield format_update("log", "💾 State saved successfully.")
        
    # Inside the MultiAgentTrafficSystem class
    async def broadcast_commitment(self, commitment: Commitment):
        """
        Broadcasts the details of a successful commitment to all agents.
        This is an async generator that yields updates.
        """
        def format_update(msg_type, data):
            return json.dumps({"type": msg_type, "data": data}) + "\n"
        
        yield format_update("log", f"📢 BROADCASTING: Deal confirmed between {commitment.debtor} and {commitment.creditor}.")
        
        broadcast_message = (
            f"DEAL_CONFIRMED: {commitment.debtor} will adjust by "
            f"{commitment.time_adjustment} mins. A future obligation to "
            f"{commitment.creditor} has been recorded."
        )
        
        for agent in self.classroom_agents:
            if agent.name != commitment.debtor and agent.name != commitment.creditor:
                yield format_update("broadcast_update", {"recipient": agent.name, "message": broadcast_message})

    
    def save_commitments_to_file(self, filename="commitments.json"):
            print(f"\n💾 Saving state to {filename}...")
            state_to_save = {'commitments': [], 'reputations': {}}
            
            # Use a set to track unique commitments to avoid duplicates
            unique_commitments = set()
            
            for agent in self.classroom_agents:
                for commitment in agent.commitments_made:
                    # Create a unique identifier for the commitment
                    commit_id = (commitment.debtor, commitment.creditor, commitment.created_at.isoformat())
                    if commit_id not in unique_commitments:
                        commit_dict = asdict(commitment)
                        commit_dict['created_at'] = commitment.created_at.isoformat()
                        state_to_save['commitments'].append(commit_dict)
                        unique_commitments.add(commit_id)

                state_to_save['reputations'][agent.name] = agent.reputation_scores
                
            with open(filename, 'w') as f:
                json.dump(state_to_save, f, indent=4)
            print("✅ State saved successfully.")

    def load_commitments_from_file(self, filename="commitments.json"):
        print(f"💾 Attempting to load state from {filename}...")
        try:
            with open(filename, 'r') as f:
                saved_state = json.load(f)
            
            agent_map = {agent.name: agent for agent in self.classroom_agents}
            
            # Clear existing commitments to prevent duplication on load
            for agent in self.classroom_agents:
                agent.commitments_made.clear()
                agent.commitments_received.clear()

            # Load Commitments
            loaded_commitments = saved_state.get('commitments', [])
            for commit_data in loaded_commitments:
                commit_data['created_at'] = datetime.fromisoformat(commit_data['created_at'])
                commitment = Commitment(**commit_data)
                if commitment.debtor in agent_map:
                    agent_map[commitment.debtor].commitments_made.append(commitment)
                if commitment.creditor in agent_map:
                    agent_map[commitment.creditor].commitments_received.append(commitment)

            # Load Reputations
            loaded_reputations = saved_state.get('reputations', {})
            for agent_name, reputations in loaded_reputations.items():
                if agent_name in agent_map:
                    agent_map[agent_name].reputation_scores.update(reputations) # <-- Change to .update()
            
            print(f"✅ Loaded {len(loaded_commitments)} commitments and reputation scores.")

        except FileNotFoundError:
            print("State file not found. Starting a new session.")
        except Exception as e:
            print(f"❌ Error loading state: {e}")
    
        # In MultiAgentTrafficSystem
    # --- NEW: Add this entire method ---
    def select_negotiation_target(self, initiator: ClassroomAgent) -> Optional[ClassroomAgent]:
        potential_targets = [agent for agent in self.classroom_agents if agent.name != initiator.name]
        if not potential_targets:
            return None

        for commitment in initiator.commitments_made:
            if commitment.status == 'pending':
                for target in potential_targets:
                    if target.name == commitment.creditor:
                        print(f"  -> Heuristic: [{initiator.name}] is prioritizing [{target.name}] to settle a debt.")
                        return target

        sorted_by_rep = sorted(potential_targets, key=lambda a: initiator.reputation_scores[a.name], reverse=True)
        print(f"  -> Heuristic: [{initiator.name}] is choosing from targets sorted by reputation.")
        return sorted_by_rep[0]
        
        
        

# Async tool functions for agents
async def monitor_bottleneck() -> str:
    """Tool function to monitor bottleneck capacity"""
    capacity = random.randint(40, 60)
    congestion = random.uniform(0.1, 0.9)
    return f"Bottleneck capacity: {capacity} students/min, Congestion: {congestion:.2f}"

async def estimate_students(classroom_id: str) -> str:
    """Tool function to estimate student count"""
    count = random.randint(30, 80)
    return f"Estimated {count} students in {classroom_id}"


def create_enhanced_agents():
    """Create agents with tool capabilities"""

    # Enhanced Bottleneck Agent with tools
    bottleneck_agent = AssistantAgent(
        name="BottleneckAgent",
        model_client=model_client,
        tools=[monitor_bottleneck],
        system_message="""You are the Bottleneck Monitoring Agent. 
        Use the monitor_bottleneck tool to check current capacity and congestion.
        Broadcast updates to classroom agents for coordination.""",
        reflect_on_tool_use=True
    )

    # Enhanced Classroom Agents with tools
    classroom_agents = []
    for i in range(1, 6):
        agent = AssistantAgent(
            name=f"ClassroomAgent_C{i}",
            model_client=model_client,
            tools=[estimate_students],
            system_message=f"""You are Classroom Agent C{i}. 
            Use tools to estimate student counts and negotiate commitments 
            with other agents to prevent traffic congestion.
            Your classroom ID is C{i}.""",
            reflect_on_tool_use=True
        )
        classroom_agents.append(agent)

    return bottleneck_agent, classroom_agents

async def demonstrate_tool_usage():
    """Demonstrate the enhanced agents with tools"""
    print("\n" + "="*50)
    print("ENHANCED AGENTS WITH TOOLS DEMONSTRATION")
    print("="*50)

    bottleneck_agent, classroom_agents = create_enhanced_agents()

    try:
        # Bottleneck agent uses monitoring tool
        print("\n🔍 Bottleneck Agent Monitoring:")
        monitor_response = await bottleneck_agent.run(
            task="Check the current bottleneck capacity and congestion level"
        )
        print(monitor_response.messages[-1].content)

        # Classroom agent uses estimation tool
        print("\n📊 Classroom Agent Assessment:")
        classroom_response = await classroom_agents[0].run(
            task="Estimate the number of students in your classroom C1"
        )
        print(classroom_response.messages[-1].content)

        print("\n✅ Tool usage demonstration completed!")

    except Exception as e:
        print(f"❌ Error in tool demonstration: {e}")

    finally:
        # Do NOT close model_client here — main() will close it once at the end.
        pass
    

# In main.py, after the read_root function
# In main.py, after the read_root function

# In main.py, REPLACE the /simulation/run endpoint

@app.post("/simulation/stop")
async def stop_simulation():
    global simulation_task
    if simulation_task and not simulation_task.done():
        simulation_task.cancel()
        return {"message": "Stop signal sent."}
    return {"message": "No active simulation to stop."}

@app.post("/simulation/run")
async def run_simulation(request: Request):
    global simulation_task
    if simulation_task and not simulation_task.done():
        return fastapi.Response(status_code=409, content="A simulation is already running.")

    form_data = await request.form()
    num_classrooms = int(form_data.get("numClassrooms", 5))

    async def run_and_broadcast():
        system = MultiAgentTrafficSystem()
        try:
            async for update in system.run_coordination_episode(num_classrooms):
                await manager.broadcast(update)
        except asyncio.CancelledError:
            await manager.broadcast(json.dumps({"type": "log", "data": "[Simulation Stopped by User]"}))
        finally:
            # Ensure final state is saved even on cancellation
            system.save_commitments_to_file()
            await manager.broadcast(json.dumps({"type": "log", "data": "💾 State saved successfully."}))


    simulation_task = asyncio.create_task(run_and_broadcast())
    
    return {"message": "Simulation started"}

async def main():
    """Main function to run demonstrations"""
    print("AUTOGEN-AGENTCHAT MULTIAGENT TRAFFIC COORDINATION")
    print("=" * 60)

    # Run the main coordination system
    system = MultiAgentTrafficSystem()

    try:
        await system.run_coordination_episode()

        # Demonstrate enhanced capabilities
        await demonstrate_tool_usage()

        print("\n" + "="*60)
        print("IMPLEMENTATION NOTES:")
        print("1. Using autogen-agentchat package (modern version)")
        print("2. Requires GEMINI API key in model client")
        print("3. Async/await pattern for all agent interactions")
        print("4. Tool integration for enhanced capabilities")
        print("5. Proper resource cleanup with model_client.close()")
        print("=" * 60)

    finally:
        # Close the model client exactly once, after all agent work is done.
        try:
            await model_client.close()
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())