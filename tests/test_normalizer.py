import unittest
import numpy as np
from sentence_transformers import SentenceTransformer
from core.preprocessor.type_normalizer import TypeNormalizer

class TestCosineSimilarity(unittest.TestCase):

    def setUp(self):
        # 创建 TypeNormalizer 实例
        self.type_normalizer = TypeNormalizer()
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def test_relations(self):
        # 测试相似关系的余弦相似度
        embs = self.model.encode(["妾室与夫君", "夫妻"])
        similarity = self.type_normalizer._cosine_similarity(embs[0], embs[1])
        self.assertEqual(similarity, 1)
        
    def test_cosine_similarity_same_vectors(self):
        # 测试相同向量的余弦相似度
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        similarity = self.type_normalizer._cosine_similarity(a, b)
        self.assertEqual(similarity, 1)

    def test_cosine_similarity_orthogonal_vectors(self):
        # 测试正交向量的余弦相似度
        a = np.array([1, 0])
        b = np.array([0, 1])
        similarity = self.type_normalizer._cosine_similarity(a, b)
        self.assertEqual(similarity, 0)

    def test_cosine_similarity_different_length_vectors(self):
        # 测试不同长度向量的余弦相似度
        a = np.array([1, 2, 3])
        b = np.array([1, 2])
        with self.assertRaises(ValueError):
            self.type_normalizer._cosine_similarity(a, b)

if __name__ == '__main__':
    unittest.main()
