from os.path import join

from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestTranscriptionsAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
    ]

    def test_get_transcriptions_reference(self):
        self.assert404("/adele/api/1.0/documents/21/transcriptions")
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)

        r = self.assert200("/adele/api/1.0/documents/21/transcriptions")
        r = json_loads(r.data)['data']

        self.assertEqual(21, r['doc_id'])
        self.assertEqual(4, r['user_id'])
        self.assertEqual(0, len(r['notes']))
        self.assertEqual('<p>Om<ex>n</ex>ib<ex>us</ex> p<ex>re</ex>sentes litt<ex>er</ex>as inspectur<ex>is</ex>, .\xa0.\xa0offic<ex>ialis</ex> cur<ex>ie</ex> Melden<ex>sis</ex>, sal<ex>u</ex>t<ex>em</ex> in D<ex>omi</ex>no. Notum facim<ex>us</ex> q<ex>uo</ex>d coram nobis constituta domicella Margareta de Essartis, relicta defuncti Galt<ex>er</ex>i Ruffi de Essartis, recognovit se vendidisse et imp<ex>er</ex>petuum q<ex>u</ex>itasse viris religiosis abb<ex>at</ex>i et conventui de Caroliloco [et imp<ex>er</ex>petuum q<ex>u</ex>itasse] duo arpenta t<ex>er</ex>re et dimid<ex>ium</ex> arabil<ex>is</ex>, sita in t<ex>er</ex>ritorio de Marchemoreto, contigua t<ex>er</ex>re predic<ex>t</ex>or<ex>um</ex> abb<ex>at</ex>is et conventus, pro q<ex>u</ex>indecim lib<ex>ris</ex> turonen<ex>sium</ex>, de q<ex>u</ex>ib<ex>us</ex> tenuit se coram nob<ex>is</ex> p<ex>ro</ex> pagata in pecunia num<ex>er</ex>ata\xa0; reno<ex>n</ex>cians q<ex>u</ex>a<ex>n</ex>tum ad hoc excepc<ex>i</ex>o<ex>n</ex>i no<ex>n</ex> num<ex>er</ex>ate sibi pecunie, no<ex>n</ex> tradite, no<ex>n</ex> solute\xa0; promittens, fide data in manu n<ex>ost</ex>ra, se istam vendicio<ex>n</ex>em firmit<ex>er</ex> imp<ex>er</ex>petuum s<ex>er</ex>vatura<ex>m</ex> et no<ex>n</ex> cont<ex>ra</ex>venturam rac<ex>i</ex>o<ex>n</ex>e h<ex>er</ex>editatis, dotalicii sive dotis seu q<ex>u</ex>aconq<ex>ue</ex> alia rac<ex>i</ex>o<ex>n</ex>e\xa0; immo d<ex>i</ex>c<ex>t</ex>is emtoribus erga om<ex>ne</ex>s rectam gara<ex>n</ex>diam portabit erga om<ex>ne</ex>s imp<ex>er</ex>petuum. Petrus v<ex>er</ex>o p<ex>res</ex>b<ex>ite</ex>r de Bolorria, frat<ex>er</ex> d<ex>i</ex>c<ex>t</ex>e Margarete, <ex>et</ex> Guiot<ex>us</ex> filius d<ex>i</ex>c<ex>t</ex>e Margarete, in n<ex>ost</ex>ra p<ex>re</ex>sencia constituti, p<ex>re</ex>d<ex>i</ex>c<ex>t</ex>am vendic<ex>i</ex>o<ex>n</ex>em voluer<ex>unt</ex>, laudav<ex>e</ex>ru<ex>n</ex>t et co<ex>n</ex>cess<ex>er</ex>unt\xa0; promittentes, fide data in manu n<ex>ost</ex>ra, q<ex>uo</ex>d cont<ex>ra</ex> p<ex>re</ex>missa p<ex>er</ex> se v<ex>e</ex>l p<ex>er</ex> alium rac<ex>i</ex>o<ex>n</ex>e h<ex>er</ex>editatis seu q<ex>u</ex>aconq<ex>ue</ex> alia rac<ex>i</ex>o<ex>n</ex>e [per se v<ex>e</ex>l per alium] no<ex>n</ex> venie<ex>nt</ex> in futurum. In cuj<ex>us</ex> rei testimoniu<ex>m</ex>, p<ex>re</ex>sentib<ex>us</ex> litt<ex>er</ex>is sigillum curie Melden<ex>sis</ex> duxim<ex>us</ex> apponendum. Dat<ex>um</ex> anno D<ex>omi</ex>ni M° CC° L° p<ex>r</ex>imo, mense novembr<ex>is</ex>.</p>', r['content'])

        # test with notes

    def test_get_transcriptions_from_user(self):
        raise NotImplementedError

    def test_delete_transcriptions(self):
        raise NotImplementedError

    def test_put_transcriptions(self):
        raise NotImplementedError

    def test_post_transcriptions(self):
        raise NotImplementedError
