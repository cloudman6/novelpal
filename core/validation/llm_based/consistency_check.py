class LLMConsistencyValidator:
    def _build_context_prompt(chunk: TextChunk, snapshot: dict) -> str:
        """动态构建知识增强的prompt"""
    
    def check_chunk(chunk: TextChunk) -> List[ConsistencyError]:
        """三阶段校验流程"""