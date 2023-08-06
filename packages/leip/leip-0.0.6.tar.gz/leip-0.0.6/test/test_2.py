#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
Test 2 - use the configuration object
"""

import os
import leip
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger(__name__)


tmpdir = tempfile.mkdtemp()
conf_een =  os.path.join(tmpdir, 'conf.een.yaml')
conf_twee = os.path.join(tmpdir, 'conf.twee.yaml')

test_een = """test_1: a
test_2:
  - 1
  - 2
  - 3"""

test_twee = """test_1: b
test_3: 
  sub_1:
    sub_2: subsubval"""

lg.info("saving dummy configuration files") 

with open(conf_een, 'w') as F:
    F.write(test_een)
with open(conf_twee, 'w') as F:
    F.write(test_twee)


lg.debug('instantiating app')
app = leip.app(
    config_files = (('een', conf_een),
                    ('twee', conf_twee))
    )

@app.arg('name', help='Name to say hello to', default='world')
@app.command
def hello(app, args):
    """
    Run the proverbial hello world test

    Help for the command is provided in the docstring. The first line
    is used for the command overview (test_1.py -h), the rest is used
    for a more extensive help per command (test_1.py hello -h).
    """
    print("Hello %s" % args.name)

@app.command
def test(app, args):
    """
    Run a few tests
    """

    global conf_een
    global conf_twee

    app.conf.animal = 'rabbit'
    app.conf.save()

    x = app.conf.simple()
    
    with open(os.path.join(conf_een)) as F:
        c1 = F.read()
    with open(os.path.join(conf_twee)) as F:
        c2 = F.read()

    assert(app.conf.test_1 == 'b')
    assert(app.conf.test_3.sub_1.sub_2 == 'subsubval')
    lg.debug("combined %s" % str(x))
    lg.debug("one:\n%s\n####" % str(c1))
    lg.debug("two:\n%s\n####" % str(c2))

app.run()

