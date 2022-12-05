from app.models import User, Role, Document, Transcription, Translation, Whitelist, Note, Commentary

teacher_role = Role.query.filter(Role.name == "teacher").one()
student_role = Role.query.filter(Role.name == "student").one()
admin_role = Role.query.filter(Role.name == "admin").one()


def reset_entity(db, model, entity_data):
    e = model.query.filter(model.id == entity_data["id"]).first()
    if e:
        db.session.delete(e)
        print(str(e), "deleted.")
        db.session.commit()

    entity = model(**entity_data)
    db.session.add(entity)
    db.session.commit()
    print(str(entity), "added.")


def load_users(db):
    # ====================
    # load users
    # ====================
    _users = [
        {
            "id": 260922,
            "username": "Indi",
            "first_name": "Henry",
            "last_name": "Jones",
            "active": 1,
            "email": "indi@indi.indi",
            "roles": [teacher_role]
        },
        {
            "id": 135556,
            "username": "LedZep",
            "first_name": "Robert",
            "last_name": "Plant",
            "active": 1,
            "email": "robert.plant@led.zep",
            "roles": [student_role]
        },
        {
            "id": 907770,
            "username": "SiouxieBanshee",
            "first_name": "Siouxie",
            "last_name": "Banshee",
            "active": 1,
            "email": "siouxie.bansheet@music.co",
            "roles": [student_role]
        }
    ]
    for u in _users:
        reset_entity(db, User, u)

    # ====================
    # load whitelist
    # ====================
    _whitelists = [
        {
            "id": 9905099,
            "label": "Classe 01",
            "users": User.query.filter(User.id.in_([u["id"] for u in _users])).all()
        }
    ]
    for w in _whitelists:
        reset_entity(db, Whitelist, w)

    return _users, _whitelists


def load_documents(db, _users, _whitelists):
    # ====================
    # load document
    # ====================
    _docs = [
        {
            "id": 99050,
            "title": "Manuscrit de Voynich",
            "subtitle": "Henry",
            "creation": 1922,
            "user_id": _users[0]["id"],
            "whitelist_id": _whitelists[0]["id"]
        }
    ]
    for d in _docs:
        reset_entity(db, Document, d)

    return _docs


def load_notes(db, _users):
    # ====================
    # load notes (2 for Jones, 1 for each student)
    # ====================
    _notes = [
        {
            "id": 10005000,
            "user_id": _users[0]["id"],
            "type_id": 0,
            "content": "<p>Annotation 1 du professeur </p>"
        },
        {
            "id": 10005001,
            "user_id": _users[0]["id"],
            "type_id": 0,
            "content": "<p>Annotation 2 du professeur</p>"
        },
        {
            "id": 10005003,
            "user_id": _users[1]["id"],
            "type_id": 0,
            "content": "<p>Annoté par %s </p>" % _users[1]["username"]
        },
        {
            "id": 10005004,
            "user_id": _users[2]["id"],
            "type_id": 0,
            "content": "<p>Annoté par %s </p>" % _users[2]["username"]
        },
    ]
    for n in _notes:
        reset_entity(db, Note, n)

    return _notes


def load_transcriptions(db, _docs, _users, _notes, _segments=False, _pos_u0=False, _pos_u1=False, _pos_u2=False):
    # ====================================================================
    # load transcriptions with notes, segmentation (teacher only)
    # and parts of speech (teacher and student 2)
    # ====================================================================

    _seg = '<adele-segment></adele-segment>' if _segments else ''

    _transcriptions = [
        {
            "id": 99050000,
            "doc_id": _docs[0]["id"],
            "user_id": _users[0]["id"],
            "content": f"<p><adele-note id='{_notes[0]['id']}'>Transcr<ex>iption</ex></adele-note> init<adele-note id='{_notes[1]['id']}'>iale</adele-note> du professeur Jones</p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ; peu importait où on la plaçait du moment qu'elle était là.</p>"
        },
        {
            "id": 99050001,
            "doc_id": _docs[0]["id"],
            "user_id": _users[1]["id"],
            "content": f"<p>Transcr<ex>iption</ex> <adele-note id='{_notes[2]['id']}'>initiale</adele-note> de {_users[1]['username']}</p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ;  peu importait où on la plaçait du moment qu'elle était là.</p>"
        },
        {
            "id": 99050002,
            "doc_id": _docs[0]["id"],
            "user_id": _users[2]["id"],
            "content": f"<p>Transcr<ex>iption</ex> <adele-note id='{_notes[3]['id']}'>initiale</adele-note> de {_users[2]['username']}</p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ; peu importait où on la plaçait du moment qu'elle était là.</p>"
        }
    ]

    for tr in _transcriptions:
        reset_entity(db, Transcription, tr)

    return _transcriptions


