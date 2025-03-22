from data_models.entity import DynamicEntity
from data_models.relation import DynamicRelation
from tenacity import retry
from utils.llm_client import LLMClient
from utils.config_manager import ConfigManager
import time
import json
import random


class EntityRecognizer:
    def __init__(self, min_confidence=0.8):
        self.config = ConfigManager().get_config()
        self.model_client = LLMClient(self.config.llm.model_used.common)
        self.min_confidence = min_confidence

    # @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=20))
    def recognize_entities_and_relations(self, text: str, context: dict = {}):
        time.sleep(random.randint(1, 10))
        sys_prompt = "你是一个网文实体识别和关系提取专家"
        prompt = self._build_prompt(text, context)
        response = self.model_client.call_llm(sys_prompt, prompt)
        return self._process_response(response, text)


    def _build_prompt(self, text: str, context: dict = {}) -> str:
        return f"""
        # 任务说明
        请深度分析以下网文段落，完成以下两个任务：
        1. 精准识别所有重要实体及其属性
        2. 提取实体之间的关键长期关系

        # 输入文本
        {text}

        # 上下文线索
        {context.get('previous_summary', '无')}

        # 复合识别规则（实体+关系）
        ## 实体规则
        1. 类型标签应简洁明确（如：'上古神器'而非'物品'）
        2. 包含至少1个属性
        3. 只包含能明确确定属性值的属性。如果某个属性的值无法判断，则必须忽略掉该属性。绝对不能出现值为'未知'、'不确定'、'未提及'等含义的属性
        4. 对不确定的类型添加置信度（0-1）
        5. 记录类型推断依据（如：'提到法宝名称和品阶'）

        ## 关系规则 
        1. 关系类型需符合修仙体系（如：师徒、道侣、本命法宝）
        2. 标记关系的正负性（positive/negative/neutral）
        3. 对不确定的关系添加置信度（0-1）

        # 复合输出示例
        {self._generate_example()}

        # 结构化格式要求
        {self._generate_schema()}
        """

    def _generate_example(self) -> str:
        return json.dumps(
            {
                "实体列表": [
                    {
                        "名称": "骨灵冷火",
                        "类型": "异火",
                        "属性": {
                            "排名": "异火榜第十一",
                            "当前宿主": "药老",
                            "温度特性": "极寒与极热并存",
                        },
                        "置信度": 0.97,
                        "推断依据": ["明确提及异火榜排名", "描述'冰火双重特性'"],
                    }
                ],
                "关系列表": [
                    {
                        "source": "药老",
                        "target": "骨灵冷火",
                        "relation": "本命异火",
                        "极性": "positive",
                        "置信度": 0.97,
                        "证据": "药老掌心跃动森白火焰",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )


    def _generate_schema(self) -> str:
        return json.dumps(
            {
                "type": "object",
                "properties": {
                    "实体列表": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "名称": {"type": "string"},
                                "类型": {"type": "string"},
                                "属性": {"type": "object"},
                                "置信度": {"type": "number"},
                                "推断依据": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["名称", "类型", "属性"],
                        },
                    },
                    "关系列表": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "relation": {"type": "string"},
                                "极性": {"type": "string"},
                                "置信度": {"type": "number"},
                                "证据": {"type": "string"},
                            },
                            "required": ["source", "target", "relation"],
                        },
                    },
                },
                "required": ["实体列表", "关系列表"],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _process_response(self, response_text: str, source_text: str) -> tuple[list, list]:
        try:
            data = json.loads(response_text)
            if data.get("properties"):
                data = data.get("properties")

            return (
                [
                    DynamicEntity.create_from_llm_response(entity_data, source_text)
                    for entity_data in data.get("实体列表", [])
                    if entity_data.get("置信度", 0) >= self.min_confidence
                ],
                [
                    DynamicRelation.create_from_llm_response(relation_data, source_text)
                    for relation_data in data.get("关系列表", [])
                    if relation_data.get("置信度", 0) >= self.min_confidence
                ]
            )

        except Exception as e:
            print(f"Response parsing failed: {str(e)}")
            return [], []
