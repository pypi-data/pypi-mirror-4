"""template automatic tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC

class AutomaticWebTest(CubicWebTC):

    def to_test_etypes(self):
        return set(('Card',))


class CardTC(CubicWebTC):
    def setup_database(self):
        self.fobj = self.request().create_entity('Card', title=u'sample card', synopsis=u'this is a sample card')

    def test_views(self):
        self.vreg['views'].select_or_none('inlined', self.fobj._cw, rset=self.fobj.cw_rset)

if __name__ == '__main__':
    unittest_main()
