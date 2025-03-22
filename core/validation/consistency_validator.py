from utils.config_manager import ConfigManager
from tenacity import retry
from utils.llm_client import LLMClient
import time
import json
import random

class ConsistencyValidator:
    def __init__(self, min_confidence=0.8):
        self.config = ConfigManager().get_config()
        self.model_client = LLMClient(self.config.llm.model_used.reasoner)
        self.min_confidence = min_confidence
        
    # @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=20))
    def validate(self, text: str, context: dict = {}) -> list:
        time.sleep(random.randint(1, 10))
        sys_prompt = "你是一名专业的网文编辑，你的任务是校对网文。"
        prompt = self._build_prompt(text, context)
        response = self.model_client.call_llm(sys_prompt, prompt)
        return self._process_response(response, text)
    
    def _build_prompt(self, text: str, context: dict = {}) -> str:
        return f"""
        # 任务说明
        基于以下上下文，逐行细致剖析新章节内容，保持恰当的审核节奏，保证不遗漏任何细节，验证新章节是否存在矛盾：
        
        # 关键实体状态
        {json.dumps(context['entities'], indent=4, ensure_ascii=False)}
        
        # 相关关系网络 
        {json.dumps(context['relations'], indent=4, ensure_ascii=False)}
        
        # 待校对新章节
        {text}
        
        # 校验重点
        1. 逐行细致剖析新章节，保持恰当的审核节奏，保证不遗漏任何细节。
        2. 找出每一行中出现的所有角色，逐个与实体和关系信息进行比对，判断该角色是否曾在其中出现。若出现过，核查该角色在此处出现是否合理，有无张冠李戴或混淆相似角色的情况；若未出现，判断此新角色的设定是否合理，是否可能是已有角色因笔误导致。一旦发现错误，即刻指出并给出正确名称。
        3. 找出每一行中出现的所有物品，比如丹药、法宝、武器等，逐个与实体和关系信息进行比对，判断该物品是否曾在其中出现。若出现过，核查该物品在此处出现是否合理，有无张冠李戴或混淆相似物品的情况；若未出现，判断此新物品的设定是否合理，是否可能是已有物品因笔误导致。一旦发现错误，即刻指出并给出正确名称。   
        4. 找出每一行中涉及角色修为的描述，比如胎息、练气、筑基等，与实体和关系信息对比，判断此修为是否与该角色匹配。若发现错误，立刻指出并给出正确的修为信息。
        5. 其他一致性逻辑错误
        
        # 输出格式
        {{
        "conflicts": [
            {{
            "original_text": "凌峰奋力驱动起斩仙剑",
            "error": "境界不符，斩仙剑是金丹期法宝，凌峰只有筑基期修为，应无法使用",
            "suggestion": "将斩仙剑改成另一筑基期法宝",
            "confidence": 0.95
            }}
        ]
        }}
        """
        
    def _process_response(self, response_text: str, source_text: str):
        try:
            data = json.loads(response_text)
            if data.get("properties"):
                data = data.get("properties")

            return data.get("conflicts", [])
        except Exception as e:
            print(f"Response parsing failed: {str(e)}")
            return []