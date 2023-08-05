"""
lava.celery.commands
====================

LAVA command definitions used by lava-celery
"""

import logging
import os
import sys
import time
import traceback

import lava.celery.config as config

from lava.tool.command import Command, CommandGroup


__all__ = ["celeryd", "celery", "celery_schedulermonitor", "hello_world",
            "run_remote"]

class celeryd(Command):
    """
    Run a celeryd worker that will subscribe to a message queue and execute
    tasks sent to it.
    """

    @classmethod
    def register_arguments(cls, parser):
        super(celeryd, cls).register_arguments(parser)
        parser.add_argument(
            '-u', '--url',
            default=config.BROKER_URL,
            help="The rabbitmq broker url to subscribe to")

    def invoke(self):
        os.environ["CELERY_CONFIG_MODULE"] = "lava.celery.config"
        config.BROKER_URL = self.args.url
        sys.argv = ['celeryd']
        import celery.bin.celeryd
        celery.bin.celeryd.main()

class celery(CommandGroup):
    """
    Access celery commands.
    Celery is an implementation of distributed task queue. LAVA uses celery to
    spread work across multiple virual and physical machines.
    """

    namespace = "lava.celery.commands"


class hello_world(Command):
    """
    Say "Hello World!"

    This command can be used to validate cloud configuration as the text is
    streamed remotely in that case.
    """

    @classmethod
    def register_arguments(cls, parser):
        super(hello_world, cls).register_arguments(parser)
        parser.add_argument(
            '-r', '--return-code',
            default=0,
            type=int,
            help="Exit code of the command")
        parser.add_argument(
            '-m', '--message',
            default="hello world",
            help="Text message to print")
        parser.add_argument(
            '-d', '--delay',
            default=None,
            type=float,
            help="Delay between subsequent lines (in seconds)")
        parser.add_argument(
            '-c', '--count',
            default=1,
            type=int,
            help="Say hello that many times")

    def invoke(self):
        for i in range(self.args.count):
            text = "{0}: {1}".format(self.args.message, i)
            self.say("{0}", text)
            print "stdout", text
            print >>sys.stderr, "stderr", text
            if self.args.delay is not None:
                time.sleep(self.args.delay)
        return self.args.return_code


class run_remote(Command):
    """
    Cloudify a LAVA command
    Runs an existing LAVA commmand somewhere in the cloud.
    """

    logger = logging.getLogger("lava-celery")

    @classmethod
    def register_arguments(cls, parser):
        super(run_remote, cls).register_arguments(parser)
        parser.add_argument(
            '-s', '--silent',
            action="store_true",
            default=False,
            help="Don't print say() calls")
        group = parser.add_argument_group(title="Celery configuration")
        group.add_argument("--queue", default=None)
        group.add_argument("--routing-key", default=None)
        group.add_argument(
            "--connect-timeout",
            metavar="TIMEOUT",
            default=3,
            help=("Fail to queue the request if the message broker cannot be"
                  " reached after the TIMEOUT of seconds"),
            type=int)
        group.add_argument(
            "--countdown",
            metavar="DELAY",
            default=0,
            type=int,
            help=("Postpones execution of this command until after DELAY"
                  " seconds have elapse"))
        group.add_argument(
            "--expires",
            default=None,
            metavar="AMOUNT",
            help=("Expire the message if not acknowledged by a worker after"
                  " the specified AMOUNT of seconds have elapsed"),
            type=int)
        parser.add_argument(
            "args", nargs="...",
            help="LAVA command to invoke, e.g. celery hello-world")

    def _configure_celery(self):
        # XXX: This is very, very ugly
        # We really need a way to sensibly configure this stuff
        os.environ["CELERY_CONFIG_MODULE"] = "lava.celery.config"
        import celery

    def _setup_plumbing(self, channel):
        """
        Setup basic messaging objects: the exchange and the queue.

        The exchange is based on a template exchange from the .queues module.
        Just a regular directly-routed exchange. The exchange is not durable
        and uses transient messages (this part may need adjustments later if we
        need durability and persistence). This exchange is called
        'lava.celery.stream'.

        The queue is used for getting the output of this particular command and
        is unique for our connection (by being exclusive). The broker will
        auto-assign a name to this queue.

        There are some additional calls here. Typically .declare() and
        .queque_bind() are automatically handled by the Consumer class but here
        that does not work as our queue has no fixed name. We have to manually
        declare the queue and bind it to a manually declared exchange.  The
        queue's routing key is set to the same automatically generated queue
        name. This way the task worker can use a well-known exchange name and
        explicitly provided routing key to send the output of this particular
        command.
        """
        from lava.celery.queues import StreamExchange, StreamQueue
        # Exchange for all console IO
        exchange = StreamExchange(channel)
        exchange.declare()
        # Queue for this client data
        queue = StreamQueue(channel)
        queue.declare()
        queue.routing_key = queue.name
        queue.queue_bind()
        self.logger.debug("Message stream queue name is: %r", queue.name)
        return queue

    def _process_message(self, body, message):
        self.logger.debug("Remote worker message: %r", message.payload)
        if 'say' in message.payload:
            if self.args.silent is False:
                self.say("{0} >>> {1}",
                         message.payload['command'],
                         # NOTE: we escape { as self.say() calls .format()
                         message.payload['say'].replace("{", "{{"))
            message.ack()
        elif 'stdout' in message.payload:
            sys.stdout.write(message.payload['stdout'])
        elif 'stderr' in message.payload:
            sys.stderr.write(message.payload['stderr'])
        elif 'done' in message.payload:
            self.keep_running = False
            self.retval = message.payload['done']
            message.ack()
        else:
            self.say("Unknown message: {0}", message)
            message.reject()

    def invoke(self, arg0="lava", files=None):
        self._configure_celery()
        # Importing only after we call ._configure_celery()
        from celery.messaging import establish_connection
        from kombu import Consumer
        from lava.celery.tasks import run_command
        # Return value of the remote command
        self.retval = None
        # Read stout/stderr for as long as possible
        # Let's setup a consumer first, this will give us a queue
        connection = establish_connection()
        try:
            with connection.channel() as channel:
                # Setup plumbing
                queue = self._setup_plumbing(channel)
                # Run the task - this is fire and forget
                # because the task has ignore_result annotation.
                async_result = run_command.apply_async(
                    # Invoke a command with specified arguments.  NOTE: that we
                    # pass queue.name here which is conveniently also the
                    # routing key. See ._setup_plumbing() for an explanation.
                    args=[queue.name, self.args.args, arg0, files],
                    # Routing key for the celery task workers. This routing
                    # key is different from queue.name. It is used by celery
                    # and celeryd to associate workers with tasks to perform.
                    # If you need specialized task worker then provide a custom
                    # routing key and spawn a custom celeryd that only takes
                    # messages with that key.
                    routing_key=self.args.routing_key,
                    # Specify broker connection timeout
                    connect_timeout=self.args.connect_timeout,
                    # Specify the delay when this message should be processed by celeryd
                    countdown=self.args.countdown,
                    # Specify when this message should expire
                    expires=self.args.expires)
                self.logger.debug("Celery task enqueued: %r", async_result)
                # Consumer that processes messages sent by CloudifiedDispatcher
                with Consumer(channel, queue,
                              callbacks=[self._process_message],
                              # NOTE: Don't declare anything as that's done in
                              # _setup_plumbing()
                              auto_declare=False):
                    # Loop flag
                    self.keep_running = True
                    while self.keep_running:
                        connection.drain_events()
        finally:
            self.logger.debug("Shutting down AMQP connection")
            # Tear down the connection
            connection.close()
        self.logger.debug("Remote processing done, return code is %r", self.retval)
        return self.retval

