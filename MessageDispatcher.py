class MessageDispatcher(object):
    def __init__(self):
        self.handlers = {}
        self.file_handle = None

    def reg(self,identify,handle):
        try:
            self.handlers[identify] = handle
        except:
            for i in identify:
                self.handlers[i] = handle

    def reg_file(self,handle):
        self.file_handle = handle

    def get(self,identify):
        try:
            return self.handlers[identify]
        except:
             for h in self.handlers:
                if h in identify:
                    return self.handlers[h]
        return None
    
    async def dispatch(self,ev,bot,jdb):
        msg_text = ''
        try:
            msg_text = ev.message.text
        except:
            try:
                msg_text = str(ev.data)
                msg_text = str(msg_text).replace("'","").replace('b','')
            except:
                msg_text = str(ev.query.query)
        cmd = ''
        try:
            cmd = msg_text.split(' ')[0]
        except:pass
        handle = self.get(cmd)
        if handle:
           await handle(ev,bot,jdb)
        try:
            if ev.message.file:
                if self.file_handle:
                    await self.file_handle(ev,bot,jdb)
        except:pass
        pass