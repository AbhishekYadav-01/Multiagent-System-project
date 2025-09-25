"""
Updated AutoGen Implementation for Traffic Bottleneck Coordination
MAS Assignment - Multiagent Systems Course
Using autogen-agentchat package (modern version)
"""

import asyncio
import json
import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

# Updated imports for autogen-agentchat
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
load_dotenv()

# Model client configuration for autogen-agentchat
model_client = OpenAIChatCompletionClient(
    model="gemini-2.5-flash",
    api_key=os.getenv('GEMINI_API_KEY')
)

@dataclass
class Commitment:
    """Represents a commitment between agents"""
    debtor: str
    creditor: str
    time_adjustment: int  # minutes (positive = early, negative = late)
    future_obligation: str
    created_at: datetime
    episode: str  # e.g., "Monday_11AM"

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

    def __init__(self, classroom_id: str):
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
        self.violation_count = 0
        self.professor_flexibility = random.choice(["high", "medium", "low"])

    async def assess_situation(self, traffic_update: str) -> str:
        """Assess current situation based on traffic update"""
        assessment_task = f"""
        Assess the situation for {self.classroom_id}:
        - Current student count: {self.student_count}
        - Professor flexibility: {self.professor_flexibility}
        - Active commitments: {len(self.commitments_made)}
        - Violation count: {self.violation_count}

        Traffic update: {traffic_update}

        Based on this information, determine if coordination is needed.
        """

        response = await self.agent.run(task=assessment_task)
        return str(response.messages[-1].content)

    async def propose_commitment(self, target_agent: str, time_adjustment: int, future_obligation: str) -> str:
        """Propose a commitment to another agent"""
        proposal_task = f"""
        Create a commitment proposal to {target_agent}:
        - I will adjust my lecture end time by {time_adjustment} minutes
        - In return, {future_obligation}
        - This will help coordinate {self.student_count} students from {self.classroom_id}

        Format this as a formal proposal message.
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

class MultiAgentTrafficSystem:
    """Main system orchestrating all agents"""

    def __init__(self):
        self.bottleneck_agent = BottleneckAgent()
        self.classroom_agents = []

        # Create 5 classroom agents
        for i in range(1, 6):
            agent = ClassroomAgent(f"C{i}")
            self.classroom_agents.append(agent)

    async def run_coordination_episode(self):
        """Run one episode of traffic coordination"""
        print("\n" + "="*60)
        print("MULTIAGENT TRAFFIC COORDINATION SIMULATION")
        print("Episode: Monday 11:00 AM")
        print("Using autogen-agentchat framework")
        print("="*60)

        try:
            # Step 1: Bottleneck agent broadcasts traffic state
            print("\n1. TRAFFIC MONITORING PHASE")
            traffic_update = await self.bottleneck_agent.broadcast_traffic_state()
            print(f"Agent B: {traffic_update}")

            # Step 2: Classroom agents assess situations
            print("\n2. SITUATION ASSESSMENT PHASE")
            assessments = []
            for agent in self.classroom_agents:
                assessment = await agent.assess_situation(traffic_update)
                assessments.append(assessment)
                print(f"{agent.classroom_id}: {assessment[:100]}...")

            # Step 3: Negotiation phase (simplified demonstration)
            print("\n3. NEGOTIATION PHASE")
            c1, c2 = self.classroom_agents[0], self.classroom_agents[1]

            proposal = await c1.propose_commitment(
                target_agent=c2.classroom_id,
                time_adjustment=-2,  # finish 2 minutes early
                future_obligation="next week you can extend 2 minutes"
            )
            print(f"C1 → C2: {proposal}")

            # Simulate acceptance
            acceptance_task = f"Evaluate and respond to this proposal: {proposal}"
            response = await c2.agent.run(task=acceptance_task)
            print(f"C2 Response: {response.messages[-1].content}")

            # Step 4: Create commitment if accepted
            commitment = c1.create_commitment(
                debtor="C1",
                creditor="C2",
                time_adjustment=-2,
                future_obligation="Next Monday: C2 gets +2 minutes extension"
            )

            c1.commitments_made.append(commitment)
            c2.commitments_received.append(commitment)

            print("\n4. COMMITMENT EXECUTION")
            print(f"Commitment created: {commitment.debtor} → {commitment.creditor}")
            print(f"Time adjustment: {commitment.time_adjustment} minutes")
            print(f"Future obligation: {commitment.future_obligation}")

            # Step 5: Coordinated exits
            print("\n5. COORDINATED STUDENT EXITS")
            print("11:28 AM: C1 students exit (60 students, 2 min early)")
            print("11:30 AM: C2 students exit (45 students, on time)")
            print("11:30 AM: C3 students exit (75 students, split batch)")
            print("11:32 AM: Remaining students exit")

            print("\n✅ Coordination episode completed successfully!")

        except Exception as e:
            print(f"❌ Error in coordination episode: {e}")

        finally:
            # Do NOT close model_client here — main() will close it once at the end.
            pass

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
        print("2. Requires OpenAI API key in model client")
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
