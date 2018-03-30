import os
import unittest

from sqlalchemy.sql.elements import and_

from app import db
from app.models import AlignmentTranslation

NS_TI = {"ti": "http://www.tei-c.org/ns/1.0"}
TEST_DATA_DIR = "app/tests/data"


class TestTranscriptionTranslationAlignment(unittest.TestCase):

    doc_list = []

    @classmethod
    def get_alignment_stmt(cls, transcription_id) :
        return """
        SELECT
          transcription.id as transcription_id,
          translation.id as translation_id,
          COALESCE(substr(transcription.content, ptr_transcription_start, 
            ptr_transcription_end - ptr_transcription_start), '') as transcription,
          COALESCE(substr(translation.content, ptr_translation_start, 
            ptr_translation_end - ptr_translation_start), '') as translation
        FROM
          transcription
          LEFT JOIN alignment_translation
            on transcription.id = alignment_translation.transcription_id
          LEFT JOIN  translation
            ON alignment_translation.translation_id = translation.id
        WHERE
          transcription.id = {transcription_id}     
        ORDER BY
   CASE WHEN NOT EXISTS(SELECT * FROM alignment_translation where transcription_id={transcription_id}  AND ptr_transcription_end IS NULL)
  THEN
    ptr_transcription_start
  ELSE
    ptr_translation_start
  END,
    CASE WHEN NOT EXISTS(SELECT * FROM alignment_translation where transcription_id={transcription_id}  AND ptr_transcription_end IS NULL)
  THEN
    ptr_transcription_end
  ELSE
    ptr_translation_end
  END
        """.format(transcription_id=transcription_id)

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
            stmt = TestTranscriptionTranslationAlignment.get_alignment_stmt(doc)
            res = db.engine.execute(stmt)
            res = [r for r in res]

            # expect consistency between translation and traduction ids (error shouldn't happen)
            transcription_ids = set()
            translation_ids = set()
            for (transcription_id, translation_id, a, b) in res:
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

                stmt = TestTranscriptionTranslationAlignment.get_alignment_stmt(doc)
                res = db.engine.execute(stmt)
                res = [r for r in res]

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

            print("Alignment transcription/translation for doc {0} is OK".format(doc) )


if __name__ == '__main__':
    unittest.main()
