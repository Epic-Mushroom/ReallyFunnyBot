import unittest
from unittest.mock import patch, MagicMock

import json_utils


class TestUpdateFishDatabase(unittest.TestCase):
    @patch('json_utils.fishing_database')
    @patch('json_utils.update_inventory')
    @patch('json_utils.update_file')
    def test_updates_user_found(self, update_file_mock, update_inventory_mock, fishing_database_mock):
        database_mock = [{'username': 'testuser', 'items': [], 'last_fish_time': 1111, 'value': 0, 'times_fished': 0}]
        fishing_database_mock.return_value = database_mock
        json_utils.update_fish_database('testuser', None, 1, 1)
        self.assertEqual(database_mock[0]['last_fish_time'], 1111)
        self.assertEqual(database_mock[0]['times_fished'], 0)
        update_file_mock.assert_called_once_with(database_mock)

    @patch('json_utils.fishing_database')
    @patch('json_utils.update_inventory')
    @patch('json_utils.update_file')
    def test_updates_user_not_found(self, update_file_mock, update_inventory_mock, fishing_database_mock):
        database_mock = [
            {'username': 'not_testuser', 'items': [], 'last_fish_time': 1111, 'value': 0, 'times_fished': 0}]
        fishing_database_mock.return_value = database_mock
        json_utils.update_fish_database('testuser', None, 1, 1)
        self.assertEqual(len(database_mock), 2)
        self.assertEqual(database_mock[1]['username'], 'testuser')
        self.assertEqual(database_mock[1]['times_fished'], 1)
        update_file_mock.assert_called_with(database_mock)

    @patch('json_utils.fishing_database')
    @patch('json_utils.update_inventory')
    @patch('json_utils.update_file')
    def test_fish_provided(self, update_file_mock, update_inventory_mock, fishing_database_mock):
        database_mock = [
            {'username': 'not_testuser', 'items': [], 'last_fish_time': 1111, 'value': 0, 'times_fished': 0}]
        fishing_database_mock.return_value = database_mock
        fish = MagicMock()
        json_utils.update_fish_database('testuser', fish, 1, 1)
        update_inventory_mock.assert_called_once_with([], fish, count=1)

    @patch('json_utils.fishing_database')
    @patch('json_utils.update_inventory')
    @patch('json_utils.update_file')
    def test_fish_not_provided(self, update_file_mock, update_inventory_mock, fishing_database_mock):
        database_mock = [
            {'username': 'not_testuser', 'items': [], 'last_fish_time': 1111, 'value': 0, 'times_fished': 0}]
        fishing_database_mock.return_value = database_mock
        json_utils.update_fish_database('testuser', None, 1, 1)
        update_inventory_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
