class VectorKnowledgeBase:
    def query_related_states(entity: str, top_k=5) -> List[KnowledgePoint]:
        """带时间衰减的向量检索"""