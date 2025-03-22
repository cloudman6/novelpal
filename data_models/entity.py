from pydantic import BaseModel
from typing import Dict, List, Optional
import re

class DynamicEntity(BaseModel):
    name: str
    type: str
    attributes: Dict[str, str]
    metadata: Dict[str, any] = {
        "confidence": 0.9,
        "position": {
            "start": 0,
            "end": 0,
            "sentence": ""
        },
        "type_trace": []
    }

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create_from_llm_response(cls, data: dict, source_text: str):
        start, end = cls.locate_entity(source_text, data["名称"])
        sentence = cls.extract_context(source_text, start, end)
        
        # 过滤 attributes 字典
        filtered_attributes = {
            key: value for key, value in data.get("属性", {}).items()
            if value not in ["未知", "不确定", "未提及"]
        }
        
        return cls(
            name=data["名称"],
            type=data["类型"],
            # 使用过滤后的 attributes 字典
            attributes=filtered_attributes,
            metadata={
                "confidence": data.get("置信度", 0.8),
                "position": {
                    "start": start,
                    "end": end,
                    "sentence": sentence
                },
                "type_trace": data.get("类型推断依据", [])
            }
        )

    @staticmethod
    def locate_entity(text: str, entity_name: str) -> tuple[int, int]:
        match = re.search(re.escape(entity_name), text)
        return (match.start(), match.end()) if match else (0, 0)

    @staticmethod
    def extract_context(text: str, start: int, end: int) -> str:
        sentences = re.split(r'[。！？…]', text)
        for sent in sentences:
            if start <= len(sent) <= end:
                return sent
        return text[max(0,start-50):end+50]