import os
import mediapipe as mp
import numpy as np
import cv2
import random
from detect import *
from progress.bar import Bar
from threading import Event

def count_videos(video_path, actions):
    print("Counting Videos...")
    video_amount = np.zeros(actions.size, dtype=int)

    #Counting videos in each label in the dataset
    for action in range(len(actions)):
        video_amount[action] = len(os.listdir(os.path.join(video_path, actions[action])))
    return video_amount

#Check if the event passed from the gui has been set. If so, return True
def is_stop_requested(event):
    should_stop = False

    if event.is_set():
        print("Thread stopping..")
        should_stop = True
    return should_stop

def extract_data(actions, video_amount, desired_length, data_path, shape_size, video_path, stop_event = Event()):
    #create folder for each action

    for action in range(len(actions)):
        no_sequences = video_amount[action]
        #use video in video_list at some point Look down below for help
        for sequence in range (no_sequences):  
            try:
                os.makedirs(os.path.join(data_path, actions[action], str(sequence)))
            except:
                pass #THROW EXCEPTIONS HERE!

    mp_holistic = mp.solutions.holistic 

    #set mediapipe model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        #goes through the actions
        for action in actions:
            #Verify stop event hasnt been requested/set
            if is_stop_requested(stop_event):
                break

            #gets list of videos
            video_list = os.listdir(os.path.join(video_path, action))

            video_number = 0

            #goes through the list of videos
            with Bar(f'Extracting datapoints for action {action}...', max = len(video_list)) as bar:
                for video in video_list:
                    if is_stop_requested(stop_event):
                        break

                    #grabs video
                    cap = cv2.VideoCapture(os.path.join(video_path, action, video))
                    #counts amount of frames in video
                    video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    #if video is shorter than desired amount of frames start frame is set to 0
                    if desired_length >= video_length:
                        start = 0
                    #else starts at a random frame that will results in desired amount of frames
                    else:
                        max_start = video_length - desired_length
                        start = random.randint(0, max_start)

                    #sets start frame
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                    #goes through frames
                    for frame_num in range(desired_length):
                        if is_stop_requested(stop_event):
                            break
                        
                        #uses read to get frame
                        has_frame, frame = cap.read()
                        #if no frame exists, fill in blank
                        if not has_frame:
                            frame = cv2.imread('black.png')
                        #gets results back from detection method
                        results = detect_keypoints(frame, holistic)

                        #gets keypoints from extract_keypoints function
                        #keypoints = extract_keypoints(results)
                        keypoints = extract_all_keypoints(results, shape_size)
                        
                        #sets path for numpy array
                        #npy_path = os.path.join(DATA_PATH, action, str(video), str(frame_num))
                        npy_path = os.path.join(data_path, action, str(video_number), str(frame_num))
                        
                        #saves numpy array with keypoints
                        np.save(npy_path, keypoints)
                    bar.next()
                    video_number += 1

                    #releases the videocapture
                    cap.release()