import logging
import os

from nose.tools import assert_equal, assert_true, \
    assert_not_equal

from .tests_integraion_base import TestsIntegration

logger = logging.getLogger(__name__)


__all__ = ("TestsDocument",)


class TestsDocument(TestsIntegration):

    def tearDown(self):
        super(TestsDocument, self).tearDown()

        c = self.conn
        c.collection.test.delete()

    def test_document_creation(self):
        c = self.conn

        logger.info("Creationg new collection 'test'")

        body = {
            "value": 1,
            "testing": True,
            "options": [
                1,
                2,
                3
            ]
        }

        c.collection.test.create()
        count_before = c.collection.test.count()

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 1)

        c.collection.test.documents.create(body)
        assert_equal(c.collection.test.count(), count_before + 2)

    def test_document_deletion(self):
        c = self.conn

        logger.info("Creating collection 'test'")
        c.collection.test.create()

        logger.info("Creating sample document")

        doc = c.collection.test.documents.create([1])

        assert_not_equal(doc, None)

        count = c.collection.test.documents.count

        assert_true(doc.delete())

        assert_equal(
            c.collection.test.documents.count,
            count - 1
        )

    def test_document_deletion_collection(self):
        c = self.conn.collection

        logger.info("Creating collection 'test'")
        c.test.create()

        doc1 = c.test.documents.create({"a": 1})
        doc2 = c.test.documents.create({"a": 2})

        prev_count = int(c.test.documents.count)

        # delete by document itself
        c.test.documents.delete(doc1)

        assert_equal(int(c.test.documents.count), prev_count - 1)

        # delete by reference only
        c.test.documents.delete(doc2.id)

        assert_equal(c.test.documents.count, prev_count - 2)

    def test_document_update(self):
        c = self.conn.collection

        logger.info("Creating collection 'test'")
        c.test.create()

        doc = c.test.documents.create({1: 1})

        c.test.documents.update(doc, {2: 2})

        assert_equal(
            c.test.documents().first.body["1"], 1)
        assert_equal(
            c.test.documents().first.body["2"], 2)

        c.test.documents.delete(doc)

        doc1 = c.test.documents.create({"name": "John"})

        c.test.documents.update(doc1.id, {"position": "manager"})

        assert_equal(
            dict(
                [(key, val) for key, val in
                    c.test.documents().first.body.iteritems()
                    if key in ["name", "position"]]
            ),
            {
                "name": "John",
                "position": "manager"
            }
        )

    def test_document_body_setter(self):
        c = self.conn.collection

        logger.info("Creating collection 'test'")
        c.test.create()

        doc = c.test.documents.create({"data": 1})

        data = {"data": 2}
        doc.body = data
        doc.save()
        assert_not_equal(doc, None)

        inter = list(
            set(c.test.documents().first.body).intersection(
                set(data)))
        assert_equal(
            data[inter[0]],
            c.test.documents().first.body[inter[0]])

    def test_list_of_documents(self):
        c = self.conn.collection

        c.test.create()

        docs = [
            {"title": "doc1"},
            {"title": "doc2"},
            {"title": "doc3"}
        ]
        for doc in docs:
            c.test.documents.create(doc)

        for index, doc in enumerate(c.test.documents()):
            for src in docs:
                flag = False

                for key, val in src.iteritems():
                    if doc.body.get(key) == val:
                        flag = True
                        break

                if flag:
                    break

            assert_true(flag)


# execute integrational tests only if `INTEGRATIONAL`
# environemnt variable passed
if 'INTEGRATION' not in os.environ:
    TestsDocument = None
