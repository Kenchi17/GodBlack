import os
import config
from utils import b_to_str,sizeof_fmt,get_disk_space,get_file_size,get_url_file_name
from pathlib import Path
import shutil

from telethon import Button,TelegramClient


from utils import b_to_str,sizeof_fmt,get_disk_space


import zipfile

USERPATHS = {}

async def list_dir(path):
    path = str(path).replace('/root','')
    if path[0]!='/':
        path = '/'+path
    path = 'root' + path
    fullpath = os.path.abspath(path)
    list = os.listdir(fullpath)
    result = []
    for item in list:
        result.append(path+'/'+item)
    return result

async def list_dir_msg(path):
    path = str(path).replace('/root','')
    if path[0]!='/':
        path = '/'+path
    path = 'root' + path
    fullpath = os.path.abspath(path)
    result = os.listdir(fullpath)
    shutilinfo = get_disk_space(fullpath)
    msg = ''
    msg += '💾 '+shutilinfo['used']+'/' + shutilinfo['total']+'\n\n'
    msg += '🗂 '+path+' 🗂\n\n'
    i = 0
    for f in result:
        if '.' in f:
            msg += str(i)+' - '+'📄'+f+'\n'
        else:
            msg += str(i)+' - '+'📁'+f+'\n'
        i+=1
    return msg


async def ls(ev,bot,jdb,message_edited=None):
    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = '/'
    try:
        path = user_data['path']
    except:
        user_data['path'] = path
        jdb.save_data_user(username,user_data)
    try:
        tokens = str(text).split(' ',1)
        cmd = tokens[0]
        data = ''
        if len(tokens)>1:
            data = tokens[1]
        if '/ls' in cmd:
            text = await list_dir_msg(path)
    except:pass
    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text)
    pass

async def cd(ev,bot,jdb,message_edited=None):
    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = '/'
    try:
        path = user_data['path']
    except:
        user_data['path'] = path
        jdb.save_data_user(username,user_data)
    try:
        tokens = str(text).split(' ',1)
        cmd = tokens[0]
        data = ''

        if len(tokens)>1:
            data = tokens[1]
        if '/cd' in cmd:
            index = -1
            if data!='':
                try:
                    index = int(data)
                except:pass
            if index!=-1:
                list = await list_dir(path)
                data = list[index]
            if path[-1] != '/':
                path += '/'
            data = path + data
            if '..' in data:
                tokenspath = str(data).split('/')
                data = ''
                i = 0
                for t in tokenspath:
                    if t=='..' :continue
                    if t=='' :data+='/'
                    if tokenspath[i+1] != '..':
                       data+=t
                    i+=1
            user_data['path'] = data
            jdb.save_data_user(username,user_data)
            text = await list_dir_msg(data)
            pass
    except:pass
    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text)
    pass

async def rm(ev,bot,jdb,message_edited=None):
    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = '/'
    try:
        path = user_data['path']
    except:
        user_data['path'] = path
        jdb.save_data_user(username,user_data)
    try:
        tokens = str(text).split(' ',1)
        cmd = tokens[0]
        data = ''
        if len(tokens)>1:
            data = tokens[1]
        if '/rm' in cmd:
            if data!='':
                index = -1
                name = data
                try:
                    index = int(data)
                except:pass
                if index!=-1:
                    result = await list_dir(path)
                    try:
                        os.remove(result[index])
                    except:
                        shutil.rmtree(result[index])
                    text = await list_dir_msg(path)
    except:pass
    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text)
    pass

async def write_zip_path(path,zip):
    list = os.listdir(path)
    for f in list:
        if '.' in f:
            pathfull = path+'/'+f
            filename = get_url_file_name(pathfull,None)
            zip.write(pathfull,filename)

async def zip(ev,bot,jdb,message_edited=None):
    message = await bot.send_message(ev.sender_id,'⏳Procesando...')
    username = ev.message.chat.username
    user_data = jdb.get_user(username)
    text = ev.message.text
    path = '/'
    try:
        path = user_data['path']
    except:
        user_data['path'] = path
        jdb.save_data_user(username,user_data)
    try:
        tokens = str(text).split(' ')
        cmd = tokens[0]
        index = -1
        splitSize = -1
        if len(tokens)>1:
            index = int(tokens[1])
        if len(tokens)>2:
            splitSize = int(tokens[2])
        if '/zip' in cmd:
                if index!=-1:
                    result = await list_dir(path)
                    item = result[index]
                    fullpath = os.path.abspath(item)
                    pathobj = Path(fullpath)
                    size = get_file_size(fullpath)
                    filename = get_url_file_name(item,None)
                    if splitSize!=-1:
                        size = 1024 * 1024 * splitSize
                    await message.edit(text='📚Comprimiendo...📚')
                    multifile = zipfile.MultiFile(item,size+1024)
                    zip = zipfile.ZipFile(multifile,  mode='w', compression=zipfile.ZIP_DEFLATED)
                    if '.' in filename:
                        zip.write(item,filename)
                    else:
                        await write_zip_path(item,zip)
                    zip.close()
                    multifile.close()
                    text = await list_dir_msg(path)
    except:pass
    try:
        await message.edit(text)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text)
    pass