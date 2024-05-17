import network
import socket
from time import sleep
from picozero import pico_led
from machine import Pin, PWM

ssid = 'networkName'
password = 'networkPassword'

greenLED = Pin(20, Pin.OUT)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        greenLED.toggle()
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    greenLED.on()
    return ip





def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    return connection





def webpage(state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./forward">
            <input type="submit" value="Forward" style="height:350px; width:350px"/>
            </form>
            <form action="./stop">
            <input type="submit" value="Stop" style="height:350px; width:350px" />
            </form>
            <form action="./reverse">
            <input type="submit" value="Reverse" style="height:350px; width:350px" />
            </form>
            <p>RC Car is in {state} state</p>
            <p>
            </body>
            </html>
            """
    return str(html)



#RC CAR FUNCTIONS/VARIABLES

led = machine.Pin("LED", machine.Pin.OUT)

#PWM
speed = PWM(Pin(0))
speed.freq(10000)
speed.duty_u16(1000)



#Front Lwheels
#left
in1 = Pin(11, Pin.OUT) #left white
in2 = Pin(10, Pin.OUT) #blue
#right
in3 = Pin(9, Pin.OUT) #purple
in4 = Pin(8, Pin.OUT) #white right


#Rear Wheels
#Left
in5 = Pin(15, Pin.OUT) #brown
in6 = Pin(14, Pin.OUT) #red

#Right
in7 = Pin(13, Pin.OUT) #yellow
in8 = Pin(12, Pin.OUT) #green


#Func to come to a stop
def stop():
    print('stop')
    in1.off()
    in2.off()
    in3.off()
    in4.off()
    in5.off()
    in6.off()
    in7.off()
    in8.off()
    led.off()

#Func to move forward
def forwards():
    print('forwards')
    in1.off()
    in2.on()
    in3.low()
    in4.high()
    in5.on()
    in6.off()
    in7.off()
    in8.on()
    led.on()

#Function to move backwards
def backwards():
    print('backwards')
    in1.on()
    in2.off()
    in3.on()
    in4.off()
    in5.off()
    in6.on()
    in7.on()
    in8.off()
    led.on()
    
def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/forward?':
            state = 'FORWARD'
            forwards()
        elif request =='/stop?':
            state = 'OFF'
            print("turning off")
            stop()
        elif request =='/reverse?':
            state = 'REVERSE'
            backwards()
        html = webpage(state)
        client.send(html)
        client.close()





try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
    greenLED.toggle()
except KeyboardInterrupt:
    machine.reset()