from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class AgentState:
    # User Input
    query: str = ""

    # Planner Output
    plan: Dict[str, Any] = field(default_factory=dict)

    # Research Output
    research: Dict[str, Any] = field(default_factory=dict)

    # Analysis Output
    analysis: Dict[str, Any] = field(default_factory=dict)

    # Visualization Output
    visualization: Dict[str, Any] = field(default_factory=dict)

    # Final Report
    report: str = ""

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Error Tracking
    errors: List[str] = field(default_factory=list)