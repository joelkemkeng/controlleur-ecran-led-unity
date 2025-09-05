import socket
import ehub
import artnet
import excel

UDP_IP = "127.0.0.1"
UDP_PORT = 8765

# Création d'un objet de socket
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

screen_data = excel.get_screen_data('Ecran.xlsx')

# Réception continue de packets UDP suivi de leur traitement et retransmission via Artnet
while True:
    data, addr = sock.recvfrom(64*1024) # buffer size is 1024 bytes
    entities_list = ehub.get_entities_list(data)



    columns = []
    for data in range(0, len(screen_data[0])):
        columns.append([])
    #print(columns)

    for data in screen_data[0]:
        #print("loop " + str(data[4]))
        #print(data)
        #column[universe] = []
        for entity in entities_list:
            #print("OKAY")
            if entity[0] in range(data[1], data[2]):
                columns[data[4]].extend([entity[1], entity[2], entity[3]])
                #print("test")
                #print(columns[data[4]])
        artnet.send_artnet_packet(data[3], data[4], columns[data[4]])

    #for data in screen_data[0]:
    #    print(columns[data[4]])
    #    artnet.send_artnet_packet(data[3], data[4], columns[data[4]])
    #column0 = []

    #for entity in entities_list:
        #if (entity[0] in range(100, 269)):
            #column0.extend([entity[1], entity[2], entity[3]])

    #print(column0)

    #artnet.send_artnet_packet("192.168.1.45", 0, column0)

