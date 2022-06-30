import os
import config
from utils import b_to_str,sizeof_fmt,get_disk_space
from pathlib import Path
import shutil

from telethon import Button,TelegramClient


#1_0_0_0_0_0_0_0
def paths_command(command):
    indexs = str(command).split('_')
    path = ''
    for i in indexs:
        if i =='':continue
        root = os.path.join(os.getcwd(),config.ROOT_DIR,path)
        index = int(i)
        list = os.listdir(root)
        path += list[index] + '\\'
    return path

def last_path_command(command):
    last = ''
    i = len(command) - 1
    while i>=0:
        char = command[i]
        if char == '_':
            last = command[0:i]
            break
        i-=1
    return last

def list_dir_command(command):
    paths = paths_command(command)
    root = os.path.join(os.getcwd(),config.ROOT_DIR)
    root_exist = os.path.exists(root)
    if not root_exist:
        os.mkdir(root)
    path = os.path.join(os.getcwd(),config.ROOT_DIR,paths)
    try:
        return os.listdir(path)
    except:pass
    return None

def get_command_info(command):
    path = paths_command(command)
    fullpath = os.path.join(os.getcwd(),config.ROOT_DIR,path)
    if path=='':
        path = 'root'
    path_obj = Path(fullpath)
    name = path
    if path!='root':
       name = path.split('\\')[-2]
    sizef = 0
    pathf = fullpath
    isfile = False
    if path_obj.is_file():
       isfile = True
       fpath = fullpath[0:len(fullpath)-1]
       pathf = fpath
       sizef = os.path.getsize(fpath)
    else:
        isfile = False
        list = os.listdir(path_obj)
        for f in list:
            sizef += os.path.getsize(fullpath+f)
    return {'name':name,'sizef':sizeof_fmt(sizef),'fullpath':pathf,'isfile':isfile}

async def delete(ev,bot:TelegramClient,jdb,message_edited=None):
    path_command = ''
    try:
        text = str(b_to_str(ev.data))
        path_command = text.split(' ')[1]
    except:pass
    info = get_command_info(path_command)
    try:
        os.unlink(info['fullpath'])
    except:
        shutil.rmtree(info['fullpath'])
    path_command = last_path_command(path_command)
    await render(path_command,ev,bot,jdb)

async def handle(ev,bot:TelegramClient,jdb,message_edited=None):
    path_command = ''
    try:
        text = str(b_to_str(ev.data))
        path_command = text.split(' ')[1]
    except:pass
    await render(path_command,ev,bot,jdb)
    
async def render(path_command,ev,bot:TelegramClient,jdb,message_edited=None):
    paths = paths_command(path_command)
    root = os.path.join(os.getcwd(),config.ROOT_DIR,paths)
    list_dir = list_dir_command(path_command)
    buttons = []
    text = 'reply options'
    if list_dir: # this is a folder
        if root != os.path.join(os.getcwd(),config.ROOT_DIR,''):
            buttons.append([Button.inline('💢Eliminar💢','del_root ' + path_command)])
        else:
            if len(list_dir)<=0:
                buttons = None
        list_count = len(list_dir)
        i=0
        while i<list_count:
             row = [Button.inline(list_dir[i],'open_root ' + path_command + '_' + str(i))]
             try:
                 row.append(Button.inline(list_dir[i+1],'open_root ' + path_command + '_' + str(i+1)))
                 row.append(Button.inline(list_dir[i+2],'open_root ' + path_command + '_' + str(i+1)))
             except:pass
             buttons.append(row)
             i+=3
        dinfo = get_command_info(path_command)
        shutilinfo = get_disk_space()
        text = '💾 '+shutilinfo['used']+'/' + shutilinfo['total']+'\n\n'
        text+= '📁'+dinfo['name']+'📁\n'
        text+= '📦 '+dinfo['sizef']+'\n\n'
    else: # this is file
        finfo = get_command_info(path_command)
        shutilinfo = get_disk_space()
        text = '💾 '+shutilinfo['used']+'/' + shutilinfo['total']+'\n\n'
        text+= '📁'+finfo['name']+'📁\n'
        text+= '📦 '+finfo['sizef']+'\n\n'

        if root != os.path.join(os.getcwd(),config.ROOT_DIR,''):
            buttons.append([Button.inline('💢Eliminar💢','del_root ' + path_command)])
        pass
    if root != os.path.join(os.getcwd(),config.ROOT_DIR,''):
            back_command = last_path_command(path_command)
            buttons.append([Button.inline('<< Atras','open_root ' + back_command)])
    else:
        buttons.append([Button.inline('📕<< Menu Principal','user_start')])
    try:
        await bot.edit_message(ev.chat.id,ev.query.msg_id,text=text, buttons=buttons)
    except Exception as ex:
        await bot.send_message(ev.sender_id,text, buttons=buttons)
    pass