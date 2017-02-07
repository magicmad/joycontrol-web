#!/usr/bin/python

import RPi.GPIO as GPIO
from i2clibraries import i2c_hmc5883l
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os.path
import datetime
import math


#Tonado server port
PORT = 90

PinMotor1Pwm = 18
PinMotor1Fw = 4
PinMotor1Back = 17
PinMotor2Pwm = 23
PinMotor2Fw = 27
PinMotor2Back = 22

# GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(PinMotor1Pwm, GPIO.OUT)
GPIO.setup(PinMotor1Fw, GPIO.OUT)
GPIO.setup(PinMotor1Back, GPIO.OUT)
GPIO.setup(PinMotor2Pwm, GPIO.OUT)
GPIO.setup(PinMotor2Fw, GPIO.OUT)
GPIO.setup(PinMotor2Back, GPIO.OUT)

pwm1 = GPIO.PWM(PinMotor1Pwm, 50)
pwm1.start(0)

pwm2 = GPIO.PWM(PinMotor2Pwm, 50)
pwm2.start(0)


#HMC compass
#choosing which i2c port to use, RPi2 model B uses port 1
hmc5883l = i2c_hmc5883l.i2c_hmc5883l(1) 
hmc5883l.setContinuousMode()
#magnetic declination for roethlein (degrees, minute)
hmc5883l.setDeclination(2, 41)
# milisec
compassInterval = 250


def driveMotorL(speed):
    #print("speed L: " + str(speed))

    if abs(speed) < 10:
        speed = 0

    if speed == 0:
        GPIO.output(PinMotor1Fw, GPIO.LOW)
        GPIO.output(PinMotor1Back, GPIO.LOW)
    if speed > 0:
        GPIO.output(PinMotor1Fw, GPIO.HIGH)
        GPIO.output(PinMotor1Back, GPIO.LOW)
    if speed < 0:
        GPIO.output(PinMotor1Fw, GPIO.LOW)
        GPIO.output(PinMotor1Back, GPIO.HIGH)
        speed *= -1

    pwm1.ChangeDutyCycle(speed)


def driveMotorR(speed):
    #print("speed R: " + str(speed))

    if abs(speed) < 10:
        speed = 0

    if speed == 0:
        GPIO.output(PinMotor2Fw, GPIO.LOW)
        GPIO.output(PinMotor2Back, GPIO.LOW)
    if speed > 0:
        GPIO.output(PinMotor2Fw, GPIO.LOW)
        GPIO.output(PinMotor2Back, GPIO.HIGH)
    if speed < 0:
        GPIO.output(PinMotor2Fw, GPIO.HIGH)
        GPIO.output(PinMotor2Back, GPIO.LOW)
        speed *= -1

    pwm2.ChangeDutyCycle(speed)


def getHeading():
    (degrees, minutes) = hmc5883l.getHeading()
    return degrees + minutes / 60


#Tornado Folder Paths
settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)


# main http connection - show index.html
class MainHandler(tornado.web.RequestHandler):
  def get(self):
     print("[HTTP](MainHandler) User Connected.")
     self.render("index.html")


# websocket connection - 
class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print('user is connected.\n')
    # enable fast transfer
    self.set_nodelay(True)
    # read and send compass value
    self.sendHeading()

  def on_message(self, message):
    print('received message: %s\n' %message)
    #self.write_message(message + ' OK')
    parts = message.split(";")
    if len(parts) == 2:
        driveMotorR(float(parts[0]))
        driveMotorL(float(parts[1]))

  def on_close(self):
    print('connection closed\n')

  def sendHeading(self):
    self.write_message("C" + str(getHeading()))
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=compassInterval), self.sendHeading)


application = tornado.web.Application([
  (r'/', MainHandler),
  (r'/ws', WSHandler),
  ], **settings)


if __name__ == "__main__":
    #try:
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(PORT)
        print("Tornado Server starting..")
        main_loop = tornado.ioloop.IOLoop.instance().start()
    #except:
        #print "Exception triggered - Tornado Server stopped."
        #GPIO.cleanup()

#End of Program
