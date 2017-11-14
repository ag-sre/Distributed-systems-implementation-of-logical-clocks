import random
import socket
import time
from multiprocessing import Process
import sys

def masterfunc(port,cnt,msg_clock,tot):
    try:
        host='127.0.0.1'
        s = socket.socket()
        s.bind((host, port))
        s.listen(5)
        while True:
            conn, address = s.accept()
            print "MASTER IS NOW CONNECTED TO CLIENT "+str(cnt-1)
            initialmsg = msg_clock.split(",")
            msg_id = int(initialmsg[0])
            msg_value = float(initialmsg[1])
            t_diff1=0
            conn.send(msg_clock)
            data = conn.recv(1024)
            print "MASTER RECEIVED CLIENT "+str(cnt-1)+" LOCAL CLOCK: "+str(data)
            print "********************************************************************"
            clmsg = data.split(",")
            check=0
            if (int(clmsg[0])==2):
                msg_id = int(clmsg[0])
                msg_value2 = float(clmsg[1])
                t_diff1=msg_value-msg_value2
                # print t_diff1
                print "CLIENT 1 TIME DIFFERENCE "+str(t_diff1)
                clock_adj = msg_value + (float(tot) / 3)
                new_cl = msg_value2 - clock_adj
                print "********************************************************************"
            elif (int(clmsg[0]) == 3):
                msg_id = int(clmsg[0])
                msg_value3 = float(clmsg[1])
                t_diff2 = msg_value-msg_value3
                print "CLIENT 2 TIME DIFFERENCE "+str(t_diff2)
                avg_part=tot/3
                print "********************************************************************"
                if(cnt==3):
                    avg_int = int(avg_part)
                    avg_fract = avg_part - avg_int
                    # print avg_int
                    # print avg_fract
                    if(float(avg_fract)>0.59):
                        avg_int+=1
                        avg_fract=avg_fract-0.59
                        avg_part=float(avg_int)+float(avg_fract)
                    print "BERKLEY'S AVERAGE CALCULATED AT MASTER: "+str(float("{0:.2f}".format(avg_part)))
                    cnt=1
                    clock_adjust=msg_value+(float(avg_part))
                    adj_int = int(clock_adjust)
                    adj_fract = clock_adjust - adj_int
                    if (float(adj_fract) > 0.59):
                        adj_int += 1
                        avg_fract = adj_fract - 0.59
                        clock_adjust = float(adj_int) + float(avg_fract)
                    cl_clock=float("{0:.2f}".format(clock_adjust))
                    new_cl=msg_value3-clock_adjust
                    print "MODIFIED MASTER'S LOGICAL CLOCK : " +str(float("{0:.2f}".format(clock_adjust)))
                    client_clock(cnt,cl_clock)
                    conn.send(str(clock_adjust))
                    clock_adjst=conn.recv(1024)
                    client_clock(cnt+1, cl_clock)
                    if(cl_clock==clock_adjust):
                        print "ALL THE THREE CLOCKS ARE NOW SYNCHRONIZED"
                    else:
                        print "CLOCKS NOT SYNCHRONIZED"
            else:
                print "Invalid response"
        conn.close()
    except (KeyboardInterrupt, SystemExit):
        print("Closing app.. Bye Bye")
        sys.exit(0)
def client_clock(cnt,val):
    if (int(cnt)<3):
        print "MODIFIED CLIENT "+str(cnt)+" CLOCK: "+str(val)

def client(port,c,clientclock,tot):
    try:
        host='127.0.0.1'
        s = socket.socket()
        syn_clock=0
        print "********************************************************************"
        print "CLIENT "+str(c-1)+" CONNECTING TO MASTER"
        s.connect((host, port))
        clientclock=str(clientclock)
        print "CLIENT "+str(c-1)+" LOGICAL CLOCK :" +str(clientclock)
        msg_clock = str(c)+',' + str(clientclock)
        data = s.recv(1024)
        print "CLIENT "+str(c-1)+" MESSAGE RECEIVED FROM MASTER "+ str(data)
        s.send(msg_clock)
        # print ""+data
        if(c==3):
            syn_clock = s.recv(1024)
            clock_adust=(syn_clock)+clientclock
            s.send(clock_adust)
            client_clock(c,clock_adust)
        s.close()
    except (KeyboardInterrupt, SystemExit):
        print("Closing app.. Bye Bye")
        sys.exit(0)

if __name__ == "__main__":
    client_ports=[7000,9000,8000]
    count =2
    logical_clock = float(random.randint(2, 20))
    cllogical_clock = float("{0:.2f}".format(random.choice([3,6,9,12,15,18,21])))
    daemon=8000
    print "               DEMONSTRATION OF BERKELEY ALGORITHM                 "
    print "********************************************************************"
    print "MASTER CONNECTED TO PORT :" + str(daemon)
    print "MASTER'S LOGICAL CLOCK : " + str(cllogical_clock)
    print "********************************************************************"
    msg_clock = '1,' + str(cllogical_clock)
    cnt=1
    total = 0
    print "********************************************************************"
    print "CLIENT PORTS TO BE CONNECTED :"
    for client_port in client_ports:
        if(client_port!=daemon):
           print "CLIENT "+str(cnt)+": " +str(client_port)
           cnt+=1
    print "********************************************************************"
    for client_port in client_ports:
        if(client_port!=daemon):
            logical_clock = float("{0:.2f}".format(random.choice([3, 6, 9, 12, 15, 18, 21])))
            total = total+ (logical_clock-cllogical_clock)
            Process(target=masterfunc, args=(client_port,count,msg_clock,total)).start()
            Process(target=client, args=(client_port,count,logical_clock,total)).start()
            time.sleep(3)
            count+=1
