import unittest
from unittest.mock import patch
import json
from pymongo import MongoClient
from core.knowledge.entity_storage import EntityStorage
from bson import ObjectId
from utils.id_generator import IDGenerator

class TestEntityStorage(unittest.TestCase):
    def setUp(self):
        # 初始化 EntityStorage 实例
        self.storage = EntityStorage()

    def test_fetch_entities_success(self):

        # 定义要查询的 entity_ids
        entity_ids = [IDGenerator.get_id("李玄宣"), IDGenerator.get_id("安思危")]

        # 调用方法
        result = self.storage.fetch_entities(entity_ids)

        # 解析结果
        data_list = json.loads(result)

        # 断言
        self.assertEqual(len(data_list), 2)
         # 遍历 data_list 中的每个元素
        for item in data_list:
            # 检查元素中是否包含 'entity_id' 键
            self.assertIn('entity_id', item)
            # 检查 name 的值是否为 Alice 或 Bob
            self.assertIn(item['base_info']['name'], ['李玄宣', '安思危'])
            
    def test_fetch_entities_not_found(self):
        # 模拟没有查询到结果
        # 定义要查询的 entity_ids
        entity_ids = ["nonexistent_entity"]

        # 调用方法
        result = self.storage.fetch_entities(entity_ids)

        # 解析结果
        data_list = json.loads(result)

        # 断言
        self.assertEqual(len(data_list), 0)

    def test_fetch_entities_empty_list(self):
        # 模拟查询结果

        # 定义要查询的 entity_ids 为空列表
        entity_ids = []

        # 调用方法
        result = self.storage.fetch_entities(entity_ids)

        # 解析结果
        data_list = json.loads(result)

        # 断言
        self.assertEqual(len(data_list), 0)

if __name__ == '__main__':
    unittest.main()
