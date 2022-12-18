import RPi.GPIO as GPIO
import serial
import time

# from sx126x import sx126x

# This Mac Address : e4:5f:01:da:aa:c8
# Opposite Mac Address : e4:5f:01:da:ab:78

# This LoRa's Address is 21
# Opposite LoRa's Address is 100

# To send an image
# This is a protocol of LoRa
class HSLR:
    
    M0 = 22
    M1 = 27
    # if the header is 0xC0, then the LoRa register settings dont lost when it poweroff, and 0xC2 will be lost. 
    # cfg_reg = [0xC0,0x00,0x09,0x00,0x00,0x00,0x62,0x00,0x17,0x00,0x00,0x00]
    cfg_reg = [0xC2,0x00,0x09,0x00,0x00,0x00,0x62,0x00,0x17,0x00,0x00,0x00]
    get_reg = bytes(12)
    rssi = False
    addr = 65535
    serial_n = ""
    send_to = 0
    addr_temp = 0
    freq = 868
    power = 22
    air_speed = 2400

    SX126X_UART_BAUDRATE_1200 = 0x00
    SX126X_UART_BAUDRATE_2400 = 0x20
    SX126X_UART_BAUDRATE_4800 = 0x40
    SX126X_UART_BAUDRATE_9600 = 0x60
    SX126X_UART_BAUDRATE_19200 = 0x80
    SX126X_UART_BAUDRATE_38400 = 0xA0
    SX126X_UART_BAUDRATE_57600 = 0xC0
    SX126X_UART_BAUDRATE_115200 = 0xE0

    SX126X_AIR_SPEED_300bps = 0x00
    SX126X_AIR_SPEED_1200bps = 0x01
    SX126X_AIR_SPEED_2400bps = 0x02
    SX126X_AIR_SPEED_4800bps = 0x03
    SX126X_AIR_SPEED_9600bps = 0x04
    SX126X_AIR_SPEED_19200bps = 0x05
    SX126X_AIR_SPEED_38400bps = 0x06
    SX126X_AIR_SPEED_62500bps = 0x07

    SX126X_PACKAGE_SIZE_240_BYTE = 0x00
    SX126X_PACKAGE_SIZE_128_BYTE = 0x40
    SX126X_PACKAGE_SIZE_64_BYTE = 0x80
    SX126X_PACKAGE_SIZE_32_BYTE = 0xC0

    SX126X_Power_22dBm = 0x00
    SX126X_Power_17dBm = 0x01
    SX126X_Power_13dBm = 0x02
    SX126X_Power_10dBm = 0x03
    
    
    
    def __init__(self, serial_num, freq, addr, power, rssi):
                
        self.HEADER_SIZE = 12
        self.PACKET_SIZE = 240
        self.PAYLOAD_SIZE = 228
        
        # size of Header's components
        self.DEST_EUI_SIZE = 6
        self.SEQUENCE_NUMBER_SIZE = 2
        self.FLAG_SIZE = 1
        self.PAYLOAD_SIZE_OF_SiZE = 1
        self.CHECKSUM_SIZE = 2
        
        # environment setting
        self.FREQUENCY = freq
        self.ADDRESS = addr
        self.POWER = power
        self.RSSI = rssi
        self.SEND_TO = addr
        self.SERIAL_NUMBER = serial_num
    
        # MAC Address
        self.SOURCE_MAC = b'\xe4_\x01\xda\xaa\xc8'  # e4:5f:01:da:aa:c8
        self.DEST_MAC = b'\xe4_\x01\xda\xabx'   # e4:5f:01:da:ab:78
        
        # FLAGS
        self.SYN = 1
        self.SYNACK = 2
        self.ACK = 3
        self.DATA = 4
        self.BVACK = 5
        self.FIN = 6
        
        self.FLAG = 0
        
        # To check BVACK packet's index
        self.BVACK_INDEX = bytearray(0)
        self.BVACK_LENGTH = 5
        self.BVACK_ELEMENT_SIZE = 2
        
        # To manage BVACK packet
        self.expectedResult = [1, 2, 3, 4, 5]
        self.top = self.expectedResult[-1]
        
        # HEADER INDEX
        self.DEST_EUI_INDEX = 0
        self.SEQUENCE_NUMBER_INDEX = 6
        self.FLAG_INDEX = 8
        self.PAYLOAD_SIZE_INDEX = 9
        self.CHECKSUM_INDEX = 10
        
        # About Image
        self.imageSize = 0
        self.imageWidth = 0
        self.imageHeight = 0
        self.IMAGE_SIZE_INDEX_END = 4
        self.IMAGE_WIDTH_INDEX_END = 6
        self.IMAGE_HEIGHT_INDEX_END = 8
        
        # To manage Sequence fluently
        self.sequenceNumber = 0
        self.maxSequenceNumber = 0
        
        # Initial the GPIO for M0 and M1 Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0,GPIO.OUT)
        GPIO.setup(self.M1,GPIO.OUT)
        GPIO.output(self.M0,GPIO.LOW)
        GPIO.output(self.M1,GPIO.HIGH)

        # The hardware UART of Pi3B+,Pi4B is /dev/ttyS0
        self.ser = serial.Serial(serial_num,9600)
        self.ser.flushInput()
        self.set(freq,addr,power,rssi)        
        
    def set(self,freq,addr,power,rssi,air_speed=2400,\
            net_id=0,buffer_size = 240,crypt=0,\
            relay=False,lbt=False,wor=False):
        self.SEND_TO = addr
        self.ADDRESS = addr
        
        # We should pull up the M1 pin when sets the module
        GPIO.output(self.M0,GPIO.LOW)
        GPIO.output(self.M1,GPIO.HIGH)
        time.sleep(0.1)
        low_addr = addr & 0xff
        high_addr = addr >> 8 & 0xff
        net_id_temp = net_id & 0xff
        if freq > 850:
            freq_temp = freq - 850
        elif freq >410:
            freq_temp = freq - 410
        
        air_speed_temp = self.air_speed_cal(air_speed)
        # if air_speed_temp != None:
        
        buffer_size_temp = self.buffer_size_cal(buffer_size)
        # if air_speed_temp != None:
        
        power_temp = self.power_cal(power)
        #if power_temp != None:

        if rssi:
            rssi_temp = 0x80
        else:
            rssi_temp = 0x00

        l_crypt = crypt & 0xff
        h_crypt = crypt >> 8 & 0xff

        self.cfg_reg[3] = high_addr
        self.cfg_reg[4] = low_addr
        self.cfg_reg[5] = net_id_temp
        self.cfg_reg[6] = self.SX126X_UART_BAUDRATE_9600 + air_speed_temp
        # 
        # it will enable to read noise rssi value when add 0x20 as follow
        # 
        self.cfg_reg[7] = buffer_size_temp + power_temp + 0x20
        self.cfg_reg[8] = freq_temp
        #
        # it will output a packet rssi value following received message
        # when enable seventh bit with 06H register(rssi_temp = 0x80)
        #
        self.cfg_reg[9] = 0x03 + rssi_temp
        self.cfg_reg[10] = h_crypt
        self.cfg_reg[11] = l_crypt
        self.ser.flushInput()

        for i in range(2):
            self.ser.write(bytes(self.cfg_reg))
            r_buff = 0
            time.sleep(0.2)
            
            # print(self.ser.inWaiting())
            if self.ser.inWaiting() > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.inWaiting())
                if r_buff[0] == 0xC1:
                    pass
                    # print("parameters setting is :",end='')
                    # for i in self.cfg_reg:
                        # print(hex(i),end=' ')
                        
                    # print('\r\n')
                    # print("parameters return is  :",end='')
                    # for i in r_buff:
                        # print(hex(i),end=' ')
                    # print('\r\n')
                else:
                    pass
                    #print("parameters setting fail :",r_buff)
                break
            else:
                print("setting fail,setting again")
                self.ser.flushInput()
                time.sleep(0.2)
                print('\x1b[1A',end='\r')
                if i == 1:
                    print("setting fail,Press Esc to Exit and run again")
                    # time.sleep(2)
                    # print('\x1b[1A',end='\r')
                pass

        GPIO.output(self.M0,GPIO.LOW)
        GPIO.output(self.M1,GPIO.LOW)
        time.sleep(0.1)

    def air_speed_cal(self,airSpeed):
        air_speed_c = {
            1200:self.SX126X_AIR_SPEED_1200bps,
            2400:self.SX126X_AIR_SPEED_2400bps,
            4800:self.SX126X_AIR_SPEED_4800bps,
            9600:self.SX126X_AIR_SPEED_9600bps,
            19200:self.SX126X_AIR_SPEED_19200bps,
            38400:self.SX126X_AIR_SPEED_38400bps,
            62500:self.SX126X_AIR_SPEED_62500bps
        }
        return air_speed_c.get(airSpeed,None)

    def power_cal(self,power):
        power_c = {
            22:self.SX126X_Power_22dBm,
            17:self.SX126X_Power_17dBm,
            13:self.SX126X_Power_13dBm,
            10:self.SX126X_Power_10dBm
        }
        return power_c.get(power,None)

    def buffer_size_cal(self,bufferSize):
        buffer_size_c = {
            240:self.SX126X_PACKAGE_SIZE_240_BYTE,
            128:self.SX126X_PACKAGE_SIZE_128_BYTE,
            64:self.SX126X_PACKAGE_SIZE_64_BYTE,
            32:self.SX126X_PACKAGE_SIZE_32_BYTE
        }
        return buffer_size_c.get(bufferSize,None)

    def get_settings(self):
        # the pin M1 of lora HAT must be high when enter setting mode and get parameters
        GPIO.output(M1,GPIO.HIGH)
        time.sleep(0.1)
        
        # send command to get setting parameters
        self.ser.write(bytes([0xC1,0x00,0x09]))
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            self.get_reg = self.ser.read(self.ser.inWaiting())
        
        # check the return characters from hat and print the setting parameters
        if self.get_reg[0] == 0xC1 and self.get_reg[2] == 0x09:
            fre_temp = self.get_reg[8]
            addr_temp = self.get_reg[3] + self.get_reg[4]
            air_speed_temp = self.get_reg[6] & 0x03
            power_temp = self.get_reg[7] & 0x03
            
            air_speed_dic = {
                0x00:"300bps",
                0x01:"1200bps",
                0x02:"2400bps",
                0x03:"4800bps",
                0x04:"9600bps",
                0x05:"19200bps",
                0x06:"38400bps",
                0x07:"62500bps"
            }
            power_dic ={
                0x00:"22dBm",
                0x01:"17dBm",
                0x02:"13dBm",
                0x03:"10dBm"
            }
            
            print("Frequence is {0}.125MHz.",fre_temp)
            print("Node address is {0}.",addr_temp)
            print("Air speed is "+ air_speed_dic(air_speed_temp))
            print("Power is " + power_dic(power_temp))
            GPIO.output(M1,GPIO.LOW)

    def get_channel_rssi(self):
        GPIO.output(self.M1,GPIO.LOW)
        GPIO.output(self.M0,GPIO.LOW)
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.write(bytes([0xC0,0xC1,0xC2,0xC3,0x00,0x02]))
        time.sleep(0.5)
        re_temp = bytes(5)
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            re_temp = self.ser.read(self.ser.inWaiting())
        if re_temp[0] == 0xC1 and re_temp[1] == 0x00 and re_temp[2] == 0x02:
            print("the current noise rssi value: -{0}dBm".format(256-re_temp[3]))
            # print("the last receive packet rssi value: -{0}dBm".format(256-re_temp[4]))
        else:
            # pass
            print("receive rssi value fail")
            # print("receive rssi value fail: ",re_temp)
    
    # send {sound: 1} or {start: 1} to pi1
    def transmitType(self, payload):
        
        # send b'{type: 1}'
        self.ser.write(payload.encode())
                
        time.sleep(0.5)

    # Function to receive first image from pi1
    def receiveImage(self):
        while True:
            # get Syn Packet
            self.receiveSynPacket()
            
            self.maxSequenceNumber = int((self.imageSize - 1) / self.PAYLOAD_SIZE) + 1
            print("----- max sequence number : " + str(self.maxSequenceNumber))

            # send SYN-ACK Packet
            self.transmitSYNACK()
            
            # get Data Packets and transmit Bvack Packet
            imageBytes = self.receiveDataPacket()
            print(imageBytes)
            print("image length : " + str(len(imageBytes)))
            
            # get Fin Packet and send Ack and Fin packet
            self.fourHandShake()
            
            return [imageBytes, self.imageWidth, self.imageHeight]
        
    # receive packet from pi1 (especially coordinates)
    def receivePacket(self):
        if self.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = self.ser.read(self.ser.inWaiting())
            packet = r_buff[:-1]
            
            return packet
        
    # receive SYN packet from pi1. SYN packet inform the starting point of communication
    def receiveSynPacket(self):
        while True:
            if self.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                packet = r_buff[:-1]
                
                # check that header is correct and get payload
                payload = self.parse(packet)
                
                print("Receive SYN packet")
                print(self.FLAG)
                
                # if received packet is SYN, get image size, width, height
                if self.FLAG == self.SYN:
                    self.imageSize = int.from_bytes(payload[:self.IMAGE_SIZE_INDEX_END], 'big')
                    self.imageWidth = int.from_bytes(payload[self.IMAGE_SIZE_INDEX_END:self.IMAGE_WIDTH_INDEX_END], 'big')
                    self.imageHeight = int.from_bytes(payload[self.IMAGE_WIDTH_INDEX_END:self.IMAGE_HEIGHT_INDEX_END], 'big')
                    
                    print("image size : " + str(self.imageSize))
                    print("width : " + str(self.imageWidth))
                    print("height : " + str(self.imageHeight))
                    
                    break

    # get DATA packet from pi1
    def receiveDataPacket(self):
        imageBytes = bytearray(self.imageSize)
        
        # check current time for sending BVACK packet
        startTime = time.time()
        
        while True:
            endTime = time.time()
            
            if self.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                packet = r_buff[:-1]
                
                # check the packet and get payload
                payload = self.parse(packet=packet)

                # take payload into imageBytes
                imageBytes[(self.sequenceNumber-1)*self.PAYLOAD_SIZE:self.sequenceNumber*self.PAYLOAD_SIZE] = payload
                
                # to check how many payload does receiver get
                print(str(self.sequenceNumber) + " / " + str(self.maxSequenceNumber))
                
                # if BVACK_INDEX is full, send BVACK Packet. 
                # or if DATA packet sending is finished, send BVACK packet.
                # or timeout(15s)
                if (len(self.BVACK_INDEX) >= self.BVACK_ELEMENT_SIZE*self.BVACK_LENGTH) \
                    or (self.maxSequenceNumber == self.sequenceNumber) \
                        or ((endTime - startTime) >= 15):
                    print("bvack sending...")
                    
                    self.BVACK_INDEX = bytearray(0)
                    
                    for i in range(0, len(self.expectedResult)):
                        if self.expectedResult[i] <= self.maxSequenceNumber:
                            self.BVACK_INDEX += self.expectedResult[i].to_bytes(self.BVACK_ELEMENT_SIZE, 'big')
                    
                    first = self.BVACK_INDEX[:self.BVACK_ELEMENT_SIZE]
                    second = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE:self.BVACK_ELEMENT_SIZE*2]
                    third = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*2:self.BVACK_ELEMENT_SIZE*3]
                    forth = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*3:self.BVACK_ELEMENT_SIZE*4]
                    fifth = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*4:self.BVACK_ELEMENT_SIZE*5]
                    
                    print("["+str(first)+", "+str(second)+", "+str(third)+", "+str(forth)+", "+str(fifth)+" ]")
                    
                    self.transmitBvack(self.BVACK_INDEX)
                    
                    # initialize variables for loop
                    self.BVACK_INDEX = bytearray()
                    startTime = time.time()
                
            # if time interval is over the 10, send BVACK packet.
            if (endTime - startTime) >= 10:
                print("bvack sending...(time)")
                
                self.BVACK_INDEX = bytearray(0)
                    
                for i in range(0, len(self.expectedResult)):
                    if self.expectedResult[i] <= self.maxSequenceNumber:
                        self.BVACK_INDEX += self.expectedResult[i].to_bytes(self.BVACK_ELEMENT_SIZE, 'big')
                
                first = self.BVACK_INDEX[:self.BVACK_ELEMENT_SIZE]
                second = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE:self.BVACK_ELEMENT_SIZE*2]
                third = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*2:self.BVACK_ELEMENT_SIZE*3]
                forth = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*3:self.BVACK_ELEMENT_SIZE*4]
                fifth = self.BVACK_INDEX[self.BVACK_ELEMENT_SIZE*4:self.BVACK_ELEMENT_SIZE*5]
                
                print("["+str(first)+", "+str(second)+", "+str(third)+", "+str(forth)+", "+str(fifth)+" ]")
                
                self.transmitBvack(self.BVACK_INDEX)
                
                # initialize variables for loop
                self.BVACK_INDEX = bytearray()
                startTime = time.time()
                
            # if getting DATA packet is finished, break the loop
            if self.maxSequenceNumber == self.sequenceNumber:
                print("break the getting Data packet loop")
                break
                    
        return imageBytes
                    
    # four-way handshake
    def fourHandShake(self):
        while True:
            if self.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                packet = r_buff[:-1]
                
                # check the packet and get payload
                payload = self.parse(packet=packet)
                                
                # if not get FIN FLAG, exit
                if self.FLAG != self.FIN:
                    print("can't get FIN Packet")
                    exit()
                
                # send Ack packet and Fin packet
                self.transmitAck()
                self.transmitFin()
                break
        
        # receive Ack packet
        while True:
            if self.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                packet = r_buff[:-1]
                
                # check the packet and get payload
                payload = self.parse(packet=packet)
                
                if self.FLAG != self.ACK:
                    print("can't get ACK Packet")
                    exit()
                
                break

        self.expectedResult = [1, 2, 3, 4, 5]

    # add header to payload    
    def addHeader(self, sequenceNum, flag, payload=bytearray(0)):
        if len(payload) > self.PAYLOAD_SIZE:
            print("payload size is over")
            exit()
        
        header = bytearray(self.HEADER_SIZE)
        
        # change int to byte
        sequenceNum = sequenceNum.to_bytes(self.SEQUENCE_NUMBER_SIZE, 'big')
        flag = flag.to_bytes(self.FLAG_SIZE, 'big')
        payloadSize = len(payload).to_bytes(self.PAYLOAD_SIZE_OF_SiZE, 'big')
        
        header[self.DEST_EUI_INDEX:self.SEQUENCE_NUMBER_INDEX] = self.DEST_MAC
        header[self.SEQUENCE_NUMBER_INDEX:self.FLAG_INDEX] = sequenceNum
        header[self.FLAG_INDEX:self.PAYLOAD_SIZE_INDEX] = flag
        header[self.PAYLOAD_SIZE_INDEX:self.CHECKSUM_INDEX] = payloadSize
        
        # get checksum value
        checkSum = self.calCheckSum(header[:self.CHECKSUM_INDEX], payload)
        
        # set checksum into header
        header[self.CHECKSUM_INDEX:self.HEADER_SIZE] = checkSum
        
        t = int.from_bytes(flag, 'big')
        flagName = "TEMP"
        if t == 1:
            flagName = "SYN"
        elif t == 2:
            flagName = "SYNACK"
        elif t == 3:
            flagName = "ACK"
        elif t == 4:
            flagName = "DATA"
        elif t == 5:
            flagName = "BVACK"
        elif t == 6:
            flagName = "FIN"
        
        return header + payload
    
    # calculate checksum to compare with received checksum and calculated checksum.
    def calCheckSum(self, header, payload):
        tempPacket = header + payload
        
        sum = 0
        for i in range(0, len(tempPacket), 2):
            int_val = int.from_bytes(payload[i:i+2], 'big')
            sum = bin(sum + int_val)[2:]
            if len(sum) > 16:
                sum = int(sum[1:], 2) + 1
            else:
                sum = int(sum, 2)
                    
        # one's complement
        checkSum = bin(0b1111111111111111 - sum)[2:]
        checkSum = int(checkSum, 2)
        checkSum = checkSum.to_bytes(2, 'big')
        
        return checkSum
        
    # check the checksum to compare with received checksum and calculated checksum.
    def check(self, packet):

        checkSum = packet[self.CHECKSUM_INDEX:self.HEADER_SIZE]

        sum = 0
        
        calculatedCheckSum = self.calCheckSum(packet[:self.CHECKSUM_INDEX], packet[self.HEADER_SIZE:])

        if calculatedCheckSum == bytes(checkSum):
            return True
        else:
            return False


    # check an integrity and remove header of the packet
    def parse(self, packet):
        
        # check CheckSum
        result = self.check(packet)
        if result == False:
            print("got checksum : " + str(packet[self.PAYLOAD_SIZE_INDEX:self.CHECKSUM_INDEX]))
            print("calculated checksum : " + str(self.calCheckSum(packet[:self.CHECKSUM_INDEX], packet[self.HEADER_SIZE:])))
            
            print("integrity is wrong")
            return []
        
        # check DEST EUI
        destEUI = packet[self.DEST_EUI_INDEX:self.SEQUENCE_NUMBER_INDEX]
        if destEUI != self.SOURCE_MAC:
            print("destEUI is incorrect")
            return []
        
        # check sequence number
        sequenceNumber = int.from_bytes(packet[self.SEQUENCE_NUMBER_INDEX:self.FLAG_INDEX], 'big')
        self.sequenceNumber = sequenceNumber

        if sequenceNumber in self.expectedResult:
            self.expectedResult.remove(sequenceNumber)
        
        # check payload size
        payloadSize = int.from_bytes(packet[self.PAYLOAD_SIZE_INDEX:self.CHECKSUM_INDEX], 'big')
        if len(packet[self.HEADER_SIZE:]) != payloadSize:
            print("length is incorrect")
            return []
        
        payload = packet[self.HEADER_SIZE:]
        
        # check flag and set flag to respond
        flag = int.from_bytes(packet[self.FLAG_INDEX:self.PAYLOAD_SIZE_INDEX], 'big')
        
        self.FLAG = flag
        
        # if flag is DATA, put sequence number into the BVACK_INDEX
        if flag == self.DATA:
            self.BVACK_INDEX += packet[self.SEQUENCE_NUMBER_INDEX:self.FLAG_INDEX]
        
        flagName = "TEMP"
        if flag == 1:
            flagName = "SYN"
        elif flag == 2:
            flagName = "SYNACK"
        elif flag == 3:
            flagName = "ACK"
        elif flag == 4:
            flagName = "DATA"
        elif flag == 5:
            flagName = "BVACK"
        elif flag == 6:
            flagName = "FIN"
        
        print("----- here is parse -----")
        print("|         dest eui         | sequence Num |  FLAG  | Paylaod size |")
        print("| "  + str(destEUI) +    " |      "+str(sequenceNumber)+"       |"+" {:<7}".format(flagName)+"|      "+str(len(payload))+"      |")
        print("Expected Result List : " +str(self.expectedResult))
        
        
        return payload

    # transmit SYN-ACK packet to pi1
    def transmitSYNACK(self):
        
        # add Header with SYNACK FLAG
        packet = self.addHeader(sequenceNum=0, flag=self.SYNACK)
        
        # send packet
        self.ser.write(packet)
        
        print("SYN-ACK packet sent")
        
        time.sleep(0.5)
        
    # for sending and resending DATA packet
    def transmitData(self, payload, sequenceNum):
        
        # add Header with DATA FLAG
        packet = self.addHeader(sequenceNum=sequenceNum, flag=self.DATA, payload=payload)
        
        # new packet send. and sequenceNumber start from 1
        if sequenceNum == self.sequenceNumber:
            self.sequenceNumber+=1
        
        #send packet
        self.ser.write(packet)
        
        time.sleep(2)

    # transmit ACK packet to pi1
    def transmitAck(self):
        
        # add Header with ACK FLAG
        packet = self.addHeader(sequenceNum=0, flag=self.ACK)
    
        # send packet
        self.ser.write(packet)
        
        print("Ack is sent")
        
        time.sleep(0.5)
    
    # transmit BVACK packet to pi1 for checking packet loss
    def transmitBvack(self, payload):
        
        # add Header with ACK FLAG
        packet = self.addHeader(sequenceNum=0, flag=self.BVACK, payload=payload)
        
        # send packet
        self.ser.write(packet)        
        
        # calculate the expected result again
        i = 1
        while len(self.expectedResult) < 5:
            self.expectedResult.append(self.top + i)
            i+=1
        
        self.top = self.expectedResult[-1]
        
        time.sleep(0.5)
    
    # transmit FIN packet to pi1
    def transmitFin(self):
        
        # add Header with ACK FLAG
        packet = self.addHeader(sequenceNum=0, flag=self.FIN)
        
        # send packet
        self.ser.write(packet)
        
        self.FLAG = self.FIN
        
        print("Fin is sent")
        
        time.sleep(0.5)
