
import re
from fuzzywuzzy import fuzz




PLACEHOLDER = '@'
threshold = 30

data_with_tags = """ i<ex>n</ex> n<ex>ost</ex>ra constituti p<ex>re</ex>sentiaRicardus d<ex>i</ex>c<ex>t</ex>us de Gres de S<ex>an</ex>c<ex>t</ex>o Felice <ex>et</ex> Aya ejus uxor<ex>et</ex> Eufemia eor<ex>um</ex> filia recognov<ex>er</ex>unt se imp<ex>er</ex>petuumvendidisse p<ex>ro</ex> co<ex>m</ex>muni eor<ex>um</ex> utilitate ac necessitateabbati <ex>et</ex> conventui S<ex>an</ex>c<ex>t</ex>i G<ex>er</ex>emari Flaviacen<ex>sis</ex>q<ex>u</ex>amdam peciam t<ex>er</ex>re s<ex>em</ex>entis q<ex>u</ex>am h<ex>ab</ex>ebant excaduco Asceline de Amuchi, matertere dicti Ricardi,circiter sex minas continentem, sitam ante mesumde Amuchi, d<ex>i</ex>c<ex>t</ex>or<ex>um</ex> abbatis et <ex>con</ex>ventus, q<ex>u</ex>am abeisdem abbate <ex>et</ex> <ex>con</ex>ventu tenebant ad campipartem,pro centum et decem solidis parisiensium sibi a dictisabbate et <ex>con</ex>ventu plene <ex>et</ex> integ<ex>r</ex>e p<ex>er</ex>solutis, ut ip<ex>s</ex>iRicardus, Aya ejus uxor <ex>et</ex> Eufemia eor<ex>um</ex> filia coramnob<ex>is</ex> recognov<ex>er</ex>unt ; fidem coram nob<ex>is</ex> p<ex>re</ex>stantescorporalem p<ex>re</ex>d<ex>i</ex>c<ex>t</ex>i Ricardus, Aya ejus uxor <ex>et</ex>Eufemia eor<ex>um</ex> filia, no<ex>n</ex> vi nec metu ad hoc inductes<ex>ed</ex> mera <ex>et</ex> spontanea voluntate sua, ut asserebant,q<ex>uo</ex>d ip<ex>s</ex>i decet<ex>er</ex>o r<ex>ati</ex>one cuj<ex>us</ex>cu<ex>m</ex>q<ex>ue</ex> juris, <ex>et</ex>maxime d<ex>i</ex>c<ex>t</ex>a Aya r<ex>ati</ex>one dotis, in t<ex>er</ex>ra p<ex>re</ex>d<ex>i</ex>c<ex>t</ex>a venditap<ex>er</ex> se v<ex>e</ex>l p<ex>er</ex> alium nichil reclamab<ex>un</ex>t v<ex>e</ex>l facientreclamari,sed sup<ex>er</ex> eadem t<ex>er</ex>ra vendita d<ex>i</ex>c<ex>t</ex>is abbati <ex>et</ex> conventui<ex>con</ex>tra om<ex>ne</ex>s legitimam portabunt garandiam ;renuntiantes in hoc f<ex>a</ex>c<ex>t</ex>o, fide data, excepc<ex>i</ex>o<ex>n</ex>i no<ex>n</ex>num<ex>er</ex>ate <ex>et</ex> no<ex>n</ex> recepte pecunie <ex>et</ex> om<ex>n</ex>ib<ex>us</ex> aliisexcepc<ex>i</ex>o<ex>n</ex>ib<ex>us</ex> <ex>et</ex> juris auxilio tam cano<ex>n</ex>ici quam civilisq<ex>uo</ex>d s<ex>ib</ex>i cont<ex>r</ex>a p<ex>re</ex>sens instrum<ex>en</ex>tum posset p<ex>ro</ex>desse<ex>et</ex> d<ex>i</ex>c<ex>t</ex>is abbati <ex>et</ex> conventui prodesse*.In cuj<ex>us</ex> rei testimo<ex>n</ex>ium, p<ex>re</ex>sentes litt<ex>er</ex>as sigillocurie Belvacen<ex>sis</ex> fecim<ex>us</ex> <ex>com</ex>muniri. Act<ex>um</ex> annoD<ex>omi</ex>ni M° CC° XL° octavo, die 1248, le lune post Jubilat<ex>e</ex>."""
data = re.sub('<[^>]*>', PLACEHOLDER, data_with_tags)

searched_term = 'constituti presentia'

["Omnibus presentes litteras inspecturis", "officialis Belvacensis",
 "salutem in Domino.", "Noverint universi quod", ""]

ptr_start = 0
ptr_end = ptr_start + 1
old_ratio = 0
not_found = True
r = 0

while threshold < 100 and r < 90:

    ptr_start = 0
    ptr_end = ptr_start + 1
    old_ratio = 0
    not_found = True
    r = 0

    #find ptr_end
    while ptr_end < len(data) - 1 and not_found:
        r = fuzz.ratio(searched_term, data[ptr_start:ptr_end])
        #print(ptr_start, ptr_end, r, data[ptr_start:ptr_end])
        if (r < old_ratio and r > threshold) or r == 100:
            not_found = False
            r = old_ratio
        else:
            old_ratio = r
            ptr_end += 1

    if PLACEHOLDER != '':
      ptr_end += -1  # previous position was better

    #look if ptr_start can be moved forward
    not_found = r != 100
    while ptr_start < len(data)-1 and not_found:

        r = fuzz.ratio(searched_term, data[ptr_start:ptr_end])
        #print(ptr_start, ptr_end, r, data[ptr_start:ptr_end])
        if (r < old_ratio and r > threshold) or r == 100:
            not_found = False
            r = old_ratio
        else:
            old_ratio = r
            ptr_start += 1

    if PLACEHOLDER != '':
        ptr_start += -1 # previous position was better

    threshold += 10


print(ptr_start, ptr_end, r, "'{0}'".format(data[ptr_start:ptr_end]), threshold)

slots = [m.start() for m in re.finditer(PLACEHOLDER, data[ptr_start:ptr_end])]
start_tag_slots = [m.start() for m in re.finditer('<', data_with_tags)]

tags = []
for st_slot in start_tag_slots:
    et_slot = data_with_tags[st_slot::].index('>')
    if et_slot == -1:
        raise ValueError("tag not closed")
    else:
        tags.append((st_slot, st_slot+et_slot+1, data_with_tags[st_slot:st_slot+et_slot+1]))

print(tags)


#how many tags before ptr_start
slots_before = [m.start() for m in re.finditer(PLACEHOLDER, data[0:ptr_start])]

new_ptr_start = ptr_start + sum([len(t) for (s,e,t) in tags[0:len(slots_before)]]) - len(PLACEHOLDER)*len(slots_before)

#print(len(slots_before), len(slots))
#print(data[ptr_start:ptr_end])
#print([t for (s,e,t) in tags[len(slots_before):len(slots_before)+len(slots)]])
#print(new_ptr_start)

new_end_ptr = new_ptr_start + sum([len(t) for (s,e,t) in tags[len(slots_before):len(slots_before)+len(slots)]])+ len(data[ptr_start:ptr_end].replace(PLACEHOLDER, ''))

print("'{0}'".format(searched_term),
      "'{0}'".format(data_with_tags[new_ptr_start:new_end_ptr]))