def load_translations(db, _users, _docs, _notes, _segments=False):
    # =============================================================
    # load translations with notes and segmentation (teacher only)
    # =============================================================

    _seg = '<adele-segment></adele-segment>' if _segments else ''

    _translations = [
        {
            "id": 22050000,
            "doc_id": _docs[0]["id"],
            "user_id": _users[0]["id"],
            "content": f"<p>Traduction init<adele-note id='{_notes[1]['id']}'>iale</adele-note> du professeur Jones </p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ; peu importait où on la plaçait du moment qu'elle était là.</p>"
        },
        {
            "id": 22050001,
            "doc_id": _docs[0]["id"],
            "user_id": _users[1]["id"],
            "content": f"<p>{_users[1]['username']} traduit <adele-note id='{_notes[2]['id']}'>ainsi</adele-note> : </p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ; peu importait où on la plaçait du moment qu'elle était là.</p>"
        },
        {
            "id": 22050002,
            "doc_id": _docs[0]["id"],
            "user_id": _users[2]["id"],
            "content": f"<p>{_users[2]['username']} traduit <adele-note id='{_notes[3]['id']}'>ainsi</adele-note> : </p>{_seg}<p>Pour les citoyens d'Ankh-Morpork, l'orthographe était pour ainsi dire en sus. Ils y croyaient comme ils croyaient à la ponctuation ; peu importait où on la plaçait du moment qu'elle était là.</p>"
        }
    ]

    for tl in _translations:
        reset_entity(db, Translation, tl)

    return _translations


def load_commentaries(db, _docs, _users, _notes):
    # ====================
    # load commentaries
    # teacher has zero coms, user 1 has two coms; user 2 has one com
    # ====================
    _commentaries = [
        {
            "id": 10003001,
            "doc_id": _docs[0]["id"],
            "type_id": 1,
            "user_id": _users[1]["id"],
            "content": f"<p>commentaire diplomatique <adele-note id='{_notes[2]['id']}'>initial</adele-note> de l'utilisateur {_users[1]['username']}</p>"
        },
        {
            "id": 10003002,
            "doc_id": _docs[0]["id"],
            "type_id": 2,
            "user_id": _users[1]["id"],
            "content": f"<p>commentaire historique <adele-note id='{_notes[2]['id']}'>initial</adele-note> de l'utilisateur {_users[1]['username']}</p>"
        },
        {
            "id": 10004001,
            "doc_id": _docs[0]["id"],
            "type_id": 1,
            "user_id": _users[2]["id"],
            "content": f"<p>commentaire diplomatique <adele-note id='{_notes[3]['id']}'>initial</adele-note> de l'utilisateur {_users[2]['username']}</p>"
        },
    ]
    for com in _commentaries:
        reset_entity(db, Commentary, com)

    return _commentaries


def load_fixtures(db):
    users, whitelists = load_users(db)
    docs = load_documents(db, _users=users, _whitelists=whitelists)
    notes = load_notes(db, _users=users)

    # transcriptions and translations without parts of speech and segmentation
    # transcriptions = load_transcriptions(db, _docs=docs, _users=users, _notes=notes)
    # translations = load_translations(db, _docs=docs, _users=users, _notes=notes)

    # transcriptions with segmentation (for transcription/translation alignment) and parts of speech for user0 (teacher) and user2
    transcriptions = load_transcriptions(db, _docs=docs, _users=users, _notes=notes, _segments=True, _pos_u0=True,
                                         _pos_u2=True)
    translations = load_translations(db, _docs=docs, _users=users, _notes=notes, _segments=True)
    coms = load_commentaries(db, _docs=docs, _users=users, _notes=notes)