class celery_schedulermonitor(run_remote):
    """
    Launches a schedulermonitor task on a celery worker node.
    """

    @classmethod
    def register_arguments(cls, parser):
        super(celery_schedulermonitor, cls).register_arguments(parser)

        group = parser.add_argument_group(title="Dispatcher Configuration")
        group.add_argument('--settings-module',
            default="lava_server.settings.debian",
            help='The Django server settings module to use.')
        group.add_argument('dispatcher', metavar='dispatcher',
            help='The dispatcher to use like "lava-dispatch"')
        group.add_argument('boardname', metavar='boardname',
            help='The board to run the job on')
        group.add_argument('json_file', metavar='json_file',
            help='The job definition to run')

    def _get_logfile_impl(self, logfile):
        self.logfile = logfile.path

    def _get_logfile(self):
        os.environ["DJANGO_SETTINGS_MODULE"] = self.args.settings_module
	# Because settings imports stuff from django.db, we need to make sure
	# that the settings are actually imported before we import
	# lava_scheduler_daemon.dbjobsource which also imports stuff from
	# django.db and leads to circular import pain.
        from django.conf import settings
        settings.INSTALLED_APPS
        from lava_scheduler_daemon.dbjobsource import DatabaseJobSource
        from twisted.internet import reactor

        source = DatabaseJobSource()

        def run():
            d = source.getLogFileForJobOnBoard(self.args.boardname)
            d = d.addCallback(self._get_logfile_impl)
            d.addCallback(lambda result: reactor.stop())

        reactor.callWhenRunning(run)
        reactor.run()
        return self.logfile

    def invoke(self):
        logfile = self._get_logfile()

        files = {}
        with open(self.args.json_file, 'r') as f:
            files[self.args.json_file] = f.read()

        self._logfd = open(logfile, 'wb')

        self.args.args = ['manage', 'schedulermonitor',
            self.args.dispatcher, self.args.boardname, self.args.json_file]
        super(celery_schedulermonitor, self).invoke('lava-server', files)

    def _process_message(self, body, message):
        self.logger.debug("Remote worker message: %r", message.payload)
        try:
            if 'stdout' in message.payload:
                s = message.payload['stdout'].encode('utf-8', errors='ignore')
                self._logfd.write(s)
                self._logfd.flush()
            elif 'stderr' in message.payload:
                s = message.payload['stderr'].encode('utf-8', errors='ignore')
                self._logfd.write(s)
                self._logfd.flush()
            else:
                if 'done' in message.payload:
                    self._logfd.close()
                super(celery_schedulermonitor, self)._process_message(body, message)
        except:
            traceback.print_exc()
