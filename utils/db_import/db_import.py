# -*- coding: utf-8 -*-
import copy
import itertools
import re
import os
import pprint
import lxml.etree as ET

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session

def name_for_collection_relationship(base, local_cls, referred_cls,constraint):
    disc = '_'.join(col.name for col in constraint.columns)
    return referred_cls.__name__.lower() + '_' + disc + "_collection"

"""
CONSTS
"""
ROOT="/Users/mrgecko/Documents/Dev/Data/adele/dossiers"
DEST="../sql"
NS_TI={"ti":"http://www.tei-c.org/ns/1.0"}
USERNAME="jpilla"


NOTE_TYPES={
  "TERM" : 0
}

"""
GLOBAL
"""
note_id = 0
translation_id = 0
transcription_id = 0

##Base = automap_base()
##engine = create_engine("sqlite:////Users/mrgecko/Documents/Dev/Data/adele/adele.sqlite")
##Base##.prepare(engine, reflect=True, name_for_collection_relationship=name_for_collection_relationship)
##session = create_session(bind=engine)

"""
XPATH
"""
XPATH_TI_FACSIM_COORDS_TRANSCRIPTION="//ti:div[@type='facsimile']//ti:seg/@rend"
XPATH_TI_FACSIM_ANNO_TRANSCRIPTION="//ti:div[@type='facsimile']//ti:seg"

XPATH_TI_FACSIM_COORDS_FIGDESC="//ti:figDesc//ti:seg/@rend"
XPATH_TI_FACSIM_ANNO_FIGDESC="//ti:figDesc//ti:seg"

XPATH_TI_TRANSCRIPTION="//ti:div[@type='transcription']"
XPATH_TI_TRANSLATION="//ti:div[@type='translation']"

XPATH_TI_ARGUMENT="//ti:div[@type='regeste']/ti:p"



"""
helpers
"""
get_manifest_url = lambda id: "http://193.48.42.68/adele/iiif/manifests/man{0}.json".format(id)
get_image_id = lambda id: "http://193.48.42.68/loris/adele/dossiers/{0}.jpg/full/full/0/default.jpg".format(id)

get_insert_stmt = lambda table,fields,values: "INSERT INTO {0} ({1}) VALUES ({2});".format(table, fields, values)
get_update_stmt = lambda table,values,where_clause="": "UPDATE {0} SET {1} {2};".format(table, values, where_clause)
get_delete_stmt = lambda table,where_clause="": "DELETE FROM {0} {1};".format(table, where_clause)

clean_entities = lambda s: s.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
nullIfNone = lambda v, callback=None : "null" if v is None else callback(v) if callback is not None else v
escapeQuotes = lambda s: s.replace('"', '\\"')

def get_rid_of_terms(content):
    while content.find('<term') > -1:
        content = re.sub('<term[^>]*>', repl='', string=content, count=1)
        content = re.sub('</term[^>]*>', repl='', string=content, count=1)
    return content


def stringify_children(node):
    from itertools import chain
    from lxml.etree import tounicode

    if node.tail is not None and '\n' in node.tail:
        node.tail = ""

    s = ''.join(
        chunk for chunk in chain(
            (node.text,),
            chain(*((tounicode(child, with_tail=False), child.tail) for child in node.getchildren())),
            (node.tail,)) if chunk)
    s = s.replace(' xmlns="http://www.tei-c.org/ns/1.0"', '')
    s = s.replace(u'\xa0', ' ')
    return re.sub('\n', '', s)#.rstrip()

p = re.compile("<[^>]+>((.|\s)*)<\/[^>]+>")
def get_tag_xml_content(node):
    m = re.match(p, ET.tounicode(node))
    return m.group(1) if m is not None else None

def get_text_format(div):
    verses = div.xpath("ti:l", namespaces=NS_TI)
    head = div.xpath("ti:head", namespaces=NS_TI)
    p = div.xpath("ti:p", namespaces=NS_TI)
    return {
        "verses": verses, "has_verses" : len(verses) > 0,
        "head": head, "has_head" : len(head) > 0,
        "p": p, "has_p" : len(p) > 0
    }


def remove_nodes(node, tag, ns):
    ET.strip_elements(node, "{"+ns+"}"+tag, with_tail=False)
    return node


def extract_terms(e):
    global note_id
    es = stringify_children(e)
    terms = []

    for term in e.xpath("//ti:term", namespaces=NS_TI):
        terms.append({"content": term.get("n"),
                      "id": note_id,
                      "type_id": NOTE_TYPES["TERM"]
                      })
        note_id += 1
    return (es, terms)


