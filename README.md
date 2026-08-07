AgentIQ - Autonomous Research & Business Intelligence Platform

AgentIQ is a production-oriented multi-agent AI system designed totransform a high-level business question into a structured researchworkflow, gather information from external sources, analyze thefindings, generate visual insights, and produce a final report.
Instead of treating an LLM as a single chatbot, AgentIQ treats theproblem as an orchestrated intelligence pipeline where specializedagents collaborate through a shared state and a LangGraph workflow.
The project is being developed with a strong focus on agentorchestration, reliability, structured outputs, extensibility, andreal-world business intelligence workflows.

Why AgentIQ?
A typical LLM application follows a simple pattern:

User → Prompt → LLM → Answer

That works for simple questions, but complex research problems usuallyrequire multiple stages:
Understanding the objective
Breaking the objective into actionable tasks

Gathering current information
Working with structured and unstructured data
Comparing evidence
Performing analysis
Creating visualizations
Reviewing the generated findings
Producing a professional report

AgentIQ is designed around that second model:

                    ┌─────────────────────┐
                    │      User Query     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Planner Agent    │
                    │ Goal decomposition  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   LangGraph         │
                    │   Orchestrator      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │  Research   │   │    Data     │   │  Document   │
      │    Agent    │   │    Agent    │   │    Agent    │
      └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Analysis Agent    │
                    └──────────┬──────────┘
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
              ┌─────────────┐     ┌─────────────┐
              │ Visualization│     │   Reviewer   │
              │    Agent     │     │    Agent     │
              └──────┬──────┘     └──────┬──────┘
                     │                   │
                     └─────────┬─────────┘
                               ▼
                    ┌─────────────────────┐
                    │    Report Agent     │
                    │ Final Intelligence  │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Structured Report   │
                    └─────────────────────┘

The exact routing is evolving as the architecture is refactored. Thediagram represents the intended direction rather than claiming everypath is already fully implemented.



Core Idea

AgentIQ separates responsibilities across specialized components ratherthan placing the entire workload inside one prompt.
Planner Agent
Converts a broad objective into a structured execution plan.
Example:

Input:
"Analyze the Indian EV market"

Output:
- Research current market trends
- Analyze government policies
- Evaluate major players
- Examine consumer behavior
- Identify opportunities and risks

Research Agent
Collects relevant external information using web search tools andprepares research findings for downstream analysis.

Data Agent
Handles structured-data-oriented tasks and prepares data for analysis.

Document Agent
Provides the foundation for working with uploaded documents and documentintelligence workflows.

Analysis Agent
Synthesizes research and data into meaningful business insights,comparisons, trends, and conclusions.

Visualization Agent
Converts analytical findings into useful visual representations whereappropriate.

Reviewer Agent
Acts as a quality-control layer. It is intended to validate whether thegenerated analysis is coherent, sufficiently supported, and aligned withthe original objective.

Report Agent
Combines the outputs into a structured final report suitable forbusiness research and decision-support workflows.

Architecture

AgentIQ is built around LangGraph-based orchestration rather than asimple sequential chain.

The central design principle is:
State
  ↓
Decision
  ↓
Agent
  ↓
State Update
  ↓
Decision
  ↓
Next Agent



This makes it possible to introduce:

Conditional routing
Parallel execution
Retries
Failure handling
Human review points
Agent-level observability
Persistent state
More complex multi-step workflows

The project is intentionally being refactored toward these capabilitiesrather than continuously adding agents to a rigid sequentialarchitecture.

Current Technology Stack

Layer                 Technology

Language              PythonAgent Orchestration   LangGraphLLM Framework         LangChainLLM Provider          GroqWeb Research          TavilyData Processing       PandasVisualization         MatplotlibConfiguration         Python environment variablesTesting               PytestVersion Control       Git / GitHub

Planned / evolving technologies


The architecture is designed to accommodate additional components suchas:
Vector databases
RAG pipelines
MCP
PostgreSQL
Document processing pipelines
PDF/DOCX generation
Production frontend
Cloud deployment
Observability and evaluation

These are part of the roadmap and should not be interpreted as fullyimplemented in the current baseline.

