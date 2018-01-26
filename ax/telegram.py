import collections
import json
from threading import Thread

from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from .log import get_logger
from .zmq import QueuePub, QueueSub


class Bot(Thread):
    def __init__(self, name='Toby', in_queue='toby.telegram.to_user'
                 , out_queue='toby.telegram.from_user'
                 , logger_name='Toby.Bot.Telegram'):
        Thread.__init__(self)
        self.name = name
        self.updater = None
        self.logger = get_logger(logger_name)
        self.CMD = collections.namedtuple('CMD', 'doc handler')
        self.cmd_list = dict()
        self.dispatcher = None
        self.running = False
        self.sub = QueueSub(in_queue, logger_name=logger_name).sub
        pub = QueuePub(logger_name=logger_name)
        self.pub = lambda msg: pub.pub(out_queue, msg)

    def connect(self, token):
        self.logger.info('Starting Bot ' + self.name)
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.logger.debug('Connected to Telegram')
        process_cmd = lambda bot, upd: self.process_txt(bot, upd, input_type='command')
        process_msg = lambda bot, upd: self.process_txt(bot, upd, input_type='message')
        cmd_handler = MessageHandler(Filters.command, process_cmd)
        txt_handler = MessageHandler(Filters.text, process_msg)
        self.dispatcher.add_handler(cmd_handler)
        self.dispatcher.add_handler(txt_handler)
        self.start()
        self.updater.start_polling()
        self.logger.info('Bot is online')

    def process_txt(self, bot, update, input_type):
        msg = {"user_id": update.message.from_user,
               "chat_id": update.message.chat_id,
               "type": "message",
               "message": update.message.text}
        self.pub(msg)

    def register_cmd(self, cmd, fun, override=False):
        """
             The function of register a new command

             Input:
                 cmd: the command
                 fun: function for the command
                 override: [optional] default to False, allow to override existing

        """
        if cmd in self.cmd_list and not override:
            raise ValueError('[Error] Command is in list, override flag is not set to True to override')
        else:

            if not fun.__doc__:
                raise ValueError('[Error] Function doc missing, please provide')
            if cmd in self.cmd_list:
                self.dispatcher.remove_handler(self.cmd_list[cmd].handler)
            cmd_handler = CommandHandler(cmd, fun)
            self.cmd_list[cmd] = self.CMD(doc=fun.__doc__, handler=cmd_handler)
            self.dispatcher.add_handler(cmd_handler)

    def run(self):
        self.running = True
        while self.running:
            in_msg = json.loads(self.sub(), strict=False)
            self.updater.bot.send_message(in_msg["chat_id"], in_msg["message"])
