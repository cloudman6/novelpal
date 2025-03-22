import unittest
from data_models.alias_resolver import AliasResolver

class TestAliasResolver(unittest.TestCase):

    def setUp(self):
        self.alias_resolver = AliasResolver()

    def test_resolve_alias(self):
        
        # 全名
        alias = "李玄锋"
        expected_value = "李玄锋"
        resolved_value = self.alias_resolver.resolve(alias)
        self.assertEqual(resolved_value, expected_value)

        # 别名
        alias = "玄锋"
        expected_value = "李玄锋"
        resolved_value = self.alias_resolver.resolve(alias)
        self.assertEqual(resolved_value, expected_value)
        
        # 别名
        alias = "锋儿"
        expected_value = "李玄锋"
        resolved_value = self.alias_resolver.resolve(alias)
        self.assertEqual(resolved_value, expected_value)
     
        # 数据库以为的名字
        alias = "新名字"
        expected_value = "新名字"
        resolved_value = self.alias_resolver.resolve(alias)
        self.assertEqual(resolved_value, expected_value)

if __name__ == '__main__':
    unittest.main()