from core.preprocessor.pipeline import PreprocessingPipeline
from core.knowledge.entity_storage import EntityStorage
from core.knowledge.relation_storage import RelationStorage
from utils.logger import Logger


async def main():
    logger = Logger.get_logger(__name__)
    pipeline = PreprocessingPipeline()
    entity_storage = EntityStorage()
    relation_storage = RelationStorage()
    
    chapter_range = [1, 51]
    for i in range(chapter_range[0], chapter_range[1]+1):
        file_path = f"chapters/{i}.txt"
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"=================== Start processing chapter {i} =================== " )
        entities, relations = pipeline.process(content)
        logger.info(f"=================== Storing entities for chapter {i} =================== " )
        entity_storage.store_entities(entities, i)
        logger.info(f"=================== Storing relations for chapter {i} =================== " )
        relation_storage.store_relations(entities, relations, i)
        logger.info(f"=================== Finish processing chapter {i} =================== " )
         

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())