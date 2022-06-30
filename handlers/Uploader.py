from MoodleClient import MoodleClient
from NexCloudClient import NexCloudClient

import os

import ProxyCloud

from utils import get_file_size,get_file_size,sizeof_fmt,nice_time,text_progres,porcent,b_to_str
from telethon import Button,TelegramClient


import zipfile
import datetime
import asyncio

async def progress_upload(filename, currentBits, totalBits, speed , time, args, stop=False):
    try:
        bot = args[0]
        message = args[1]
        text = '<b>'
        text += '📡 Subiendo Archivo....\n\n'
        text += '➤ Archivo: '+filename+'\n'
        text += text_progres(currentBits,totalBits)+'\n'
        text += '➤ Porcentaje: '+str(porcent(currentBits,totalBits))+'%\n\n'
        text += '➤ Total: '+sizeof_fmt(totalBits)+'\n\n'
        text += '➤ Descargado: '+sizeof_fmt(currentBits)+'\n\n'
        text += '➤ Velocidad: '+sizeof_fmt(speed)+'/s\n\n'
        text += '➤ Tiempo de Descarga: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
        text += '</b>'
        await message.edit(text,parse_mode='HTML')
    except Exception as ex:
        print(str(ex))

async def upload(ev,bot,jdb,message_edited=None):
    message = await bot.send_message(ev.sender_id,'⏳Procesando...')

    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = user_data['path']

    tokens = text.split(' ')

    index = -1
    cloudtype = 'moodle'
    uptype = 'draft'
    splitsize = -1
    buttons = None

    if len(tokens)>1:
        index = int(tokens[1])
    if len(tokens)>2:
        cloudtype = tokens[2]
    if len(tokens)>3:
        uptype = tokens[3]
    if len(tokens)>4:
        splitsize = int(tokens[4])

    if index!=-1:
         if path=='/':
             path = 'root'
         list = os.listdir(path)
         if path[-1]!='/':
             path+='/'

         item = path + list[index]
         filefullsize = get_file_size(item)
         filefullname = str(item).split('/')[-1]

         files = []
         files.append(item)

         if splitsize!=-1:
             await message.edit('📚Comprimiendo Archivos...📚')
             filename = str(item).split('/')[-1]
             multifile = zipfile.MultiFile(item,1024*1024 * splitsize)
             zip = zipfile.ZipFile(multifile,  mode='w', compression=zipfile.ZIP_DEFLATED)
             zip.write(item,filename)
             zip.close()
             multifile.close()
             files.clear()
             files = multifile.files

         if cloudtype == 'moodle':
             proxy = None
             if user_data['proxy']!='':
                 proxy = ProxyCloud.parse(user_data['proxy'])
             client = MoodleClient(
                 user_data['moodle_user'],
                           user_data['moodle_password'],
                           user_data['moodle_host'],
                           user_data['moodle_repo_id'],
                           proxy)
             await message.edit('🗳Logeandose...🗳')
             loged = client.login()
             itemid = None
             if loged:
                 buttons = []
                 evidence = None
                 blog = None
                 if uptype=='evidencia':
                     evidence = client.createEvidence(filefullname)
                 i=-1
                 buttonsadd = []
                 for item in files:
                     i+=1
                     if i>=2:
                         buttons.append(buttonsadd)
                         buttonsadd.clear()
                         i=-1
                     if uptype == 'draft':
                         filename = str(item).split('/')[-1]
                         filesize = get_file_size(item)
                         text = '📡 Subiendo Archivo(s)....\n\n'
                         text += '👨🏻‍💻 '+filename+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if len(files)>1:
                            text += '📚 '+str(len(files))+' Partes\n'
                         await message.edit(text)
                         itemid,data = await client.upload_file_draft(item,progress_upload,(bot,message))
                         text = '💚 Subiendo con Éxito 💚\n\n'
                         text += '👨🏻‍💻 '+filefullname+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if 'url' in data:
                            buttonsadd.append(Button.url('🔗'+filename+'🔗',data['url']))
                     if uptype == 'evidencia':
                         filename = str(item).split('/')[-1]
                         filesize = get_file_size(item)
                         text = '📡 Subiendo Archivo(s)....\n\n'
                         text += '👨🏻‍💻 '+filename+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if len(files)>1:
                            text += '📚 '+str(len(files))+' Partes\n'
                         await message.edit(text)
                         itemid,data = await client.upload_file(item,evidence,itemid,progress_upload,(bot,message))
                         text = '💚 Subiendo con Éxito 💚\n\n'
                         text += '👨🏻‍💻 '+filefullname+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if 'url' in data:
                            buttonsadd.append(Button.url('🔗'+filename+'🔗',data['url']))
                     if uptype == 'blog':
                         filename = str(item).split('/')[-1]
                         filesize = get_file_size(item)
                         text = '📡 Subiendo Archivo(s)....\n\n'
                         text += '👨🏻‍💻 '+filename+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if len(files)>1:
                            text += '📚 '+str(len(files))+' Partes\n'
                         await message.edit(text)
                         itemid,data = await client.upload_file_blog(item,blog,itemid,progress_upload,(bot,message))
                         text = '💚 Subiendo con Éxito 💚\n\n'
                         text += '👨🏻‍💻 '+filefullname+'\n'
                         text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                         if 'url' in data:
                            buttonsadd.append(Button.url('🔗'+filename+'🔗',data['url']))
                 if evidence:
                     client.saveEvidence(evidence)
                 if uptype=='blog':
                     blog = client.createBlog(filefullname,itemid)
                 if len(buttonsadd)>0:
                    buttons.append(buttonsadd)
             else:
                 text = '❌Error En La Autenticacion❌'
         if cloudtype == 'cloud':
            proxy = None
            if user_data['proxy']!='':
                proxy = ProxyCloud.parse(user_data['proxy'])
            client = NexCloudClient(
                 user_data['moodle_user'],
                           user_data['moodle_password'],
                           user_data['moodle_host'],
                           proxy)
            loged = client.login()
            if loged:
                 i=-1
                 buttonsadd = []
                 for item in files:
                    i+=1
                    if i>=2:
                         buttons.append(buttonsadd)
                         buttonsadd.clear()
                         i=-1
                    filename = str(item).split('/')[-1]
                    filesize = get_file_size(item)
                    text = '📡 Subiendo Archivo(s)....\n\n'
                    text += '👨🏻‍💻 '+filename+'\n'
                    text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                    if len(files)>1:
                       text += '📚 '+str(len(files))+' Partes\n'
                    await message.edit(text)
                    data = client.upload_file(item)
                    text = '💚 Subiendo con Éxito 💚\n\n'
                    text += '👨🏻‍💻 '+filefullname+'\n'
                    text += '📦Tamaño Total: '+sizeof_fmt(filefullsize)+' \n'
                    if 'url' in data:
                        buttonsadd.append(Button.url('🔗'+filename+'🔗',data['url']))
                    if len(buttonsadd)>0:
                        buttons.append(buttonsadd)
            else:
                 text = '❌Error En La Autenticacion❌'
    try:
        await message.edit(text,buttons=buttons)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text,buttons=buttons)
    pass