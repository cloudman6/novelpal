import re
from typing import List, Dict
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter

@dataclass
class NovelChunk:
    text: str
    start_pos: int
    end_pos: int
    metadata: Dict = None
    entities: List = None

class NovelSplitter:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            keep_separator = "end",
            chunk_size = 1000,
            chunk_overlap = 200,
            separators=self._get_separators()
        )

    def _get_separators(self) -> List[str]:
        """优先按网文特征分割"""
        return [
            "\n\n",   # 空行分隔
            r"(?<=。|！|？|……)\n",  # 段落结尾
            "”", "。", "！", "？", "……"  # 句子结尾
        ]

    def split_with_context(self, text: str) -> List[NovelChunk]:
        chunks = self.splitter.split_text(text)

        # 重新计算原始位置
        return self._align_positions(text, chunks)

    def _align_positions(self, text: str, chunks: List[str]) -> List[NovelChunk]:
        """将处理后的分块映射回原始文本位置"""
        # 实现基于差异映射的位置对齐算法
        # 此处简化实现，实际需处理换行符插入带来的偏移
        position = 0
        aligned_chunks = []
        for chunk in chunks:
            start = text.find(chunk)
            if start == -1:
                start = position  # 降级处理
            end = start + len(chunk)
            aligned_chunks.append(NovelChunk(
                text=text[start:end],
                start_pos=start,
                end_pos=end
            ))
            position = end
        return aligned_chunks