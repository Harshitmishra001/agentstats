from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Literal

class FailureCategory(Enum):
    # ── Core taxonomy: FOSSEE/IIT Bombay research-validated (code-generation errors) ──
    BOUNDARY_INDEXING          = "boundary_indexing"
    CONDITIONAL_BOOLEAN        = "conditional_boolean"
    STATE_MANAGEMENT           = "state_management"
    ALGORITHMIC_STRATEGY       = "algorithmic_strategy"
    EDGE_CASE_HANDLING         = "edge_case_handling"
    SPEC_MISUNDERSTANDING      = "specification_misunderstanding"
    # ── Extension: agent-orchestration errors (v1, not yet formally validated) ──
    TOOL_ORCHESTRATION_ERROR   = "tool_orchestration_error"
    # ── Tier 1: Infrastructure errors (rule-based) ──
    INFRA_TIMEOUT              = "infra_timeout"
    INFRA_RATE_LIMIT           = "infra_rate_limit"
    INFRA_AUTH_ERROR           = "infra_auth_error"
    INFRA_MALFORMED_JSON       = "infra_malformed_json"
    INFRA_TOOL_NOT_FOUND       = "infra_tool_not_found"
    # ── Fallback ──
    NONE                       = "none"

class Span(BaseModel):
    id: str
    parent_id: Optional[str] = None
    tool_name: str
    model: Optional[str] = None
    start_ts: float
    end_ts: Optional[float] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_estimate: float = 0.0
    status: Literal["success", "error", "running"] = "running"
    raw_error: Optional[str] = None
    failure_category: FailureCategory = FailureCategory.NONE
    failure_reason: Optional[str] = None
    retries: int = 0
