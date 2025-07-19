from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from edgar.company_reports import TenK
from edgar.company_reports import FilingStructure
from typing_extensions import TypedDict, NotRequired, List

# Define classes 
class PeerInfo(TypedDict):
    name: str # as per ticker
    ticker: str

class ClientMemory(TypedDict): 
    cik: str
    name: str #as per ticker
    tickers: str
    peers: NotRequired[List[PeerInfo]]


class KeyValuePair(BaseModel):
    key: str = Field(..., description="Name of the metric or fact")
    value: str = Field(..., description="Value associated with the key")

class FilingItemSummary(BaseModel):
    item_code: str = Field(..., description="Filing section code like 'ITEM 1A'")
    title: str = Field(..., description="Title of the filing section, e.g., 'Business' or 'Risk Factors'")
    description: str = Field(..., description="High-level description of what this item covers")
    summary: Optional[str] = Field(None, description="Summary of the item extracted from the filing")
    key_values: List[KeyValuePair] = Field(default_factory=list)

    @field_validator("item_code")
    def validate_item_code(cls, v):
        allowed_items = get_tenk_items()
        if v not in allowed_items:
            raise ValueError(f"Invalid item_code: {v}. Must be one of: {allowed_items}")
        return v

class FilingSummary(BaseModel):
    ticker: str
    filingdate: str 
    form: str
    filingitemsummaries: List[FilingItemSummary]

class FilingChunks(BaseModel):
    ticker: str
    filingdate: str 
    form: str
    item_code: str
    chunk: str 
    embedding: List[float]

class LLMGeneratedFilingItemSummary(BaseModel):
    summary: Optional[str]
    key_values: List[KeyValuePair] = Field(default_factory=list)

class InferredItemCodes(BaseModel):
    item_codes: List[str] = Field(..., description="List of relevant 10-K item codes like ['ITEM 1A', 'ITEM 7A']")

def get_tenk_items():
    all_items = []
    #print(dir(TenK.structure))  
    all_items = []
    for part_dict in TenK.structure.structure.values():
        all_items.extend(part_dict.keys())
    return all_items

def get_tenk_item_descriptions() -> dict[str, str]:
    descriptions = {}
    for part_dict in TenK.structure.structure.values():
        for item_code, meta in part_dict.items():
            title = meta.get("Title", "")
            desc = meta.get("Description", "")
            descriptions[item_code] = f"{title}: {desc}"
    return descriptions

## START - UNUSED CLASSES 
class BusinessSection(BaseModel):
    heading: str = Field(..., description="Section heading")
    description: str = Field(..., description="Description of what the section covers")
    summary: str | None = Field(None, description="Summary extracted from the filing")
    key_values: List[KeyValuePair] = Field(default_factory=list)

class FilingItemSummary(BaseModel):
    title: str = Field(..., description="Title of the filing section, e.g., 'Business' or 'Risk Factors'")
    description: str = Field(..., description="High-level description of what this item covers")
    sections: List[BusinessSection]
## END UNUSED CLASSES 

## START - UNUSED FUNCTIONS 
def generate_item_descriptions(structure: FilingStructure) -> str:
    lines = []
    for part, items in structure.structure.items():
        for item_code, content in items.items():
            title = content.get("Title", "No Title")
            desc = content.get("Description", "").strip()
            lines.append(f"  - \"{item_code}\": {title} — {desc}")
    return "\n".join(lines)
## END - UNUSED FUNCTIONS
