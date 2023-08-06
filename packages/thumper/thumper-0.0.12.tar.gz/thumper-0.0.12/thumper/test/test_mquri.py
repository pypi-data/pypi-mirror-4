'''implement tests for the message queue uri connection scheme'''

from thumper import MQUri
from thumper.rabbit import MQUriException


# URI Username    Password    Host    Port    Vhost
# mq://user:pass@host:10000/vhost   "user"  "pass"  "host"  10000   "vhost"
## mq://user%61:%61pass@ho%61st:10000/v%2fhost   "usera" "apass" "hoast" 10000   "v/host"
# mq://
# mq://:@/  ""  ""          ""
# mq://user@    "user"
# mq://user:pass@   "user"  "pass"
# mq://host         "host"
# mq://:10000               10000
# mq:///vhost                   "vhost"
# mq://host/                "host"  ""
# mq://host/%2f             "host"  "/"
# mq://[::1]            "[::1]" (i.e. the IPv6 address ::1)


def test_full_complete():
    '''test a uri with all the bells and whistles'''
    uri = "mq://user:pass@host:10000/vhost"
    mquri = MQUri(uri)
    assert mquri.username == 'user'
    assert mquri.password == 'pass'
    assert mquri.hostname == 'host'
    assert mquri.hostport == 10000
    assert mquri.vhost == 'vhost'


def test_full_simple():
    '''test the 90% use case'''
    uri = "amqps://user:pass@host/vhost"
    mquri = MQUri(uri)
    assert mquri.username == 'user'
    assert mquri.password == 'pass'
    assert mquri.hostname == 'host'
    assert mquri.hostport is None
    assert mquri.vhost == 'vhost'


def test_empty_but_valid():
    '''test a non-sensical but valid uri'''
    uri = "mq://"
    mquri = MQUri(uri)
    assert mquri.username is None
    assert mquri.password is None
    assert mquri.hostname is ''
    assert mquri.hostport is None
    assert mquri.vhost == '/'


def test_invalid_mquri():
    '''test a non-mquri string'''
    uri = "http://"
    try:
        _ = MQUri(uri)
        assert False
    except MQUriException:
        assert True


def test_blank_strings():
    '''test blank values'''
    uri = "amqp://:@/"
    mquri = MQUri(uri)
    assert mquri.username == ''
    assert mquri.password == ''
    assert mquri.hostname == ''
    assert mquri.hostport is None
    assert mquri.vhost == '/'


def test_user_and_blank_strings():
    '''# mq://user@    '''
    uri = "mq://user@"
    mquri = MQUri(uri)
    assert mquri.username == 'user'
    assert mquri.password is None
    assert mquri.hostname == ''
    assert mquri.hostport is None
    assert mquri.vhost == '/'


def test_user_pass():
    '''username and password only'''
    uri = "mq://user:pass@"
    mquri = MQUri(uri)
    assert mquri.username == 'user'
    assert mquri.password == 'pass'
    assert mquri.hostname == ''
    assert mquri.hostport is None
    assert mquri.vhost == '/'


def test_host():
    '''mquri with host only info'''
    uri = 'mq://host'
    mquri = MQUri(uri)
    assert mquri.username is None
    assert mquri.password is None
    assert mquri.hostname == 'host'
    assert mquri.hostport is None
    assert mquri.vhost == '/'
