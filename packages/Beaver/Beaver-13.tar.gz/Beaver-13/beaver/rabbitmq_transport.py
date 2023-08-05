import datetime
import pika

import beaver.transport
from beaver.transport import TransportException


class RabbitmqTransport(beaver.transport.Transport):

    def __init__(self, file_config, beaver_config):
        super(RabbitmqTransport, self).__init__(file_config, beaver_config)

        self.rabbitmq_key = beaver_config.get('rabbitmq_key')
        self.rabbitmq_exchange = beaver_config.get('rabbitmq_exchange')

        # Setup RabbitMQ connection
        credentials = pika.PlainCredentials(
            beaver_config.get('rabbitmq_username'),
            beaver_config.get('rabbitmq_password')
        )
        parameters = pika.connection.ConnectionParameters(
            credentials=credentials,
            host=beaver_config.get('rabbitmq_host'),
            port=int(beaver_config.get('rabbitmq_port')),
            virtual_host=beaver_config.get('rabbitmq_vhost')
        )
        self.connection = pika.adapters.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare RabbitMQ queue and bindings
        self.channel.queue_declare(queue=beaver_config.get('rabbitmq_queue'))
        self.channel.exchange_declare(
            exchange=self.rabbitmq_exchange,
            exchange_type=beaver_config.get('rabbitmq_exchange_type'),
            durable=bool(beaver_config.get('rabbitmq_exchange_durable'))
        )
        self.channel.queue_bind(
            exchange=self.rabbitmq_exchange,
            queue=beaver_config.get('rabbitmq_queue'),
            routing_key=self.rabbitmq_key
        )

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    self.channel.basic_publish(
                        exchange=self.rabbitmq_exchange,
                        routing_key=self.rabbitmq_key,
                        body=self.format(filename, timestamp, line),
                        properties=pika.BasicProperties(
                            content_type="text/json",
                            delivery_mode=1
                        )
                    )
            except UserWarning:
                raise TransportException("Connection appears to have been lost")
            except Exception, e:
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException("Unspecified exception encountered")  # TRAP ALL THE THINGS!

    def interrupt(self):
        if self.connection:
            self.connection.close()

    def unhandled(self):
        return True
