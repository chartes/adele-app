from app import db
from app.models import Transcription, TranscriptionHasNote, Translation, Commentary, CommentaryHasNote, TranslationHasNote, \
    Note


class TranscriptionNoteBinder(object):
    
    username_field = "transcription_username"
    get_endpoint_name = "api_bp.api_documents_transcriptions_notes"

    @staticmethod
    def get_notes(doc_id):
        # TODO gérer erreur
        transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id).all()
        notes = []
        for tr in transcriptions:
            for thn in tr.notes:
                if thn.note is not None:
                    notes.append(thn.note)
        return notes

    @staticmethod
    def bind(note, data, usr_id, doc_id):
        # TODO gerer erreur
        transcription = Transcription.query.filter(Transcription.user_id == usr_id,
                                                   Transcription.doc_id == doc_id).first()
        transcription_has_note = TranscriptionHasNote()
        transcription_has_note.transcription = transcription
        transcription_has_note.transcription_id = transcription.id
        transcription_has_note.note = note
        transcription_has_note.ptr_start = data["ptr_start"]
        transcription_has_note.ptr_end = data["ptr_end"]
        note.transcription = [transcription_has_note]
        return note

    @staticmethod
    def update(doc_id, data):
        # TODO gérer erreur
        # get the note to update
        note = Note.query.filter(Note.id == data["note_id"]).one()
        note.content = data["content"]

        transcription_has_note = note.transcription[0]
        transcription_has_note.ptr_start = data["ptr_start"]
        transcription_has_note.ptr_end = data["ptr_end"]

        db.session.add(note)
        db.session.add(transcription_has_note)

        return note


class TranslationNoteBinder(object):

    username_field = "translation_username"
    get_endpoint_name = "api_bp.api_documents_translations_notes"

    @staticmethod
    def get_notes(doc_id):
        # TODO gérer erreur
        translations = Translation.query.filter(Translation.doc_id == doc_id).all()
        notes = []
        for tr in translations:
            for thn in tr.notes:
                if thn.note is not None:
                    notes.append(thn.note)
        return notes

    @staticmethod
    def bind(note, data, usr_id, doc_id):
        # TODO gerer erreur
        translation = Translation.query.filter(Translation.user_id == usr_id,
                                               Translation.doc_id == doc_id).first()
        translation_has_note = TranslationHasNote()
        translation_has_note.translation = translation
        translation_has_note.translation_id = translation.id
        translation_has_note.note = note
        translation_has_note.ptr_start = data["ptr_start"]
        translation_has_note.ptr_end = data["ptr_end"]
        note.translation = [translation_has_note]
        return note

    @staticmethod
    def update(doc_id, data):
        # TODO gérer erreur
        # get the note to update
        note = Note.query.filter(Note.id == data["note_id"]).one()

        translation_has_note = note.translation[0]
        translation_has_note.ptr_start = data["ptr_start"]
        translation_has_note.ptr_end = data["ptr_end"]

        db.session.add(note)
        db.session.add(translation_has_note)

        return note


class CommentaryNoteBinder(object):

    username_field = "commentary_username"
    get_endpoint_name = "api_bp.api_documents_commentaries_notes"

    @staticmethod
    def get_notes(doc_id):
        # TODO gérer erreur
        commentaries = Commentary.query.filter(Commentary.doc_id == doc_id).all()
        notes = []
        for tr in commentaries:
            for thn in tr.notes:
                if thn.note is not None:
                    notes.append(thn.note)
        return notes

    @staticmethod
    def bind(note, data, usr_id, doc_id):
        # TODO gerer erreur
        commentary = Commentary.query.filter(Commentary.user_id == usr_id,
                                             Commentary.doc_id == doc_id,
                                             Commentary.type_id == data["type_id"]).first()
        commentary_has_note = CommentaryHasNote()
        commentary_has_note.commentary = commentary
        commentary_has_note.commentary_id = commentary.id
        commentary_has_note.note = note
        commentary_has_note.ptr_start = data["ptr_start"]
        commentary_has_note.ptr_end = data["ptr_end"]
        note.commentary = [commentary_has_note]
        return note

    @staticmethod
    def update(doc_id, data):
        # TODO gérer erreur
        # get the note to update
        note = Note.query.filter(Note.id == data["note_id"]).one()

        commentary_has_note = note.commentary[0]
        commentary_has_note.ptr_start = data["ptr_start"]
        commentary_has_note.ptr_end = data["ptr_end"]

        db.session.add(note)
        db.session.add(commentary_has_note)

        return note
