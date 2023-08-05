# -*- coding: utf-8 -*-
"""
"""
import json
import uuid
import thread
import logging
import threading
from Queue import LifoQueue

import zmq
from zmq import ZMQError

from . import frames


class MessageOutError(Exception):
    """Raised for attempting to send an invalid message."""


class Transceiver(object):

    def __init__(self, config={}, message_handler=None):
        """Set up a receiver which connects to the messaging hub.

        :param config: This is a dict in the form::

            config = dict(
                incoming='tcp://localhost:15566', # default
                outgoing='tcp://localhost:15567',
                idle_timeout=1000, # milliseconds:
            )

        """
        self.log = logging.getLogger("evasion.messenger.endpoint.Transceiver")

        self.endpoint_uuid = str(uuid.uuid4())

        self.exit_time = threading.Event()
        self.wait_for_exit = threading.Event()

        self.incoming = None # configured in main().
        self.incoming_uri = config.get("incoming", 'tcp://localhost:15566')
        self.log.info("Recieving on <%s>" % self.incoming_uri)

        self.outgoing_uri = config.get("outgoing", 'tcp://localhost:15567')
        self.log.info("Sending on <%s>" % self.outgoing_uri)

        self.idle_timeout = int(config.get("idle_timeout", 2000))
        self.log.info("Idle Timeout (ms): %d" % self.idle_timeout)

        self.message_handler = message_handler
        self.sync_message = frames.sync_message(
            "endpoint-%s" % self.endpoint_uuid
        )

        # Queue up messages to be sent in the main message loop
        self._out_queue = LifoQueue()


    def main(self):
        """Running the main loop sending and receiving.

        This will keep running until stop() is called. This
        sets the exit flag causing clean up and shutdown.

        """
        self.exitTime = False

        context = zmq.Context()
        incoming = context.socket(zmq.SUB)
        incoming.setsockopt(zmq.SUBSCRIBE, '')
        incoming.connect(self.incoming_uri)

        outgoing = context.socket(zmq.PUSH);
        outgoing.connect(self.outgoing_uri);

        def _shutdown():
            try:
                incoming.close()
            except ZMQError:
                self.log.exception("main: error calling incoming.close()")
            try:
                outgoing.close()
            except ZMQError:
                self.log.exception("main: error calling outgoing.close()")
            try:
                context.term()
            except ZMQError:
                self.log.exception("main: error calling context.term()")

        try:
            poller = zmq.Poller()
            poller.register(incoming, zmq.POLLIN)

            while not self.exit_time.is_set():
                try:
                    events = poller.poll(self.idle_timeout)

                except ZMQError as e:
                    # 4 = 'Interrupted system call'
                    if e.errno == 4:
                        self.log.info("main: exit time: %s" % e)
                        break
                    else:
                        self.log.info("main: <%s>" % e)
                        break

                except Exception:
                    self.log.exception("main: fatal error while polling ")
                    break

                else:
                    if (events > 0):
                        msg = incoming.recv_multipart()
                        self.message_in(tuple(msg))

                    # Now recover and queued outgoing messages:
                    if not self._out_queue.empty():
                        message = self._out_queue.get_nowait()
                        if message:
                            try:
                                # send sync hub followed by message. The sync
                                # will kick the hub into life if its just
                                # started:
                                outgoing.send_multipart(self.sync_message)
                                outgoing.send_multipart(message)

                            except ZMQError as e:
                                # 4 = 'Interrupted system call'
                                if e.errno == 4:
                                    self.log.info((
                                        "main: sigint or other signal interrupt"
                                        ", exit time <%s>"
                                    ) % e)
                                    break
                                else:
                                    self.log.info("main: <%s>" % e)
                                    break

                            except Exception:
                                self.log.exception("main: fatal error sending ")
                                break

                            finally:
                                self._out_queue.task_done()

        finally:
            self.wait_for_exit.set()
            _shutdown()


    def start(self):
        """Set up zmq communication and start receiving messages from the hub.
        """
        # coverage can't seem to get to this:
        def _main(notused): # pragma: no cover
            self.exit_time.clear()
            self.wait_for_exit.clear()
            self.main()
        thread.start_new(_main, (0,))


    def stop(self, wait=2):
        """Stop receiving messages from the hub and clean up.

        :param wait: The time in seconds to wait before giving up
        on a clean shutdown.

        """
        self.log.info("stop: shutting down messaging.")
        self.exit_time.set()
        self.wait_for_exit.wait(wait)
        self.log.info("stop: done.")


    def message_out(self, message):
        """This sends a message to the messagehub for dispatch to all connected
        endpoints.

        :param message: A tuple or list representing a multipart ZMQ message.

        If the message is not a tuple or list then MessageOutError
        will be raised.

        Note: The message is actually queued here so that the main loop will
        send it when its ready.

        :returns: None.

        """
        if isinstance(message, list) or isinstance(message, tuple):
            self._out_queue.put(message)
        else:
            m = "The message must be a list or tuple instead of <%s>" % type(
                message
            )
            raise MessageOutError(m)


    def message_in(self, message):
        """Called on receipt of an evasion frame to determine what to do.

        The message_handler set in the constructer will be called if one
        was set. If none was set then the message will be logged at the
        DEBUG level.

        :param message: A tuple or list representing a multipart ZMQ message.

        :returns: None.

        """
        if self.message_handler:
            try:
                #self.log.debug("message_in: message <%s>" % str(message))
                self.message_handler(message)
            except:
                self.log.exception("message_in: Error handling message - ")
        else:
            self.log.debug("message_in: message <%s>" % str(message))


