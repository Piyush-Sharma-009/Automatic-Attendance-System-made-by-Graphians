import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image


# Train Image
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    try:
        # Initialize LBPH Recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2,
            neighbors=8,
            grid_x=6, 
            grid_y=6,
            threshold=80.0
        )
        
        # Load face detector
        detector = cv2.CascadeClassifier(haarcasecade_path)
        if detector.empty():
            raise ValueError("Failed to load face detection model")
        
        faces, ids = [], []
        print("Collecting training images...")
        
        # Process each student's directory
        for student_dir in os.listdir(trainimage_path):
            student_path = os.path.join(trainimage_path, student_dir)
            
            if not os.path.isdir(student_path) or '_' not in student_dir:
                continue
                
            try:
                enrollment = student_dir.split('_')[0]
                student_id = int(enrollment)
            except (IndexError, ValueError):
                continue
                
            # Process images
            image_files = sorted([f for f in os.listdir(student_path) 
                               if f.lower().endswith(('.png', '.jpg', '.jpeg'))])[:20]
                               
            for image_file in image_files:
                image_path = os.path.join(student_path, image_file)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    continue
                    
                face_rects = detector.detectMultiScale(
                    image, 
                    scaleFactor=1.05,
                    minNeighbors=4,
                    minSize=(60, 60)
                )
                
                if len(face_rects) == 1:
                    x, y, w, h = face_rects[0]
                    face_img = image[y:y+h, x:x+w]
                    face_img = cv2.equalizeHist(face_img)
                    face_img = cv2.resize(face_img, (200, 200))
                    faces.append(face_img)
                    ids.append(student_id)
        
        # Validation
        if len(faces) < 10:
            raise ValueError(f"Only {len(faces)} valid faces found - need more training data")
        if len(set(ids)) < 2:
            raise ValueError("Need at least 2 different students for training")
        
        # Train and save
        print(f"Training with {len(set(ids))} students and {len(faces)} samples...")
        recognizer.train(faces, np.array(ids))
        os.makedirs(os.path.dirname(trainimagelabel_path), exist_ok=True)
        recognizer.save(trainimagelabel_path)
        
        res = f"Trained {len(set(ids))} students with {len(faces)} total samples"
        if message:
            message.configure(text=res)
        text_to_speech("Training completed successfully")
        
    except Exception as e:
        error_msg = f"Training Error: {str(e)}"
        print(error_msg)
        if message:
            message.configure(text=error_msg)
        text_to_speech("Training failed. Please check console for details.")


def getImagesAndLabels(path):
    """Alternative implementation that matches TrainImage's preprocessing"""
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = []
    ids = []
    
    for student_dir in os.listdir(path):
        student_path = os.path.join(path, student_dir)
        if not os.path.isdir(student_path) or '_' not in student_dir:
            continue
            
        try:
            student_id = int(student_dir.split('_')[0])
        except (IndexError, ValueError):
            continue
            
        for image_file in os.listdir(student_path)[:20]:  # Limit to 20 images
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            image_path = os.path.join(student_path, image_file)
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
                
            face_rects = detector.detectMultiScale(image, 1.05, 4, minSize=(60, 60))
            if len(face_rects) == 1:
                x, y, w, h = face_rects[0]
                face_img = cv2.resize(cv2.equalizeHist(image[y:y+h, x:x+w]), (200, 200))
                faces.append(face_img)
                ids.append(student_id)
    
    return faces, ids