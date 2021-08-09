import cv2
import picamera
import numpy as np 
import io
import pymongo
import serial
import time
import os
import math
from datetime import datetime
from pymongo import MongoClient

def main():
    try:

        client = MongoClient("113.198.137.140",27017)
        db = client.exercise

        ser = serial.Serial('/dev/ttyACM0', 9600)
        
        bf_x = 359.0
        bf_y = 204.0
        tag = 0.0

        #Load YOLO
        net = cv2.dnn.readNet("yolov3-tiny-pi-2_best.weights","yolov3-tiny-pi.cfg")
        classes = []
        with open("obj-pi.names","r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        outputlayers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


        with picamera.PiCamera() as camera:
            camera.start_preview(fullscreen=False, window=(100,20,640,480))
            while True:
                camera.capture('123.jpg')

                src = cv2.imread('123.jpg')
                img = cv2.resize(src, None,fx=1,fy=1)
                height,width,channels = img.shape

                #detecting objects
                blob = cv2.dnn.blobFromImage(img,0.00392,(416,416),(0,0,0),True,crop=False)


                # for b in blob:
                #     for n,img_blob in enumerate(b):
                #         cv2.imshow(str(n),img_blob)
            
                net.setInput(blob)
                outs = net.forward(outputlayers)
                #print(outs[1])

        
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.5:
                            #onject detected
                            center_x= int(detection[0]*width)
                            center_y= int(detection[1]*height)
        
                dis = math.sqrt(math.pow((center_x-bf_x),2) + math.pow((center_y-bf_y),2))
                bf_x = center_x
                bf_y = center_y
                print(center_x)
                print(center_y)
                sound_s = ser.readline()
                sound = float(sound_s)
                vib_s = ser.readline()
                vib = float(vib_s)
                gas_s = ser.readline()
                gas = float(gas_s)
                gas_test = float(3.0)
                ambientTemp_s = ser.readline()
                ambientTemp = float(ambientTemp_s)
                objectTemp_s = ser.readline()
                objectTemp = float(objectTemp_s)
                if sound > 5.0 or vib > 5.0 or gas > 5.0:
                    print("svg error")
                    camera.stop_preview()
                    os.system("python ~/test.py")
                now = datetime.now()
                nowtime = now.strftime('%Y-%m-%d %H:%M:%S')
                data = {
                        "sound" : sound,    
                        "vib" : vib,
                        "gas" : gas_test,
                        "ambientTemp" : ambientTemp,
                        "objectTemp" : objectTemp,
                        "dis" : dis,
                        "tag" : tag,
                        "date" : nowtime
                    }
                print(data)
                db.exercise_collection.insert(data)
                time.sleep(6)
            camera.stop_preview()
    except Exception as e:
        print(e)
        os.system("python ~/test.py")
        
if __name__ == "__main__":
    main()
