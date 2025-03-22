import unittest
from unittest.mock import patch
from core.knowledge.relation_storage import RelationStorage
from utils.id_generator import IDGenerator
import json

class TestRelationStorage(unittest.TestCase):
    def setUp(self):
        # 在每个测试用例执行前初始化 RelationStorage 实例
        self.relation_storage = RelationStorage()

    def test_fetch_relations_valid_entity_ids(self):
        # 定义要查询的 entity_ids
        entity_ids = [IDGenerator.get_id("安氏"), IDGenerator.get_id("空衡"), IDGenerator.get_id("李周巍")]

        result = self.relation_storage.fetch_relations(entity_ids)
        
        # 解析结果
        data_list = json.loads(result)
        
        # 断言结果不为空
        self.assertIsNotNone(data_list)
        
    def test_fetch_relations_empty_entity_ids(self):
        # 模拟空的实体 ID 列表
        entity_ids = []

        result = self.relation_storage.fetch_relations(entity_ids)
        # 解析结果
        data_list = json.loads(result)
        
        # 断言结果为一个空列表转换后的 JSON 字符串
        self.assertEqual(data_list, [])

    def test_fetch_relations_nonexistent_entity_id(self):
        # 模拟不存在的实体 ID 列表
        entity_ids = ["nonexistent_id1", "nonexistent_id2"]

        result = self.relation_storage.fetch_relations(entity_ids)
        # 解析结果
        data_list = json.loads(result)

        # 断言结果为一个空列表转换后的 JSON 字符串
        self.assertEqual(data_list, [])


if __name__ == '__main__':
    unittest.main()
