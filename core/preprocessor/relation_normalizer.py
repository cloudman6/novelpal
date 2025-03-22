from sentence_transformers import SentenceTransformer
import numpy as np
from data_models.relation import DynamicRelation
import json
import os

class RelationNormalizer:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.relation_mapping_file = 'config/relation_mapping.json'
        self.relation_mapping = self._load_relations()
        self.similarity_threshold = 0.8

    def normalize(self, relations: list[DynamicRelation]) -> list[DynamicRelation]:
        return [self._normalize_single(relation) for relation in relations]

    def _load_relations(self):
        if os.path.exists(self.relation_mapping_file):
            with open(self.relation_mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._load_initial_relations()

    def _save_relations(self):
        with open(self.relation_mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.relation_mapping, f, ensure_ascii=False, indent=4)

    def _normalize_single(self, relation: DynamicRelation) -> DynamicRelation:
        relation_type = relation.relation
        embeddings = self.model.encode([relation_type] + self.relation_mapping)
        
        similarities = [
            self._cosine_similarity(embeddings[0], emb)
            for emb in embeddings[1:]
        ]
        
        max_idx = np.argmax(similarities)
        if similarities[max_idx] > self.similarity_threshold:
            relation.relation = self.relation_mapping[max_idx]
        else:
            self.relation_mapping.append(relation_type)
            self._save_relations()
        
        return relation

    @staticmethod
    def _cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _load_initial_relations(self):
        return [
            "夫妻", "兄弟姐妹", "朋友", "敌对", "师徒", "同门"
        ]