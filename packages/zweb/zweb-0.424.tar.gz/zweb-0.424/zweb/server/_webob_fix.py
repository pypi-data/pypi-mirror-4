import webob.request

def readinto(self, buff):
    if not self.remaining:
        return 0
    sz0 = min(len(buff), self.remaining)
    data = self.file.read(sz0)
    sz = len(data)
    self.remaining -= sz
    #if not data:
    if sz < sz0 and self.remaining:
        pass
        #raise DisconnectionError(
        #    "The client disconnected while sending the POST/PUT body "
        #    + "(%d more bytes were expected)" % self.remaining
        #)
    buff[:sz] = data
    return sz

webob.request.LimitedLengthFile.readinto = readinto
