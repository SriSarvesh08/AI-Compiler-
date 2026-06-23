"""
Intent Extractor — Stage 1 of the Compiler Pipeline.

Takes a natural language prompt describing an application and extracts
structured intent data including domain, features, and user roles.

This is the ONLY fully implemented pipeline stage for Day 1.
"""

import json
import logging
import time

import google.generativeai as genai
from google.generativeai.types import generation_types
import openai
import anthropic
import os

from schemas.intent_schema import IntentOutput

logger = logging.getLogger(__name__)

# System prompt instructs the AI to behave as a compiler's first pass —
# extracting structured intent from natural language, not generating code.
SYSTEM_PROMPT = """You are the Intent Extraction stage of an AI Application Compiler.
Your job is to analyze a natural language software requirement and extract structured intent data.

You MUST return ONLY a valid JSON object with this exact structure:
{
  "domain": "<string: the application domain, e.g. CRM, E-Commerce, LMS, Healthcare, Corporate>",
  "features": ["<string: feature in snake_case>", ...],
  "roles": ["<string: user role in lowercase>", ...],
  "access_rules": ["<string: restricted access rule or permission constraint>", ...]
}

Rules:
1. "domain" must be a concise category name (1-3 words).
2. "features" must be a list of distinct modules/features extracted from the prompt, formatted in snake_case. Ensure you separate different modules (e.g., student_dashboard, patient_dashboard, ai_recommendations, custom_reporting, premium_access).
3. "roles" must be an exhaustive list of ALL user types mentioned (e.g., "student", "patient", "employee", "admin", "manager", "doctor", "faculty", "premium_organization").
4. "access_rules" must capture any explicit rules about what roles can or cannot access (e.g., "doctors can access patient records", "managers cannot access patient data").
5. Do NOT include any explanation, markdown, or text outside the JSON object.
6. Do NOT wrap the JSON in code fences or backticks.
7. Return ONLY the raw JSON object.
"""


