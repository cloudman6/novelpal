from openai import OpenAI
from utils.config_manager import ConfigManager
from utils.logger import Logger

class LLMClient:
    def __init__(self, model: str):
        self.logger = Logger.get_logger(__name__)
        # 获取配置对象
        self.config = ConfigManager().get_config()
        
        # 从配置中获取模型配置
        self.llm = self.config.llm.get(model, self.config.llm.deepseek)

        if not self.llm:
            raise ValueError("LLM configuration not found in the config file.")
        
        self.client = OpenAI(
            api_key=self.llm.api_key,
            base_url=self.llm.base_url
        )

    def call_llm(self, sys_prompt: str, prompt: str) -> str:
        self.logger.info(f"Calling LLM with prompt: {prompt}")
        # 使用 OpenAI 的 ChatCompletion 接口
        response = self.client.chat.completions.create(
            model=self.llm.model,  
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        self.logger.info(f"LLM response: {response}")
        # 返回生成的内容
        content = response.choices[0].message.content 

        parts = content.split('```json\n', 1)

        if len(parts) > 1:
            # 取分割后的第二部分
            json_str = parts[1]
            # 再以 ``` 为分隔符进行分割，取第一部分
            json_str = json_str.split('```', 1)[0]
        else:
            json_str = content

        return json_str