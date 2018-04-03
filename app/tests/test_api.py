from datetime import datetime
import pprint
import unittest
import urllib
import json

from app import app as flask_app


class TestAPIEndPoints(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.test_client()

    def test_api_align_translation_ok(self):
        resp = self.app.get("/api/v1/alignment/translation/33/33")
        self.assertEqual(resp.status_code, 200)
        r = json.loads(resp.data)

        self.assertIn("data", r)
        self.assertNotIn("errors", r)

        for seg in r["data"]:
            self.assertIsInstance(seg['ptr_transcription_start'], (int, type(None)))
            self.assertIsInstance(seg['ptr_transcription_end'], (int, type(None)))
            self.assertIsInstance(seg['ptr_translation_start'], (int, type(None)))
            self.assertIsInstance(seg['ptr_translation_end'], (int, type(None)))
            self.assertIsInstance(seg['transcription'], (str, type(None)))
            self.assertIsInstance(seg['translation'], (str, type(None)))

            #test data type if transcription is shorter or longer than translation
            if isinstance(seg['ptr_transcription_start'], type(None)) and \
               isinstance(seg['ptr_transcription_end'],  type(None)):
                self.assertEqual(len(seg['transcription']), 0)

            if isinstance(seg['ptr_translation_start'], type(None)) and \
               isinstance(seg['ptr_translation_end'], type(None)):
                self.assertEqual(len(seg['translation']), 0)


    def test_api_align_translation_not_found(self):
        resp = self.app.get("/api/v1/alignment/translation/1/2")
        self.assertEqual(resp.status_code, 200)
        r = json.loads(resp.data)

        self.assertNotIn("data", r)
        self.assertIn("errors", r)
        self.assertEqual(r["errors"]["status"], 404)

    def test_api_document_ok(self):
        DOC_ID = 95
        resp = self.app.get("/api/v1/document/{0}".format(DOC_ID))
        self.assertEqual(resp.status_code, 200)
        r = json.loads(resp.data)

        self.assertIn("data", r)
        self.assertNotIn("errors", r)

        self.assertIsInstance(r["data"]["acte_types"], list)
        self.assertIsInstance(r["data"]["argument"], (str, type(None)))
        self.assertIsInstance(r["data"]["copy_cent"], (int, type(None)))
        self.assertIsInstance(r["data"]["copy_year"], (str, type(None)))
        self.assertIsInstance(r["data"]["countries"], list)
        self.assertIsInstance(r["data"]["creation"], (int, type(None)))
        self.assertIsInstance(r["data"]["creation_lab"], (str, type(None)))
        self.assertIsInstance(r["data"]["date_insert"], str)
        self.assertIsInstance(r["data"]["date_update"], str)
        self.assertIsInstance(r["data"]["districts"], list)
        self.assertIsInstance(r["data"]["editors"], list)
        self.assertIsInstance(r["data"]["id"], int)
        self.assertIsInstance(r["data"]["images"], list)
        self.assertIsInstance(r["data"]["institution"], (dict, type(None)))
        self.assertIsInstance(r["data"]["pressmark"], (str, type(None)))
        self.assertIsInstance(r["data"]["title"], str)

        self.assertEqual(r["data"]["id"], DOC_ID)
        # Test date format
        date_time_object = datetime.strptime(r["data"]["date_insert"], '%Y-%m-%d %H:%M:%S')
        date_time_object = datetime.strptime(r["data"]["date_update"], '%Y-%m-%d %H:%M:%S')

    def test_api_document_not_found(self):
        DOC_ID = 10000
        resp = self.app.get("/api/v1/document/{0}".format(DOC_ID))
        self.assertEqual(resp.status_code, 200)
        r = json.loads(resp.data)

        self.assertNotIn("data", r)
        self.assertIn("errors", r)
        self.assertEqual(r["errors"]["status"], 404)

    #def test_api_document_manifest(self):
    #    raise NotImplementedError
    #
    #def test_api_document_transcriptions(self):
    #    raise NotImplementedError
    #
    #def test_api_document_translations(self):
    #    raise NotImplementedError
