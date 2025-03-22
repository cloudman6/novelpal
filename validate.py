from core.preprocessor.pipeline import PreprocessingPipeline
from core.knowledge.entity_storage import EntityStorage
from core.knowledge.relation_storage import RelationStorage
from utils.logger import Logger
from utils.id_generator import IDGenerator
from core.validation.consistency_validator import ConsistencyValidator
import json

async def main():
    logger = Logger.get_logger(__name__)
    pipeline = PreprocessingPipeline()
    entity_storage = EntityStorage()
    relation_storage = RelationStorage()
    validator = ConsistencyValidator()

    file_path = f"chapters/new.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    entities, relations = pipeline.process(content)
    entity_ids = [IDGenerator.get_id(entity.name) for entity in entities]
    entity_ids = list(set(entity_ids))
    entities = entity_storage.fetch_entities(entity_ids)
    relations = relation_storage.fetch_relations(entity_ids)
    context = {
        "entities": entities,
        "relations": relations
    }
    
    conflicts = validator.validate(content, context)
    logger.info(json.dumps(conflicts, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())