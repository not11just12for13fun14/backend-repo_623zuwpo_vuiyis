"""
Database Schemas for the Legal Document Generator

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., LegalTemplate -> "legaltemplate").
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    label: str
    value: str


class Question(BaseModel):
    key: str = Field(..., description="Unique key used in the template placeholders, e.g., {{full_name}} -> key='full_name'")
    label: str = Field(..., description="Question label shown to the user")
    help: Optional[str] = Field(None, description="Helper text to guide the user")
    type: Literal["text", "textarea", "number", "date", "select", "multiselect", "email", "phone"] = "text"
    required: bool = True
    placeholder: Optional[str] = None
    options: Optional[List[QuestionOption]] = None


class LegalTemplate(BaseModel):
    key: str = Field(..., description="Stable identifier for the template, e.g., 'affidavit_of_loss'")
    title: str = Field(..., description="Human-friendly title")
    description: Optional[str] = None
    category: str = Field("General", description="Template category")
    jurisdiction: str = Field("Republic of the Philippines", description="Jurisdiction footer/header text")
    requires_notarization: bool = Field(True, description="Whether the document typically requires notarization")
    questions: List[Question]
    content: str = Field(..., description="Template body with {{placeholders}} to be replaced by answers")
    acknowledgement: Optional[str] = Field(None, description="Optional notarial acknowledgement section with placeholders")


class GeneratedDocument(BaseModel):
    template_key: str
    answers: Dict[str, Any]
    rendered_text: str
    rendered_html: Optional[str] = None
    title: str

