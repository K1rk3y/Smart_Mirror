# import the necessary packages
from imutils.video import VideoStream
from collections import defaultdict
import argparse
import datetime
import imutils
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
# otherwise, we are reading from a video file
else:
    vs = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

step = 0
frame_skip = 30
bounding_boxes = {}
face_list = {}
tracking_list = {}


def tracking(label):
    if label in tracking_list:
        if tracking_list[label] < 6:
            tracking_list[label] += 1
            return None
        else:
            tracking_list.pop(label)
            return label
    else:
        tracking_list[label] = 0
        return None
        

def find_center(box):
    a, b, c, d = box
    center_x = (a + c) / 2
    center_y = (b + d) / 2
    return center_x, center_y


def process_coordinates(coo):
    directions = []
    for i in range(len(coo)):
        prev_box = coo[i - 1] if i > 0 else None
        current_box = coo[i]
        next_box = coo[i + 1] if i < len(coo) - 1 else None
        
        current_center = find_center(current_box)
        prev_center = find_center(prev_box) if prev_box else None
        next_center = find_center(next_box) if next_box else None
        
        # Determine shift direction based on current box and its neighboring boxes
        if prev_center and current_center[0] < prev_center[0]:
            directions.append(-1)
        elif next_center and current_center[0] > next_center[0]:
            directions.append(1)
        else:
            directions.append(0)

    opt = sum(directions) / len(directions)
    
    return opt    


# loop over the frames of the video
while True:
    motion_list = {}
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Clear"
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    if step >= frame_skip and step % frame_skip == 0:
        firstFrame = gray
        # call the facial recogonition api, returns coordinates of the faces identified and labels
        face_list = 

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        
        #if len(faces_identified) > 0:
        #   for face in faces_identified:
        #       if str(face) not in bounding_boxes:
        #           bounding_boxes[str(face)] = []
        #
        #       if face is found in bounding_boxes_coordinates:
        #           cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #           text = "Individual Detected"
        #       else:
        #           cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #           text = "Undefined Motion Detected"
        #           continue
        #else:
        #   cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #   text = "Undefined Motion Detected"
    
    # read the dictionary for every 30 times 6 revolutions after the first api call, 
    # ideally there should be 6 coordinates entries for every face logged in the dictionary, 
    # each of the 6 entries spaced out by 30 frames
    # clear the dictionary at the end

    for face in face_list:
        done_tracking = tracking(face)
        
        if done_tracking is not None:
            motion = process_coordinates(bounding_boxes[done_tracking])
            motion_list[done_tracking] = motion
            bounding_boxes[done_tracking] = []
            
    print(motion_list)
        
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
        
    step += 1   
    if step == 9000:
        step = 0

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
