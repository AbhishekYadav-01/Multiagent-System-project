# Multiagent System Design Report
## Traffic Bottleneck Coordination using AutoGen Framework

**Assignment**: MAS-Assignment-1  
**Framework**: Microsoft AutoGen  

---

## Executive Summary

This report presents the design and implementation approach for a multiagent system (MAS) that coordinates shared resource access—specifically, managing traffic flow through a narrow road leading to a lecture hall complex. The system uses Microsoft's AutoGen framework to implement cooperative agents that negotiate commitments to prevent congestion during simultaneous lecture endings.

The proposed solution addresses the core challenge of coordinating multiple autonomous classroom agents with a bottleneck monitoring agent to ensure smooth student egress while maintaining fairness and preventing violations through a commitment-based protocol.

---

## 1. System Architecture

### 1.1 Agent Design

**Bottleneck Agent (Agent B)**
- **Role**: Central traffic monitor and information broadcaster
- **Responsibilities**:
  - Monitor bottleneck point capacity (50 students/minute)
  - Estimate total students across all classrooms
  - Broadcast capacity and congestion information
  - Track system-wide performance metrics

**Classroom Agents (C1, C2, C3, C4, C5)**
- **Role**: Individual classroom coordinators
- **Responsibilities**:
  - Monitor classroom attendance
  - Negotiate commitments with peer agents
  - Coordinate staggered student exits
  - Maintain commitment history and honor obligations
  - Consult with professors on lecture duration flexibility

### 1.2 Communication Architecture

The system implements AutoGen's GroupChat framework with the following message types:

- **TRAFFIC_UPDATE**: Broadcast from Agent B with current capacity
- **COMMITMENT_PROPOSAL**: Negotiation messages between classroom agents
- **COMMITMENT_ACCEPTANCE/REJECTION**: Response to proposals
- **DEAL_BROADCAST**: Announcement of successful agreements
- **VIOLATION_ALERT**: Warning for commitment violations

---

## 2. Commitment Protocol Design

### 2.1 Commitment Structure

```json
{
  "debtor": "agent_id",
  "creditor": "agent_id", 
  "time_adjustment": "integer_minutes",
  "future_obligation": "description",
  "episode": "time_slot_identifier",
  "created_at": "timestamp"
}
```

### 2.2 Negotiation Process

1. **Information Gathering**: Agent B broadcasts current bottleneck state
2. **Situation Assessment**: Classroom agents evaluate their student counts and professor flexibility
3. **Proposal Generation**: Agents with excess capacity offer time adjustments
4. **Negotiation**: Bilateral commitment discussions with future obligations
5. **Broadcasting**: Successful deals announced to all agents
6. **Execution**: Coordinated student exits in 2-minute intervals
7. **History Update**: Commitment records updated for future episodes

### 2.3 Violation Management

- **Three-Strike Rule**: Agents violating commitments >3 times trigger violation events
- **Commitment Tracking**: Persistent history across weekly episodes
- **Flexibility Assessment**: Professor cooperation levels influence negotiation strategies

---

## 3. Race Condition Prevention

### 3.1 Coordination Mechanisms

**Message Ordering**: Sequential processing through AutoGen's conversation management
**Resource Locks**: Prevent simultaneous bottleneck capacity allocation
**Atomic Operations**: Commitment creation/acceptance as single transactions
**Timeout Mechanisms**: Prevent infinite negotiation loops

### 3.2 Fairness Heuristics

- **Round-robin negotiation opportunities**
- **Historical commitment balance tracking**
- **Professor flexibility consideration**
- **Student count proportional adjustments**

---

## 4. Implementation Approach

### 4.1 Technology Stack

- **Framework**: Microsoft AutoGen v0.2+
- **Language**: Python 3.9+
- **LLM Provider**: OpenAI GPT-4 (configurable)
- **Dependencies**: pandas, matplotlib, asyncio, pydantic

### 4.2 Project Structure

```
mas_traffic_coordination/
├── src/
│   ├── agents/          # Agent implementations
│   ├── models/          # Data structures
│   ├── protocols/       # Communication protocols
│   ├── utils/           # Utilities and visualization
│   └── simulation/      # Simulation engine
├── config/              # Configuration files
├── tests/               # Unit and integration tests
├── results/             # Simulation outputs
└── docs/                # Documentation
```

### 4.3 Core Components

**BottleneckAgent Class**
- Inherits from `autogen.ConversableAgent`
- Implements traffic monitoring and broadcasting
- Tracks system performance metrics

**ClassroomAgent Class**
- Inherits from `autogen.ConversableAgent`
- Implements commitment negotiation logic
- Maintains local state and history

**Commitment Management System**
- Persistent storage for commitment history
- Violation detection and alerting
- Performance analytics and reporting

---

## 5. Simulation Environment

### 5.1 Environment Parameters

- **Classrooms**: 5 (C1-C5)
- **Bottleneck Capacity**: 50 students/minute
- **Student Range**: 30-80 per classroom
- **Time Slot**: Monday 11:00 AM (recurring)
- **Batch Interval**: 2 minutes
- **Simulation Episodes**: 10+ weeks

### 5.2 Test Scenarios

1. **Baseline**: No coordination (measure congestion)
2. **Basic Coordination**: Simple commitment protocol
3. **Advanced Coordination**: With violation tracking
4. **Stress Test**: Maximum capacity scenarios
5. **Robustness Test**: Agent failures and recovery

### 5.3 Success Metrics

- **Congestion Reduction**: Bottleneck utilization <80%
- **Fairness Index**: Balanced commitment distribution
- **Protocol Efficiency**: Successful negotiation rate
- **System Reliability**: Violation rate <5%

---

## 6. Expected Results

### 6.1 Performance Improvements

Based on similar multiagent coordination studies, the system is expected to achieve:

- **30-50% reduction** in peak bottleneck congestion
- **90%+ successful** commitment negotiations
- **Balanced workload** distribution across classrooms
- **Sub-5% violation** rate with proper incentive alignment

### 6.2 Emergent Behaviors

- **Coalition formation** between compatible agents
- **Dynamic load balancing** based on attendance patterns  
- **Learning and adaptation** over multiple episodes
- **Robust recovery** from individual agent failures
---

## 8. Risk Mitigation

### 8.1 Technical Risks

**AutoGen Complexity**: Mitigated by starting with simple agent interactions
**LLM Costs**: Using efficient prompting and local model alternatives
**Race Conditions**: Implementing proper synchronization mechanisms
**Scalability**: Designing for modular agent addition/removal

### 8.2 Schedule Risks

**Implementation Complexity**: Buffer time built into timeline
**Integration Challenges**: Early and frequent testing
**Performance Issues**: Parallel development of optimization strategies

---

## 9. Conclusion

The proposed multiagent system leverages AutoGen's conversation-driven architecture to solve a realistic resource coordination problem. The commitment-based protocol enables cooperative behavior while maintaining agent autonomy, addressing the core requirements of preventing congestion through distributed coordination.

The implementation approach balances theoretical rigor with practical considerations, providing a robust foundation for extension to other shared resource coordination scenarios.

---

## References

1. Microsoft AutoGen Framework Documentation
2. FIPA Agent Communication Language Specification
3. Multi-Agent Reinforcement Learning for Traffic Coordination
4. Commitment Protocols in Multiagent Systems
5. Race Condition Prevention in Distributed Systems

---

**Next Steps**: Proceed with AutoGen environment setup and begin basic agent implementation following the provided code templates and configuration files.
