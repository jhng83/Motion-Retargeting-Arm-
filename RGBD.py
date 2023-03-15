# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import cv2
import mediapipe as mp
import pyrealsense2 as rs
import sys
import numpy as np

def get_Rotation(Vec1, Vec2):
    
    dot_product = np.dot(Vec1, Vec2)
    mag_x = np.linalg.norm(Vec1)
    mag_y = np.linalg.norm(Vec2)
    
    # Calculate angle in radians
    cos_angle = dot_product / (mag_x * mag_y)
    angle = np.arccos(cos_angle)
    
    # Convert angle to degrees
    angle_degrees = np.degrees(angle)
    
    return angle_degrees

# Initialize the RealSense camera
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)
'''
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)
depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
'''
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

scale_percent = 150 # percent of original size

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose,mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
            
  while True:
    frames = pipeline.wait_for_frames(timeout_ms=10000)
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not color_frame:
      
      # If loading a video, use 'break' instead of 'continue'.
      continue
    
    # Convert the color frame to an OpenCV image
    image = np.asanyarray(color_frame.get_data())
    # Extract the depth information of each landmark
    depth_image = np.asanyarray(depth_frame.get_data())

    
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    depth_image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    results_pose = pose.process(image)
    
    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results_pose.pose_landmarks:
        for landmark in results_pose.pose_landmarks.landmark:
            mp_drawing.draw_landmarks(
                image,
                results_pose.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        # Get the indices of the landmarks representing the left arm
        left_arm_landmark_indices = [11, 13, 15]
        
        # Get the coordinates of the left arm
        left_arm_coordinates = []
        
        for idx, lmk in enumerate(results_pose.pose_landmarks.landmark):
            if idx in left_arm_landmark_indices and lmk.visibility >0.5:
                if 0<int(lmk.x * image.shape[1])<640 and 0<int(lmk.y * image.shape[0])<480:
                    z = depth_image[int(lmk.y * image.shape[0]), int(lmk.x * image.shape[1])]
                    left_arm_coordinates.append((int(lmk.x * image.shape[1]), int(lmk.y * image.shape[0]),z))
                    image = cv2.circle(image, (int(lmk.x * image.shape[1]), int(lmk.y * image.shape[0])), 5, (0, 255, 0), -1)
                    
        if len(left_arm_coordinates)==3:
            
            Elbow_X = str(left_arm_coordinates[1][0]-left_arm_coordinates[0][0])
            Elbow_Y = str(left_arm_coordinates[1][1]-left_arm_coordinates[0][1])
            Elbow_Z = str(int(left_arm_coordinates[1][2])-int(left_arm_coordinates[0][2]))
            Wrist_X = str(left_arm_coordinates[2][0]-left_arm_coordinates[0][0])
            Wrist_Y = str(left_arm_coordinates[2][1]-left_arm_coordinates[0][1])
            Wrist_Z = str(int(left_arm_coordinates[2][2])-int(left_arm_coordinates[0][2]))
            
            Rel_joint_Pt = [left_arm_coordinates[1][0]-left_arm_coordinates[0][0], 
                        left_arm_coordinates[1][1]-left_arm_coordinates[0][1], 
                        int(left_arm_coordinates[1][2])-int(left_arm_coordinates[0][2]),
                        left_arm_coordinates[2][0]-left_arm_coordinates[0][0],
                        left_arm_coordinates[2][1]-left_arm_coordinates[0][1],
                        int(left_arm_coordinates[2][2])-int(left_arm_coordinates[0][2])]
            Rel_joint_Pt_str = ', '.join(str(i) for i in Rel_joint_Pt)


            # Print the coordinates of the left arm
            left_arm_coordinates_str = ', '.join([f'({x},{y},{z})' for x, y,z in left_arm_coordinates])
            
            
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
             
            # resize image
            image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            image =cv2.flip(image, 1)
            cv2.putText(image,left_arm_coordinates_str,(50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0, 255), 2, cv2.LINE_AA)  
            cv2.putText(image,Rel_joint_Pt_str,(50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0, 255), 2, cv2.LINE_AA)            
            #print("coordinates:" + left_arm_coordinates_str, flush=True)
            print("Entry," +Elbow_X+","+Elbow_Y+","+Elbow_Z+","+Wrist_X+","+Wrist_Y+","+Wrist_Z, flush=True)
            sys.stdout.flush()
        
        else:
          
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
             
            # resize image
            image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
            image =cv2.flip(image, 1)        
           
           
    # Flip the image horizontally for a selfie-view display.
    
    
    cv2.imshow('MediaPipe Pose',image )
    
    
    if cv2.waitKey(5) & 0xFF == ord('q'):
      break
cv2.destroyAllWindows()
