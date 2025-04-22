"""
MS Learn course data models
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ModuleUnit(BaseModel):
    """Individual unit within a module"""
    title: str = Field(..., description="Title of the unit")
    duration: str = Field(..., description="Duration of the unit")
    url: Optional[str] = Field(None, description="URL of the unit if available")

class Module(BaseModel):
    """Course module"""
    title: str = Field(..., description="Title of the module")
    description: str = Field(..., description="Module description")
    duration: str = Field(..., description="Total duration of the module")
    units: List[ModuleUnit] = Field(default_factory=list, description="List of units in this module")
    url: str = Field(..., description="URL of the module")

class Course(BaseModel):
    """MS Learn course structure"""
    code: str = Field(..., description="Course code (e.g., SC-300)")
    title: str = Field(..., description="Full course title")
    description: str = Field(..., description="Course description")
    level: str = Field(..., description="Course difficulty level")
    prerequisites: List[str] = Field(default_factory=list, description="Course prerequisites")
    modules: List[Module] = Field(default_factory=list, description="Course modules")
    metadata: dict = Field(default_factory=dict, description="Additional course metadata") 