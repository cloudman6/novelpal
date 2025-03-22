import datetime
from neo4j import GraphDatabase
from bson import ObjectId
from utils.config_manager import ConfigManager
from utils.id_generator import IDGenerator
from utils.logger import Logger
import json

class RelationStorage:
    def __init__(self):
        self.logger = Logger.get_logger(__name__)
        self.config = ConfigManager().get_config()
        self.driver = GraphDatabase.driver(self.config.storage.neo4j.uri)

    def fetch_relations(self, entity_ids):
        def _fetch_relations(tx, entity_ids):
            # 查询 entity_ids 的所有关系
            query = """
            MATCH (a:Entity)-[r]->(b:Entity)
            WHERE a.entity_id IN $entity_ids AND b.entity_id IN $entity_ids
            RETURN a, r, b
            """
            result = tx.run(query, entity_ids=entity_ids)
            
            # 将查询结果转换为列表
            relations = []
            for record in result:
                source_node = record["a"]
                relationship = record["r"]
                target_node = record["b"]
                relations.append({
                    "source_node": dict(source_node),
                    "relationship": dict(relationship),
                    "target_node": dict(target_node)
                })
            return relations

        # 在事务中执行查询
        with self.driver.session() as session:
            relations = session.execute_read(_fetch_relations, entity_ids)
        
        return relations

    def store_relations(self, entities, relations, chapter_num):
        self._upsert_entities(entities)
        self._handle_relations(relations, chapter_num)
                
    def _upsert_entities(self, entities):
        entity_dicts = []
        for entity in entities:
            entity_dict = {
                "id": IDGenerator.get_id(entity.name),
                "name": entity.name,
                "type": entity.type,
            }
            entity_dicts.append(entity_dict)
            
        def _batch_upsert_entities(tx, entities):
            query = """
            UNWIND $entities AS entity
            MERGE (e:Entity {entity_id: entity.id})
            ON CREATE SET 
                e.name = entity.name,
                e.type = entity.type
            RETURN e
            """
            result = tx.run(query, entities=entities)
            # 在事务内处理结果
            for record in result:
                self.logger.info(f"{record['e']}")
            return result

        with self.driver.session() as session:
            session.execute_write(_batch_upsert_entities, entity_dicts)

    def _handle_relations(self, relations, chapter_num):
        relation_dicts = []
        for relation in relations:
            relation_dict = {
                "relation_id": str(ObjectId()),
                "source_id": IDGenerator.get_id(relation.source),
                "target_id": IDGenerator.get_id(relation.target),
                "type": relation.relation,
                "polarity": relation.metadata['polarity'],
                "evidence": relation.metadata['evidence'],
                "chapters": [chapter_num],
            }
            relation_dicts.append(relation_dict)
            
        def _batch_handle_relationship(tx, rels):
            # 1. 标记旧关系为失效
            disable_query = """            
            UNWIND $rels AS rel
            MATCH (a:Entity)-[r:HAS_RELATION]->(b:Entity)
            WHERE a.entity_id = rel.source_id AND b.entity_id = rel.target_id 
            AND r.is_current = true
            AND r.type = rel.type 
            AND r.polarity <> rel.polarity
            SET r.is_current = false, 
                r.replaced_by = rel.relation_id
            RETURN r
            """
            tx.run(disable_query, rels=rels)
            
            # 2. 创建新关系（带历史版本）
            create_query = """           
            UNWIND $rels AS rel
            MATCH (a:Entity {entity_id: rel.source_id}), (b:Entity {entity_id: rel.target_id})
            MERGE (a)-[r:HAS_RELATION {type: rel.type, polarity: rel.polarity}]->(b)
            ON CREATE SET 
                r.relation_id = rel.relation_id,
                r.chapters = rel.chapters,
                r.evidence = rel.evidence,
                r.created_at = $created_at,
                r.is_current = true
            RETURN r
            """
            result = tx.run(create_query, rels=rels, created_at=datetime.datetime.now().isoformat())
            # 在事务内处理结果
            for record in result:
                self.logger.info(f"{record['r']}")
            return result

        with self.driver.session() as session:
            session.execute_write(_batch_handle_relationship, relation_dicts)