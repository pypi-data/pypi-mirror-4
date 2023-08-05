import unittest

from rested import Metadata

from mock import MagicMock


class TestMetadata(unittest.TestCase):
    def setup_metadata(self):
        metadata = Metadata()
        return metadata

    def test_add_entity(self):
        m = self.setup_metadata()
        entity = MagicMock()
        m.add_entity(entity)
        self.assertTrue(entity.name in m._entities)

    def test_conflict_add_entity(self):
        m = self.setup_metadata()
        entity = MagicMock()
        m.add_entity(entity)
        self.assertRaises(ValueError, m.add_entity, entity)

    def test_add_w_extra(self):
        m = self.setup_metadata()
        entity = MagicMock()
        extra = MagicMock()
        m.add_entity(entity, extra)
        self.assertTrue(entity.name in m._entities)
        self.assertEquals((entity, extra), m._entities[entity.name])
