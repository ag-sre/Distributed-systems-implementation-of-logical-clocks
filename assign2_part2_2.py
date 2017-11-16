import socket
import threading
import struct
import time
from collections import defaultdict
import multiprocessing
import random
n=3

class Clock:
    def __init__(self,val):
       self.clock=val

    def update_clock(self):
        self.clock=self.clock+1

    def get_clock(self):
        return self.clock


class BufferQueue:
    def __init__(self):
        self.hold_mesg=defaultdict()
        self.ack_buffer=defaultdict()

    def return_buffer(self):
        return self.hold_mesg

    def task_done(self,mesg):
        self.hold_mesg.pop(mesg)

    def ack_count(self,pid):
        if pid in self.ack_buffer.keys():
            return self.ack_buffer[pid]
        else:
            return 0


def sender(MCAST_GRP,mesg,port,clock):
    #clock.update_clock()
    current = multiprocessing.current_process()
    send_clock=mesg.split(":")
    send_clock=int(send_clock[2])
    print("sending from process:"+str(current.pid),"at clock",send_clock)
    clock.update_clock()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(mesg.encode('utf-8'), (MCAST_GRP, port))

def receiver(MCAST_GRP,port,process_clock,hold_queue):
    current = multiprocessing.current_process()
    current_pid = current.pid
    current_pid = int(current_pid)
    print("process",str(current_pid),"started")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket   .SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data = sock.recv(10240)
        process_clock.update_clock()
        data=data.decode('utf-8')
        mesg=data
        hold_queue.hold_mesg[mesg]=current_pid


def sender_ack(process_clock,hold_queue):
    current=multiprocessing.current_process()
    current=int(current.pid)
    while True:
        if len(hold_queue.return_buffer())>=n:
            key_list=[]
            for key in hold_queue.return_buffer().keys():
                mesg=key.split(":")
                key_list.append((int(mesg[2]),int(mesg[1])))
            for key,val in sorted(key_list):
                mesg=str(val)+" ack "+str(current)
                MCAST_GRP="224.1.1.2"
                port=5355
                ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                ack_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                ack_sock.sendto(mesg.encode('utf-8'), (MCAST_GRP, port))
                process_clock.update_clock()
            break

def receiver_ack(hold_queue,clock):
    MCAST_GRP = "224.1.1.2"
    port = 5355
    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ack_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ack_sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    ack_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    current_pid=int(multiprocessing.current_process().pid)
    while True:
        ack=ack_sock.recv(1024)
        clock.update_clock()
        ack=ack.decode('utf-8')
        ack=ack.split("ack")
        if ack[0] in hold_queue.ack_buffer.keys():
            hold_queue.ack_buffer[ack[0]]+=1
        else:
            hold_queue.ack_buffer[ack[0]]=1
        if(hold_queue.ack_count(ack[0])>=n):
            mesg="message_from__process_id:"+ack[0]+" received by process: "+str(current_pid)
            hold_queue.ack_buffer[ack[0]]=0
            hold_queue.hold_mesg["message_from__process_id:"+ack[0]]=0
            print(mesg)

def process_start():
    multicast_port = 5355
    MCAST_GRP = '224.1.1.1'
    #r=random.randint(1,3)
    clock=Clock(1)
    hold_queue=BufferQueue()
    recv_thread = threading.Thread(target=receiver, args=(MCAST_GRP, multicast_port,clock,hold_queue))
    recv_thread.start()
    mesg = "messsage_from_"
    current = multiprocessing.current_process()
    process_id=current.pid
    mesg += "__process_id:" + str(process_id)+":"+str(1)
    sender_thread = threading.Thread(target=sender, args=(MCAST_GRP, mesg, multicast_port,clock))
    senderAck=threading.Thread(target=sender_ack,args=(clock,hold_queue))
    recvAck=threading.Thread(target=receiver_ack,args=(hold_queue,clock))
    time.sleep(2)
    sender_thread.start()
    time.sleep(2)
    recvAck.start()
    time.sleep(2)
    senderAck.start()


if __name__=="__main__":
    p1=multiprocessing.Process(target=process_start)
    p1.start()
    p2 = multiprocessing.Process(target=process_start)
    p2.start()
    p3 = multiprocessing.Process(target=process_start)
    p3.start()