class SubscribeError(Exception):
    """Raised for problems subscribing to a signal."""


class Register(object):
    """This is used in a process to a callbacks for signals which
    can be published locally or remotely.
    """
    def __init__(self, config={}, transceiver=None):
        """
        :param config: This is passed to the transceiver.

        The config will only be passed if transceiver argument
        has not been provided.

        :param transceiver: This is an optional transceiver instance.

        This transceiver will be used instead of creating one.

        The Register adds its message_handler method as the
        message handler passed to Transceiver if created internally.

        """
        self.log = logging.getLogger("evasion.messenger.endpoint.Register")

        self._subscriptions = dict()

        if not transceiver:
            self.transceiver = Transceiver(config, self.message_handler)
        else:
            self.transceiver = transceiver


    @property
    def endpoint_uuid(self):
        """Return the transceiver's endpoint_uuid."""
        return self.transceiver.endpoint_uuid


    @property
    def exit_time(self):
        """Returns True if the transceiver is shutting down i.e. stop called."""
        return self.transceiver.exit_time.isSet()


    @classmethod
    def validate_signal(cls, signal):
        """Sanity check the given signal string.

        :param signal: This must be a non empty string.

        ValueError will be raised if signal is not a string or empty.

        :returns: For a given string a stripped upper case string.

        >>> Register.signal(' tea_time ')
        >>> 'TEA_TIME'

        """
        if not isinstance(signal, basestring):
            raise ValueError(
                "The signal must be a string and not <%s>" % type(
                signal
            ))

        signal = signal.strip().upper()
        if not signal:
            raise ValueError("The signal must not be an empty string")

        return signal


    def start(self):
        """Call the transceiver's start()."""
        self.transceiver.start()


    def stop(self):
        """Call the transceiver's stop()."""
        self.transceiver.stop()


    def main(self):
        """Call the transceiver's main() running the mainloop until stopped."""
        self.transceiver.main()


    def handle_dispath_message(self, endpoint_uuid, signal, data, reply_to):
        """Handle a DISPATCH message received.

        This will look in the subscriptions for the signal. It will then
        go through calling each function present.

        The signature of the function subscribed must be:

        .. code-block:: python

            signal_subscriber(endpoint_uuid, data, reply_to)

        :returns: None.

        """
        signal = self.validate_signal(signal)

        if signal in self._subscriptions:
            for signal_subscriber in self._subscriptions[signal]:
                try:
                    reply_to = reply_to if reply_to != '0' else None
                    signal_subscriber(endpoint_uuid, data, reply_to)
                except:
                    self.log.exception((
                        "handle_dispath_message: the callback <%s> for signal "
                        "<%s> has errored - "
                    ) % (signal_subscriber, signal))


    def handle_hub_present_message(self, payload):
        """Handle a HUB_PRESENT message.

        :param payload: This the content of a HUB_PRESENT message from the hub.

        Currently it is a dict in the form:

        .. code-block:: python

            dict(version='X.Y.Z')

        :returns: None.

        """
        #self.log.debug("handle_hub_present_message: %s" % payload)


    def handle_sync_message(self, payload):
        """Handle a SYNC message received from the HUB.

        :param payload: version of the hub message.

        Currently it is a dict in the form:

        .. code-block:: python

            {"from": "endpoint-<uuid string>"}

            # or

            {"from": "hub-<uuid string>"}

        :returns: None.

        """
        #self.log.debug("handle_hub_present_message: %s" % payload)


    def unhandled_message(self, reason, message):
        """Called when and unknown or malformed message is handled.

        :param reason: 'unknown' or 'error'

        :param message: The raw message received.

        """
        if reason == 'unknown':
            self.log.warn("message_handler: unknown command <%s> ignore." % (
                message[0]
            ))
        else:
            self.log.error("message_handler: invalid message <%s>" % message)


    def message_handler(self, message):
        """Called to handle a ZMQ Evasion message received.

        :param message: This must be a message in the Evasion frame format.

        The message_handler will attempt to decode the first word and
        use it to call the corresponding method.

        """
        try:
            fields_present = len(message)

            if fields_present > 0:
                command = message[0]
                if command and isinstance(command, basestring):
                    command = command.strip().lower()

                command_args = []
                if fields_present > 1:
                    command_args = message[1:]

                if command == "dispatch":
                    endpoint_uuid, signal, data, reply_to = command_args
                    data = json.loads(data)
                    self.handle_dispath_message(
                        endpoint_uuid, signal, data, reply_to
                    )

                elif command == "hub_present":
                    data = json.loads(command_args[0])
                    self.handle_hub_present_message(data)

                elif command == "sync":
                    data = json.loads(command_args[0])
                    self.handle_sync_message(data)

                else:
                    self.unhandled_message('unknown', message)

        except Exception:
            m = "message_handler: error processing message <%s> " % str(message)
            self.log.exception(m)
            self.unhandled_message('error', message)


    def subscribe(self, signal, callback):
        """Called to subscribe to a string signal.

        :param signal: A signal to subscribe too e.g. tea_time.

        The signal must be a string or SubscribeError will be raised.
        The signal will be stripped and uppercased for internal stored.

        Case is not important an us internally is forced to lower case in all
        operations.

        :param callback: This is a function who takes a two arguments.

        If the callback is already subscribed then the subscribe request
        will be ignored.

        The first argument is a data dict representing any data coming with
        the signal. The second is a reply_to argument. If this is not None
        then a reply not expected.

        E.g.::

            def my_handler(data, reply_to=None):
                '''Do something no reply'''


            def my_handler(data, reply_to='uuid string'):
                '''Do something and reply with results'''

        """
        signal = self.validate_signal(signal)

        if signal not in self._subscriptions:
            self._subscriptions[signal] = []

        if callback not in self._subscriptions:
            self._subscriptions[signal].append(callback)
        else:
            self.log.warn((
                "subscribe: The callback<%s> is already subscribed. "
                "Ignoring request."
            ) % str(callback))



    def unsubscribe(self, signal, callback):
        """Called to remove a callback for a signal.

        :param signal: The signal used in a call to subscribe.
        :param callback: The function to unsubscribe.

        """
        signal = self.validate_signal(signal)

        if signal in self._subscriptions:
            try:
                self._subscriptions[signal].remove(callback)
            except ValueError:
                self.log.warn((
                    "unsubscribe: The callback<%s> is not subscribed for <%s>. "
                    "Ignoring request."
                ) % (str(callback), signal))
            else:
                self.log.debug((
                    "unsubscribe: The callback<%s> has been unsubscribed "
                    "from <%s>"
                ) % (callback, signal))


    def publish(self, signal, data):
        """Called to publish a signal to all subscribers.

        :param signal: The signal used in a call to subscribe.

        :param data: This is a dictionary of data.

        """
        #self.log.debug("publish: sending <%s> to hub <%s>"% (signal, data))
        dispatch_message = frames.dispatch_message(
            self.endpoint_uuid,
            signal,
            data,
        )
        self.transceiver.message_out(dispatch_message)



