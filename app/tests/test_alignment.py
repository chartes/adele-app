import os
import unittest

from sqlalchemy.sql.elements import and_

from app import db
from app.database.alignment.alignment_translation import align_translation
from app.models import AlignmentTranslation

NS_TI = {"ti": "http://www.tei-c.org/ns/1.0"}
TEST_DATA_DIR = "app/tests/data"


class TestTranscriptionTranslationAlignment(unittest.TestCase):

    doc_list = []

    @classmethod
    def setUpClass(cls):
        #load the list of the fn of the tested documents
        cls.doc_list = []
        for root, directories, filenames in os.walk(os.path.join(TEST_DATA_DIR, 'transcription')):
            for filename in filenames:
                if filename.endswith(".txt"):
                    cls.doc_list.append(filename.split(".")[0])

        cls.doc_list.sort()
        print("Tested docs:", cls.doc_list)

    def test_both_ids_match(self):
        """
        Translation and corresponding transcription ids may be equal. If not mandatory, it is still wishable.
        :return:
        """
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            res = align_translation(doc, doc)

            # expect consistency between translation and traduction ids (error shouldn't happen)
            transcription_ids = set()
            translation_ids = set()
            for (transcription_id, translation_id, ptr1, ptr2, ptr3, ptr4, a, b) in res:
                if translation_id is not None: #sometime there's just no translation.
                    transcription_ids.add(transcription_id)
                    translation_ids.add(translation_id)
            self.assertSetEqual(transcription_ids, translation_ids, "Something is wrong with the IDs")

    def test_alignment_is_correct(self):
        """
        Test alignment between static txt files and rows fetched from the db
        :return:
        """
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            with open(os.path.join(TEST_DATA_DIR, "transcription", "{0}.txt").format(doc), "r") as transcription_f, \
                 open(os.path.join(TEST_DATA_DIR, "translation", "{0}.txt").format(doc), "r") as translation_f:
                transcription_lines = transcription_f.read().splitlines()
                translation_lines = translation_f.read().splitlines()

                res = align_translation(doc, doc)

                if len(translation_lines) == 0:
                    translation_ids = set([l["translation_id"] for l in res if l["translation_id"] != None])
                    self.assertEqual(0, len(translation_ids), "There is no translation for doc {0}".format(doc))
                else:
                    """
                    Test line count
                    """
                    line_cnt_file = len(transcription_lines)
                    line_cnt_db = len(AlignmentTranslation.query.filter(and_(AlignmentTranslation.transcription_id==doc,AlignmentTranslation.ptr_transcription_start!=None)).all())
                    self.assertEqual(line_cnt_file, line_cnt_db, "Transcription lines count does not match for doc {0}".format(doc))

                    line_cnt_file = len(translation_lines)
                    line_cnt_db = len(AlignmentTranslation.query.filter(and_(AlignmentTranslation.transcription_id==doc,AlignmentTranslation.ptr_translation_start!=None)).all())
                    self.assertEqual(line_cnt_file, line_cnt_db, "Translation lines count does not match for doc {0}".format(doc))
                    """
                    Test alignment database vs test file
                    """
                    for i, transcription in enumerate(transcription_lines):
                        self.assertEqual(transcription, res[i]["transcription"] if res[i]["transcription"] is not None else '', "Transcription ptrs look wrong for doc {0}".format(doc))

                    for i, translation in enumerate(translation_lines):
                        self.assertEqual(translation, res[i]["translation"] if res[i]["translation"] is not None else '', "Translation ptrs look wrong for doc {0}".format(doc))

            #print("Alignment transcription/translation for doc {0} is OK".format(doc) )


if __name__ == '__main__':
    unittest.main()
