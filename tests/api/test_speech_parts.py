from os.path import join

from app import db
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestSpeechPartsAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "alignments_discours", "alignments_discours_doc_21_prof1.sql"),
    ]

    def test_insert_speech_parts_into_text(self):
        self.load_fixtures(TestSpeechPartsAPI.FIXTURES)

        from app.api.alignments.alignments_discours import add_speechparts_refs_to_text
        from app.models import AlignmentDiscours

        text = "<p>this is a simple <b>text</b>.</p>"
        alignments = AlignmentDiscours.query.filter(AlignmentDiscours.user_id == 4,
                                                    AlignmentDiscours.transcription_id == 21).all()

        rich_content = add_speechparts_refs_to_text(text, alignments)
        expected_output = "<p><span class='speech-part type-01' data-note-id='0000000001'>this</span><span class='speech-part type-02' data-note-id='0000000002'> is a simple</span> <span class='speech-part type-03' data-note-id='0000000003'><b>text</b></span>.</p>"

        self.assertEqual(expected_output, rich_content)

    def test_view_speech_parts(self):
        self.load_fixtures(TestSpeechPartsAPI.FIXTURES)

        self.assert404("/api/1.0/documents/21/view/speech-parts")
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)

        r = self.assert200("/api/1.0/documents/21/view/speech-parts")
        r = json_loads(r.data)['data']

        self.assertEqual(3, len(r['notes']))
