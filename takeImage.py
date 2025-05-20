import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time



# take Image of user
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen, text_to_speech):
    # Input validation
    if not l1 and not l2:
        t = 'Please Enter your Enrollment Number and Name.'
        text_to_speech(t)
        return
    elif not l1:
        t = 'Please Enter your Enrollment Number.'
        text_to_speech(t)
        return
    elif not l2:
        t = 'Please Enter your Name.'
        text_to_speech(t)
        return

    try:
        # Initialize camera with faster setup
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW for faster initialization on Windows
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduced resolution for faster processing
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not cam.isOpened():
            raise RuntimeError("Camera not opened")
            
        detector = cv2.CascadeClassifier(haarcasecade_path)
        Enrollment = l1
        Name = l2
        sampleNum = 0
        directory = f"{Enrollment}_{Name}"
        path = os.path.join(trainimage_path, directory)
        
        # Create directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)
        
        # Capture loop
        while sampleNum < 20:  # Reduced from 50 to 20
            ret, img = cam.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum += 1
                cv2.imwrite(
                    os.path.join(path, f"{Name}_{Enrollment}_{sampleNum}.jpg"),
                    gray[y:y+h, x:x+w]
                )
                cv2.imshow("Frame", img)
                
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
                
        cam.release()
        cv2.destroyAllWindows()
        
        # Save student details
        with open("StudentDetails/studentdetails.csv", "a+", newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow([Enrollment, Name])
        
        res = f"Images Saved for ER No: {Enrollment} Name: {Name}"
        message.configure(text=res)
        text_to_speech(res)
        
    except FileExistsError:
        F = "Student Data already exists"
        text_to_speech(F)
    except Exception as e:
        text_to_speech(f"An error occurred: {str(e)}")