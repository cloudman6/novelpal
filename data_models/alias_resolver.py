import json

class AliasResolver:
    def __init__(self, alias_file='config/alias.json'):
        with open(alias_file, 'r', encoding='utf-8') as file:
            self.alias_db = json.load(file)

        # 构建反向映射字典：{别名: 全名}
        self.alias_to_fullname = self._build_alias_mapping()

    def resolve(self, name):
        """解析输入名称，返回对应的标准全名"""
        # 规则1：已知全名直接返回
        if name in self.alias_db:
            return name
        
        # 规则2：已知别名返回全面
        if name in self.alias_to_fullname:
            return self.alias_to_fullname[name]
        
        # 其他：直接返回
        return name

    def _build_alias_mapping(self):
        """构建别名到全名的反向映射"""
        mapping = {}
        for fullname, aliases in self.alias_db.items():
            for alias in aliases:
                # 确保别名唯一性（如果冲突则覆盖）
                mapping[alias] = fullname
        return mapping