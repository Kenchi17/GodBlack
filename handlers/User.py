from telethon import Button,TelegramClient
import telethon
from utils import b_to_str
from infos import createStat
import config as cfg
from utils import sizeof_fmt,send_edit


async def setting(ev,bot,jdb,message_edited=None):
    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    cmd = ''
    data = ''
    try:
        cmd = str(text).split(' ')[0]
        data = str(text).split(' ')[1]
    except:pass
    if cmd == '/set_account':
        user = ''
        password = ''
        if data!='':
           datatokens = str(data).split(',')
           if len(datatokens)>0:
               user = datatokens[0]
           if len(datatokens)>1:
               password = datatokens[1]
        user_data['moodle_user'] = user
        user_data['moodle_password'] = password
        jdb.save_data_user(username,user_data)
    if cmd == '/set_host':
        if data!='':
            user_data['moodle_host'] = data
            jdb.save_data_user(username,user_data)
    if cmd == '/set_proxy':
        if data!='':
            user_data['proxy'] = data
            jdb.save_data_user(username,user_data)
    if cmd == '/set_repoid':
        if data!='':
            user_data['moodle_repo_id'] = int(data)
            jdb.save_data_user(username,user_data)
    if cmd == '/set_typecloud' or cmd == '/set_typemoodle':
       try:
        value = 'cloud'
        if 'typemoodle' in cmd:value = 'moodle'
        user_data['cloudtype'] = value
        jdb.save_data_user(username,user_data)
        jdb.save()
       except:pass
    jdb.save()
    await config(ev,bot,jdb,message_edited)
    pass

async def inline(ev,bot,jdb,message_edited=None):
    result = []
    builder:telethon.custom.InlineBuilder = ev.builder
    text = ev.query.query
    cmd = str(text).split(' ')[0]
    data = ''
    try:
        data = str(text).split(' ')[1]
    except:pass
    if cmd == 'account':
        user = ''
        password = ''
        if data!='':
           datatokens = str(data).split(',')
           if len(datatokens)>0:
               user = datatokens[0]
           if len(datatokens)>1:
               password = datatokens[1]
        description = 'Usuario : ' + user + '\n'
        description+= 'Contraseña : ' + password
        article = await builder.article(title='Configurar Cuenta: ',description=description,text='/set_account '+data)
        result.append(article)
    if cmd == 'repoid':
        description = ''
        if data!='':
            description = 'RepoID : ' + data + '\n'
        article = await builder.article(title='Configurar RepoID: ',description=description,text='/set_repoid '+data)
        result.append(article)
    if cmd == 'zips':
        description = ''
        dataint = 1
        if data!='':
            try:
                dataint = int(data)
                data = sizeof_fmt(1024*1024*dataint)
            except:pass
            description = 'Zips : ' + data + '\n'
        article = await builder.article(title='Configurar Zips: ',description=description,text='/set_zips '+str(dataint))
        result.append(article)
    if cmd == 'proxy':
        description = ''
        if data!='':
            description = 'Proxy : ' + data + '\n'
        article = await builder.article(title='Configurar Proxy: ',description=description,text='/set_proxy '+data)
        result.append(article)
    await ev.answer(result)
    pass


async def config(ev,bot,jdb,message_edited=None):
    username = ev.chat.username
    userinfo = jdb.get_user(username)
   
    text = createStat(username,userinfo,jdb.is_admin(username))

    buttons = []
    buttons.append([Button.inline('📕 << Menu Principal','user_start')])

    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text, buttons=buttons)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text, buttons=buttons)
    pass

async def start(ev,bot,jdb,message_edited=None):
    text = '👋 Bienvenido A TGUploaderPro.👋\n\n'
    text+= 'Toma Nota....✍🏼\n\n'
    text+= '🧑🏻‍🏫 TGUploaderPro es un bot simple,facil y rapido, destinado a la descarga y subida de contenido gratis en cuba 🙀. Si asi como oyes.!\n\n'
    text+= 'Su uso es sencillo , aca de bajo 👇 te dejo las opciones.\n'

    buttons = [
        [Button.inline('🗂Abrir Directorio🗂','open_root')],
        [Button.inline('⚙️Configuraciones⚙️','user_config')]
    ]

    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text, buttons=buttons)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text, buttons=buttons)
    pass