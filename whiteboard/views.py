'''
In the following code the object's hsv value is taken and its being detected. 
Then a white board is formed with different buttons on the screen like clear button and different color buttons. 
Then a function by which it takes the boundary of the object and by that we can write on the whiteboard. 
Then by pressing "s" the whiteboard gets saved in form of image(.jpg).
'''

import numpy as np 
from cv2 import cv2
from collections import deque
import time
import urllib.request
import keyboard
from django.shortcuts import render, redirect
from django.http.response import StreamingHttpResponse, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import condition

def steerPoint():
    bpoints = [deque(maxlen=1024)]
    gpoints = [deque(maxlen=1024)]
    rpoints = [deque(maxlen=1024)]
    ypoints = [deque(maxlen=1024)]
    #assigning index values
    blue_index = 0
    green_index = 0
    red_index = 0
    yellow_index = 0
    kernel = np.ones((5,5),np.uint8)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    #starting the painting window setup
    paintWindow = np.zeros((471,636,3)) + 255
    paintWindow = cv2.circle(paintWindow, (75,45), 25, (0,0,0), 2)
    paintWindow = cv2.circle(paintWindow, (225,45), 20, colors[0], -1)
    paintWindow = cv2.circle(paintWindow, (280,45), 20, colors[1], -1)
    paintWindow = cv2.circle(paintWindow, (335,45), 20, colors[2], -1)
    paintWindow = cv2.circle(paintWindow, (390,45), 20, colors[3], -1)
    cv2.putText(paintWindow, "CLEAR", (55, 50), cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
   

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        #Flipping the frame just for convenience
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #HSV value for blue object
        u_hue = 153
        u_saturation = 255
        u_value = 255
        l_hue = 64
        l_saturation = 72
        l_value = 49
        
        Upper_hsv = np.array([u_hue,u_saturation,u_value])
        Lower_hsv = np.array([l_hue,l_saturation,l_value])

        #detect the object and remove background environment
        mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)
        cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        center = None
        # Ifthe contours(boundry detection of the object) are formed
        if len(cnts) > 0:
        # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            #checking if any button above the screen is clicked/cursor hovered to
            if center[1] <= 80:
                if 75 <= center[0] <= 125: # Clear Button
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]
                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0
                    paintWindow[78:,:,:] = 255
                elif 225 <= center[0] <= 265:
                        colorIndex = 0 # Blue
                elif 280 <= center[0] <= 320:
                        colorIndex = 1 # Green
                elif 335 <= center[0] <= 375:
                        colorIndex = 2 # Red
                elif 390 <= center[0] <= 430:
                        colorIndex = 3 # Yellow
            else :
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1
        points = [bpoints, gpoints, rpoints, ypoints]

        #draw on the whiteboard with the color selected
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2,cv2.LINE_AA)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2,cv2.LINE_AA)
        
        #convert frame into jpg format
        ret, jpeg = cv2.imencode('.jpg', paintWindow)

        #For saving whiteboard as image
        if keyboard.is_pressed('s'):
            file_name = "Trace_Image_" + time.strftime('%Y%m%d%H%M%S') + ".jpg"
            cv2.imwrite(file_name, paintWindow)

        #return frames in form of image 
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + 
                b'\r\n')
         
        

def homePage(request):
    return render(request, 'homePage.html')

def demoPage(request):
    return render(request, 'demoPage.html')

def homeSteer(request):
    return render(request, 'whiteboardWindow.html')
    
def demoSteer(request):
    return render(request, 'whiteboardWindow.html')
    
def whiteboard(request):
    return StreamingHttpResponse(steerPoint(),content_type='multipart/x-mixed-replace; boundary=frame')
