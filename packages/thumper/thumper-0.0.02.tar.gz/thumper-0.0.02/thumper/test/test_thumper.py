'''minimal testing for thumper'''

import datetime
import decimal

from thumper import Producer
from thumper import Consumer


def test_producer_init():
    '''test we can import and minimally init Producer'''
    uri = "mq://guest:guest@localhost"
    producer = Producer(exchange_name='thumper-test', uri=uri)
    producer.close()


def test_consumer_init():
    '''test we can import and minimally init Consumer'''
    uri = "mq://guest:guest@localhost"
    consumer = Consumer(uri=uri)
    consumer.close()


def test_producer_with():
    '''test use in a context mgr user case'''
    uri = "mq://guest:guest@localhost"
    route_key = 'test.producer.with'
    exchange_name = 'thumper-test'
    with Producer(uri=uri, exchange_name=exchange_name) as producer:
        for msg in ['msg %s' % x for x in xrange(10)]:
            producer.publish(msg, route_key)


def test_producer_serialize():
    '''test different data types/structures'''
    uri = "mq://guest:guest@localhost"
    route_key = 'test.producer.serialize'
    exchange_name = 'thumper-test'
    msg_list = ['string', {'foo': 1}, [1, 2, 3], datetime.datetime.now(),
                datetime.date.today(), 3.14159, 3, decimal.Decimal('5.95')]
    with Producer(uri=uri, exchange_name=exchange_name) as producer:
        for msg in msg_list:
            producer.publish(msg, route_key)


def test_message_dlvry():
    '''test message delivery from producer to consumer'''
    uri = "mq://guest:guest@localhost"
    route_key = 'test.producer.serialize'
    exchange_name = 'thumper-test'
    q_name = 'thumper-q'
    msg_list = ['string', {'foo': 1}, [1, 2, 3], datetime.datetime.now(),
                datetime.date.today(), 3.14159, 3, decimal.Decimal('5.95')]
    consumer = Consumer(uri)
    consumer.declare_exchange(exchange_name=exchange_name,
                              durable=False, auto_delete=True)
    consumer.declare_queue(queue_name=q_name, routing_key=route_key,
                           durable=False, auto_delete=True)

    def ifunc(msg):
        '''call back function'''
        tmpl = 'callback on %s decoded from [%s]'
        print tmpl % (msg.body, msg.properties['content_type'])

    consumer.attach_action(callback=ifunc, queue_name=q_name,
                           consumer_tag='lambda')

    with Producer(uri=uri, exchange_name=exchange_name) as producer:
        for msg in msg_list:
            producer.publish(msg, route_key)
            consumer.channel.wait()

    consumer.close()


def test_message_fidelity():
    '''test message fidelity from producer to consumer'''
    uri = "mq://guest:guest@localhost"
    route_key = 'test.producer.serialize'
    exchange_name = 'thumper-test'
    q_name = 'thumper-q'
    msg_list = ['string', {'foo': 1}, [1, 2, 3], datetime.datetime.now(),
                datetime.date.today(), 3.14159, 3, decimal.Decimal('5.95')]
    msg_rcvd = []
    consumer = Consumer(uri)
    consumer.declare_exchange(exchange_name=exchange_name,
                              durable=False, auto_delete=True)
    consumer.declare_queue(queue_name=q_name, routing_key=route_key,
                           durable=False, auto_delete=True)

    def ifunc(msg):
        '''call back function'''
        assert msg.body in msg_list
        msg_rcvd.append(msg.body)

    consumer.attach_action(callback=ifunc, queue_name=q_name,
                           consumer_tag='lambda')

    with Producer(uri=uri, exchange_name=exchange_name) as producer:
        for msg in msg_list:
            producer.publish(msg, route_key)
            consumer.channel.wait()

    consumer.close()
    assert msg_rcvd == msg_list


def test_consumer_with():
    '''test consumer with context mgr pattern'''
    uri = "mq://guest:guest@localhost"
    route_key = 'test.producer.serialize'
    exchange_name = 'thumper-test'
    q_name = 'thumper-q'
    msg_list = ['string', {'foo': 1}, [1, 2, 3], datetime.datetime.now(),
                datetime.date.today(), 3.14159, 3, decimal.Decimal('5.95')]
    msg_rcvd = []

    def ifunc(msg):
        '''call back function'''
        assert msg.body in msg_list
        msg_rcvd.append(msg.body)

    with Consumer(uri) as consumer:
        consumer.declare_exchange(exchange_name=exchange_name,
                                  durable=False, auto_delete=True)
        consumer.declare_queue(queue_name=q_name, routing_key=route_key,
                               durable=False, auto_delete=True)

        consumer.attach_action(callback=ifunc, queue_name=q_name,
                               consumer_tag='ifunc')

        with Producer(uri=uri, exchange_name=exchange_name) as producer:
            for msg in msg_list:
                producer.publish(msg, route_key)
                consumer.channel.wait()

    assert msg_rcvd == msg_list


def test_multi_callbacks_1q():
    '''test single consumer queue with multiple callbacks on a single
    consumer - will round robin'''

    uri = "mq://guest:guest@localhost"
    route_key = 'app.ext.domain.host'
    exchange_name = 'thumper-test'
    q_name = 'thumper-q'
    msg_list = ['string', {'foo': 1}, [1, 2, 3], datetime.datetime.now(),
                datetime.date.today(), 3.14159, 3, decimal.Decimal('5.95')]
    msg_rcvd1 = []
    msg_rcvd2 = []

    def ifunc1(msg):
        '''call back function'''
        assert msg.body in msg_list
        # print "ifunc1 [%s]" % msg.body
        msg_rcvd1.append(msg.body)

    def ifunc2(msg):
        '''call back function'''
        assert msg.body in msg_list
        # print "ifunc2 [%s]" % msg.body
        msg_rcvd2.append(msg.body)

    with Consumer(uri, exchange_name, q_name, route_key) as consumer:
        consumer.attach_action(callback=ifunc1, queue_name=q_name,
                               consumer_tag="ifunc1")
        consumer.attach_action(callback=ifunc2, queue_name=q_name,
                               consumer_tag="ifunc2")

        with Producer(uri=uri, exchange_name=exchange_name) as producer:
            for msg in msg_list:
                producer.publish(msg, route_key)
                consumer.channel.wait()

    # print msg_list
    # print msg_rcvd1
    # print msg_rcvd2

    msg_cmb = [y for x in map(None, msg_rcvd1, msg_rcvd2) for y in x if y is not None]
    assert msg_cmb == msg_list

