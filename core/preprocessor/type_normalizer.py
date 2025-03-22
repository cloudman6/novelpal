from sentence_transformers import SentenceTransformer
import numpy as np
from data_models.entity import DynamicEntity
import json
import os

class TypeNormalizer:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.type_mapping_file = 'config/type_mapping.json'
        self.type_mapping = self._load_types()
        self.similarity_threshold = 0.8

    def normalize(self, entities: list[DynamicEntity]) -> list[DynamicEntity]:
        return [self._normalize_single(entity) for entity in entities]

    def _load_types(self):
        if os.path.exists(self.type_mapping_file):
            with open(self.type_mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._load_initial_types()

    def _save_types(self):
        with open(self.type_mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.type_mapping, f, ensure_ascii=False, indent=4)

    def _normalize_single(self, entity: DynamicEntity) -> DynamicEntity:
        entity_type = entity.type
        embeddings = self.model.encode([entity_type] + self.type_mapping)
        
        similarities = [
            self._cosine_similarity(embeddings[0], emb)
            for emb in embeddings[1:]
        ]
        
        max_idx = np.argmax(similarities)
        if similarities[max_idx] > self.similarity_threshold:
            entity.type = self.type_mapping[max_idx]
            entity.metadata["type_trace"].append(
                f"归一化为: {self.type_mapping[max_idx]}"
            )
        else:
            self.type_mapping.append(entity_type)
            entity.metadata["type_trace"].append("新增类型并添加到预定义类型中")
            self._save_types()
        
        return entity

    @staticmethod
    def _cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _load_initial_types(self):
        return [
            "人物", "妖兽", "修为", "天材地宝", "地理位置", "宗门势力", "功法秘籍", "法宝灵器"
        ]