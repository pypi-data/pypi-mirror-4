__all__ = ["Metadata"]


class Metadata(object):
    """
    Metadata that keeps track of registered entities.
    """

    def __init__(self):
        self._entities = dict()

    def add_entity(self, entity, extra=None):
        if entity.name in self._entities:
            raise ValueError(
                "Entity already registered '{0}' ({1})".format(
                    entity.name, extra))

        self._entities[entity.name] = (entity, extra)

    def get_entity(self, name):
        entity_data = self._entities.get(name)

        if entity_data is None:
            raise KeyError(
                "No entity registered with name '{0}'".format(
                    name))

        return entity_data

    def resolve_entity(self, name):
        """
        Iterative resolved for relation reference graphs.
        """
        original_entity, extra = self.get_entity(name)
        original_entity.check()

        original_relations = list()

        queue = [(original_entity, original_relations)]

        while queue:
            parent_entity, parent_relations = queue.pop()

            for relation in parent_entity.relations:
                entity, extra = self.get_entity(relation.ref)
                entity.check()

                relations = list()

                parent_relations.append((relation, (entity, relations)))
                queue.append((entity, relations))

        return original_entity, original_relations
