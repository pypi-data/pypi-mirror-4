import unittest2

from querylist import QueryList


class QueryListActsAsList(unittest2.TestCase):
    """QueryLists should act just like lists if the wrapper is compatible
    with the src data elements"""
    def setUp(self):
        self.src_list = [{'foo': 1}, {'foo': 2}, {'foo': 3}]
        self.query_list = QueryList(self.src_list)

    def test_QueryList_items_are_equal_to_its_source_lists_items(self):
        self.assertEqual(self.src_list, self.query_list)

    def test_QueryList_length_is_equal_to_its_source_lists_length(self):
        self.assertEqual(len(self.src_list), len(self.query_list))

    def test_QueryLists_can_append_like_lists(self):
        dbl_list = self.src_list + self.src_list
        dbl_query_list = self.query_list + self.query_list

        self.assertEqual(dbl_query_list, dbl_list)

    def test_QueryList_slicing_works_like_list_slicing(self):
        self.assertEqual(self.query_list[:2], self.src_list[:2])

    def test_QueryList_indexing_works_like_list_indexing(self):
        self.assertEqual(self.query_list[1], self.src_list[1])
