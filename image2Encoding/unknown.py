import face_recognition
import redis
import numpy as np
import os
import cv2
import threading
import uuid
# import pdb
# pdb.set_trace()


def ConvertImage2Encoded(filepath):
    LoadedImage = face_recognition.load_image_file(filepath)
    EncodedFace = face_recognition.face_encodings(LoadedImage)[0]
    return EncodedFace


def RedisConn():
    r = redis.Redis(host='localhost', port=10002, db=0, password="eYVX7Ew24VmmxKPCDmwMtggyKVge8oLd2t81")
    return r


def SaveEncoding(Encoding,Name,redisDB):
    # Serialize each array and store in Redis as a string
    redisDB.delete(Name)
    redisDB.set(Name,Encoding.dumps()) 

def GetAllEncodings(redisDB):
    list_keys = [key.decode() for key in redisDB.keys()]
    Final_encodings = []
    for key in list_keys:
        arr = np.loads(redisDB.get(key))
        Final_encodings.append(list(arr))
    return Final_encodings

def GetAllRedisKeys(redisDB):
    list_keys = [key.decode() for key in redisDB.keys()]
    return list_keys

def count_files(path):
    return len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])


def strip_file_name(file_name):
    return file_name.split('.')[0]

def DataCountInRedis(redisDB):
    obj_count = redisDB.dbsize()
    return obj_count

def GetFileNames(path):
    files = os.listdir(path)
    return files

BasePath = "/home/mohammad/Aftab/faceRecognition/pics/"

# start redis
RedisClient = RedisConn()

# start the model trainer:
state = False
def TrainModel(BasePath):
    global state
    RedisClient = RedisConn()
    while True:
        # check the count of objects in redis database
        CountInRedis = DataCountInRedis(RedisClient)

        # check if there is a new file in the pics folder
        CountFiles = count_files(BasePath)

        # if there are new files get the name of the new files in pics folder
        if CountInRedis != CountFiles:
            state = False
            files = GetFileNames(BasePath)
            redisKeys = GetAllRedisKeys(RedisClient)
            newKeys = []
            newFiles = []
            for file in files:
                key = strip_file_name(file)
                if key not in redisKeys:
                    newKeys.append(key)
                    newFiles.append(file)
            newEncodingList = []
            # encode the new files with correct format
            for file in newFiles:
                EncodedData = ConvertImage2Encoded(BasePath + file)
                newEncodingList.append(EncodedData)

            # zip the encoding with its label
            zippedData = list(zip(newEncodingList,newKeys))

            # save the new encoding with name in the redis databse
            for Encoding,Name in zippedData:
                SaveEncoding(Encoding,Name,RedisClient)
        state = True


# run the model
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
# Get a reference to webcam #0 (the default one) (WEBCAM)
# video_capture = cv2.VideoCapture(0)
# video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# RTSP
Url = "rtsp://admin:Cam1live@192.168.1.2:554/onvif1"
video_capture = cv2.VideoCapture(Url)
video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

known_face_encodings = []
known_face_names = []
# update the running model :
def UpdateModel():
    # time.sleep(30)
    global known_face_encodings
    global known_face_names
    global state
    RedisClient = RedisConn()
    while True:
        try:
            if state == True:
                # Create arrays of known face encodings and their names
                known_face_encodings = GetAllEncodings(RedisClient)
                known_face_names = GetAllRedisKeys(RedisClient)
            else:
                known_face_encodings = []
                known_face_names = []
        except:
            pass
    

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Run the Model:
def RunModel(process_this_frame,video_capture):
    global known_face_encodings
    global known_face_names
    global state
    RedisClient = RedisConn()
    while True:
        # Grab a single frame of video
        if len(known_face_encodings) != 0 or len(known_face_names) != 0:
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if process_this_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                Unknowns = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    try:
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                        name = "Unknown"

                        # # If a match was found in known_face_encodings, just use the first one.
                        # if True in matches:
                        #     first_match_index = matches.index(True)
                        #     name = known_face_names[first_match_index]

                        # Or instead, use the known face with the smallest distance to the new face
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                    
                        if name == "Unknown":
                            Unknowns.append(face_encoding)
                        face_names.append(name)
                    except:
                        continue

            process_this_frame = not process_this_frame
            for face in Unknowns:
                matches = face_recognition.compare_faces(known_face_encodings, face)
                face_distances = face_recognition.face_distance(known_face_encodings, face)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    continue
                FileName = "Unknown-"+str(uuid.uuid4())
                Path = BasePath + FileName + ".jpg"
                cv2.imwrite(Path, frame)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

thread1 = threading.Thread(target=TrainModel,args=(BasePath,))
thread2 = threading.Thread(target=UpdateModel)
thread3 = threading.Thread(target=RunModel,args=(process_this_frame,video_capture))

thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()


