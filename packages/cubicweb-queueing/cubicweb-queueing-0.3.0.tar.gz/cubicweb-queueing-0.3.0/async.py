import sys
import os.path as osp
import logging
import json

from cubicweb import dbapi
from logilab.common.registry import traced_selection

# XXX optparse
appid, zmq_address, resource_eid, queueable_eid, login, authobj, testmode = sys.argv[1:]
logger = logging.getLogger('queueing.async')
# XXX OPTPARSE
testmode = 'test' in testmode

if testmode:
    # this will make  cubes.queuing.test.data.enties appear as test.data.entities
    # hence dependant cubes tests will fail to unregister stuff recorded there
    # for `from cubes.queueing.test.data.entities import Foo` will yield a different Foo
    sys.path[:] = sys.path[1:]

try:
    cnx = dbapi.connect(zmq_address,
                        login=login,
                        queueable_eid=queueable_eid,
                        authobj=json.loads(authobj),
                        cnxprops=dbapi.ConnectionProperties('zmq'))
except Exception, exc:
    logger.error('impossible to open the connection (%s)', exc)
    raise

if testmode:
    # we force a lookup in test/data/entities
    cnx.load_appobjects(subpath=('entities', 'views', 'test/data/entities'))
else:
    cnx.load_appobjects()

cu = cnx.cursor()
try:
    ent_from_eid = lambda eid: cu.execute(
        'Any X WHERE X eid %(x)s', {'x': eid}).get_entity(0, 0)
    resource = ent_from_eid(resource_eid)
    queueable = ent_from_eid(queueable_eid)
    resource.cw_adapt_to('QResource').execute(queueable)
    cnx.commit()
except Exception, exc:
    cnx.rollback()
    logger.error('execution rollbacked (cause: %s)', exc)
    import traceback as tb
    logger.error(tb.format_exc())
finally:
    cnx.close()
