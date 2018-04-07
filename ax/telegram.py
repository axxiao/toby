"""
The telegram interface

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-04-07"
__version__ = "0.1"

    Version:
        0.1 (07/04/2018): init version


Classes:
    Cache - To access redis cache
    PubSub - To access redis pub/sub queues
"""
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from ax.log import get_logger
from threading import Thread
from ax.queue import Queue
from .exception import BotError
import json
import os
import requests
import collections
from .tools import get_ngrok_url

queue_to_user='toby.telegram.to_user'
queue_from_user='toby.telegram.from_user'


class Bot(Thread):
    """
    The Bot in back ground service mode
    """
    def __init__(self, name='Toby', in_queue=queue_to_user
                 , out_queue=queue_from_user
                 , logger_name='Toby.Bot.Telegram'):
        Thread.__init__(self)
        self.name = name
        self.updater = None
        self.logger = get_logger(logger_name)
        self.CMD = collections.namedtuple('CMD', 'doc handler')
        self.cmd_list = dict()
        self.dispatcher = None
        self.running = False
        self.queue = Queue(logger_name=logger_name)
        self.sub = self.queue.sub
        # self.pub = lambda msg: self.queue.pub(out_queue, msg)
        self.in_queue = in_queue
        self.out_queue = out_queue

    def pub(self, msg):
        self.logger.debug(str(msg))
        self.queue.pub(self.out_queue, msg)

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

    def disconnect(self):
        self.running = False
        self.updater.stop()

    def process_txt(self, bot, update, input_type):
        msg = {"user_id": update.message.from_user,
               "chat_id": update.message.chat_id,
               "type": "message",
               "message": update.message.text}
        self.logger.debug(str(msg))
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
            try:
                in_msg = self.sub(self.in_queue, timeout=3600, wildcard=False)
                self.logger.debug(in_msg)
                in_msg = json.loads(in_msg, strict=False)
                self.updater.bot.send_message(in_msg["chat_id"], in_msg["message"])
            except:
                pass


def send_request(msg, method='sendMessage', token=None, timeout=None, file=None):
    """
    Send request to Telegram API
    :param msg: in json, content of the request
    :param method: the method, default to sendMessage
    :param token: bot token if None, will use environment variable TOBY_TELEGRAM_TOKEN
    :param timeout: timeout time of the request, default to None
    :param file: file to upload, default to None
    :return: status
    """
    if token is None:
        token = os.environ['TOBY_TELEGRAM_TOKEN']
    url = 'https://api.telegram.org/bot' + token + '/' + method
    rtn = requests.post(url, json=msg, timeout=timeout).json() if msg else requests.post(url, files=file, timeout=timeout).json()
    if not rtn.get("ok", False):
        # request Failed
        raise BotError(rtn.get('error_code', -1), rtn.get('description', 'unknown error'))
    return rtn


def send_photo(chat_id, photoFile, caption=None, token=None):
    """
    Send photo
    :param chat_id: the chat id
    :param photoFile: the photo file, can be url or file: e.g. open('/data/xxx.png', 'rb')
    :param caption: caption of the file (when use url)
    :param token: bot token if None, will use environment variable TOBY_TELEGRAM_TOKEN
    :return: status
    """
    if type(photoFile) == str:
        req = json.loads('{"chat_id":"' + chat_id + '"')
        if caption:
            req['caption'] = caption
        req['photo'] = photoFile
        return send_request(req, method='sendPhoto', token=token)
    else:
        method = 'sendPhoto?chat_id=' + str(chat_id)
        files = {'photo': photoFile}
        return send_request(None, method=method, token=token, file=files)


def init_bot_webhook(url='https://alexxiao.me', token=None, certificate=None, allowed_updates=['message', 'callback_query']):
    """
    Init web hook
    :param url: the server url, set to None get local ngrok_url
    :param token: bot token if None, will use environment variable TOBY_TELEGRAM_TOKEN
    :param certificate: InputFile of self-signed certificate
    :param allowed_updates: List the types of updates you want your bot to receive
    :return:
    """
    tgt_url=get_ngrok_url() if url is None else url
    if token is None:
        token = os.environ['TOBY_TELEGRAM_TOKEN']
    tgt_url +='' if tgt_url[-1] == '/' else '/'+token
    req=json.loads('{"url":"'+tgt_url+'", "max_connections":20}')
    req['allowed_updates'] = allowed_updates
    if certificate:
        req['certificate'] = certificate
    return send_request(req, method='setWebhook', token=token)
