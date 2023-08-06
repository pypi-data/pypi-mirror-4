# -*- coding: utf-8 -*-

from pptx.oxml import oxml_fromstring, oxml_tostring

import pdb

nsmap = 'http://schemas.openxmlformats.org/presentationml/2006/main'

xml = '<p:sp xmlns:p="%s"><p:nvSpPr/></p:sp>' % nsmap
sp = oxml_fromstring(xml)
pdb.set_trace()
msg = 'got:\n\n%s' % oxml_tostring(sp)
