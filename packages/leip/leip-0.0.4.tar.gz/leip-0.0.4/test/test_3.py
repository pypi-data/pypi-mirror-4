#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Test 2 - use the configuration object
"""

import os
import leip
import tempfile
import logging
import shutil

logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger(__name__)


tmpdir = tempfile.mkdtemp()
conf_drie = os.path.join(tmpdir, 'conf.drie.yaml')

test_drie = """
plugin:
  test:
    module: 'leip_test_3'
    
"""

lg.info("saving dummy configuration files") 

with open(conf_drie, 'w') as F:
    F.write(test_drie)

lg.debug('instantiating app')
app = leip.app(
    config_files = (('drie', conf_drie),))

@app.command
def test(app, args):
    """
    Run a few tests
    """

    print 'run test'

app.run()
shutil.rmtree(tmpdir)
