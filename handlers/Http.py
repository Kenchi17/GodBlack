import config
import datetime


from telethon import Button,TelegramClient
from pydownloader.downloader import Downloader

import infos

from utils import get_file_size,sizeof_fmt,nice_time,text_progres,porcent,b_to_str


Downloaders = []


async def cancel(ev,bot,jdb,message_edited=None):
    try:
        cancelid = str(b_to_str(ev.data)).split(' ')[1]
        for d in Downloaders:
            if cancelid in d.id:
                await d.stop()
                Downloaders.remove(d)
    except:pass
    pass

async def progress_download(downloader, filename, currentBits, totalBits, speed , time, args, stop=False):
    try:
        bot = args[0]
        message = args[1]
        id = args[2]
        text = '<b>'
        text += '📡 Descargando Archivo....\n\n'
        text += '➤ Archivo: '+filename+'\n'
        text += text_progres(currentBits,totalBits)+'\n'
        text += '➤ Porcentaje: '+str(porcent(currentBits,totalBits))+'%\n\n'
        text += '➤ Total: '+sizeof_fmt(totalBits)+'\n\n'
        text += '➤ Descargado: '+sizeof_fmt(currentBits)+'\n\n'
        text += '➤ Velocidad: '+sizeof_fmt(speed)+'/s\n\n'
        text += '➤ Tiempo de Descarga: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
        text += '</b>'
        await message.edit(text,parse_mode='HTML',
                           buttons=[[Button.inline('💢Cancelar💢','cancel_download '+str(id))]])
    except Exception as ex:
        print(str(ex))
    pass


async def handle(ev,bot,jdb,message_edited=None):
    
    try:

        url = ev.message.text

        message = await bot.send_message(ev.sender_id,'⏳Procesando...')

        downloader = Downloader(config.ROOT_DIR + '/')
        Downloaders.append(downloader)
        file = await downloader.download_url(url,progressfunc=progress_download,args=(bot,message,downloader.id))
        filesize = get_file_size(file)

        buttons = []
        buttons.append([Button.inline('🗂Abrir Carpeta🗂','open_root')])

        if not downloader.stoping:
            text = '<b>'
            text += '💚 Descargado con Éxito 💚\n\n'
            filename = str(file).split('/')[-1]
            text += '👨🏻‍💻 '+filename+'\n'
            text += '📦Tamaño Total: '+sizeof_fmt(filesize)+' \n'
            text += '</b>'
        else:
            text = '<b>'
            text += '❌ Se Cancelo La Descarga ❌\n'
            filename = str(file).split('/')[-1]
            text += '👨🏻‍💻 '+filename+'\n'
    
        try:
            await message.edit(text=text, buttons=buttons,parse_mode='HTML')
        except Exception as ex:
            await bot.send_message(ev.sender_id,text, buttons=buttons,parse_mode='HTML')

    except Exception as ex:
        text = f'❌'+str(ex)+'❌'
        await message.edit(text=text,parse_mode='HTML')
        pass
    pass
