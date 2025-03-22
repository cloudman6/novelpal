from pymongo import MongoClient
from bson import ObjectId
from utils.config_manager import ConfigManager
import datetime
from utils.id_generator import IDGenerator
import json

class EntityStorage:
    def __init__(self):
        self.config = ConfigManager().get_config()
        self.client = MongoClient(self.config.storage.mongodb.uri)
        self.db = self.client[self.config.storage.mongodb.db_name]
        self.collection = self.db[self.config.storage.mongodb.entity_collection_name]
        self.collection.create_index([("entity_id", 1)], unique=True)

    def fetch_entities(self, entity_ids):
        # 查询 entity_ids 的所有实体
        results = self.collection.find({"entity_id": {"$in": entity_ids}})

        # 将查询结果转换为列表
        entities = []
        for result in results:
            # 将 _id 转换为字符串，因为 JSON 不能直接序列化 ObjectId
            result['_id'] = str(result['_id'])
            # 处理 version_chain 中的 version 字段
            if 'version_chain' in result:
                for version_info in result['version_chain']:
                    version_info['version'] = str(version_info['version'])
            entities.append(result)

        return entities
            
    def store_entities(self, entities, chapter_num):
        """处理NER结果并存储"""
        for entity in entities:
            # 生成唯一实体ID（使用 sha256 哈希算法）
            entity_id = f"{IDGenerator.get_id(entity.name)}"
            
            # 检查文档是否存在
            existing_doc = self.collection.find_one({"entity_id": entity_id})
            exists = existing_doc is not None
            
            # 创建或更新实体
            new_version = self._new_version(entity, chapter_num)
            pipeline = [
                {
                    "$set": {
                        "base_info": {
                            "$cond": {
                                "if": exists,
                                # 如果文档存在，保持 base_info 不变
                                "then": "$base_info",
                                # 如果文档不存在，插入初始 base_info
                                "else": {
                                    "name": entity.name,
                                    "type": entity.type,
                                    "ner_source":  {
                                        "first_mention": {
                                        "chapter": chapter_num,
                                        # 'text': self._extract_context(entity.metadata['sentence']),
                                        "position": entity.metadata["position"]
                                        }
                                    },
                                },
                            }
                        },
                        "canonical_state": {
                            "$cond": {
                                "if": exists,
                                "then": {
                                    "$mergeObjects": [
                                        {"$ifNull": ["$canonical_state", {}]},
                                        self._build_canonical_state(
                                            entity, chapter_num
                                        ),
                                    ]
                                },
                                "else": self._build_canonical_state(
                                    entity, chapter_num
                                ),
                            }
                        },
                        "version_chain": {
                            "$cond": {
                                "if": exists,
                                "then": {
                                    "$concatArrays": [
                                        [new_version],
                                        {
                                            "$map": {
                                                "input": "$version_chain",
                                                "as": "item",
                                                "in": {
                                                    "$mergeObjects": [
                                                        "$$item",
                                                        {"is_current": False},
                                                    ]
                                                },
                                            }
                                        }
                                    ]
                                },
                                "else": [new_version],
                            }
                        },
                    }
                }
            ]
            self.collection.update_one({"entity_id": entity_id}, pipeline, upsert=True)

    def _build_canonical_state(self, entity, chapter):
        """构建权威状态"""
        return {
            **entity.attributes,
            "valid_from": chapter,
            "sources": {
                "$concatArrays": [
                    {"$ifNull": ["$canonical_state.sources", []]},  # 处理首次创建的情况
                    [f"ner#{chapter}"],
                ]
            },
        }

    def _new_version(self, entity, chapter):
        """创建新版本记录"""
        return {
            "version": ObjectId(),  # 使用ObjectId作为版本号
            "type": "ner_auto",
            "state": entity.attributes,
            "chapter": chapter,
            "confidence": entity.metadata["confidence"],
            "is_current": True,
            "timestamp": datetime.datetime.now().isoformat(),
        }
