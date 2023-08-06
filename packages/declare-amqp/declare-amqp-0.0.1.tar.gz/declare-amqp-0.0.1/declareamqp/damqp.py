from argparse import ArgumentParser
import os

from haigha.connections.rabbit_connection import RabbitConnection
from haigha.message import Message
import yaml

def run(args):
    host = os.getenv('AMQP_HOST', 'localhost')
    user = os.getenv('AMQP_USER', 'guest')
    password = os.getenv('AMQP_PASS', 'guest')
    vhost = os.getenv('AMQP_VHOST', '/')

    connection = RabbitConnection(
      user=user, password=password,
      vhost=vhost, host=host,
      heartbeat=None, debug=True)

    config = get_config(args.config)

    ch = connection.channel()
    for exchange in config.get('exchanges'):
        print 'Declaring exchange:'
        print '\t', exchange
        ch.exchange.declare(
            exchange['name'],
            exchange['type'],
            durable=exchange['durable'],
            auto_delete=exchange['auto_delete'],
        )

    for queue in config.get('queues'):
        print 'Declaring queue:'
        print '\t', queue
        ch.queue.declare(
            queue['name'],
            auto_delete=queue['auto_delete'],
        )
        for binding in queue['bindings']:
            print 'Binding queue:'
            print '\t', binding
            ch.queue.bind(
                queue['name'],
                binding['exchange'],
                binding['binding_key'],
            )
    #ch.basic.publish( Message('body', application_headers={'hello':'world'}),
    #  'test_exchange', 'test_key' )
    #print ch.basic.get('test_queue')
    connection.close()


def get_args():
    parser = ArgumentParser(description='Declare some AMQP')
    parser.add_argument('--config', metavar='config', type=str, help='Config file to use')

    return parser.parse_args()

def get_config(path):
    print path
    config_file = open(path)
    content = config_file.read()
    config_file.close()
    return yaml.load(content)


if __name__ == '__main__':
    run(get_args())
