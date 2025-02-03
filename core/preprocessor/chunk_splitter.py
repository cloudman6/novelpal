class ContextAwareSplitter:
    def split_with_context(text: str, max_len=1000) -> List[TextChunk]:
        """智能分块，保留上下文"""
        # 实现基于语义的分块算法