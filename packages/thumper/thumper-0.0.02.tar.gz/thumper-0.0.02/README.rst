===========
Thumper
===========

Simplifies interactions with RabbitMQ by focusing on design patterns based on Topic
Exchanges. More information can be found here:
http://www.rabbitmq.com/tutorials/tutorial-five-python.html

Goals
=====
Embrace Kenneth Reitz's `thoughts on the 90% rule <http://pyvideo.org/video/1785/python-for-humans-1>`_, i.e. requests module.

Messages are serialized as needed, starting from no serialization for strings to json and falling back to yaml if the more
simple open serialization methods are not capable of serializing the object/message. i.e. datetime/date/decimal/etc.

.. sourcecode:: python

    #!/usr/bin/env python

    from rabbit import Producer

    with Producer(uri) as producer:
        for message in <iterable/generator>:
            producer.publish(message, routing_key)


.. sourcecode:: python

    from rabbit import Consumer

    with Consumer(uri, exchange, queue, routing_key) as consumer:
        consumer.attach_action(...)
        consumer.handle_messages(...)

or for even more control of exchanges and queues:

.. sourcecode:: python

    from rabbit import Consumer

    with Consumer(uri) as consumer:
        consumer.declare_exchange(...)
        consumer.declare_queue(...)
        consumer.attach_action(...)
        consumer.handle_messages(...)

