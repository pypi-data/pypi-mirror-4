from contextlib import contextmanager
import threading

from cubicweb.server.cwzmq import ZMQRepositoryServer

@contextmanager
def zmq_server_launch(config, repo, ip='127.0.0.1', port='41415'):
    # start server and hack Queueable adapter to force async run
    address = 'zmqpickle-tcp://%s:%s' % (ip, port)
    config['zmq-repository-address'] = address
    zmq_server = ZMQRepositoryServer(repo)
    zmq_server.connect(address)
    zmq_server_task = threading.Thread(target=zmq_server.run)
    zmq_server_task.start()
    print 'zmq server started'
    yield
    # stop zmq server and cleanup zmq repo related config
    config['zmq-repository-address'] = None
    zmq_server.quit()
    zmq_server_task.join(1)
    print 'zmq server stoped'

class QueueingTestMixin(object):

    def setup_database(self):
        super(QueueingTestMixin, self).setup_database()
        self.create_entity = self.request().create_entity
        self.host1 = self.create_entity('Host', name=u'h1')
        self.host2 = self.create_entity('Host', name=u'h2')
        self.host3 = self.create_entity('Host', name=u'h3')
        self.run1 = self.create_entity('Run', name=u'r1')
        self.run2 = self.create_entity('Run', name=u'r2')
        self.run3 = self.create_entity('Run', name=u'r3')
        self.queue1 = self.create_entity('ResourceQueue', name=u'queue1',
                                         has_resources=(self.host1, self.host2))

    def assertQEntitiesEqual(self, queue, entities):
        self.assertEqual([e for e in queue], entities)

    def assertQEntityUsesResource(self, qentity):
        qentity.cw_clear_all_caches()
        self.assertEqual(len(qentity.uses_resource), 1)

    def assertQEntityUsesNoResource(self, qentity):
        qentity.cw_clear_all_caches()
        self.assertEqual(len(qentity.uses_resource), 0)