class IntentExtractor:
    """Extracts structured intent from natural language application descriptions.

    Uses the OpenAI API to parse user prompts into a standardized IntentOutput
    format. Includes retry logic, JSON validation, and Pydantic schema enforcement.
    """

    def __init__(self, api_key: str, model: str = "gemini"):
        """Initialize the IntentExtractor.

        Args:
            api_key: Gemini API key (fallback).
            model: Provider to use ('gemini', 'openai', 'claude').
        """
        self.model_provider = model.lower()
        if self.model_provider == "gemini" and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        logger.info(f"IntentExtractor initialized with model provider: {self.model_provider}")

    async def extract(self, prompt: str) -> tuple[IntentOutput, float]:
        """Extract intent from a natural language prompt.

        Args:
            prompt: The user's natural language application description.

        Returns:
            A tuple of (IntentOutput, extraction_time_ms).

        Raises:
            ValueError: If the AI response cannot be parsed into valid IntentOutput.
            APIError: If the OpenAI API returns an error.
        """
        logger.info(f"Starting intent extraction for prompt: {prompt[:100]}...")
        start_time = time.perf_counter()

        try:
            raw_response = await self._call_ai(prompt)
            intent = self._parse_response(raw_response)
            extraction_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"Intent extraction successful (LLM) | "
                f"Domain: {intent.domain} | "
                f"Features: {len(intent.features)} | "
                f"Roles: {len(intent.roles)} | "
                f"Time: {extraction_time_ms:.2f}ms"
            )

            return intent, extraction_time_ms

        except Exception as e:
            logger.warning(
                f"LLM intent extraction failed, falling back to rule-based: {e}"
            )
            # Fall through to rule-based

        # Rule-based fallback
        intent = self._extract_rule_based(prompt)
        extraction_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Intent extraction successful (rule-based) | "
            f"Domain: {intent.domain} | "
            f"Features: {len(intent.features)} | "
            f"Roles: {len(intent.roles)} | "
            f"Time: {extraction_time_ms:.2f}ms"
        )

        return intent, extraction_time_ms

    # ──────────────────────────────────────────────
    # Rule-Based Fallback
    # ──────────────────────────────────────────────

    # Domain detection keywords
    DOMAIN_KEYWORDS: dict[str, list[str]] = {
        "CRM": ["crm", "customer relationship", "contacts", "leads", "sales pipeline"],
        "E-Commerce": ["e-commerce", "ecommerce", "shopping", "cart", "checkout", "product listing", "store"],
        "Healthcare": ["hospital", "healthcare", "medical", "patient", "doctor", "clinic", "appointment"],
        "Education": ["lms", "learning", "course", "student", "teacher", "school", "university", "faculty", "educational"],
        "Finance": ["banking", "finance", "payment", "invoice", "billing", "accounting", "transaction", "loan"],
        "HRMS": ["hrms", "hr ", "human resource", "employee", "payroll", "leave", "attendance"],
        "Project Management": ["project management", "task", "kanban", "sprint", "agile", "scrum"],
        "Real Estate": ["real estate", "property", "listing", "tenant", "landlord", "rental"],
        "Social Media": ["social", "post", "feed", "follow", "like", "comment", "profile"],
        "Support": ["support", "ticket", "helpdesk", "issue", "agent", "customer service"],
        "Inventory": ["inventory", "stock", "warehouse", "supplier", "supply chain"],
        "Hotel": ["hotel", "booking", "room", "reservation", "guest", "hospitality"],
        "Library": ["library", "book", "librarian", "catalog", "borrow"],
    }

    # Feature detection keywords
    FEATURE_KEYWORDS: dict[str, list[str]] = {
        "login": ["login", "sign in", "log in"],
        "signup": ["signup", "sign up", "register", "registration"],
        "dashboard": ["dashboard", "overview", "home page", "main page"],
        "contacts": ["contacts", "contact management", "address book"],
        "role_based_access": ["role-based", "role based", "rbac", "permissions", "access control"],
        "premium_plan": ["premium", "subscription", "paid plan", "pro plan", "pricing"],
        "billing": ["billing", "invoice", "payment", "checkout", "charge"],
        "analytics": ["analytics", "reports", "statistics", "metrics", "charts"],
        "notifications": ["notification", "alert", "email notification", "push"],
        "messaging": ["messaging", "chat", "message", "inbox", "conversation"],
        "search": ["search", "filter", "find", "lookup"],
        "user_management": ["user management", "manage users", "user list"],
        "settings": ["settings", "preferences", "configuration", "config"],
        "profile": ["profile", "account settings", "my account"],
        "file_upload": ["upload", "file upload", "attachment", "media"],
        "export": ["export", "download", "csv", "pdf export"],
        # Domain-specific features
        "appointments": ["appointment", "booking", "schedule", "calendar"],
        "medical_records": ["medical record", "health record", "patient record", "diagnosis"],
        "courses": ["course", "curriculum", "syllabus", "lesson", "module"],
        "enrollment": ["enroll", "enrollment", "registration"],
        "video_streaming": ["video", "streaming", "video player", "media player"],
        "shopping_cart": ["cart", "shopping cart", "basket"],
        "product_listings": ["product", "listing", "catalog", "item"],
        "orders": ["order", "purchase", "checkout"],
        "payroll": ["payroll", "salary", "compensation", "wage"],
        "leave_management": ["leave", "time off", "vacation", "pto"],
        "org_charts": ["org chart", "organization chart", "hierarchy", "reporting structure"],
        "stock_tracking": ["stock", "inventory tracking", "stock level"],
        "supplier_management": ["supplier", "vendor", "procurement"],
        "money_transfer": ["transfer", "money transfer", "send money", "wire"],
        "room_search": ["room", "room search", "room type", "accommodation"],
        "tickets": ["ticket", "raise ticket", "issue", "bug report"],
        "ai_recommendations": ["ai recommendation", "ai ", "machine learning", "recommendation engine"],
        "custom_reporting": ["custom report", "reporting", "report builder"],
    }

    # Role detection keywords
    ROLE_KEYWORDS: dict[str, list[str]] = {
        "admin": ["admin", "administrator", "super admin", "superadmin"],
        "user": ["user", "end user", "regular user"],
        "manager": ["manager", "supervisor", "team lead"],
        "student": ["student", "learner", "pupil"],
        "teacher": ["teacher", "instructor", "professor", "faculty"],
        "doctor": ["doctor", "physician", "specialist", "clinician"],
        "patient": ["patient", "client"],
        "employee": ["employee", "staff", "worker"],
        "customer": ["customer", "buyer", "shopper", "consumer"],
        "agent": ["agent", "support agent", "representative"],
        "librarian": ["librarian", "library staff"],
        "guest": ["guest", "visitor"],
        "vendor": ["vendor", "supplier", "seller", "merchant"],
        "premium_organization": ["premium organization", "premium org", "enterprise"],
        "analyst": ["analyst", "data analyst"],
    }

    def _extract_rule_based(self, prompt: str) -> IntentOutput:
        """Extract intent from a prompt using keyword matching.

        This is the deterministic fallback when the LLM is unavailable.

        Args:
            prompt: The user's natural language application description.

        Returns:
            IntentOutput with extracted domain, features, roles, and access_rules.
        """
        prompt_lower = prompt.lower()

        # 1. Detect domain
        domain = "General"
        best_score = 0
        for d, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            if score > best_score:
                best_score = score
                domain = d

        # 2. Detect features
        features: list[str] = []
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                features.append(feature)

        # If no features detected, infer from domain
        if not features:
            features.append("dashboard")

        # 3. Detect roles
        roles: list[str] = []
        for role, keywords in self.ROLE_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                roles.append(role)

        # Always ensure at least 'user' and 'admin'
        if "admin" not in roles:
            roles.append("admin")
        if not any(r for r in roles if r != "admin"):
            roles.append("user")

        # 4. Detect access rules
        access_rules: list[str] = []
        import re
        # Pattern: "<role> can/cannot/should/must <action>"
        rule_patterns = [
            r"(\w+(?:\s\w+)?)\s+(?:can|should|must)\s+(?:only\s+)?access\s+(.+?)(?:\.|,|$)",
            r"(\w+(?:\s\w+)?)\s+(?:cannot|can't|should not|must not)\s+access\s+(.+?)(?:\.|,|$)",
            r"only\s+(\w+(?:\s\w+)?)\s+(?:can|should)\s+(.+?)(?:\.|,|$)",
        ]
        for pattern in rule_patterns:
            matches = re.findall(pattern, prompt_lower)
            for match in matches:
                access_rules.append(f"{match[0].strip()} -> {match[1].strip()}")

        return IntentOutput(
            domain=domain,
            features=features,
            roles=roles,
            access_rules=access_rules,
        )

    # ──────────────────────────────────────────────
    # LLM-Based Extraction
    # ──────────────────────────────────────────────

    async def _call_ai(self, prompt: str) -> str:
        """Call the Gemini API to extract intent.

        Args:
            prompt: The user's application description.

        Returns:
            Raw response content from the AI model.
        """
        max_retries = 2
        last_error = None

        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}"

        for attempt in range(max_retries + 1):
            try:
                content = ""
                if self.model_provider == "openai":
                    oai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    resp = await oai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    )
                    content = resp.choices[0].message.content
                elif self.model_provider == "claude":
                    anth_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                    resp = await anth_client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        system=SYSTEM_PROMPT,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=4000,
                        temperature=0.1
                    )
                    content = resp.content[0].text
                else:
                    # Gemini default
                    response = self.model.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=4000,
                            response_mime_type="application/json",
                        )
                    )
                    content = response.text

                if not content:
                    raise ValueError("Empty response from AI model")

                logger.debug(f"Raw AI response (attempt {attempt + 1}): {content}")
                return content

            except generation_types.StopCandidateException as e:
                logger.error(f"Generation stopped unexpectedly: {e}")
                raise ValueError("Generation stopped unexpectedly") from e
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt < max_retries:
                        time.sleep(15 * (attempt + 1))  # Slower backoff for Free Tier
                    continue
                else:
                    logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt < max_retries:
                        time.sleep(1)
                    continue

        raise last_error or ValueError("Failed to get response after retries")

    def _parse_response(self, raw_response: str) -> IntentOutput:
        """Parse the AI response into a validated IntentOutput.

        Handles common response issues like markdown fencing, extra whitespace,
        and validates against the Pydantic schema.

        Args:
            raw_response: Raw string response from the AI model.

        Returns:
            Validated IntentOutput instance.

        Raises:
            ValueError: If the response cannot be parsed or validated.
        """
        # Clean up common response artifacts
        cleaned = raw_response.strip()

        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            # Remove opening fence (with optional language tag)
            first_newline = cleaned.index("\n")
            cleaned = cleaned[first_newline + 1:]
            # Remove closing fence
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.error(f"Raw response: {raw_response}")
            raise ValueError(f"AI returned invalid JSON: {e}") from e

        # Validate against Pydantic schema
        try:
            intent = IntentOutput(**data)
        except Exception as e:
            logger.error(f"AI response failed schema validation: {e}")
            logger.error(f"Parsed data: {data}")
            raise ValueError(f"AI response does not match IntentOutput schema: {e}") from e

        return intent