Project Structure
AgentIQ/
│
├── agents/
│   ├── analysis_agent.py
│   ├── data_agent.py
│   ├── document_agent.py
│   ├── planner_agent.py
│   ├── report_agent.py
│   ├── research_agent.py
│   ├── reviewer_agent.py
│   └── visualization_agent.py
│
├── app/
│   └── streamlit_app.py
│
├── config/
│   └── settings.py
│
├── graph/
│   ├── nodes.py
│   ├── pipeline.py
│   ├── state.py
│   └── workflow.py
│
├── pipeline/
│   └── pipeline.py
│
├── prompts/
│   ├── analysis_prompt.py
│   ├── analyst_prompt.py
│   ├── data_prompt.py
│   ├── planner_prompt.py
│   ├── report_prompt.py
│   ├── research_prompt.py
│   └── reviewer_prompt.py
│
├── schemas/
│   ├── analysis_schema.py
│   ├── data_schema.py
│   ├── planner_schema.py
│   └── research_schema.py
│
├── state/
│   └── agent_state.py
│
├── tools/
│   ├── chart_tool.py
│   ├── csv_tool.py
│   ├── pdf_tool.py
│   ├── report_tool.py
│   ├── search_tool.py
│   └── web_search.py
│
├── tests/
│   ├── test_analysis.py
│   ├── test_data.py
│   ├── test_pipeline.py
│   ├── test_planner.py
│   ├── test_report.py
│   ├── test_research.py
│   ├── test_search.py
│   └── test_visualization.py
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md



Execution Flow
A simplified execution flow currently looks like:

User Query
    │
    ▼
Planner
    │
    ▼
Structured Agent State
    │
    ▼
LangGraph Workflow
    │
    ├── Research
    ├── Data Processing
    ├── Document Processing
    │
    ▼
Analysis
    │
    ├── Visualization
    └── Review
    │
    ▼
Report Generation
    │
    ▼
Final Business Intelligence Output

The workflow is being redesigned so that agents are not simply executedone after another. The graph should eventually determine which agentshould run, when it should run, whether it should retry, and whether itsoutput is good enough to continue.

Example Use Case
Suppose the user enters:
Analyze the Indian EV market
AgentIQ should be able to turn that single request into a structuredresearch process.

Step 1 --- Planning

The Planner identifies the objective and creates tasks such as:
1. Research Indian EV market trends
2. Analyze government policies and incentives
3. Evaluate major market participants
4. Study consumer adoption
5. Identify opportunities and risks


Step 2 --- Research

The Research Agent gathers relevant information from external sources.


Step 3 --- Analysis

The Analysis Agent compares the findings and identifies:
Market trends
Growth drivers
Adoption barriers
Competitive dynamics
Policy impact
Business opportunities


Step 4 --- Visualization

Relevant quantitative findings can be converted into charts or othervisual representations.



Step 5 --- Review

The Reviewer evaluates the generated output against the originalobjective.



Step 6 --- Reporting

The Report Agent produces a structured research report containing:
Executive Summary
Market Overview
Key Findings
Data & Analysis
Competitive Landscape
Policy Analysis
Opportunities
Risks
Conclusion
Sources


Design Principles

1. Specialized Agents
Each agent should have a clearly defined responsibility.
An agent should not become a generic "do everything" LLM wrapper.

2. Shared State
Agents communicate through structured state rather than relying onhidden context.
This improves:
Traceability
Debugging
Routing
Validation
Extensibility

3. Structured Outputs

Where possible, agent outputs should follow schemas instead ofunrestricted text.
This allows downstream components to consume results predictably.

4. Tool-Based Intelligence

Agents should use tools when tools are more reliable than puregeneration.
Examples:
Web Search
CSV Processing
PDF Processing
Chart Generation
Report Generation

5. Reliability Over Agent Count

The goal is not to maximize the number of agents.
The goal is to build an orchestration system where a smaller number ofwell-designed agents can reliably solve complex workflows.

6. Testability
Agent logic, tools, schemas, and workflows should be testableindependently.



Environment Setup

1. Clone the repository
git clone https://github.com/Sagarsingh19/AgentIQ.git
cd AgentIQ

2. Create a virtual environment
Windows:
python -m venv venv
venv\Scripts\activate

macOS/Linux:
python3 -m venv venv
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Configure environment variables

Create a .env file:
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

Never commit .env to Git.
The repository should contain an .env.example file containingplaceholders only.


Running AgentIQ

