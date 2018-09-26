import re
from lxml import etree


NS_TI = {"ti": "http://www.tei-c.org/ns/1.0"}
XPATH_TI_TRANSCRIPTION = "//ti:div[@type='transcription']/ti:l"
XPATH_TI_TRANSLATION = "//ti:div[@type='translation']/ti:l"

p = re.compile("<[^>]+>((.|\s)*)<\/[^>]+>")
def get_tag_xml_content(node):
    m = re.match(p, etree.tounicode(node))
    return m.group(1) if m is not None else None

def get_rid_of_terms(content):
    while content.find('<term') > -1:
        content = re.sub('<term[^>]*>', repl='', string=content, count=1)
        content = re.sub('</term[^>]*>', repl='', string=content, count=1)
    return content


def get_insert_alignment(id, a, b, c, d):
    return "INSERT INTO main.alignment_translation values(%s,%s,%s,%s,%s,%s);\n" % (id, id, a, b, c ,d)


def get_insert_transcription(id, user_id, txt):
    return "INSERT INTO main.transcription values(%s, %s, %s, '%s');\n" % (id, id, user_id, txt.replace("'", "\'"))


def get_insert_translation(id, user_id, txt):
    return "INSERT INTO main.translation values(%s, %s, %s, '%s');\n" % (id, id, user_id, txt.replace("'", "\'"))


def get_ptrs(lines):
    offset = 0
    full_text = ""
    ptrs_list = []
    for i, l in enumerate(lines):

        xml = get_tag_xml_content(l)
        empty = xml is None

        if not empty:

            if i == 0:
                xml = "<p>" + xml
            if i < len(lines) - 1:
                xml += " "
            else:
                xml += "</p>"

            t = get_rid_of_terms(xml)
            ptrs = (offset, offset + len(t))
            # print("%s-%s: '%s'" % (ptrs[0], ptrs[1], t))
            offset += len(t)
            full_text += t
            ptrs_list.append(ptrs)
        else:
            pass
            ptrs_list.append((offset, offset))
            # print("******************")
    return full_text, ptrs_list



def write_al_stmts(al, doc_id, ptrs_transcription, ptrs_translation):
    for i, (a, b) in enumerate(ptrs_transcription):
        c, d = ptrs_translation[i]
        stmt = get_insert_alignment(doc_id, a, b, c, d)
        al.write(stmt)


alignment_filename = "./alignment.sql"
transcription_translation_filename = "./transcription_translation.sql"
SRC_PATH = '/home/mrgecko/dev/ENC/adele/dossiers'

with open(alignment_filename, 'w') as al, open(transcription_translation_filename, 'w') as tt:
    from os import listdir
    from os.path import isfile, join

    files = [25]#[20,22,23,24,25,26,27,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95]

    for doc_id in files:
        #print(doc_id)
        filename = "/home/mrgecko/dev/ENC/adele/dossiers/%s.xml" % doc_id
        with open(filename, 'r') as f:
            tree = etree.parse(f)

            lines = tree.xpath(XPATH_TI_TRANSCRIPTION, namespaces=NS_TI)
            transcription, ptrs_transcription = get_ptrs(lines)

            lines = tree.xpath(XPATH_TI_TRANSLATION, namespaces=NS_TI)
            translation, ptrs_translation = get_ptrs(lines)

            tt.write("DELETE FROM main.transcription where doc_id=%s;\n" % doc_id)
            tt.write("DELETE FROM main.translation where doc_id=%s;\n" % doc_id)

            tt.write(get_insert_transcription(doc_id, 4, transcription))
            tt.write(get_insert_translation(doc_id, 4, translation))

            if len(ptrs_transcription) > 0 and len(ptrs_translation) > 0:
                al.write("-- doc %s\n" % doc_id)
                al.write("DELETE FROM main.alignment_translation where main.alignment_translation.transcription_id=%s;\n" % doc_id)

                if len(ptrs_transcription) == len(ptrs_translation):
                    write_al_stmts(al, doc_id, ptrs_transcription, ptrs_translation)
                    for i, (a, b) in enumerate(ptrs_transcription):
                        c, d = ptrs_translation[i]
                        print("'%s'" % transcription[a:b])
                elif len(ptrs_transcription) > len(ptrs_translation):
                    print("Doc %s has a transcription longer than its translation" % doc_id)
                    last_idx = len(ptrs_translation) - 1
                    ptrs_transcription[last_idx:] = [(ptrs_transcription[last_idx][0], ptrs_transcription[len(ptrs_transcription)-1][1])]
                    write_al_stmts(al, doc_id, ptrs_transcription, ptrs_translation)
                    for i, (a, b) in enumerate(ptrs_transcription):
                        c, d = ptrs_translation[i]
                        print(a, b, "'%s'" % transcription[a:b])
                else:
                    print("Doc %s has a translation longer than its transcription" % doc_id)
                    last_idx = len(ptrs_transcription) - 1
                    ptrs_translation[last_idx:] = [(ptrs_translation[last_idx][0], ptrs_translation[len(ptrs_translation)-1][1])]
                    write_al_stmts(al, doc_id, ptrs_transcription, ptrs_translation)
                    #print(ptrs_transcription, ptrs_translation)
                    for i, (a, b) in enumerate(ptrs_translation):
                        c, d = ptrs_translation[i]
                        print("'%s'" % translation[c:d])
                #
            else:
                print("no transcription nor translation for doc %s " % doc_id)