"""
inserts
"""
def insert_image_zone(dossier):
    values = []
    zone_id = 1
    for t in dossier["image_zone"]:
        values.append([
            dossier["manifest_url"],
            dossier["img_id"],
            str(zone_id),
            t["coords"],
            nullIfNone(t["note"], lambda t: "'{0}'".format(t))
        ])
        zone_id += 1
    #generate insert statements
    stmts = [ get_insert_stmt("image_zone", "manifest_url,img_id,zone_id,coords,note",
                              '"{0}","{1}",{2},"{3}",{4}'.format(*value))
        for value in values
    ]
    return stmts

def insert_image(dossier):
    stmts = [
        get_insert_stmt("image",
                        "manifest_url,img_id,doc_id",
                        '"{0}","{1}",{2}'.format(dossier["manifest_url"], dossier["img_id"], dossier["id"]))
    ]
    return stmts

def insert_text(dossier, text_name):
    stmts = []
    if len(dossier[text_name]) > 0:
        content = " ".join(dossier[text_name])
        #create note ptrs
        idx=0
        while content.find("<term") > -1:
            ptr_start = content.find("<term")
            content = re.sub("<term[^>]*>", repl='', string=content, count=1)
            ptr_end = content.find("</term")
            content = re.sub("</term[^>]*>", repl='', string=content, count=1)
            dossier[text_name+"_notes"][idx]["ptr_start"] = ptr_start
            dossier[text_name+"_notes"][idx]["ptr_end"] = ptr_end
            idx += 1

        stmts = [
            get_insert_stmt(text_name,
                            "id,doc_id,user_id,content",
                            "{0},{1},'{2}','{3}'".format(dossier["id"], dossier["id"], 1, content)
                            )
        ]
    return stmts

def insert_translation(dossier):
    return insert_text(dossier, "translation")

def insert_transcription(dossier):
    return insert_text(dossier, "transcription")

def insert_note(note):
    note["content"] = note["content"].replace("@", ">")
    stmts = [
        get_insert_stmt("note",
                        "id,type_id,user_id,content",
                        "{0},{1},'{2}','{3}'".format(note["id"], note["type_id"], USERNAME, note["content"]))
    ]
    return stmts

def insert_note_types():
    stmts = [
        get_insert_stmt("note_type",
                        "note_type_id,note_type_label",
                        "{0},'{1}'".format(id, label)
                        )
        for label, id in NOTE_TYPES.items()
    ]
    return stmts

def insert_transcription_has_note(dossier):
    stmts = [
        get_insert_stmt("transcription_has_note",
                        "transcription_id,note_id,ptr_start,ptr_end",
                        "{0},{1},{2},{3}".format(dossier["transcription_id"], note["id"],
                                                 note["ptr_start"], note["ptr_end"])
                        )
        for note in dossier["transcription_notes"]
    ]

    #if dossier["id"] == '20':
    #    pprint.pprint(dossier)
    #    print(stmts)

    return stmts

def insert_translation_has_note(dossier):
    #ids  = [d["id"] for d in dossier["transcription_notes"]]
    #for i, id in enumerate(ids):
    #    dossier["translation_notes"][i]["id"] = id

    stmts = [
        get_insert_stmt("translation_has_note",
                        "translation_id,note_id,ptr_start,ptr_end",
                        "{0},{1},{2},{3}".format(dossier["translation_id"],
                                                 note["id"],
                                                 note["ptr_start"], note["ptr_end"])
                        )
        for note in dossier["translation_notes"]
    ]
    return stmts

def update_argument(dossier):
    argument = "null" if dossier["argument"] is None else "'{0}'".format(clean_entities(dossier["argument"]))
    stmts = [
        get_update_stmt("document",
                        "argument={0}".format(argument),
                        "WHERE doc_id={0}".format(dossier["id"]))
    ]
    return stmts

def insert_alignemnt_transcription_translation(session, id1, id2, p1, p2, p3, p4):
    #print(id1, id2, p1, p2, p3, p4)
    #altr = Base.metadata.tables["alignment_translation"].insert()
    #ins = altr.values(translation_id=id1,
    #                  transcription_id=id2,
    #                  ptr_transcription_start=p1,
    #                  ptr_transcription_end=p2,
    #                  ptr_translation_start=p3,
    #                  ptr_translation_end=p4,
    #)
    #ins.compile()
    #res = session.execute(ins)
    res = None
    return res