The current project can be started through:
python main.py
The exact execution interface is expected to evolve as the applicationarchitecture and production frontend are developed.
Testing
Run the test suite with:
pytest


Individual test modules can also be executed:

pytest tests/test_planner.py
pytest tests/test_research.py
pytest tests/test_analysis.py
pytest tests/test_pipeline.py

Tests are being expanded alongside the architectural refactor.
Development Workflow

AgentIQ is developed using a feature-branch workflow.

main
 │
 ├── feature/reviewer-agent
 ├── feature/document-ingestion
 ├── feature/conditional-routing
 ├── feature/rag
 └── feature/report-generation

The main branch represents the stable project baseline.
Development should follow:

Create branch
     ↓
Implement feature
     ↓
Run tests
     ↓
Commit
     ↓
Push branch
     ↓
Open Pull Request
     ↓
Review
     ↓
Merge into main


Example:
git checkout main
git pull origin main
git checkout -b feature/document-ingestion

# Develop and test

git add .
git commit -m "feat: add document ingestion pipeline"
git push -u origin feature/document-ingestion




Roadmap

AgentIQ is being developed in phases.

Phase 1 --- Foundation
Planner Agent
Research Agent
Analysis Agent
Visualization Agent
Report Agent
Structured agent state
Groq integration
Tavily integration
Initial LangGraph workflow
Basic tests



Phase 2 --- Architecture Refactor

Centralized state management
Graph-based orchestration
Node registration
Workflow compilation
Conditional routing
Parallel execution
Retry mechanisms
Failure handling
Better state transitions
Agent-level validation


Phase 3 --- Intelligence & Reliability

Reviewer Agent integration
Self-correction loops
Evidence validation
Source quality evaluation
Structured citations
Agent evaluation framework
Observability and tracing


Phase 4 --- Document Intelligence

PDF ingestion
DOCX ingestion
CSV/Excel ingestion
Document parsing
Chunking
Embeddings
Vector search
RAG
Multi-document research



Phase 5 --- Advanced Agentic Capabilities

MCP integration
Additional external tools
Dynamic tool selection
Long-running workflows
Human-in-the-loop checkpoints
Persistent workflow state



Phase 6 --- Production Application

Production frontend
Authentication
File upload interface
Research history
Report download
API layer
Containerization
Cloud deployment
Monitoring



What Makes AgentIQ Different?

AgentIQ is not intended to be another chatbot with several promptsbehind it.
The core engineering problem is orchestration.

The system needs to answer questions such as:
What needs to be done?
Which agent should do it?
Can multiple tasks run simultaneously?
What happens if a tool fails?
How do we know the output is valid?
Should another agent review it?
Should the workflow retry?
How should information move between agents?
How do we maintain state across a long workflow?
How can the same architecture support web research,
uploaded documents, structured datasets and external tools?

These are the problems AgentIQ is being designed to solve.



Future Vision

The long-term goal is to turn AgentIQ into a general-purpose AIresearch and business intelligence engine.
A user should eventually be able to provide:
A business question
+
Optional documents
+
Optional datasets
+
Optional constraints

and receive:
Research
+
Evidence
+
Analysis
+
Visualizations
+
Review
+
A professional report

without manually coordinating the individual steps.
The architecture is intentionally designed so that additionalcapabilities can be introduced as tools, agents, or graph nodes withoutrebuilding the entire system.


Project Status

Current status: Active development
The initial multi-agent foundation is implemented and the project isundergoing a deeper architectural refactor.


The immediate priority is not adding an increasing number of agents. Itis improving the underlying orchestration layer so that AgentIQ becomes:
More reliable
More modular
More testable
More observable
More extensible
Better suited for production deployment
Contributing
Contributions and collaborative development are welcome.


For major changes:

Create a feature branch.
Keep the change focused.
Add or update tests.
Update documentation where necessary.
Open a Pull Request.
Explain the architectural impact of the change.


Avoid committing:

.env
API keys
large generated files
local virtual environments
temporary outputs
machine-specific configuration

License
License information will be added as the project moves toward its publicrelease stage.

Built With
Python · LangGraph · LangChain · Groq · Tavily · Pandas · Matplotlib ·Pytest · GitHub

AgentIQ is an evolving engineering project focused on buildingreliable multi-agent systems for autonomous research and businessintelligence.
