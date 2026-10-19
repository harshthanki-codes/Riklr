"""
QueryPlan definition using Pydantic
Zero SQL hallucination: enforces closed enums for intents, metrics, and parameters.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class IntentEnum(str, Enum):
    METRIC_QUERY = "metric_query"
    COMPARE_DEFINITIONS = "compare_definitions"
    DISTRIBUTOR_BRIEF = "distributor_brief"
    CHANNEL_RISK = "channel_risk"
    PENDING_CREDITS = "pending_credits"
    OVERDUE = "overdue"
    STOPPED_BUYING = "stopped_buying"
    DATA_HEALTH = "data_health"
    OUT_OF_SCOPE = "out_of_scope"

class MetricEnum(str, Enum):
    M01_GROSS_SALES = "M01"
    M02_NET_SALES = "M02"
    M04_TARGET_ACHIEVEMENT = "M04"
    M05_RETURN_RATE_QTY = "M05"
    M06_RETURN_RATE_USD = "M06"
    M07_SELL_THROUGH = "M07"
    M08_OVERDUE = "M08"
    M09_ACTIVE_DIST_SALES = "M09"
    M10_ACTIVE_DIST_FINANCE = "M10"
    AMBIGUOUS_SALES = "AMBIGUOUS_SALES"

class QueryPlan(BaseModel):
    intent: IntentEnum
    metric: Optional[MetricEnum] = None
    region: Optional[str] = None
    territory: Optional[str] = None
    distributor_id: Optional[str] = None
    fiscal_year: int = 2026
    language: str = "en"
    confidence: float = 1.0
    refusal_reason: Optional[str] = None
