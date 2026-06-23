"""
Schema Generator — Stage 3 of the Compiler Pipeline.

Takes the system design (ApplicationArchitecture) and generates
concrete schemas including:
- UI Schema (components, pages)
- API Schema (endpoints, methods, bodies)
- Database Schema (tables, columns, types)
- Auth Schema (roles, protected routes)

Uses OpenAI with temperature=0 for deterministic output.
Includes a rule-based fallback if the LLM API is unavailable.
"""

import json
import logging
import time
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import generation_types

from schemas.architecture_schema import ApplicationArchitecture, SchemaGenerationOutput
from schemas.ui_schema import UISchema, UIPage, UIComponent
from schemas.api_schema import APISchema, APIEndpoint
from schemas.db_schema import DatabaseSchema, Table, Column
from schemas.auth_schema import AuthSchema, AuthRole, ProtectedRoute

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# LLM System Prompt
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Schema Generation stage of an AI Application Compiler.
Your job is to convert a high-level application architecture into strict schemas for UI, API, Database, and Auth.

You MUST return ONLY a valid JSON object with this exact structure:
{
  "ui_schema": {
    "pages": [
      {
        "name": "<string>",
        "route": "<string>",
        "layout": "<string>",
        "components": [
          {
            "type": "<string>",
            "name": "<string>",
            "data_source": "<string|null>",
            "action": "<string|null>"
          }
        ],
        "required_api_endpoints": ["<string>"]
      }
    ]
  },
  "api_schema": {
    "endpoints": [
      {
        "path": "<string>",
        "method": "<string>",
        "description": "<string>",
        "request_body": {},
        "response_body": {},
        "auth_required": <bool>,
        "allowed_roles": ["<string>"]
      }
    ]
  },
  "db_schema": {
    "tables": [
      {
        "name": "<string>",
        "columns": [
          {
            "name": "<string>",
            "type": "<string>",
            "required": <bool>,
            "relation": "<string|null>"
          }
        ]
      }
    ]
  },
  "auth_schema": {
    "roles": [
      {
        "name": "<string>",
        "permissions": ["<string>"]
      }
    ],
    "protected_routes": [
      {
        "route": "<string>",
        "allowed_roles": ["<string>"]
      }
    ]
  }
}

