from pydantic import BaseModel

class RevitInput(BaseModel):
    """Shape of the input coming from Revit plugin"""
    host_element: str      # e.g., "Retaining Wall", "Core-Shaft"
    adjacent_element: str  # e.g., "Foundation", "Soffit"
    exposure: str          # e.g., "Exterior", "Interior"

class SearchResult(BaseModel):
    """Shape of the response to the user"""
    suggested_detail: str
    confidence: float
    reason: str

class DetailUpload(BaseModel):
    """Shape for adding new knowledge"""
    detail_name: str