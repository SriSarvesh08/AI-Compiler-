"""
Database Schema — Pydantic models for the Database Design stage.

Defines models for database specifications including:
- Tables/collections with columns and types
- Required constraints
- Relationships
"""

from pydantic import BaseModel, Field


class Column(BaseModel):
    """A column definition within a database table."""
    name: str = Field(..., description="Column name in snake_case")
    type: str = Field(..., description="Data type (e.g., 'uuid', 'string', 'integer')")
    required: bool = Field(default=False, description="Whether the column is required (NOT NULL)")
    relation: str | None = Field(None, description="Foreign key relation (e.g., 'users.id')")


class Table(BaseModel):
    """A database table specification."""
    name: str = Field(..., description="Table name in snake_case, plural")
    columns: list[Column] = Field(..., description="List of columns in the table")


class DatabaseSchema(BaseModel):
    """Complete database schema generated from architecture."""
    tables: list[Table] = Field(..., description="List of all database tables")
