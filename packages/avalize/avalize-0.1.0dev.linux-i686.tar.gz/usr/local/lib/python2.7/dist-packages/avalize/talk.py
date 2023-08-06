import socket
import sys
import sqlite3
import os
import easygui as eg
from subprocess import Popen

datadir = os.path.expanduser(os.path.join('~', '.avalize'))
if not os.path.exists(datadir):
    os.makedirs(datadir)
    assert os.path.exists(datadir)

def receivedata():
    length = sock.recv(16)
    length = int(length)
    sock.sendall("go")
    buff=''
    while len(buff) < length:
        buff += sock.recv( length - len(buff) )
    return buff

def senddata(string):
    length = len(string)
    sock.sendall(str(length))
    data = sock.recv(16)
    if data == "go":
        sock.sendall(string)
        print "sent."
    else:
        print "abort."

req = sys.argv[1]

if req == "list":
    fil = sys.argv[2]
    abspath = os.path.abspath(fil)
    conn = sqlite3.connect(datadir+"/data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO filelist (filepath) VALUES ('" + abspath + "')")
    conn.commit()
    conn.close()
elif req == "unlist":
    fil = sys.argv[2]
    conn = sqlite3.connect(datadir+"/data.db")
    cursor = conn.cursor()
    if fil.isdigit() == True:
        query = "DELETE FROM filelist WHERE id='%s'" % fil
        cursor.execute(query)
        conn.commit()
    else:
        query = "DELETE FROM filelist WHERE filepath LIKE '%"+fil+"%'"
        cursor.execute(query)
        conn.commit()
    conn.close()
elif req == "mylist":
    conn = sqlite3.connect(datadir+"/data.db")
    cursor = conn.cursor()
    flist = "MY AVALIZED FILES:"
    for row in cursor.execute("SELECT * FROM filelist"):
        flist += "\n" + str(row[0]) + " - " + str(row[1])
    print flist
elif req == "server":
   execfile("listen.py")
elif req == "config":
    conn = sqlite3.connect(datadir+"/data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE filelist (
                  id INTEGER PRIMARY KEY,
                  filepath text
                  ) 
               """)
    conn.close()
elif req == "help":
    print "avalize lets systems share files they've made publically available."
    print "USAGE:"
    print "start your avalize server:	avalize server"
    print "make a file available:		avalize list [filepath]"
    print "un-avalize a file:		avalize unlist [filename, path, or list id]"
    print "see your public list:		avalize mylist"
    print "see another's public list:	avalize getlist [target ip]"
    print "get file from another's list:	avalize getfile [target ip] [filename, path, or listing id]"
    print "to manually send a file:	avalize sendfile [target ip] [filepath]"
elif req == "sendfile" or req == "getfile" or req == "getlist":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (sys.argv[2], 10006)
    sock.connect(server_address)
    try:
        if req == "getfile":
            rfil = sys.argv[3]
            sock.sendall("gf*" + rfil)
            ismatch = sock.recv(16)
            if ismatch == "y":
                sock.sendall("go")
                print "receiving file..."
                data = receivedata()
                lfil = eg.filesavebox(msg=None, title=None, default=rfil, filetypes=None)
                if lfil == "None":
                    print "aborting."
                else:
                    lf = open(lfil, 'wb')
                    lf.write(data)
                    lf.close()
                    print "received. saved to " + lfil
            elif ismatch == "n":
                print "the file you requested is not publically available. check for typos and try again."
        elif req == "getlist":
            sock.sendall("gl")
            data = receivedata()
            print data
        elif req == "sendfile":
            fil = sys.argv[3]
            print "requesting manual transmission... "
            sock.sendall("sf*" + fil)
            confirmation = sock.recv(16)
            if confirmation == "y":
                print "peer accepted transmission."
                print "sending file..."
                elephant = open(fil)
                content = file.read(elephant)
                senddata(content)
            else:
                print "peer rejected transmission, aborting."
    finally:
        sock.close()
else:
    print "not a valid command, home-biscuit. try running 'avalize help'."
