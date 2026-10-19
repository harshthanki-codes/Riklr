"""
Multilingual NL Router & Transliteration Lexicon
Maps English, Portuguese, and Romanized/Native Marathi & Hindi into structured QueryPlans.
Guarantees zero SQL generation and polite refusals for unsupported questions.
"""
import re
from typing import Dict, Any, Optional
from .plan import QueryPlan, IntentEnum, MetricEnum

# Lexicons for multilingual matching (handles Romanized Marathi/Hindi & Portuguese)
LEXICON = {
    "credits": [
        "credit", "credits", "credit note", "scheme", "schemes", 
        "rebate", "baki", "kab aayega", "kadhi yenar", "credit note kab", "pending credit"
    ],
    "overdue": [
        "overdue", "outstanding", "arrears", "disputed", "kitna hai", 
        "kiti aahe", "baki kitna", "pagamento em atraso", "vencido"
    ],
    "sell_through": [
        "sell-through", "sell through", "scans", "dealer scans", "loyalty", 
        "saida", "escoamento", "scan rate"
    ],
    "risk": [
        "risk", "channel risk", "loading", "dumping", "excess stock", 
        "estoque alto", "retorno", "hazard", "warning"
    ],
    "sales": [
        "sales", "revenue", "gross sales", "net sales", "faturamento", 
        "vendas", "bikri", "total sales", "vikri"
    ],
    "out_of_scope": [
        "weather tomorrow", "forecast next year", "previsao de vendas para a safra", 
        "who is the ceo", "stock price", "bonus calculation formula"
    ]
}

def detect_language(text: str) -> str:
    # Unicode script check
    if re.search(r'[\u0900-\u097F]', text):
        return "mr" if ("आहे" in text or "किती" in text or "नाही" in text) else "hi"
    
    text_l = text.lower()
    if any(w in text_l for w in ["qual", "quanto", "vendas", "revendas", "distribuidor", "safra", "insumos"]):
        return "pt"
    if any(w in text_l for w in ["kiti", "aahe", "kadhi", "baki"]):
        return "mr"
    if any(w in text_l for w in ["kitna", "kab", "aayega", "batao", "hai"]):
        return "hi"
    return "en"

class NLRouter:
    def route_query(self, text: str, user_scope_territory: Optional[str] = None) -> QueryPlan:
        text_l = text.lower().strip()
        lang = detect_language(text)

        # Check out-of-scope first
        if any(w in text_l for w in LEXICON["out_of_scope"]):
            return QueryPlan(
                intent=IntentEnum.OUT_OF_SCOPE,
                language=lang,
                confidence=0.9,
                refusal_reason="This question falls outside the commercial data model (e.g. forward-looking subjective forecast or general knowledge). Supported topics include: Net Sales, Gross Sales, Pending Scheme Credits, Distributor Briefs, and Channel Risk."
            )

        # Pending Credits check
        if any(w in text_l for w in LEXICON["credits"]) and any(w in text_l for w in ["pending", "status", "kab", "kadhi", "when", "unissued"]):
            return QueryPlan(
                intent=IntentEnum.PENDING_CREDITS,
                territory=user_scope_territory,
                language=lang,
                confidence=0.95
            )

        # Overdue / Outstanding check
        if any(w in text_l for w in LEXICON["overdue"]):
            return QueryPlan(
                intent=IntentEnum.OVERDUE,
                metric=MetricEnum.M08_OVERDUE,
                territory=user_scope_territory,
                language=lang,
                confidence=0.95
            )

        # Channel Risk Radar check
        if any(w in text_l for w in LEXICON["risk"]):
            return QueryPlan(
                intent=IntentEnum.CHANNEL_RISK,
                region="BR" if "brazil" in text_l or "br" in text_l else None,
                language=lang,
                confidence=0.90
            )

        # Distributor Brief check
        if "brief" in text_l or "notebook" in text_l or "visit" in text_l or "distributor" in text_l:
            return QueryPlan(
                intent=IntentEnum.DISTRIBUTOR_BRIEF,
                territory=user_scope_territory,
                language=lang,
                confidence=0.90
            )

        # Sales metric check (handles ambiguity rule)
        if any(w in text_l for w in LEXICON["sales"]):
            if "net" in text_l:
                metric = MetricEnum.M02_NET_SALES
            elif "gross" in text_l:
                metric = MetricEnum.M01_GROSS_SALES
            else:
                metric = MetricEnum.AMBIGUOUS_SALES

            return QueryPlan(
                intent=IntentEnum.METRIC_QUERY,
                metric=metric,
                territory=user_scope_territory,
                language=lang,
                confidence=0.95
            )

        # Default fallback
        return QueryPlan(
            intent=IntentEnum.OUT_OF_SCOPE,
            language=lang,
            confidence=0.4,
            refusal_reason="I can't answer that reliably. Please ask about Sales, Scheme Credits, Receivables, or Distributor Pre-Visit Briefs."
        )
