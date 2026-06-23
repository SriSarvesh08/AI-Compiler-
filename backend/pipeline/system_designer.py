"""
System Designer — Stage 2 of the Compiler Pipeline.

Takes the extracted intent (domain, features, roles) and generates
a structured application architecture including entities, pages,
flows, role permissions, and design assumptions.

Uses OpenAI with temperature=0 for deterministic output.
Includes a rule-based fallback if the LLM API is unavailable.
"""

import json
import logging
import time
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import generation_types

from schemas.intent_schema import IntentOutput
from schemas.architecture_schema import (
    ApplicationArchitecture,
    Entity,
    Page,
    Flow,
    RolePermission,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# LLM System Prompt
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """You are the System Design stage of an AI Application Compiler.
Your job is to convert a structured intent (domain, features, roles, access_rules) into a complete application architecture.

You MUST return ONLY a valid JSON object with this exact structure:
{
  "app_name": "<string: Human-readable application name>",
  "entities": [
    {
      "name": "<string: PascalCase entity name>",
      "description": "<string: What this entity stores>"
    }
  ],
  "pages": [
    {
      "name": "<string: Human-readable page name>",
      "route": "<string: URL route like /login>",
      "purpose": "<string: What this page does>"
    }
  ],
  "flows": [
    {
      "name": "<string: Flow name>",
      "steps": ["<string: step 1>", "<string: step 2>", ...]
    }
  ],
  "roles": [
    {
      "name": "<string: lowercase role name>",
      "permissions": ["<string: permission in snake_case>", ...]
    }
  ],
  "assumptions": ["<string: design assumption>", ...]
}

Rules:
1. Generate entities based on ALL features. Complex apps must have multiple entities (e.g., User, Student, Patient, Employee, Record, Report).
2. Generate pages for EVERY feature that requires a UI screen.
   - Each dashboard feature must become a separate page (e.g., Student Dashboard, Patient Dashboard, Employee Dashboard).
   - Each management module must become a separate page (e.g., Employee Management, Role Management).
   - Analytics, reporting, and premium features must become their own distinct protected pages.
   - You MUST generate a comprehensive set of pages, not just Home.
3. Generate user flows that describe end-to-end workflows (3-5 steps each).
4. For each role extracted in the intent, generate appropriate permissions using snake_case (e.g., "view_patient_records", "manage_employees").
5. Carefully incorporate any access_rules provided in the intent. For example, if a role "cannot access patient data", do NOT give them patient permissions.
6. Admin roles should have superset permissions. Regular user roles should have limited permissions.
7. Do NOT include any explanation, markdown, or text outside the JSON object.
8. Do NOT wrap the JSON in code fences or backticks.
9. Return ONLY the raw JSON object.
"""


# ──────────────────────────────────────────────
# Feature → Domain Knowledge Mappings
# ──────────────────────────────────────────────

# Maps common feature keywords to entity templates for rule-based fallback
FEATURE_ENTITY_MAP: dict[str, list[dict[str, str]]] = {
    "login": [{"name": "User", "description": "Stores user account and authentication information"}],
    "auth": [{"name": "User", "description": "Stores user account and authentication information"}],
    "authentication": [{"name": "User", "description": "Stores user account and authentication information"}],
    "signup": [{"name": "User", "description": "Stores user account and authentication information"}],
    "register": [{"name": "User", "description": "Stores user account and authentication information"}],
    "contacts": [{"name": "Contact", "description": "Stores contact details and information"}],
    "contact_management": [{"name": "Contact", "description": "Stores contact details and information"}],
    "dashboard": [],
    "analytics": [{"name": "AnalyticsEvent", "description": "Stores analytics events and metrics"}],
    "role_based_access": [{"name": "Role", "description": "Stores role definitions and access control rules"}],
    "rbac": [{"name": "Role", "description": "Stores role definitions and access control rules"}],
    "premium_plan": [{"name": "Subscription", "description": "Stores premium plan and payment status"}],
    "billing": [{"name": "Subscription", "description": "Stores premium plan and payment status"}],
    "payment": [{"name": "Payment", "description": "Stores payment transactions and billing history"}],
    "products": [{"name": "Product", "description": "Stores product catalog information"}],
    "product_catalog": [{"name": "Product", "description": "Stores product catalog information"}],
    "orders": [{"name": "Order", "description": "Stores customer orders and order items"}],
    "cart": [{"name": "Cart", "description": "Stores shopping cart items per user session"}],
    "courses": [{"name": "Course", "description": "Stores course content and metadata"}],
    "lessons": [{"name": "Lesson", "description": "Stores individual lesson content within courses"}],
    "enrollment": [{"name": "Enrollment", "description": "Tracks user enrollment in courses"}],
    "assignments": [{"name": "Assignment", "description": "Stores assignment details and submissions"}],
    "messages": [{"name": "Message", "description": "Stores user messages and conversations"}],
    "chat": [{"name": "Message", "description": "Stores chat messages between users"}],
    "notifications": [{"name": "Notification", "description": "Stores user notifications and alerts"}],
    "posts": [{"name": "Post", "description": "Stores user-created posts and content"}],
    "comments": [{"name": "Comment", "description": "Stores comments on posts or content"}],
    "profiles": [{"name": "Profile", "description": "Stores user profile information"}],
    "settings": [],
    "search": [],
    "reports": [{"name": "Report", "description": "Stores generated reports and report configurations"}],
    "inventory": [{"name": "InventoryItem", "description": "Tracks inventory stock levels and items"}],
    "tasks": [{"name": "Task", "description": "Stores task details, assignments, and status"}],
    "projects": [{"name": "Project", "description": "Stores project information and team assignments"}],
    "calendar": [{"name": "Event", "description": "Stores calendar events and schedules"}],
    "files": [{"name": "File", "description": "Stores uploaded file metadata and references"}],
    "uploads": [{"name": "File", "description": "Stores uploaded file metadata and references"}],
}

# Maps features to page templates
FEATURE_PAGE_MAP: dict[str, dict[str, str]] = {
    "login": {"name": "Login", "route": "/login", "purpose": "Allow users to sign in"},
    "auth": {"name": "Login", "route": "/login", "purpose": "Allow users to sign in"},
    "authentication": {"name": "Login", "route": "/login", "purpose": "Allow users to sign in"},
    "signup": {"name": "Register", "route": "/register", "purpose": "Allow new users to create an account"},
    "register": {"name": "Register", "route": "/register", "purpose": "Allow new users to create an account"},
    "dashboard": {"name": "Dashboard", "route": "/dashboard", "purpose": "Show overview and analytics"},
    "contacts": {"name": "Contacts", "route": "/contacts", "purpose": "Manage customer contacts"},
    "contact_management": {"name": "Contacts", "route": "/contacts", "purpose": "Manage customer contacts"},
    "analytics": {"name": "Analytics", "route": "/analytics", "purpose": "View detailed analytics and reports"},
    "role_based_access": {"name": "User Management", "route": "/users", "purpose": "Manage users and role assignments"},
    "rbac": {"name": "User Management", "route": "/users", "purpose": "Manage users and role assignments"},
    "premium_plan": {"name": "Billing", "route": "/billing", "purpose": "Manage premium plans and payments"},
    "billing": {"name": "Billing", "route": "/billing", "purpose": "Manage billing and payments"},
    "payment": {"name": "Payments", "route": "/payments", "purpose": "Process and view payment history"},
    "products": {"name": "Products", "route": "/products", "purpose": "Browse and manage products"},
    "product_catalog": {"name": "Products", "route": "/products", "purpose": "Browse and manage product catalog"},
    "orders": {"name": "Orders", "route": "/orders", "purpose": "View and manage customer orders"},
    "cart": {"name": "Cart", "route": "/cart", "purpose": "Review and checkout shopping cart"},
    "courses": {"name": "Courses", "route": "/courses", "purpose": "Browse and manage courses"},
    "lessons": {"name": "Lessons", "route": "/lessons", "purpose": "View and manage lesson content"},
    "enrollment": {"name": "Enrollment", "route": "/enrollment", "purpose": "Manage course enrollments"},
    "assignments": {"name": "Assignments", "route": "/assignments", "purpose": "View and submit assignments"},
    "messages": {"name": "Messages", "route": "/messages", "purpose": "Send and receive messages"},
    "chat": {"name": "Chat", "route": "/chat", "purpose": "Real-time messaging between users"},
    "notifications": {"name": "Notifications", "route": "/notifications", "purpose": "View and manage notifications"},
    "posts": {"name": "Feed", "route": "/feed", "purpose": "View and create posts"},
    "comments": {"name": "Feed", "route": "/feed", "purpose": "View and create posts with comments"},
    "profiles": {"name": "Profile", "route": "/profile", "purpose": "View and edit user profile"},
    "settings": {"name": "Settings", "route": "/settings", "purpose": "Configure application settings"},
    "search": {"name": "Search", "route": "/search", "purpose": "Search across application content"},
    "reports": {"name": "Reports", "route": "/reports", "purpose": "Generate and view reports"},
    "inventory": {"name": "Inventory", "route": "/inventory", "purpose": "Track and manage inventory"},
    "tasks": {"name": "Tasks", "route": "/tasks", "purpose": "Create and manage tasks"},
    "projects": {"name": "Projects", "route": "/projects", "purpose": "Manage projects and teams"},
    "calendar": {"name": "Calendar", "route": "/calendar", "purpose": "View and manage events"},
    "files": {"name": "Files", "route": "/files", "purpose": "Upload and manage files"},
    "uploads": {"name": "Files", "route": "/files", "purpose": "Upload and manage files"},
}

# Default admin permissions by domain
DEFAULT_ADMIN_PERMISSIONS = [
    "view_dashboard",
    "manage_users",
    "manage_settings",
    "view_analytics",
]

# Default user permissions
DEFAULT_USER_PERMISSIONS = [
    "view_dashboard",
]


class SystemDesigner:
    """Designs application architecture from extracted intent.

    Converts intent (domain, features, roles) into a structured
    ApplicationArchitecture with entities, pages, flows, role permissions,
    and design assumptions.

    Uses OpenAI with temperature=0 for deterministic results.
    Falls back to rule-based generation if the API is unavailable.
    """

    def __init__(self, api_key: str, model: str = "gemini-pro-latest"):
        """Initialize the SystemDesigner.

        Args:
            api_key: Gemini API key.
            model: Gemini model to use for design generation.
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        logger.info(f"SystemDesigner initialized with model: {model}")

    async def design(self, intent: IntentOutput) -> tuple[ApplicationArchitecture, float]:
        """Generate application architecture from structured intent.

        Args:
            intent: Structured intent with domain, features, and roles.

        Returns:
            A tuple of (ApplicationArchitecture, design_time_ms).

        Raises:
            ValueError: If the intent is invalid or the response cannot be parsed.
        """
        logger.info(
            f"Starting system design | "
            f"Domain: {intent.domain} | "
            f"Features: {intent.features} | "
            f"Roles: {intent.roles}"
        )
        start_time = time.perf_counter()

        # Validate input
        self._validate_intent(intent)

        try:
            # Try LLM-based design first
            try:
                intent_json = json.dumps({
                    "domain": intent.domain,
                    "features": intent.features,
                    "roles": intent.roles,
                    "access_rules": intent.access_rules
                })
                raw_response = await self._call_ai(intent_json)
                architecture = self._parse_response(raw_response)
                design_time_ms = (time.perf_counter() - start_time) * 1000

                logger.info(
                    f"System design completed (LLM) | "
                    f"App: {architecture.app_name} | "
                    f"Entities: {len(architecture.entities)} | "
                    f"Pages: {len(architecture.pages)} | "
                    f"Flows: {len(architecture.flows)} | "
                    f"Roles: {len(architecture.roles)} | "
                    f"Time: {design_time_ms:.2f}ms"
                )
                self._log_assumptions(architecture.assumptions)
                return architecture, design_time_ms

            except Exception as e:
                logger.warning(
                    f"LLM design failed, falling back to rule-based: {e}"
                )
                # Fall through to rule-based

            # Rule-based fallback
            architecture = self._design_rule_based(intent)
            design_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"System design completed (rule-based) | "
                f"App: {architecture.app_name} | "
                f"Entities: {len(architecture.entities)} | "
                f"Pages: {len(architecture.pages)} | "
                f"Flows: {len(architecture.flows)} | "
                f"Roles: {len(architecture.roles)} | "
                f"Time: {design_time_ms:.2f}ms"
            )
            self._log_assumptions(architecture.assumptions)
            return architecture, design_time_ms

        except Exception as e:
            design_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"System design failed | "
                f"Error: {str(e)} | "
                f"Time: {design_time_ms:.2f}ms"
            )
            raise

    # ──────────────────────────────────────────────
    # Input Validation
    # ──────────────────────────────────────────────

    def _validate_intent(self, intent: IntentOutput) -> None:
        """Validate the intent input before processing.

        Args:
            intent: Intent to validate.

        Raises:
            ValueError: If the intent is invalid.
        """
        if not intent.domain or not intent.domain.strip():
            raise ValueError("Intent is missing a domain. Cannot design architecture without a domain.")

        if not intent.features or len(intent.features) == 0:
            raise ValueError("Intent has no features. At least one feature is required for system design.")

        if not intent.roles or len(intent.roles) == 0:
            raise ValueError("Intent has no roles. At least one user role is required for system design.")

        # Validate role format (should be lowercase strings)
        for role in intent.roles:
            if not role or not role.strip():
                raise ValueError(f"Invalid role format: empty role name detected.")
            if role != role.lower().replace(" ", "_"):
                logger.warning(
                    f"Role '{role}' is not in lowercase snake_case format. "
                    f"Normalizing to '{role.lower().replace(' ', '_')}'."
                )

        logger.info("Intent validation passed")

    # ──────────────────────────────────────────────
    # LLM-Based Design
    # ──────────────────────────────────────────────

    async def _call_ai(self, intent_json: str) -> str:
        """Call the Gemini API to generate system design.

        Args:
            intent_json: The serialized intent payload.

        Returns:
            Raw response content from the AI model.
        """
        max_retries = 2
        last_error = None

        full_prompt = f"{SYSTEM_PROMPT}\n\nIntent Payload: {intent_json}"

        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=3000,
                        response_mime_type="application/json",
                    )
                )

                content = response.text
                if not content:
                    raise ValueError("Empty response from AI model")


                logger.debug(f"Raw AI response (attempt {attempt + 1}): {content[:200]}...")
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

    def _parse_response(self, raw_response: str) -> ApplicationArchitecture:
        """Parse the LLM response into a validated ApplicationArchitecture.

        Args:
            raw_response: Raw string response from the AI model.

        Returns:
            Validated ApplicationArchitecture instance.

        Raises:
            ValueError: If the response cannot be parsed or validated.
        """
        cleaned = raw_response.strip()

        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            first_newline = cleaned.index("\n")
            cleaned = cleaned[first_newline + 1:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Raw response: {raw_response}")
            raise ValueError(f"LLM returned invalid JSON: {e}") from e

        try:
            architecture = ApplicationArchitecture(**data)
        except Exception as e:
            logger.error(f"LLM response failed schema validation: {e}")
            logger.error(f"Parsed data: {data}")
            raise ValueError(
                f"LLM response does not match ApplicationArchitecture schema: {e}"
            ) from e

        return architecture

    # ──────────────────────────────────────────────
    # Rule-Based Fallback Design
    # ──────────────────────────────────────────────

    def _design_rule_based(self, intent: IntentOutput) -> ApplicationArchitecture:
        """Generate architecture using deterministic rule-based logic.

        This is the fallback when the LLM is unavailable. It uses
        feature-to-entity and feature-to-page mappings to build
        a consistent architecture.

        Args:
            intent: Structured intent from extraction stage.

        Returns:
            ApplicationArchitecture generated from rules.
        """
        logger.info("Using rule-based design fallback")

        domain = intent.domain.strip()
        features = [f.lower().strip() for f in intent.features]
        roles = [r.lower().strip().replace(" ", "_") for r in intent.roles]

        # 1. Generate app name
        app_name = self._generate_app_name(domain)

        # 2. Generate entities
        entities = self._generate_entities(features)

        # 3. Generate pages
        pages = self._generate_pages(features, domain)

        # 4. Generate flows
        flows = self._generate_flows(features, domain)

        # 5. Generate role permissions
        role_permissions = self._generate_role_permissions(roles, features, pages)

        # 6. Generate assumptions
        assumptions = self._generate_assumptions(features, domain)

        return ApplicationArchitecture(
            app_name=app_name,
            entities=entities,
            pages=pages,
            flows=flows,
            roles=role_permissions,
            assumptions=assumptions,
        )

    def _generate_app_name(self, domain: str) -> str:
        """Generate a human-readable app name from the domain."""
        # Clean up domain and make it title case
        cleaned = domain.replace("_", " ").replace("-", " ").strip()
        return f"{cleaned.title()} Management System"

    def _generate_entities(self, features: list[str]) -> list[Entity]:
        """Generate entities from feature list using mappings."""
        seen_names: set[str] = set()
        entities: list[Entity] = []

        # Always include User entity if any auth-related feature exists
        auth_features = {"login", "auth", "authentication", "signup", "register", "role_based_access", "rbac"}
        if auth_features.intersection(features):
            entities.append(Entity(
                name="User",
                description="Stores user account and authentication information",
            ))
            seen_names.add("User")

        for feature in features:
            mapped = FEATURE_ENTITY_MAP.get(feature, [])
            for entity_data in mapped:
                if entity_data["name"] not in seen_names:
                    entities.append(Entity(**entity_data))
                    seen_names.add(entity_data["name"])

        # If no entities were generated, create a generic one
        if not entities:
            entities.append(Entity(
                name="Record",
                description="Stores primary application data records",
            ))

        return entities

    def _generate_pages(self, features: list[str], domain: str) -> list[Page]:
        """Generate pages from feature list using mappings."""
        seen_routes: set[str] = set()
        pages: list[Page] = []

        for feature in features:
            mapped = FEATURE_PAGE_MAP.get(feature)
            if mapped and mapped["route"] not in seen_routes:
                pages.append(Page(**mapped))
                seen_routes.add(mapped["route"])
            else:
                # Dynamic fallback for unmapped features
                route = f"/{feature.replace('_', '-')}"
                if route not in seen_routes:
                    pages.append(Page(
                        name=feature.replace("_", " ").title(),
                        route=route,
                        purpose=f"Manage {feature.replace('_', ' ')} module"
                    ))
                    seen_routes.add(route)

        # Ensure dashboard exists if not already
        if "/dashboard" not in seen_routes and "dashboard" in features:
            pages.insert(0, Page(
                name="Dashboard",
                route="/dashboard",
                purpose=f"Show {domain} overview and analytics",
            ))

        # If no pages generated, create a generic home page
        if not pages:
            pages.append(Page(
                name="Home",
                route="/",
                purpose=f"Main {domain} application page",
            ))

        return pages

    def _generate_flows(self, features: list[str], domain: str) -> list[Flow]:
        """Generate user flows from features."""
        flows: list[Flow] = []

        # Auth flow
        auth_features = {"login", "auth", "authentication"}
        if auth_features.intersection(features):
            flows.append(Flow(
                name="User Login Flow",
                steps=[
                    "User enters email and password",
                    "System validates credentials",
                    "System redirects user based on role",
                ],
            ))

        # Registration flow
        reg_features = {"signup", "register"}
        if reg_features.intersection(features):
            flows.append(Flow(
                name="User Registration Flow",
                steps=[
                    "User fills in registration form",
                    "System validates input and checks for duplicates",
                    "System creates user account",
                    "User is redirected to login page",
                ],
            ))

        # Contact management flow
        contact_features = {"contacts", "contact_management"}
        if contact_features.intersection(features):
            flows.append(Flow(
                name="Contact Management Flow",
                steps=[
                    "User opens Contacts page",
                    "User creates or edits contact",
                    "System saves contact data",
                ],
            ))

        # Order flow
        order_features = {"orders", "cart"}
        if order_features.intersection(features):
            flows.append(Flow(
                name="Order Processing Flow",
                steps=[
                    "User adds items to cart",
                    "User proceeds to checkout",
                    "System processes payment",
                    "System confirms order and sends notification",
                ],
            ))

        # Course enrollment flow
        course_features = {"courses", "enrollment"}
        if course_features.intersection(features):
            flows.append(Flow(
                name="Course Enrollment Flow",
                steps=[
                    "User browses available courses",
                    "User selects a course and enrolls",
                    "System confirms enrollment",
                    "User accesses course content",
                ],
            ))

        # Billing / premium flow
        billing_features = {"premium_plan", "billing", "payment"}
        if billing_features.intersection(features):
            flows.append(Flow(
                name="Subscription Management Flow",
                steps=[
                    "User navigates to billing page",
                    "User selects a plan",
                    "System processes payment",
                    "System activates premium features",
                ],
            ))

        # Task management flow
        task_features = {"tasks", "projects"}
        if task_features.intersection(features):
            flows.append(Flow(
                name="Task Management Flow",
                steps=[
                    "User creates a new task",
                    "User assigns task to team member",
                    "Team member updates task status",
                    "System notifies relevant users",
                ],
            ))

        # Messaging flow
        msg_features = {"messages", "chat"}
        if msg_features.intersection(features):
            flows.append(Flow(
                name="Messaging Flow",
                steps=[
                    "User opens messaging interface",
                    "User composes and sends a message",
                    "Recipient receives notification",
                    "Recipient reads and responds",
                ],
            ))

        # Generic data management flow if nothing else matched
        if not flows:
            flows.append(Flow(
                name=f"{domain} Data Management Flow",
                steps=[
                    "User navigates to main page",
                    "User creates or updates a record",
                    "System validates and saves data",
                    "System displays updated information",
                ],
            ))

        return flows

    def _generate_role_permissions(
        self,
        roles: list[str],
        features: list[str],
        pages: list[Page],
    ) -> list[RolePermission]:
        """Generate role-based permissions."""
        role_permissions: list[RolePermission] = []

        # Build feature-based permissions
        feature_permissions: dict[str, list[str]] = {}
        for feature in features:
            base = feature.lower().replace(" ", "_")
            feature_permissions[feature] = [
                f"view_{base}",
                f"manage_{base}",
            ]

        # Page-based view permissions
        page_view_perms = [f"view_{p.name.lower().replace(' ', '_')}" for p in pages]

        for role in roles:
            normalized_role = role.lower().replace(" ", "_")

            if normalized_role in ("admin", "administrator", "super_admin", "superadmin"):
                # Admin gets everything
                all_perms: set[str] = set(DEFAULT_ADMIN_PERMISSIONS)
                all_perms.update(page_view_perms)
                for perms in feature_permissions.values():
                    all_perms.update(perms)
                role_permissions.append(RolePermission(
                    name=normalized_role,
                    permissions=sorted(all_perms),
                ))
            else:
                # Regular roles get view-only + limited create
                user_perms: set[str] = set(DEFAULT_USER_PERMISSIONS)
                user_perms.update(page_view_perms)
                # Add create permissions for data features
                for feature in features:
                    base = feature.lower().replace(" ", "_")
                    if feature in ("contacts", "contact_management", "posts", "messages",
                                   "chat", "tasks", "orders", "comments"):
                        user_perms.add(f"create_{base}")
                role_permissions.append(RolePermission(
                    name=normalized_role,
                    permissions=sorted(user_perms),
                ))

        return role_permissions

    def _generate_assumptions(self, features: list[str], domain: str) -> list[str]:
        """Generate design assumptions based on features and domain."""
        assumptions: list[str] = []

        auth_features = {"login", "auth", "authentication", "signup", "register"}
        if auth_features.intersection(features):
            assumptions.append("Email and password authentication is used by default")

        rbac_features = {"role_based_access", "rbac"}
        if rbac_features.intersection(features):
            assumptions.append("Admin role has full access to all resources")
            assumptions.append("Role-based access control is enforced on all protected routes")

        billing_features = {"premium_plan", "billing", "payment"}
        if billing_features.intersection(features):
            assumptions.append("Premium plan is handled through a billing page")
            assumptions.append("Payment processing uses a third-party payment gateway")

        if "dashboard" in features:
            assumptions.append("Dashboard aggregates data from all major entities")

        # Always add some generic assumptions
        assumptions.append(f"Application follows a standard {domain} domain model")
        assumptions.append("RESTful API design is used for backend services")

        return assumptions

    # ──────────────────────────────────────────────
    # Logging Helpers
    # ──────────────────────────────────────────────

    def _log_assumptions(self, assumptions: list[str]) -> None:
        """Log all design assumptions made."""
        for assumption in assumptions:
            logger.info(f"  Assumption: {assumption}")
