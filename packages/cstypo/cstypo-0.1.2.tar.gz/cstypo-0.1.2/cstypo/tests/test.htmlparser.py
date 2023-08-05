# -*- coding: utf-8 -*-
import unittest

from cstypo import parser


class TestHtmlParser(unittest.TestCase):

    def test_html_tags(self):
        text = '''
<h2 id="prednasky-kde-jsem-byl">Přednášky, kde jsem byl</h2>
<h3 id="ano-chefe-karel-minarik-vojtech-hyza"><a href="http://webexpo.cz/praha2012/prednaska/ano-chefe/">Ano, Chefe! (Karel Minařík, Vojtěch Hýža)</a></h3>
<p>Profi, ale neužil jsem si to tolik. Nemám 20 serverů a v brzké době asi ani mít nebudu. Chápal jsem principy a výhody toho mít konfiguraci kódu jako kód, ale pro mě to prostě nemá význam.</p>
<h3 id="sebevrazda-v-bronxu-richard-sery"><a href="http://webexpo.cz/praha2012/prednaska/sebevrazda-v-bronxu/">Sebevražda v Bronxu (Richard Šerý)</a></h3>
        '''

        inst = parser.HtmlParser(text)
        parsed = inst.parse()

        self.assertEqual(u'''
            ''', parsed)


if __name__ == '__main__':
    unittest.main()
