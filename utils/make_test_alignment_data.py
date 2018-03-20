import copy
import os
import re

import lxml.etree as ET


TEST_DATA_DEST="../app/tests/data"
ROOT="/Users/mrgecko/Documents/Dev/Data/adele/dossiers"
NS_TI={"ti":"http://www.tei-c.org/ns/1.0"}

XPATH_TI_TRANSCRIPTION="//ti:div[@type='transcription']"
XPATH_TI_TRANSLATION="//ti:div[@type='translation']"

NOTE_TYPES={
  "TERM" : 0
}

"""
GLOBAL
"""
note_id = 0
translation_id = 0
transcription_id = 0

clean_entities = lambda s: s.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")

def get_rid_of_notes(content):
    while content.find("<term") > -1:
        content = re.sub("<term[^>]*>", repl='', string=content, count=1)
        content = re.sub("</term[^>]*>", repl='', string=content, count=1)
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


def get_text_format(div):
    verses = div.xpath("ti:l", namespaces=NS_TI)
    head = div.xpath("ti:head", namespaces=NS_TI)
    p = div.xpath("ti:p", namespaces=NS_TI)
    return {
        "verses": verses, "has_verses" : len(verses) > 0,
        "head": head, "has_head" : len(head) > 0,
        "p": p, "has_p" : len(p) > 0
    }

def extract_terms(e):
    global note_id
    #es = stringify_children(e)
    terms = []

    for term in e.xpath("//ti:term", namespaces=NS_TI):
        terms.append({"content": term.get("n"),
                      "id": note_id,
                      "type_id": NOTE_TYPES["TERM"]
                      })
        note_id += 1
    return terms


def remove_nodes(node, tag, ns):
    ET.strip_elements(node, "{"+ns+"}"+tag, with_tail=False)
    return node


if __name__ == "__main__":

    filenames = [f for f in os.listdir(ROOT) if f.endswith(".xml")]
    filenames.sort()

    for f in filenames:
        print(f)

        doc_id = f.split(".")[0]

        with open(os.path.join(TEST_DATA_DEST, "transcription", "{0}.txt").format(doc_id), "w+") as transcription_f, \
             open(os.path.join(TEST_DATA_DEST, "translation", "{0}.txt").format(doc_id), "w+") as translation_f:

            doc = ET.parse(os.path.join(ROOT, f))

            transcriptions = doc.xpath(XPATH_TI_TRANSCRIPTION, namespaces=NS_TI)
            translations = doc.xpath(XPATH_TI_TRANSLATION, namespaces=NS_TI)

            def write_to_file(verses, f):
                if len(verses) > 0:
                    tf = get_text_format(verses[0])

                    for i, v in enumerate(tf["verses"]):
                        last_verse = i == len(tf["verses"]) - 1

                        verse = ET.tounicode(v)
                        verse_wo_terms = get_rid_of_notes(verse)
                        verse = ET.fromstring(verse_wo_terms)

                        verse_wo_add = remove_nodes(verse, "add", NS_TI["ti"])

                        verse = stringify_children(verse_wo_add)
                        verse = clean_entities(verse)
                        if len(verse.strip()) > 0:
                            print('"'+verse+'"')
                            f.write("{verse}{eol}".format(verse=verse,
                                                          eol="\n" if not last_verse else ""))
                        else:
                            f.write("\n")

            write_to_file(transcriptions, transcription_f)
            write_to_file(translations, translation_f)

