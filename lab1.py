''' lab 1 Poisson Process Source model '''
import sys
import math
import numpy
import matplotlib.pyplot as plt
from numpy import random

try:
    inputn = int(sys.argv[1])
    inputl = int(sys.argv[2])
except:
    print("Input must be: py lab1.py number_packets lambda")
    exit()


class Packet:
    packet_number  = 0
    arrival_time   = 0
    departure_time = 0
    size           = 0

class Queue:
    queue_array = []
    N = 0
    time = 0
    def insert(self,Packet):
        #This function inserts a new packet to the queue
        #You need to update these variables upon the insertion:
        #N, the average number of packets in the system,
        #For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system      
            total = 0
            q = Queue.queue_array
            q.append(Packet)  #stuff to append inside the array
            Queue.time = Queue.time + Packet.arrival_time
            print(Queue.time)
            print("pkt %d arrives and find %d packets in the queue" %(Packet.size,len(q)))
            for i in range(len(q)):
                total = total + i
            # find the total packet size in the system
            Queue.N = total / len(q)
            

class Server:
	service_rate = 10*(10**9) #The server can prcocess 10Gbps
	time = 0.0 # sys time scale
	avg  = 0.0 # store averge time spent by a packet in the sys
	def service(self):
		#This function takes the next packet in the queue and handles it
		#Service time should be calculated based on the size of the packet
		#You also need to calculate the packet's departure time
		#In addition to service time, what else do you need to calculate the correct departure time of the current packet? 
            
            q = Queue.queue_array              
            if Queue.time  > (Server.time + q[0].arrival_time + q[0].size / Server.service_rate):
                # when the next arrival time is after the departure of the first packet               
                pkt = q.pop(0)
                pkt.arrival_time = pkt.arrival_time + Server.time
                pkt.departure_time = Server.time + pkt.arrival_time + pkt.size / Server.service_rate  # arrival time + service time
                # while (pkt.departure_time > Queue.time):
                #     if(pkt.departure_time < Queue.time):
                #         break
                Server.time = pkt.departure_time
                tsys = (pkt.size / Server.service_rate) * 1000000
                Server.avg = (Server.avg + tsys) / pkt.packet_number
                print("pkt %d departs having spent %.2f us in the system" %(pkt.size,tsys))
            else:           
                pass


	def summary(self):
		print("Summary:")
		print("-------------------------------------------")
		print("average number of packets in the system N : %d" %(Queue.N))
		print("average time spent by a packet in the system T : %.6f us" %(Server.avg))
		print("probability P(n) that an arriving packet finds n packets already in the system: ")
		#Here you need to plot P(n) for n from 0 to 10
		#X axis would be 0 to 10
		#Y axis would be P(n)
        x = [0,1,2,3,4,5,6,7,8,9,10]
        y = [0,0.2,0.4,0.6,0.8,1]
        plt.plot(x,y)
        plt.xlabel('n')
        plt.ylabel('P(n)')
        plt.title('Probability P(n) that an arriving packet finds n packets already in the system')
        plt.show()

        
class Source:
	# lambd  = 1000000 #Poisson process mean
	# packet_count = 10 #number of packets to generate

	def _init_(self,lambd,count):
		self.lambd = lambd
		self.count = count      
	def generate(self):
        #This function generates a packet
		#Packet size should be a random number based on exponential distribution
		#Inter-arrival time of the generated packet should be a random number based on Poisson process
		#Note from the lecture's slides: Inter-arrival time (i.e. time between successive arrivals) is an
		#exponential r.v. with parameter lambda. This basically means that you can generate Poisson process random numbers with exponential distribution
		#In addition to inter-arrival time, what else do you need to calculate the correct arrival time of the generated packet?
            # q = Queue() # new queue defined here
            # i = 0
            self.x = Packet()
            self.x.packet_number = self.count
            self.x.arrival_time = random.exponential(1/self.lambd,1) # inter arrival time
            self.x.departure_time = 0 
            self.x.size = random.poisson(10000, 1)
            # q.insert(x)


    # def __init__(self, lambd, packetnum):
    #     self.lambd = lambd
    #     self.packetnum = packetnum

    # def myfunc(self):
    #     self.packetwait =  numpy.random.exponential(1/self.lambd,1)
    #     self.packetsize = random.poisson(10000, 1)
    #     print(self.packetwait)

        
s = Source()
q = Queue()
sv = Server()

s.lambd = inputl
s.count = 1
s.generate()
q.insert(s.x)
for j in range(inputn):
    s.lambd = inputl
    s.count = j + 2
    s.generate()
    q.insert(s.x)
    sv.service()
sv.summary()