"""
validity checks
"""
check_coords_validity = lambda coords : [int(c) for c in coords.split(",")]
facsim_coords_error = []


cnt_trancription_has_verses = 0
cnt_trancription_has_head = 0
cnt_trancription_has_p = 0
cnt_translation_has_verses = 0
cnt_translation_has_head = 0
cnt_translation_has_p = 0

cnt_file_parsing_error = 0

"""
=====================================
processing
=====================================
"""
dossiers = {}
filenames = [f for f in os.listdir(ROOT) if f.endswith(".xml")]
filenames.sort()

for f in filenames:
    print(f)
    """
    Initialisation des dossiers
    """
    id = f.split(".")[0]
    dossiers[f] = {
        "id": id,
        "argument": None,
        "manifest_url": get_manifest_url(id),
        "img_id": get_image_id(id),
        "image_zone" : [],
        "transcription_notes" : [],
        "translation_notes": [],
        "transcription" : [],
        "transcription_id": id,
        "translation" : [],
        "translation_id": id,
        "alignment_transcription_ptrs" : [],
        "alignment_translation_ptrs": [],
    }

    #transcription_id += 1
    #translation_id += 1


    """
    tables image & image_zone
    """
    try:
        doc = ET.parse(os.path.join(ROOT,f))
    except:
        cnt_file_parsing_error += 1
        break

    terms = doc.xpath("//ti:term", namespaces=NS_TI)
    for t in terms:
        if t.get("n") is not None:
            if ">" in t.get("n"):
                t.set("n", t.get("n").replace(">", "@"))
                print(t.get("n"))

    """
    regeste
    """
    regeste = doc.xpath(XPATH_TI_ARGUMENT, namespaces=NS_TI)
    if len(regeste) == 0:
        pass
    else:
        dossiers[f]["argument"] = "<p>{0}</p>".format(stringify_children(regeste[0]))

    """
    For the time being we just skipp <add> tags 
    """
    facsim_coord_tr = doc.xpath(XPATH_TI_FACSIM_COORDS_TRANSCRIPTION, namespaces=NS_TI)
    facsim_note_tr = doc.xpath(XPATH_TI_FACSIM_ANNO_TRANSCRIPTION, namespaces=NS_TI)

    facsim_coord_figdesc = doc.xpath(XPATH_TI_FACSIM_COORDS_FIGDESC, namespaces=NS_TI)
    facsim_note_figdesc = doc.xpath(XPATH_TI_FACSIM_ANNO_FIGDESC, namespaces=NS_TI)

    # Récupérations des zones de transcription
    for coords_tr, note_tr in zip(facsim_coord_tr, facsim_note_tr):
        try:
            check_coords_validity(coords_tr)
            dossiers[f]["image_zone"].append({"coords": coords_tr, "note": None})
        except ValueError:
            facsim_coords_error.append((f, coords_tr))
    # Récupération des zones d'annotations & l'annotation associée
    for coords_figdesc, note_figdesc in zip(facsim_coord_figdesc, facsim_note_figdesc):
        try:
            check_coords_validity(coords_figdesc)
            dossiers[f]["image_zone"].append({"coords": coords_figdesc, "note": clean_entities(get_tag_xml_content(note_figdesc))})
        except ValueError:
            facsim_coords_error.append((f, coords_figdesc))

    """
        textes
    """
    def add_text_and_notes(f, txt_name, txt_array):
        if len(txt_array) > 0:
            tf =  get_text_format(txt_array[0])
            char_index = 1
            ##transcription
            for i, v in enumerate(tf["verses"]):
                verse = remove_nodes(copy.deepcopy(v), "add", NS_TI["ti"])
                verse, terms = extract_terms(verse)
                #verse = clean_entities(verse)
                if len(verse.strip()) > 0:
                    verse_wo_terms = clean_entities(get_rid_of_terms(verse))
                    verse_with_terms = clean_entities(verse)
                    dossiers[f][txt_name].append(verse_with_terms)
                    dossiers[f][txt_name+"_notes"] += terms

                    dossiers[f]["alignment_"+txt_name+"_ptrs"].append(
                        (char_index, char_index+len(verse_wo_terms))
                    )
                    char_index += len(verse_wo_terms)
                else:
                    #cas des verses auto fermants <l/>
                    dossiers[f]["alignment_"+txt_name+"_ptrs"].append(
                        (char_index, char_index)
                    )
            return tf
        return None


    """
    tables transcription & note & transcriptionHasNote
    """
    transcriptions = doc.xpath(XPATH_TI_TRANSCRIPTION, namespaces=NS_TI)
    add_text_and_notes(f, "transcription", transcriptions)
    """
    tables translation & note & translationHasNote
    """
    translations = doc.xpath(XPATH_TI_TRANSLATION, namespaces=NS_TI)
    tf = add_text_and_notes(f, "translation", translations)


    # update the db with the alignment data
    #if tf is not None and tf["has_verses"]:
    #    id1 = id
    #    id2 = id
    #    session.execute("DELETE FROM alignment_translation "
    #                    "WHERE translation_id={0} and transcription_id={1};".format(id1, id2))
    #
    #    for ((p1, p2), (p3, p4)) in itertools.zip_longest(
    #            dossiers[f]["alignment_transcription_ptrs"],
    #            dossiers[f]["alignment_translation_ptrs"],
    #            fillvalue=("null", "null")):
    #        insert_alignemnt_transcription_translation(session, id1, id2, p1, p2, p3, p4)
    #
    #    print("--- with verses ", f, id1, id2)


