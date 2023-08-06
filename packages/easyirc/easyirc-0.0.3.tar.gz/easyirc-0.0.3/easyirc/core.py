
#-*- coding: utf-8 -*-

from .client import EventClient
from .command import CommandManager, protocol

class BasicIRC(object):
    def __init__(self, options):
        self.client = EventClient(options['name'], options)
        self.cmdmanager = CommandManager(protocol.commands)

ircsocks = []
for connops in settings.CONNECTIONS:
    tag = connops['name']
    sock = ircsocket.IRCSocket(connops['host'], connops['port'], tag,  


while 1:
    readbuffer=readbuffer+s.recv(1024)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop( )


    for line in temp:
        line=string.rstrip(line)
        line=string.split(line)
        print line
        if line[0] == "PING":
            s.send("PONG %s\r\n" % line[1])
        if(line[1]=='PRIVMSG' and line[3] == ':.lookup'):
            if len(line) > 4:
                html = urllib.urlopen("http://dic.naver.com/search.nhn?query=%s" % (line[4:])).read()
                soup = bs4.BeautifulSoup(html)
                try:
                    s.send("PRIVMSG %s :%s\r\n" %(line[2], unicode(soup.find_all("dd")[1].get_text()).encode('utf8').strip()))

                except IndexError:
                    s.send("PRIVMSG %s :Page not found\r\n" % (line[2]))

            else:
                s.send("PRIVMSG %s :.lookup <word>\r\n" % (line[2]))









