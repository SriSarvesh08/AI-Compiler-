"""
Change Request Analyzer — Classifies modification requests.

Takes a natural language change request and classifies it into
a specific change type, identifying which layers are affected.
"""

import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    ADD_FEATURE = "add_feature"
    REMOVE_FEATURE = "remove_feature"
    UPDATE_ROLE = "update_role"
    UPDATE_PERMISSION = "update_permission"
    UPDATE_PAGE = "update_page"
    UPDATE_BUSINESS_LOGIC = "update_business_logic"
    AMBIGUOUS_CHANGE = "ambiguous_change"


# Maps change types to which pipeline layers they affect
AFFECTED_LAYERS: dict[ChangeType, list[str]] = {
    ChangeType.ADD_FEATURE: ["intent", "architecture", "ui_schema", "api_schema", "db_schema", "auth_schema"],
    ChangeType.REMOVE_FEATURE: ["intent", "architecture", "ui_schema", "api_schema", "db_schema", "auth_schema"],
    ChangeType.UPDATE_ROLE: ["intent", "architecture", "auth_schema"],
    ChangeType.UPDATE_PERMISSION: ["auth_schema"],
    ChangeType.UPDATE_PAGE: ["architecture", "ui_schema"],
    ChangeType.UPDATE_BUSINESS_LOGIC: ["api_schema", "auth_schema"],
    ChangeType.AMBIGUOUS_CHANGE: [],
}


# Pattern groups for classification
ADD_PATTERNS: list[str] = [
    r"\badd\b", r"\binclude\b", r"\bcreate\b", r"\bintroduce\b",
    r"\bbuild\b", r"\bintegrate\b", r"\bnew\b", r"\binsert\b",
    r"\bimplement\b", r"\benable\b", r"\bsupport\b",
]

REMOVE_PATTERNS: list[str] = [
    r"\bremove\b", r"\bdelete\b", r"\bdrop\b", r"\bdisable\b",
    r"\beliminate\b", r"\bget rid of\b", r"\btake out\b",
]

ROLE_PATTERNS: list[str] = [
    r"\brole\b", r"\buser type\b", r"\buser role\b",
    r"\badmin\b", r"\bmanager\b", r"\bstaff\b", r"\bmoderator\b",
    r"\bsupervisor\b", r"\bguest\b", r"\bviewer\b",
]

PERMISSION_PATTERNS: list[str] = [
    r"\bpermission\b", r"\baccess\b", r"\brestrict\b",
    r"\ballow\b", r"\bdeny\b", r"\bgrant\b", r"\brevoke\b",
    r"\bcan\s+(?:only|not)\b", r"\bcannot\b", r"\bauthoriz\b",
]

PAGE_PATTERNS: list[str] = [
    r"\bpage\b", r"\bscreen\b", r"\bview\b", r"\blayout\b",
    r"\bdashboard\b", r"\bform\b", r"\bmodal\b", r"\btab\b",
    r"\bnavigation\b", r"\broute\b", r"\bui\b",
]

FEATURE_PATTERNS: list[str] = [
    r"\bfeature\b", r"\bmodule\b", r"\bfunctionality\b",
    r"\bcapability\b", r"\bsystem\b", r"\bengine\b",
    r"\bpayment\b", r"\bbilling\b", r"\banalytics\b",
    r"\bnotification\b", r"\breporting\b", r"\bexport\b",
    r"\bchat\b", r"\bmessaging\b", r"\bsearch\b",
]

BUSINESS_LOGIC_PATTERNS: list[str] = [
    r"\bbusiness\s*logic\b", r"\bworkflow\b", r"\brule\b",
    r"\bvalidation\b", r"\btrigger\b", r"\bconstraint\b",
    r"\bpremium\b", r"\bgating\b", r"\bpaywall\b",
]


def _score_patterns(text: str, patterns: list[str]) -> int:
    """Count how many patterns match in the text."""
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


class ChangeRequestAnalyzer:
    """Analyzes a change request and classifies it."""

    def analyze(self, change_request: str) -> dict:
        """Classify a change request into a change type.

        Args:
            change_request: Natural language description of the change.

        Returns:
            Dict with change_type, affected_layers, and optional
            clarification_needed fields.
        """
        logger.info(f"Analyzing change request: {change_request[:100]}...")
        text = change_request.lower().strip()

        if len(text) < 5:
            return {
                "change_type": ChangeType.AMBIGUOUS_CHANGE,
                "affected_layers": [],
                "clarification_needed": True,
                "clarification_questions": [
                    "Your change request is too short. Please describe what you'd like to modify in more detail."
                ],
            }

        # Score each category
        scores = {
            "add": _score_patterns(text, ADD_PATTERNS),
            "remove": _score_patterns(text, REMOVE_PATTERNS),
            "role": _score_patterns(text, ROLE_PATTERNS),
            "permission": _score_patterns(text, PERMISSION_PATTERNS),
            "page": _score_patterns(text, PAGE_PATTERNS),
            "feature": _score_patterns(text, FEATURE_PATTERNS),
            "business_logic": _score_patterns(text, BUSINESS_LOGIC_PATTERNS),
        }

        logger.debug(f"Pattern scores: {scores}")

        # Determine action (add or remove)
        is_add = scores["add"] > scores["remove"]
        is_remove = scores["remove"] > scores["add"]

        # Determine target
        target_scores = {
            "role": scores["role"],
            "permission": scores["permission"],
            "page": scores["page"],
            "feature": scores["feature"],
            "business_logic": scores["business_logic"],
        }

        best_target = max(target_scores, key=target_scores.get)
        best_score = target_scores[best_target]

        # If no clear signal at all, it's ambiguous
        if best_score == 0 and scores["add"] == 0 and scores["remove"] == 0:
            return {
                "change_type": ChangeType.AMBIGUOUS_CHANGE,
                "affected_layers": [],
                "clarification_needed": True,
                "clarification_questions": [
                    "Could you clarify what you want to change?",
                    "Are you adding, removing, or updating something?",
                    "Which part of the application should be modified (pages, roles, features, permissions)?",
                ],
            }

        # Classify
        if best_target == "role":
            change_type = ChangeType.UPDATE_ROLE
        elif best_target == "permission":
            change_type = ChangeType.UPDATE_PERMISSION
        elif best_target == "page":
            change_type = ChangeType.UPDATE_PAGE
        elif best_target == "business_logic":
            change_type = ChangeType.UPDATE_BUSINESS_LOGIC
        elif is_remove:
            change_type = ChangeType.REMOVE_FEATURE
        else:
            change_type = ChangeType.ADD_FEATURE

        affected = AFFECTED_LAYERS.get(change_type, [])

        logger.info(f"Change classified as: {change_type.value} | Affected: {affected}")

        return {
            "change_type": change_type,
            "affected_layers": affected,
            "clarification_needed": False,
            "clarification_questions": [],
        }
