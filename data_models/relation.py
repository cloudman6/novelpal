from pydantic import BaseModel
from typing import Dict

class DynamicRelation(BaseModel):
    source: str
    target: str
    relation: str    
    metadata: Dict[str, any] = {
        "polarity": "neutral",
        "evidence": ""
    }

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create_from_llm_response(cls, data: dict, source_text: str):
        return cls(
            source=data["source"],
            target=data["target"],
            relation=data["relation"],
            metadata={
                "polarity": data.get("极性", "neutral"),
                "evidence": data.get("证据", "")
            }
        )