import re
RED_FLAG_PATTERNS = {
 "going_concern":{"patterns":[(r"going concern",re.I),(r"material uncertainty",re.I),(r"significant doubt",re.I)],"context_keywords":["audit","report","note","disclosure"],"weight":20},
 "related_party":{"patterns":[(r"related part(?:y|ies)",re.I),(r"\bRPT\b",0)],"context_keywords":["transaction","loan","sale","purchase","guarantee"],"weight":15},
 "pending_litigation":{"patterns":[(r"pending litigation",re.I),(r"legal proceedings",re.I),(r"\bdispute[sd]?\b",re.I),(r"arbitration",re.I)],"context_keywords":["court","high court","tribunal","appeal","filed"],"weight":12},
 "contingent_liability":{"patterns":[(r"contingent liabilit(?:y|ies)",re.I)],"context_keywords":["demand","notice","claim","guarantee"],"weight":12},
 "audit_qualification":{"patterns":[(r"qualified opinion",re.I),(r"adverse opinion",re.I),(r"disclaimer of opinion",re.I),(r"emphasis of matter",re.I)],"context_keywords":["auditor","audit","report"],"weight":20},
 "default":{"patterns":[(r"\bdefault(?:ed|ing)?\b",re.I),(r"non-payment",re.I),(r"\binsolvency\b",re.I)],"context_keywords":["loan","debt","repayment","borrower"],"weight":15},
 "regulatory":{"patterns":[(r"\bCBI\b",0),(r"\bED\b",0),(r"Enforcement Directorate",re.I),(r"\bSEBI\b",0),(r"\binvestigation\b",re.I),(r"\bscrutiny\b",re.I)],"context_keywords":["filed","registered","case","proceeding","notice","summon"],"weight":15},
 "npa":{"patterns":[(r"\bNPA\b",0),(r"non[- ]performing",re.I),(r"bad loan",re.I)],"context_keywords":["asset","loan","portfolio","provision"],"weight":15},
 "shell_company":{"patterns":[(r"shell compan(?:y|ies)",re.I),(r"\bbenami\b",re.I),(r"offshore entity",re.I)],"context_keywords":["related","entity","director","address"],"weight":20},
 "demand_notice":{"patterns":[(r"demand notice",re.I),(r"show cause",re.I),(r"\bSCN\b",0)],"context_keywords":["tax","duty","penalty","interest"],"weight":12},
 "termination":{"patterns":[(r"\bterminat(?:ed|ion)\b",re.I)],"context_keywords":["contract","agreement","license","lease"],"weight":10},
 "guarantee":{"patterns":[(r"\bguarantee[sd]?\b",re.I),(r"\bguarantor\b",re.I),(r"\bindemnity\b",re.I)],"context_keywords":["loan","credit","bank","financial"],"weight":8},
 "promoter":{"patterns":[(r"\bpromoter(?: group)?\b",re.I),(r"controlling shareholder",re.I)],"context_keywords":["share","holding","entity"],"weight":5},
 "iepf":{"patterns":[(r"\bIEPF\b",0),(r"unclaimed dividend",re.I)],"context_keywords":["transfer","authority","fund"],"weight":5}
}
