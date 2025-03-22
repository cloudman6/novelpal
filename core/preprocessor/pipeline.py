import asyncio
from concurrent.futures import ThreadPoolExecutor
from core.preprocessor.entity_recognizer import EntityRecognizer
from core.preprocessor.type_normalizer import TypeNormalizer
from core.preprocessor.relation_normalizer import RelationNormalizer
from data_models.entity import DynamicEntity
from data_models.relation import DynamicRelation
from core.preprocessor.chunk_splitter import NovelSplitter, NovelChunk
from data_models.alias_resolver import AliasResolver
from utils.config_manager import ConfigManager


class PreprocessingPipeline:
    def __init__(self):
        self.splitter = NovelSplitter()
        self.recognizer = EntityRecognizer()
        self.type_normalizer = TypeNormalizer()
        self.relation_normalizer = RelationNormalizer()
        self.aliasresolver = AliasResolver()
        self.config = ConfigManager().get_config()
        self.executor = ThreadPoolExecutor(self.config.max_workers)

    async def process_in_pool(self, text: str) -> tuple[list[DynamicEntity], list[DynamicRelation]]:
        chunks = self.splitter.split_with_context(text)
        tasks = [self._process_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        # 展平结果列表
        entities = [entity for sublist, _ in results for entity in sublist]
        relations = [relation for _, sublist in results for relation in sublist]
        
        # 处理别名
        for entity in entities:
            entity.name = self.aliasresolver.resolve(entity.name)
            
        for relation in relations:
            relation.source = self.aliasresolver.resolve(relation.source)
            relation.target = self.aliasresolver.resolve(relation.target)
            
        return entities, relations

    def process(self, text: str) -> tuple[list[DynamicEntity], list[DynamicRelation]]:
        chunks = self.splitter.split_with_context(text)
        entities = []
        relations = []

        # 顺序处理每个文本块
        for chunk in chunks:
            sub_entities, sub_relations = self._process_chunk(chunk)
            entities.extend(sub_entities)
            relations.extend(sub_relations)

        # 处理别名
        for entity in entities:
            entity.name = self.aliasresolver.resolve(entity.name)

        for relation in relations:
            relation.source = self.aliasresolver.resolve(relation.source)
            relation.target = self.aliasresolver.resolve(relation.target)

        return entities, relations

    async def _process_chunk_in_pool(self, chunk: NovelChunk) -> tuple[list[DynamicEntity], list[DynamicRelation]]:
        loop = asyncio.get_event_loop()
        # 并行处理
        raw_entities, raw_relations = await loop.run_in_executor(
            self.executor,
            self.recognizer.recognize_entities,
            chunk.text
        )
        #raw_entities = self.recognizer.recognize_entities(chunk.text)
        entities_normalized = self.type_normalizer.normalize(raw_entities)
        relations_normalized = self.relation_normalizer.normalize(raw_relations)
        #enhanced = [await self.enhancer.enhance(e) for e in normalized]
        return entities_normalized, relations_normalized
    
    def _process_chunk(self, chunk: NovelChunk) -> tuple[list[DynamicEntity], list[DynamicRelation]]:
        raw_entities, raw_relations = self.recognizer.recognize_entities_and_relations(chunk.text)
        entities_normalized = self.type_normalizer.normalize(raw_entities)
        relations_normalized = self.relation_normalizer.normalize(raw_relations)
        return entities_normalized, relations_normalized