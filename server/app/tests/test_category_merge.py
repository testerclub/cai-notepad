from unittest import TestCase, skip
import json

from app import components
from app.tests import TestUtils


class TestCategoryMerge(TestUtils, TestCase):

    CATEGORY_LIST = components.BASE_PATH + "/categories/"
    CATEGORY_GET = components.BASE_PATH + "/categories/{id}/"

    NOTE_LIST = components.BASE_PATH + "/notes/"
    NOTE_GET = components.BASE_PATH + "/notes/{id}/"

    TASK_LIST = components.BASE_PATH + "/tasks/"
    TASK_GET = components.BASE_PATH + "/tasks/{id}/"

    def __init__(self, methodName):
        TestUtils.__init__(self)
        TestCase.__init__(self, methodName)

    def setUp(self):
        self._setup_app()
        self.categories = self._insert_categories()
        self.note_map = {}
        self.task_map = {}
        for category in self.categories:
            for note in self._insert_notes(category):
                if category.id not in self.note_map:
                    self.note_map[category.id] = []
                self.note_map[category.id].append(note)
            for task in self._insert_tasks(category):
                if category.id not in self.task_map:
                    self.task_map[category.id] = []
                self.task_map[category.id].append(task)

    def tearDown(self):
        self._db.close()

    # Test merge stuff

    def test_category_merge(self):
        # given
        # - category w/ parent
        # when
        # - merge to parent / w/ delete
        category = self.categories[1]
        category_id = category["id"]
        parent_id = category["parent"]
        self.response(self.app.delete(
            self.CATEGORY_GET.format(id=category_id),
            **self.post_args,
            **self.create_user_header(TestUtils.REGULAR_USER)
        ))

        # then
        # - all the stuff under it shall be under the prior parent category
        # - the merged category should be deleted
        self.response(self.app.get(
            self.CATEGORY_GET.format(id=category_id),
            **self.post_args,
            **self.create_user_header(TestUtils.REGULAR_USER)
        ))

        for (note_id, task_id) in zip(
            [note.id for note in self.note_map[category_id]],
            [task.id for task in self.task_map[category_id]]
        ):
            note_json = self.response(self.app.get(
                self.NOTE_GET.format(id=note_id),
                **self.create_user_header(TestUtils.REGULAR_USER)
            ))
            task_json = self.response(self.app.get(
                self.TASK_GET.format(id=task_id),
                **self.create_user_header(TestUtils.REGULAR_USER)
            ))
            self.assertEqual(parent_id, note_json["parent"])
            self.assertEqual(parent_id, task_json["parent"])
            pass

    def test_category_merge_root(self):
        # given
        # - categories w/o parent
        # when
        # - merge from another user
        category = self.categories[0]
        category_id = category["id"]

        # then
        # - all the stuff under it shall not have a category
        # - the merged category should be deleted
        self.response(self.app.delete(
            self.CATEGORY_GET.format(id=category_id),
            **self.post_args,
            **self.create_user_header(TestUtils.REGULAR_ALT_USER)
        ))
        for (note_id, task_id) in zip(
            [note.id for note in self.note_map[category_id]],
            [task.id for task in self.task_map[category_id]]
        ):
            note_json = self.response(self.app.get(
                self.NOTE_GET.format(id=note_id),
                **self.create_user_header(TestUtils.REGULAR_USER)
            ))
            task_json = self.response(self.app.get(
                self.TASK_GET.format(id=task_id),
                **self.create_user_header(TestUtils.REGULAR_USER)
            ))
            self.assertEqual(None, note_json["parent"])
            self.assertEqual(None, task_json["parent"])
        pass

    def test_category_merge_rights(self):
        # given
        # - category
        # when
        # - merge from another user
        category = self.categories[1]
        merge_id = category["id"]

        # then
        # - 404 expected
        error_json = self.response(self.app.delete(
            self.CATEGORY_GET.format(id=merge_id),
            **self.post_args,
            **self.create_user_header(TestUtils.REGULAR_ALT_USER)
        ), status=404)
        self.assertTrue("message" in error_json)

    # ---- UTILS

    def _insert_category(self, payload, mock_user=TestUtils.REGULAR_USER):
        return self.response(self.app.post(
            self.CATEGORY_LIST,
            data=json.dumps(payload),
            **self.post_args,
            **self.create_user_header(mock_user)
        ), status=201)

    def _insert_categories(self):
        categories = []

        root_category = {
            "name": "Root Category",
            "parent": None
        }
        root_category_json = self._insert_category(root_category)
        root_id = root_category_json["id"]
        categories.append(root_category)

        child_categories = [{
            "name": "Child Category " + str(i),
            "parent": {"id": root_id}
        } for i in range(3)]

        categories.extend([self._insert_category(payload) for payload in child_categories])
        return categories

    def _insert_notes(self, categories):
        return [self._insert_note({
            "title": "test_title %d" % (i),
            "content": "test_content\r\n %d \r\n" % (i),
            "tags": ["these", "are", "the", "test", "tags", "we", "look", "for"]}
        ) for i in range(3)]
        pass

    def _insert_note(self, note, mock_user=TestUtils.REGULAR_USER):
        note_json = self.response(self.app.post(
            self.NOTE_LIST,
            data=json.dumps(note),
            **self.post_args,
            **self.create_user_header(mock_user)
        ), status=201)
        return note_json

    def _insert_tasks(self, category):
        return [self._insert_task({"title": "My Title %d" % (i)}) for i in range(3)]
        pass

    def _insert_task(self, task, mock_user=TestUtils.REGULAR_USER):
        response_json = self.response(self.app.post(
            self.TASK_LIST,
            data=json.dumps(task),
            **self.post_args,
            **self.create_user_header(mock_user)
        ), 201)
        self.assertTrue("id" in response_json)
        self.assertIsNotNone(response_json["id"])

        return response_json

    def _read_note(self, note_id):
        pass

    def _read_task(self, task_id):
        pass
