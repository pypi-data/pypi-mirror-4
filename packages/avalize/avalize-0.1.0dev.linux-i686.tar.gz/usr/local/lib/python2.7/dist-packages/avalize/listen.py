import socket
import sys
import os
import sqlite3
import easygui as eg

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def receivedata():
    length = connection.recv(16)
    length = int(length)
    connection.sendall("go")
    buff=''
    while len(buff) < length:
        buff += connection.recv( length - len(buff) )
    return buff

def senddata(string):	
    # send size of transmission
    length = len(string)
    connection.sendall(str(length))
    # wait for their go
    data = connection.recv(16)
    if data == "go":
        connection.sendall(string)
    else:
        print "aborting."

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (get_lan_ip(), 10006)
print >>sys.stderr, 'starting up on %s... (ctrl+c to quit)' % server_address[0]
sock.bind(server_address)
sock.listen(10)

while True:
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try: 
        data = connection.recv(250)
        if data == "gl":
            print server_address[0], "wants your avalized list, sending..."
            conn = sqlite3.connect(datadir+"/data.db")
            cursor = conn.cursor()
            flist = get_lan_ip() + "'S AVALIZED FILES:"
            for row in cursor.execute("SELECT * FROM filelist"):
                flist += "\n" + str(row[0]) + " - " + str(row[1])
            senddata(flist)
            print "sent."
        elif data.startswith("gf*"):
            parts = data.split("*", 1)
            fil = parts[1]
            conn = sqlite3.connect(datadir+"/data.db")
            cursor = conn.cursor()
            if fil.isdigit() == True:
                query = "SELECT * FROM filelist WHERE id='%s' LIMIT 1" % fil
            else:
                query = "SELECT * FROM filelist WHERE filepath LIKE '%"+fil+"%' LIMIT 1"
            for row in cursor.execute(query):
                if row[0] == "":
                    print server_address[0], "wants", fil, "but it is not avalized, aborting."
                    connection.sendall("n")
                else:
                    print server_address[0], "wants", row[1] + ", sending..."
                    connection.sendall("y")
                    go = connection.recv(16)
                    if go == "go":
                        elephant = open(row[1])
                        content = file.read(elephant)
                        senddata(content)
                        print "sent."
        elif data.startswith("sf*"):
            parts = data.split("*", 1)
            path, fil = os.path.split(parts[1])
            if eg.ynbox(server_address[0] + " wants to send " + fil + " to you.", "transmission request"):
                lfil = eg.filesavebox(msg=None, title=None, default=fil, filetypes=None)
                if lfil == "None":
                    print "aborting."
                else:
                    print "beginning transmission..."
                    connection.sendall("y")
                    data = receivedata()
                    lf = open(lfil, 'wb')
                    lf.write(data)
                    lf.close()
                    print "transmission completed,", fil, "received."
            else: 
                connection.sendall("n")
                print "aborting."
        else:
            break
            
    finally:
        connection.close()
