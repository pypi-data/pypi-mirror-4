import sys
import uuid

from twisted.internet.base import DelayedCall
from twisted.python import log
from twisted.trial import unittest

import txmongo
from txmongo._pymongo import objectid

from mongomodel import model


DelayedCall.debug = True
#log.startLogging(sys.stdout)

class TestModel(model.Model):
    "Just a test model"
    db = "txmongomodel-test-db-%s" % str(uuid.uuid4())
    collection = "test-collection"


class ModelTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.model = TestModel(pool=False)

    def tearDown(self):

        def close(ignore):

            def _close(conn):
                d = conn.disconnect()
                d.addErrback(log.err)
                return d

            d = self.model.connMan.getConnection()
            d.addCallback(_close)
            return d

        d = self.model.dropDatabase()
        d.addCallback(close)
        return d

    def test_init(self):

        def checkResult(result):
            self.assertEqual(type(result), txmongo.MongoAPI)

        d = self.model.connMan.getConnection()
        d.addCallback(checkResult)
        return d

    def test_insertKwargs(self):

        def checkResult(result):
            self.assertEqual(type(result), objectid.ObjectId)

        d = self.model.insert(key1="value 1", key2="value 2")
        d.addCallback(checkResult)
        return d

    def test_insertData(self):

        def checkResult(result):
            self.assertEqual(type(result), objectid.ObjectId)

        d = self.model.insert(**{
            "key 1": "value 1",
            "key 2": "value 2",
            "key 3": "value 3",
            "key 4": "value 4"})
        d.addCallback(checkResult)
        return d

    def test_insertMany(self):

        def checkResults(results):
            self.assertEqual(len(results), 4)
            for result in results:
                log.msg(result)
                self.assertEqual(result[0], True)

        d = self.model.insertMany([
            {"key 1": "value 1"},
            {"key 2": "value 2"},
            {"key 3": "value 3"},
            {"key 4": "value 4"}])
        d.addCallback(checkResults)
        return d
