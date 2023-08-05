from mock import Mock
from unittest2 import TestCase
from riakdoc.documents import BaseDocument
from riakdoc.indexes import StrFieldsIndex

class TestStrFieldsIndex(TestCase):
    def test_str_fields_single(self):
        """Test that a single field in data is properly made available as an index."""
        index = StrFieldsIndex('person.name')
        index.set_name('test_index')
        self.assertEqual('John Doe', index.get_value({'person': {'name': 'John Doe', }}, {}))

    def test_update_str_fields_single(self):
        """Test that a single string fields index will update an index properly."""
        index = StrFieldsIndex('person.name')
        index.set_name('test_index')
        indexes = {}
        index.update({'person': {'name': 'John Doe', }}, indexes)
        self.assertEqual('John Doe', indexes['test_index'])

    def test_multiple_str_fields_index(self):
        """Test that a multiple string fields index will create the right result value."""
        index = StrFieldsIndex(('id', 'person.category'))
        index.set_name('test_index')
        self.assertEqual('1_green', index.get_value({'id': 1, 'person': {'category': 'green'}}, {}))

    def test_nothing_returned_missing_field(self):
        """Test that if a field doesn't exist, the value for the index on it will be None."""
        index = StrFieldsIndex('my.fair.lady')
        index.set_name('test_index')
        self.assertIsNone(index.get_value({'my': 1}, {}))

class TestIndexStuff(TestCase):
    """
    Test secondary index functionality.
    """
    def setUp(self):
        self.mock_doc = Mock()
        self.mock_doc.get_indexes.return_value = set()
        self.mock_doc.exists.return_value = False

    def test_basic_update_indexes(self):
        """Test that whatever is returned from update_indexes gets written properly to Riak's set_indexes call."""
        class TestDoc(BaseDocument):
            enable_2i = True
            def update_indexes(self, indexes):
                if not 'beetle' in indexes:
                    indexes['beetle'] = 'bailey'
                return indexes

        doc = TestDoc('mykey', obj=self.mock_doc)
        doc['tommy'] = 'boy'
        doc.save()

        self.mock_doc.set_indexes.assert_called_with([('beetle', 'bailey')])

    def test_auto_index_stuff(self):
        """Test that indexes descended from BaseIndex are properly used to call set_index."""
        class TestDoc(BaseDocument):
            enable_2i = True
            complex_index = StrFieldsIndex(('id', 'person.category'))

        doc = TestDoc('mykey', obj=self.mock_doc)
        doc['id'] = 12
        doc['person'] = {'category': 'baby'}

        doc.save()

        self.mock_doc.set_indexes.assert_called_with([('complex_index', '12_baby')])

    def test_basic_dict_set(self):
        """Test that just updating indexes will get written out properly to set_indexes()"""
        class TestDoc(BaseDocument):
            enable_2i = True

        doc = TestDoc('mykey', obj=self.mock_doc)
        doc.indexes = {'hello': 'there'}
        doc.save()

        self.mock_doc.set_indexes.assert_called_with([('hello', 'there')])