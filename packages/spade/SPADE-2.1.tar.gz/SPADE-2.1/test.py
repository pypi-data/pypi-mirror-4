from test.aidTestCase   import *
from test.amsTestCase   import *
from test.basicTestCase import *
from test.bdiTestCase   import *
from test.coTestCase    import *
from test.dadTestCase   import *
from test.dfTestCase    import *
from test.eventbehavTestCase import *
from test.factsTestCase import *
from test.httpTestCase  import *
from test.jsonTestCase  import *
from test.kbTestCase    import *
from test.p2pTestCase   import *
from test.pubsubTestCase import *
from test.rpcTestCase   import *
from test.tbcbpTestCase import *
from test.xfTestCase    import *

from spade import spade_backend
from xmppd.xmppd import Server
import thread
import sys
import os
import signal

if __name__ == '__main__':

    d="test"+os.sep

    s = Server(cfgfile=d+"unittests_xmppd.xml", cmd_options={'enable_debug':[], 'enable_psyco':False})

    thread.start_new_thread(s.run,tuple())

    platform = spade_backend.SpadeBackend(d+"unittests_spade.xml")
    platform.start()


    try:
        import xmlrunner
        use_xmlrunner = True
    except:
        use_xmlrunner = False

    if use_xmlrunner:
        unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'),exit=False)
    else:
        print "XMLTestRunner not found."
        unittest.main(exit=False)

    platform.shutdown()
    s.shutdown("Jabber server terminated...")

    sys.exit(0)
    if sys.platform == 'win32':
        os._exit(0)
    else:
        os.kill(os.getpid(), signal.SIGTERM)