Rules:
1. UI Schema: Generate EXACTLY one page for EVERY page defined in the architecture. Do not skip or omit any pages.
2. UI Schema Components: Populate pages with rich components. Use "stat_card", "chart", and "table" for dashboards. Use "table", "form", "button" for management modules. DO NOT just generate a single Home page with a CreateButton.
3. API Schema: For EVERY `required_api_endpoint` specified in the UI schema, you MUST generate a matching endpoint here.
4. Database Schema: Generate a table for every entity. Create standard user tables, roles, and feature-specific tables. Database column types should be general (e.g. string, integer, boolean, uuid, datetime).
5. Auth Schema: Ensure roles match the designed roles. Map the UI routes to protected_routes accurately based on the access rules and role permissions (e.g. restrict doctor pages to doctors, student pages to students, premium analytics to premium organizations).
6. Do NOT include any explanation, markdown, or text outside the JSON object.
7. Do NOT wrap the JSON in code fences or backticks.
8. Return ONLY the raw JSON object.
"""


class SchemaGenerator:
    """Generates concrete schemas from system design.

    Converts an ApplicationArchitecture into UISchema, APISchema,
    DatabaseSchema, and AuthSchema.

    Uses OpenAI with temperature=0 for deterministic results.
    Falls back to rule-based generation if the API is unavailable.
    """

    def __init__(self, api_key: str, model: str = "gemini-pro-latest"):
        """Initialize the SchemaGenerator.

        Args:
            api_key: Gemini API key.
            model: Gemini model to use.
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        logger.info(f"SchemaGenerator initialized with model: {model}")

    async def generate(self, architecture: ApplicationArchitecture) -> tuple[SchemaGenerationOutput, float]:
        """Generate concrete schemas from system architecture.

        Args:
            architecture: Application architecture from Stage 2.

        Returns:
            A tuple of (SchemaGenerationOutput, generation_time_ms).

        Raises:
            ValueError: If generation fails or output is invalid.
        """
        logger.info(f"Starting schema generation for app: {architecture.app_name}")
        start_time = time.perf_counter()

        try:
            if self.model:
                try:
                    architecture_json = architecture.model_dump_json(indent=2)
                    content = await self._call_ai(architecture_json)
                    output = self._parse_response(content)
                    gen_time_ms = (time.perf_counter() - start_time) * 1000

                    logger.info(
                        f"Schema generation completed (LLM) | "
                        f"Time: {gen_time_ms:.2f}ms"
                    )
                    return output, gen_time_ms

                except Exception as e:
                    logger.warning(
                        f"LLM schema generation failed, falling back to rule-based: {e}"
                    )
                    # Fall through to rule-based

            # Rule-based fallback
            output = self._generate_rule_based(architecture)
            gen_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"Schema generation completed (rule-based) | "
                f"Time: {gen_time_ms:.2f}ms"
            )
            return output, gen_time_ms

        except Exception as e:
            gen_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Schema generation failed | "
                f"Error: {str(e)} | "
                f"Time: {gen_time_ms:.2f}ms"
            )
            raise

    # ──────────────────────────────────────────────
    # LLM-Based Generation
    # ──────────────────────────────────────────────

    async def _call_ai(self, architecture_json: str) -> str:
        """Call the Gemini API to generate the full schemas block.

        Args:
            architecture_json: The serialized architecture payload.

        Returns:
            Raw response content from the AI model.
        """
        max_retries = 2
        last_error = None

        full_prompt = f"{SYSTEM_PROMPT}\n\nArchitecture Payload: {architecture_json}"

        for attempt in range(max_retries + 1):
            try:
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

    def _parse_response(self, raw_response: str) -> SchemaGenerationOutput:
        """Parse the LLM response into a validated SchemaGenerationOutput.

        Args:
            raw_response: Raw string response from the AI model.

        Returns:
            Validated SchemaGenerationOutput instance.

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
            # Build models
            ui_schema = UISchema(**data.get("ui_schema", {"pages": []}))
            api_schema = APISchema(**data.get("api_schema", {"endpoints": []}))
            db_schema = DatabaseSchema(**data.get("db_schema", {"tables": []}))
            auth_schema = AuthSchema(**data.get("auth_schema", {"roles": [], "protected_routes": []}))

            return SchemaGenerationOutput(
                ui_schema=ui_schema,
                api_schema=api_schema,
                db_schema=db_schema,
                auth_schema=auth_schema
            )
        except Exception as e:
            logger.error(f"LLM response failed schema validation: {e}")
            raise ValueError(
                f"LLM response does not match expected schema structures: {e}"
            ) from e

    # ──────────────────────────────────────────────
    # Rule-Based Fallback Generation
    # ──────────────────────────────────────────────

    def _generate_rule_based(self, architecture: ApplicationArchitecture) -> SchemaGenerationOutput:
        """Generate schemas using deterministic rule-based logic.

        Args:
            architecture: ApplicationArchitecture to map to schemas.

        Returns:
            SchemaGenerationOutput generated from deterministic rules.
        """
        logger.info("Using rule-based schema generation fallback")

        # Extract useful data
        all_roles = [r.name for r in architecture.roles]
        
        db_schema = self._generate_db_schema(architecture)
        api_schema = self._generate_api_schema(architecture, all_roles)
        ui_schema = self._generate_ui_schema(architecture)
        auth_schema = self._generate_auth_schema(architecture)

        return SchemaGenerationOutput(
            ui_schema=ui_schema,
            api_schema=api_schema,
            db_schema=db_schema,
            auth_schema=auth_schema
        )

    def _generate_db_schema(self, architecture: ApplicationArchitecture) -> DatabaseSchema:
        tables = []
        for entity in architecture.entities:
            table_name = entity.name.lower() + "s"  # pluralize
            columns = [
                Column(name="id", type="uuid", required=True),
                Column(name="created_at", type="datetime", required=True),
                Column(name="updated_at", type="datetime", required=True)
            ]
            
            if entity.name.lower() == "user":
                columns.extend([
                    Column(name="email", type="string", required=True),
                    Column(name="password_hash", type="string", required=True),
                    Column(name="role", type="string", required=True)
                ])
            else:
                columns.extend([
                    Column(name="name", type="string", required=True),
                    Column(name="description", type="string", required=False)
                ])
                
            tables.append(Table(name=table_name, columns=columns))
            
        return DatabaseSchema(tables=tables)

    def _generate_api_schema(self, architecture: ApplicationArchitecture, all_roles: list[str]) -> APISchema:
        endpoints = []
        for entity in architecture.entities:
            base_path = f"/api/{entity.name.lower()}s"
            
            # GET all
            endpoints.append(APIEndpoint(
                path=base_path,
                method="GET",
                description=f"Fetch all {entity.name}s",
                response_body={f"{entity.name.lower()}s": "array"},
                auth_required=True,
                allowed_roles=all_roles
            ))
            
            # GET one
            endpoints.append(APIEndpoint(
                path=f"{base_path}/{{id}}",
                method="GET",
                description=f"Fetch a specific {entity.name}",
                response_body={entity.name.lower(): "object"},
                auth_required=True,
                allowed_roles=all_roles
            ))
            
            # POST
            endpoints.append(APIEndpoint(
                path=base_path,
                method="POST",
                description=f"Create a new {entity.name}",
                request_body={entity.name.lower(): "object"},
                response_body={entity.name.lower(): "object"},
                auth_required=True,
                allowed_roles=["admin"] if "admin" in all_roles else all_roles
            ))
            
            # DELETE
            endpoints.append(APIEndpoint(
                path=f"{base_path}/{{id}}",
                method="DELETE",
                description=f"Delete a {entity.name}",
                response_body={"success": "boolean"},
                auth_required=True,
                allowed_roles=["admin"] if "admin" in all_roles else all_roles
            ))

        # Add auth endpoints if User entity exists
        if any(e.name.lower() == "user" for e in architecture.entities):
            endpoints.append(APIEndpoint(
                path="/api/auth/login",
                method="POST",
                description="Authenticate user and return token",
                request_body={"email": "string", "password": "string"},
                response_body={"token": "string"},
                auth_required=False,
                allowed_roles=[]
            ))
            endpoints.append(APIEndpoint(
                path="/api/auth/register",
                method="POST",
                description="Register a new user",
                request_body={"email": "string", "password": "string"},
                response_body={"token": "string"},
                auth_required=False,
                allowed_roles=[]
            ))

        return APISchema(endpoints=endpoints)

    def _generate_ui_schema(self, architecture: ApplicationArchitecture) -> UISchema:
        pages = []
        for page in architecture.pages:
            components = []
            req_endpoints = []
            layout = "dashboard"
            
            if "login" in page.route or "register" in page.route or "auth" in page.route:
                layout = "auth"
                components.append(UIComponent(
                    type="form",
                    name="AuthForm",
                    action="submit_credentials"
                ))
                req_endpoints.append(f"/api{page.route}")
            else:
                base_entity = page.route.split("/")[-1]
                if base_entity:
                    components.append(UIComponent(
                        type="table",
                        name=f"{base_entity.title()}Table",
                        data_source=f"/api/{base_entity}"
                    ))
                    req_endpoints.append(f"/api/{base_entity}")
                    
                components.append(UIComponent(
                    type="button",
                    name="CreateButton",
                    action=f"open_create_modal"
                ))
            
            pages.append(UIPage(
                name=page.name,
                route=page.route,
                layout=layout,
                components=components,
                required_api_endpoints=req_endpoints
            ))
            
        return UISchema(pages=pages)

    def _generate_auth_schema(self, architecture: ApplicationArchitecture) -> AuthSchema:
        roles = []
        for r in architecture.roles:
            roles.append(AuthRole(
                name=r.name,
                permissions=r.permissions
            ))
            
        protected_routes = []
        all_roles = [r.name for r in architecture.roles]
        admin_roles = [r for r in all_roles if "admin" in r] or all_roles
        
        for p in architecture.pages:
            if p.route not in ["/login", "/register", "/auth"]:
                # If page is for management/admin stuff
                if any(x in p.route for x in ["settings", "users", "billing"]):
                    allowed = admin_roles
                else:
                    allowed = all_roles
                    
                protected_routes.append(ProtectedRoute(
                    route=f"{p.route}/*" if p.route == "/" else f"{p.route}",
                    allowed_roles=allowed
                ))
                
        return AuthSchema(roles=roles, protected_routes=protected_routes)
