# telethon imports
from telethon import TelegramClient, events, sync, Button
import asyncio

# local imports
import config
from TManager import ThreadManager
from JDatabase import JsonDatabase
from MessageDispatcher import MessageDispatcher

# import handles
import handlers.User as User
import handlers.Http as Http
import handlers.Root as Root
import handlers.File as File
import handlers.Linux as Linux
import handlers.Uploader as Uploader

import infos


async def onMessage(args):
    ev: events.NewMessage.Event = args[0]
    bot: TelegramClient = args[1]
    tmanager: ThreadManager = args[2]
    jdb: JsonDatabase = args[3]
    dispatcher: MessageDispatcher = args[4]
    threadid = tmanager.this_thread.id
    await dispatcher.dispatch(ev, bot, jdb)
    await tmanager.dispose(threadid)
    pass


def main():
    print("Runing TGUploaderPro...")

    api_id = config.TG_API_ID
    api_hash = config.TG_API_HASH
    bot_token = config.BOT_TOKEN
    tl_admin_user = config.TG_ADMIN_USER

    # set in debug
    api_id = 13108769
    api_hash = "080207b4f4d213b0ad99e15f08bfa982"
    bot_token = "5182785203:AAFFoRQ-eY06Wd77je34rebQn1d9JIVS1Hc"
    tl_admin_user = "Kenchi17"
    # end

    # create dispatcher and regs
    dispatcher = MessageDispatcher()
    # regs user
    dispatcher.reg(["/start", "user_start"], User.start)
    dispatcher.reg(["user_config"], User.config)
    dispatcher.reg(["/set_"], User.setting)
    dispatcher.reg(["account", "proxy", "repoid", "zips"], User.inline)
    # reg http
    dispatcher.reg("http", Http.handle)
    dispatcher.reg("cancel_download", Http.cancel)
    # reg files
    dispatcher.reg_file(File.handle)
    # regs Root
    dispatcher.reg(["/root", "open_root"], Root.handle)
    dispatcher.reg("del_root", Root.delete)
    # regs Linux
    dispatcher.reg(["/ls"], Linux.ls)
    dispatcher.reg(["/cd"], Linux.cd)
    dispatcher.reg(["/rm"], Linux.rm)
    dispatcher.reg(["/zip"], Linux.zip)
    # regs Upload
    dispatcher.reg(["/upload"], Uploader.upload)

    # create a bot and events
    bot = TelegramClient("bot", api_id=int(api_id), api_hash=api_hash).start(bot_token=bot_token)

    loop = asyncio.get_event_loop()
    tmanager = ThreadManager(loop)

    async def dispatch_event(ev: events.NewMessage.Event):
        jdb = JsonDatabase("database")
        jdb.check_create()
        jdb.load()
        user_name = ""
        try:
            user_name = ev.message.chat.username
        except:
            user_name = ev.chat.username
        user_info = jdb.get_user(user_name)
        if user_info or user_name in str(tl_admin_user).split(","):  # validate user
            if user_info is None:
                if user_name == tl_admin_user:
                    jdb.create_admin(user_name)
                else:
                    jdb.create_user(user_name)
                jdb.save()
            await tmanager.wait_for_free()  # limit numbre of threads bind
            await tmanager.start(targetfunc=onMessage, args=(ev, bot, tmanager, jdb, dispatcher))
        pass

    @bot.on(events.InlineQuery())
    async def click_handler(ev: events.NewMessage.Event):
        await dispatch_event(ev)

    @bot.on(events.CallbackQuery())
    async def click_handler(ev: events.NewMessage.Event):
        await dispatch_event(ev)

    @bot.on(events.NewMessage())
    async def process(ev: events.NewMessage.Event):
        await dispatch_event(ev)

    loop.run_forever()
    pass


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(str(ex))
        main()
