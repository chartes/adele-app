import os
import unittest
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from sqlalchemy import create_engine

from config import Config

NS_TI = {"ti": "http://www.tei-c.org/ns/1.0"}


class TestTranscriptionTranslationAlignment(unittest.TestCase):

    ALIGNMENT_STMT = lambda doc_id, transcription_id : """
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
      JOIN alignment_translation
        on transcription.transcription_id = alignment_translation.transcription_id
      JOIN  translation
        ON alignment_translation.translation_id = translation.translation_id
    WHERE
      transcription.transcription_id = {transcription_id} 
      and
      transcription.doc_id = {doc_id} 
      and 
      translation.doc_id = {doc_id}
    ;
    """.format(doc_id=doc_id, transcription_id=transcription_id)

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
        for root, directories, filenames in os.walk('utils/tests/data/transcription'):
            for filename in filenames:
                if filename.endswith(".txt"):
                    cls.doc_list.append(filename.split(".")[0])

        print("Tested docs:", cls.doc_list)


    def test_both_ids_match(self):
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            stmt = TestTranscriptionTranslationAlignment.ALIGNMENT_STMT(doc, doc)
            res = self.engine.execute(stmt).fetchall()
            # expect consistency between translation and traduction ids (shouldn't happen)
            transcription_ids = set()
            translation_ids = set()
            for (transcription_id, translation_id, a, b) in res:
                transcription_ids.add(transcription_id)
                translation_ids.add(translation_id)
            self.assertSetEqual(transcription_ids, translation_ids, "Something is wrong with the IDs")

    def test_alignment_is_correct(self):
        for doc in TestTranscriptionTranslationAlignment.doc_list:
            with open("utils/tests/data/transcription/{0}.txt".format(doc), "r") as transcription_f, \
                 open("utils/tests/data/translation/{0}.txt".format(doc), "r") as translation_f:
                transcription_lines = transcription_f.read().splitlines()
                translation_lines = translation_f.read().splitlines()

                stmt = TestTranscriptionTranslationAlignment.ALIGNMENT_STMT(doc, doc)
                res = self.engine.execute(stmt).fetchall()

                for i, transcription in enumerate(transcription_lines):
                    self.assertEqual(res[i]["transcription"], transcription, "Transcription ptrs look wrong for doc {0}".format(doc))

                for i, translation in enumerate(translation_lines):
                    self.assertEqual(res[i]["translation"], translation, "Translation ptrs look wrong for doc {0}".format(doc))



if __name__ == '__main__':
    unittest.main()
