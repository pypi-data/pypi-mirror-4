''' write to queue / read from a queue '''

import json
import urlparse

from amqplib import client_0_8 as amqp
import yaml

class MQUriException(BaseException):
    '''Exception class for MQUri object'''
    pass


class MQUri(object):
    ''' message queue Uniform Resource Indicator - loosely based on amqp-uri
    spec http://www.rabbitmq.com/uri-spec.html
    useful for storing connection information'''

    def __init__(self, uri):
        '''parse uri into userid, password, host, virtual_host
            i.e. mq://user:pass@host:port/virtual_host '''
        parsed = urlparse.urlparse(uri)

        if parsed.scheme not in ['mq', 'amqp', 'amqps']:
            raise(MQUriException('Invalid Message Queue URI'))
        self.username = parsed.username
        self.password = parsed.password
        self.hostname = parsed.hostname or ''
        self.hostport = parsed.port
        self.vhost = parsed.path[1:] or '/'


class Producer(object):
    '''send/queue messages to RabbitMQ'''

    DELIVERY_MODE_NONPERSISTENT = 1
    DELIVERY_MODE_PERSISTENT = 2

    def __init__(self, uri, exchange_name):
        """
        Constructor. Initiate connection with the RabbitMQ server.

        @param exchange_name name of the exchange to send messages to
        @param uri mq-uri connection string
        """
        self.exchange_name = exchange_name
        mquri = MQUri(uri)
        self.connection = amqp.Connection(host=mquri.hostname,
                                          userid=mquri.username,
                                          password=mquri.password,
                                          virtual_host=mquri.vhost,
                                          insist=False)
        self.channel = self.connection.channel()

    @staticmethod
    def serialize(message):
        '''Look at message contents and serialize as desired, then return
        an amqp.Message with the body and content_type set accordingly'''

        if type(message).__name__ == 'str':
            msg = amqp.Message(message)
            msg.properties["content_type"] = "text/plain"

        else:
            try:
                msg = amqp.Message(json.dumps(message))
                msg.properties["content_type"] = "text/json"
            except TypeError:   # some data type not supported by json
                msg = amqp.Message(yaml.dump(message))
                msg.properties["content_type"] = "text/yaml"

        print "message [%s] encoded as: %s" % (message,
                                               msg.properties['content_type'])
        return msg

    def publish(self, message, routing_key):
        """
        Publish message to exchange using routing key

        @param text message to publish
        @param routing_key message routing key
        """

        msg = self.serialize(message)
        msg.properties["delivery_mode"] = Producer.DELIVERY_MODE_PERSISTENT
        self.channel.basic_publish(exchange=self.exchange_name,
                                   routing_key=routing_key, msg=msg)

    def close(self):
        """
        Close channel and connection
        """
        self.channel.close()
        self.connection.close()

    def __enter__(self):
        '''method necessary for context mgr support'''
        return self

    def __exit__(self, e_type, e_value, e_traceback):
        '''called at context mgr loss of scope '''
        try:
            self.close()
        except amqp.AMQPChannelException:
            pass


class ConsumerError(BaseException):
    '''error class for Consumer object'''
    pass


class Consumer(object):
    '''fetch/dequeue messages from RabbitMQ'''

    def __init__(self, uri, exchange_name=None, queue_name=None,
                 routing_key=None):
        """
        Constructor. Initiate a connection to the RabbitMQ server.

        @param uri mq-uri connection string
        @param exchange_name
        @param queue_name
        @param routing_key
        """
        mquri = MQUri(uri)
        self.connection = amqp.Connection(host=mquri.hostname,
                                          userid=mquri.username,
                                          password=mquri.password,
                                          virtual_host=mquri.vhost,
                                          insist=False)
        self.channel = self.connection.channel()

        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key
        if exchange_name or queue_name or routing_key:
            if exchange_name and queue_name and routing_key:
                self.declare_exchange(exchange_name, auto_delete=True)
                self.declare_queue(queue_name, routing_key, auto_delete=True)
            else:
                raise ConsumerError('must specify all 3, exchange_name, '
                                    'queue_name and routing_key')

        self.callbacks = {}

    def close(self):
        '''Close channel and connection'''

        self.channel.close()
        self.connection.close()

    def declare_exchange(self, exchange_name, durable=True, auto_delete=False):
        """
        Create exchange.

        @param exchange_name name of the exchange
        @param durable will the server survive a server restart
        @param auto_delete should the server delete the exchange when it is
        no longer in use
        """
        self.exchange_name = exchange_name
        self.channel.exchange_declare(exchange=self.exchange_name, type='topic',
                                      durable=durable, auto_delete=auto_delete)

    def declare_queue(self, queue_name, routing_key, durable=True,
                      exclusive=False, auto_delete=False):
        """
        Create a queue and bind it to the exchange.

        @param queue_name Name of the queue to create
        @param routing_key binding key
        @param durable will the queue service a server restart
        @param exclusive only 1 client can work with it
        @param auto_delete should the server delete the exchange when it is
         no longer in use
        """
        self.queue_name = queue_name
        self.routing_key = routing_key
        #channel.queue_bind Returns a tuple containing 3 items:
        #    the name of the queue (essential for automatically-named queues)
        #    message count
        #    consumer count
        (queue_name, msg_count, consumer_count) = self.channel.queue_declare(
            queue=self.queue_name, durable=durable,
            exclusive=exclusive, auto_delete=auto_delete)
        self.channel.queue_bind(queue=self.queue_name,
                                exchange=self.exchange_name,
                                routing_key=self.routing_key)
        return (queue_name, msg_count, consumer_count)

    def basic_qos(self, prefetch_count=0):
        """
        Create a Quality of Service setting for the channel by setting a
        prefetch count.  If prefetch_count > 0, then fair dispatching is used.
        If prefetch_count=0, then every nth consumer, receives every nth job

        @param prefetch_count If prefetch_count == 1, then make sure everyone is
        working all the time, if 0, then pass the workload evenly never mind who
        is starving and who is stuffed.

        """
        prefetch_size = 0
        a_global = False
        self.channel.basic_qos(prefetch_size=prefetch_size,
                               prefetch_count=prefetch_count,
                               a_global=a_global)

    def attach_action(self, callback, queue_name=None, consumer_tag='action'):
        """Start a consumer and register a function to be called when a
            message is consumed

        @param callback function to call
        @param queue_name name of the queue
        @param consumer_tag a client-generated consumer tag to establish context
        """
        if hasattr(self, 'queue_name') or queue_name:
            self.callbacks[consumer_tag] = callback
            self.channel.basic_consume(queue=getattr(self,
                                                     'queue_name',
                                                     queue_name),
                                       callback=self.deserialize,
                                       consumer_tag=consumer_tag)

    def deserialize(self, msg):
        '''Do any necessary deserialization necessary, then call the  user
        requested call back, msg is an amqp.message structure.'''

        if msg.properties['content_type'] == u'text/plain':
            pass    # no action required
        elif msg.properties['content_type'] == u'text/json':
            msg.body = json.loads(msg.body)
        elif msg.properties['content_type'] == u'text/yaml':
            msg.body = yaml.load(msg.body)

        # Now hand the msg object off to the user specified call back
        return self.callbacks[msg.delivery_info['consumer_tag']](msg)

    def handle_messages(self):
        """
        Wait for activity on the channel.
        """
        while True:
            self.channel.wait()

    def __enter__(self):
        '''method necessary for context mgr support'''
        return self

    def __exit__(self, e_type, e_value, e_traceback):
        '''called at context mgr loss of scope '''
        try:
            self.close()
        except amqp.AMQPChannelException:
            pass
