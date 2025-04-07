from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import *
from django.conf import settings
import os
import cv2
from datetime import datetime, timedelta
import cv2
import numpy as np
import ffmpeg
import torch
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from deepface import DeepFace
from ultralytics import YOLO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import cv2
import numpy as np
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ultralytics import YOLO
from deepface import DeepFace
from django.conf import settings


def index(request):

    return render(request,"index.html")


def index_(request):

    return render(request,"index_.html")

def about(request):

    return render(request,"about.html")

def login(request):
    return render(request,"login.html")


def products(request):

    return render(request,"products.html")




# Load YOLOv8 face detection model
yolo_model = YOLO("myapp/static/model/yolov8n-face.pt")

def detect_faces(image):
    """Detect faces using YOLOv8 and return cropped face images."""
    results = yolo_model(image)
    faces = []

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = image[y1:y2, x1:x2]
            faces.append(face)

    return faces

def extract_face_embedding(face):
    """Extract 128D face embeddings using DeepFace (Facenet)."""
    try:
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        embedding = DeepFace.represent(face_rgb, model_name="Facenet", enforce_detection=False)
        return embedding[0]['embedding'] if embedding else None
    except Exception as e:
        print(f"Embedding extraction error: {e}")
        return None

def compare_faces(reference_embedding, test_embedding, threshold=0.5):
    """Compare two face embeddings using cosine similarity."""
    if reference_embedding is None or test_embedding is None:
        return False

    similarity = np.dot(reference_embedding, test_embedding) / (
        np.linalg.norm(reference_embedding) * np.linalg.norm(test_embedding)
    )
    print(f"Similarity Score: {similarity}")  # Debugging output
    return similarity > threshold


def get_video_start_time(video_path):
    """Extracts the actual start time of the video from metadata."""
    try:
        probe = ffmpeg.probe(video_path)
        start_time = probe['format']['tags'].get('creation_time', None)
        return start_time
    except Exception as e:
        print(f"Error extracting start time: {e}")
        return None

def process_video(video_path, reference_embedding):
    """Process every frame in the video, show bounding boxes, frame number, and check if the person is detected."""
    cap = cv2.VideoCapture(video_path)
    detected = False  # Flag to track detection status
    frame_count = 0  # Track the number of frames processed
    detected_frame = None  # Store the detected frame
    detection_timestamp = None  # Store the timestamp

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  # Stop if video ends

        frame_count += 1
        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)  # Get timestamp in milliseconds
        timestamp_formatted = f"{int(timestamp_ms // 60000)}:{int((timestamp_ms % 60000) // 1000):02d}"  # Format MM:SS
        print(f"Processing Frame {frame_count} | Video Time: {timestamp_formatted}")  # Debugging

        faces = detect_faces(frame)  # Detect faces in current frame
        print(f"Faces detected in frame {frame_count}: {len(faces)}")  

        for result in yolo_model(frame):
            boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                face = frame[y1:y2, x1:x2]
                embedding = extract_face_embedding(face)

                if embedding is not None:
                    similarity = np.dot(reference_embedding, embedding) / (
                        np.linalg.norm(reference_embedding) * np.linalg.norm(embedding)
                    )
                    print(f"Similarity Score in frame {frame_count}: {similarity}")  

                    if similarity > 0.5:
                        print(f"✅ Match Found! Person Detected at {timestamp_formatted}")
                        detected = True
                        detection_timestamp = timestamp_formatted
                        detected_frame = frame.copy()  # Store the detected frame
                        color = (0, 255, 0)  # Green for match
                        label = f"MATCH ({timestamp_formatted})"
                    else:
                        color = (0, 0, 255)  # Red for non-match
                        label = "NO MATCH"

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display the frame number and timestamp
        cv2.putText(frame, f"Time: {timestamp_formatted} | Frame: {frame_count}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Show the frame
        cv2.imshow("Face Detection", frame)

        # Save the detected frame if needed
        if detected and detected_frame is not None:
            cv2.imwrite("detected_frame.jpg", detected_frame)  # Save as an image
         

        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  

    cap.release()
    cv2.destroyAllWindows()  # Close OpenCV window
    print(f"Final Detection Status: {detected}") 

    if detected:
        print(f"Person detected at timestamp: {detection_timestamp}, Frame: {frame_count}")
    
    return detected, detection_timestamp, detected_frame


def detect(request):
    """Django view to process uploaded image and video for face detection and return an alert message."""
    if request.method == 'POST' and request.FILES.get('image') and request.FILES.get('video'):
        image_file = request.FILES['image']
        video_file = request.FILES['video']

        # Define media paths
        image_dir = os.path.join(settings.MEDIA_ROOT, 'images')
        video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')

        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(video_dir, exist_ok=True)

        # Save uploaded files
        image_path = os.path.join(image_dir, image_file.name)
        video_path = os.path.join(video_dir, video_file.name)

        default_storage.save(image_path, ContentFile(image_file.read()))
        default_storage.save(video_path, ContentFile(video_file.read()))

        # Read the image
        image = cv2.imread(image_path)
        
        if image is None:
            return HttpResponse("<script>alert('Failed to read the uploaded image.'); window.history.back();</script>")

        # Detect faces in image
        faces = detect_faces(image)
        if not faces:
            return HttpResponse("<script>alert('No face detected in the image.'); window.history.back();</script>")

        # Extract embedding from first detected face
        reference_embedding = extract_face_embedding(faces[0])
        if not reference_embedding:
            return HttpResponse("<script>alert('Could not extract face embedding from the image.'); window.history.back();</script>")

        # Process video to detect the person
        detected = process_video(video_path, reference_embedding)
        print(detected)

        # if detected:
        #     return HttpResponse(f"""
        #         <script>
        #             alert('Person detected in the video!');
        #             window.location.href = '/';  // Redirect to homepage
        #         </script>
        #     """)
        # else:
        #     return HttpResponse(f"""
        #         <script>
        #             alert('Person NOT found in the video.');
        #             window.location.href = '/';
        #         </script>
        #     """)

    return HttpResponse("<script>alert('Invalid request. Please upload an image and a video.'); window.history.back();</script>")

def logout(request):

    return render(request,"index.html")