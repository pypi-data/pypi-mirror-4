"""
A plugin for narc that markes a testrun as finished when all the NO_RESULT results have been finished.
"""
import configparser
import logging
from kombu import Queue, Consumer
from kombu.transport.base import Message
from narc.amqp import AMQPConnection
from slickqa import SlickConnection, Testrun, micromodels, RunStatus

class TestrunUpdateMessage(micromodels.Model):
    before = micromodels.ModelField(Testrun)
    after = micromodels.ModelField(Testrun)

class TestrunFinishedPlugin(object):
    def __init__(self, configuration, amqpcon, slick):
        assert(isinstance(configuration, configparser.ConfigParser))
        assert(isinstance(amqpcon, AMQPConnection))
        assert(isinstance(slick, SlickConnection))
        self.slick = slick
        self.logger = logging.getLogger("narc_testrunfinished.TestrunFinishedPlugin")
        self.logger.info("TestrunFinished plugin starting up")

        self.channel = amqpcon.add_channel()
        self.queue = Queue('narc_testrun_finished_responder', exchange=amqpcon.exchange, routing_key='update.Testrun', durable=True)
        self.consumer = Consumer(self.channel, queues=[self.queue,], callbacks=[self.testrun_updated,])
        amqpcon.add_consumer(self.consumer)

    def testrun_updated(self, body, message):
        assert(isinstance(message, Message))
        if not message.acknowledged:
            message.ack()
        update = TestrunUpdateMessage.from_dict(body)
        if not hasattr(update.before.summary, 'resultsByStatus'):
            self.logger.debug("No results for testrun {}: {}", update.before.id, update.before.to_json())
        elif hasattr(update.before.summary.resultsByStatus, 'NO_RESULT') and update.before.summary.resultsByStatus.NO_RESULT > 0 and update.after.summary.resultsByStatus.NO_RESULT == 0:
            self.logger.debug("Looks like testrun with id {} is now finished, I will mark it as such.", update.after.id)
            update.after.state = RunStatus.FINISHED
            self.slick.testruns(update.after).update()

