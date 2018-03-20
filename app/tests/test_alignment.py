import os
import unittest
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from sqlalchemy import create_engine

from config import Config

NS_TI = {"ti": "http://www.tei-c.org/ns/1.0"}
TEST_DATA_DIR = "app/tests/data"


class TestTranscriptionTranslationAlignment(unittest.TestCase):

    ALIGNMENT_STMT = lambda transcription_id : """
    -- Transcription vs Translation
    SELECT
      transcription.transcription_id,
      translation.translation_id,
      substr(transcription.content, ptr_transcription_start, 
        ptr_transcription_end - ptr_transcription_start) as transcription,
      substr(translation.content, ptr_translation_start, 
        ptr_translation_end - ptr_translation_start) as translation
    FROM
      transcription
      LEFT JOIN alignment_translation
        on transcription.transcription_id = alignment_translation.transcription_id
      LEFT JOIN  translation
        ON alignment_translation.translation_id = translation.translation_id
    WHERE
      transcription.transcription_id = {transcription_id}      
    ;
    """.format(transcription_id=transcription_id)

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///{url}".format(url=Config.TESTS_DB_URL))

        def name_for_collection_relationship(base, local_cls, referred_cls, constraint):
            disc = '_'.join(col.name for col in constraint.columns)
            return referred_cls.__name__.lower() + '_' + disc + "_collection"
        automap_base().prepare(cls.engine, reflect=True,
                               name_for_collection_relationship=name_for_collection_relationship)

        cls.session = create_session(bind=cls.engine)

        cls.doc_list = []
        for root, directories, filenames in os.walk(os.path.join(TEST_DATA_DIR, 'transcription')):
            for filename in filenames:
                if filename.endswith("10.txt"):
                    cls.doc_list.append(filename.split(".")[0])

        cls.doc_list.sort()
        print("Tested docs:", cls.doc_list)


    def test_both_ids_match(self):
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            stmt = TestTranscriptionTranslationAlignment.ALIGNMENT_STMT(doc)
            res = self.engine.execute(stmt).fetchall()
            # expect consistency between translation and traduction ids (shouldn't happen)
            transcription_ids = set()
            translation_ids = set()
            for (transcription_id, translation_id, a, b) in res:
                if translation_id is not None:
                    transcription_ids.add(transcription_id)
                    translation_ids.add(translation_id)
            self.assertSetEqual(transcription_ids, translation_ids, "Something is wrong with the IDs")

    def test_alignment_is_correct(self):
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            with open(os.path.join(TEST_DATA_DIR, "transcription", "{0}.txt").format(doc), "r") as transcription_f, \
                 open(os.path.join(TEST_DATA_DIR, "translation", "{0}.txt").format(doc), "r") as translation_f:
                transcription_lines = transcription_f.read().splitlines()
                translation_lines = translation_f.read().splitlines()

                stmt = TestTranscriptionTranslationAlignment.ALIGNMENT_STMT(doc)
                res = self.engine.execute(stmt).fetchall()

                if len(translation_lines) == 0:
                    translation_ids = set([l["translation_id"] for l in res if l["translation_id"] != None])
                    self.assertEqual(len(translation_ids), 0, "There is no translation for doc {0}".format(doc))
                else:
                    self.assertEqual(len([l for l in transcription_lines if len(l)>0]), len([l["transcription"] for l in res if len(l["transcription"])>0]), "Transcription lines count does not match for doc {0}".format(doc))
                    for i, transcription in enumerate(transcription_lines):
                        print(res[i])
                        self.assertEqual(res[i]["transcription"], transcription, "Transcription ptrs look wrong for doc {0}".format(doc))

                    self.assertEqual(len([l for l in translation_lines if len(l)>0]), len([l["translation"] for l in res if len(l["translation"])>0]), "Translation lines count does not match for doc {0}".format(doc))
                    for i, translation in enumerate(translation_lines):
                        self.assertEqual(res[i]["translation"], translation, "Translation ptrs look wrong for doc {0}".format(doc))

            print("Alignment transcription/translation for doc {0} is OK".format(doc) )



if __name__ == '__main__':
    unittest.main()
