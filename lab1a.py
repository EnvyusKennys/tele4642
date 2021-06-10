#this is lab1
# random variable for generating packets size - mean is 1250b
# server is 10GPS
# input is number lambda
#count in us

import sys
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
# print(str(sys.argv));
try:
    inputn = int(sys.argv[1])
    inputl = int(sys.argv[2])
except:
    print("Input must be: py lab1.py number_packets lambda")
    exit()


print(inputn, inputl)


class Packet:
    def _init_(self, packet_number, arrival_time, departure_time, size):
        self.packet_number = packet_number
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.size = size


class Source:
    def _init_(self):
        self.lambd = lambd

    def myfunc(self):
        self.packetwait = np.random.exponential(1/self.lambd, 1)  # delay in us
        # print(self.packetwait)
        self.packetsize = random.poisson(10000, 1)  # average size of 10000
        # print(self.packetsize)


class Queue:
    queue_array = []
    total = 0
    N = 0
    avg_N = 0
    P_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def insert(self, packet):
        # This function inserts a new packet to the queue
        # You need to update these variables upon the insertion:
        # N, the average number of packets in the system,
        # For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system

        self.queue_array.append(packet)  # stuff to append inside the array
        self.total = self.total + 1
        self.avg_N = self.avg_N + len(self.queue_array)
        self.N = len(self.queue_array)
        if self.N <= 10:
            self.P_array[self.N] = self.P_array[self.N] + 1


class Server:
    # 10 000 000 000 bits/s = 10000 bits/us =1 000 000 packets/s = 1 packet us
    service_rate = 10000
    timeinsystem = 0
    avg = 0
    time = 0
    packet_number = 0

    def service(self, queue):
        # This function takes the next packet in the queue and handles it
        # Service time should be calculated based on the size of the packet
        # You also need to calculate the packet's departure time
        # In addition to service time, what else do you need to calculate the correct departure time of the current packet?
        # self.time = 0 # sys time scale
        # self.avg  = 0 # store averge time spent by a packet in the sys
        #q = Queue.queue_array
        # print("boo")
        # for obj in queue.queue_array:
        #    print(obj.size)
        pkt = queue.queue_array.pop(0)
        pkt.departure_time = self.time + \
            (pkt.size / self.service_rate)  # arrival time + service time
        # print(pkt.departure_time)
        # pkt size in bits, 10 000 bits/us
        self.timeinsystem = pkt.departure_time - pkt.arrival_time
        #print(pkt.departure_time - self.time)
        self.time = pkt.departure_time
        # print(self.time)
        self.packet_number = pkt.packet_number
        self.avg = (self.avg + pkt.size / self.service_rate)
        #server_time = server_time+ self.time

    def summary(self, queue):
        print("Summary:")
        print("-------------------------------------------")
        print("average number of packets in the system N : %d" %
              (queue.avg_N/queue.total))
        print("average time spent by a packet in the system T : %.6f us" % (self.avg))
        print("probability P(n) that an arriving packet finds n packets already in the system: ")
        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [queue.P_array[0]/queue.total, queue.P_array[1]/queue.total, queue.P_array[2]/queue.total, queue.P_array[3]
             / queue.total, queue.P_array[4]/queue.total, queue.P_array[5]/queue.total, queue.P_array[6]/queue.total, queue.P_array[7]/queue.total, queue.P_array[8]/queue.total,
             queue.P_array[9]/queue.total, queue.P_array[10]/queue.total]
        plt.plot(x, y)
        plt.xlabel('n')
        plt.ylabel('P(n)')
        plt.title(
            'Probability P(n) that an arriving packet finds n packets already in the system')
        plt.show()


j = 0
global_time = 0
server_time = 0
q1 = Queue()
while j < inputn:
    s1 = Source()
    p1 = Packet()

    ser = Server()
    s1.lambd = inputl
    s1.myfunc()
    p1.packet_number = j
    p1.size = s1.packetsize
    # print(s1.packetsize)
    p1.arrival_time = global_time
    print("time = %f: pkt %d arrives and finds %d packets in the queue" %
          (global_time, p1.packet_number, len(q1.queue_array)))
    q1.insert(p1)
    # print(global_time,server_time)
    if global_time >= server_time:
        ser.time = global_time
        # print(ser.time)
        ser.service(q1)
        server_time = ser.time
        print("time = %f: pkt %d departs after spending %f us in the server" %
              (server_time, ser.packet_number, ser.timeinsystem))
        #global_time = global_time + ser.time
    # print(s1.packetwait)
    global_time = global_time + s1.packetwait
    j = j+1


while len(q1.queue_array) > 0:
    ser = Server()
    ser.time = global_time
    ser.service(q1)
    # print(ser.time)
    global_time = ser.time
    print("time = %f: pkt %d departs after spending %f us in the server" %
          (global_time, ser.packet_number, ser.timeinsystem))
    # print(ser.time)
ser.summary(q1)