"""
display
"""
print("=" * 80)
print("facsim coords error:")
pprint.pprint(set(facsim_coords_error))
print("file parsing error (nb files): {0}".format(cnt_file_parsing_error))
print("=" * 80)
#print("Transcription with verses: {0}".format(cnt_trancription_has_verses))
#print("Transcription with head: {0}".format(cnt_trancription_has_head))
#print("#Transcription with p: {0}".format(cnt_trancription_has_p))
#print("Translation with verses: {0}".format(cnt_translation_has_verses))
#print("Translation with head: {0}".format(cnt_translation_has_head))
#print("Translation with p: {0}".format(cnt_translation_has_p))

add_sql_comment = lambda f, c="=": f.write("--" + c * 40 + "\n")


print("=" * 80)
print("SQL statements written to 'insert_statements.sql'")
with open('{0}/update_document_stmts.sql'.format(DEST), 'w+') as f_document,\
     open('{0}/insert_img_stmts.sql'.format(DEST), 'w+') as f_img,\
     open('{0}/insert_transcription_stmts.sql'.format(DEST), 'w+') as f_transcription,\
     open('{0}/insert_translation_stmts.sql'.format(DEST), 'w+') as f_translation,\
     open('{0}/insert_types_stmts.sql'.format(DEST), 'w+') as f_types,\
     open('{0}/insert_notes_stmts.sql'.format(DEST), 'w+') as f_notes:

    f_img.write(get_delete_stmt("image_zone") + "\n")
    f_img.write(get_delete_stmt("image") + "\n")

    f_transcription.write(get_delete_stmt("transcription") + "\n")
    f_translation.write(get_delete_stmt("translation") + "\n")
    f_types.write(get_delete_stmt("note_type") + "\n")
    f_notes.write(get_delete_stmt("note") + "\n")
    f_notes.write(get_delete_stmt("translation_has_note") + "\n")
    f_notes.write(get_delete_stmt("transcription_has_note") + "\n")

    add_sql_comment(f_img, '#')

    for dossier in dossiers.values():

        #table_document
        for a in update_argument(dossier):
            f_document.write(a + "\n")

        #table image
        for i in insert_image(dossier):
            f_img.write(i + "\n")

        add_sql_comment(f_img, '-')

        #table image_zone
        for i in insert_image_zone(dossier):
            f_img.write(i + "\n")
        add_sql_comment(f_img, '=')

        #table transcription
        for t in insert_transcription(dossier):
            f_transcription.write(t + "\n")

        #table translation
        for t in insert_translation(dossier):
            f_translation.write(t + "\n")

        add_sql_comment(f_notes, '=')
        #table note
        for note in dossier["transcription_notes"]:
            for t in insert_note(note):
                f_notes.write(t + "\n")
        add_sql_comment(f_notes, '-')
        for note in dossier["translation_notes"]:
            for t in insert_note(note):
                f_notes.write(t + "\n")

        add_sql_comment(f_notes, '-')
        for hasNote in insert_transcription_has_note(dossier):
            f_notes.write(hasNote + "\n")
        add_sql_comment(f_notes, '-')
        for hasNote in insert_translation_has_note(dossier):
            f_notes.write(hasNote + "\n")

    #note types
    for t in insert_note_types():
        f_types.write(t + "\n")
