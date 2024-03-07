import cv2
import numpy as np
import win32api


class Detection:

    def __init__(self):
        # Initialize camera properties
        self.CameraHeight = 480.0
        self.CameraWidth = 640.0
        self.cameraIndex = 0  # The camera the user can use. A potential feature to add to the settings page
        self.cap = cv2.VideoCapture(self.cameraIndex)
        self.cap.set(3, self.CameraWidth)

        # Initialize image properties
        self.imageBGR = []
        self.imageGRAY = None
        self.imageHSV = None

        # Coordinates for face, eye, and hand
        self.face_eye_coords = {'face': None, 'eye': None, 'hand': None}
        self.face_coords = self.face_eye_coords['face']
        self.eye_coords = self.face_eye_coords['eye']
        self.hand_coords = self.face_eye_coords['hand']

        # Samples lists
        self.raw_samples = []
        self.samples = []
        self.tolerance = [30, 30, 30]
        self.mask = None

        # Load XML Haar cascade file for face and eye detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

        # Scaling factors
        self.xSF = 1
        self.ySF = 1
        # Get screen dimensions
        self.screenHeight = win32api.GetSystemMetrics(1)
        self.screenWidth = win32api.GetSystemMetrics(0)

    def faceDetect(self, frame):
        # Detect faces in the frame using the face cascade classifier
        faces = self.face_cascade.detectMultiScale(frame, 1.3, 5)

        # Check if any faces are detected
        if len(faces) > 0:
            largest = 0
            index = []
            # Find largest part of the faces
            for i in faces:
                if i[2] * i[3] > largest:
                    largest = i[2] * i[3]
                    index = i
            # Store the coordinates of the largest part
            self.face_coords = index
        else:
            # If no faces are detected, set face_coords to an empty list
            self.face_coords = []

    def featureDetect(self, frame):
        # Gets the values for the eyes
        eyes = self.eye_cascade.detectMultiScale(frame)
        self.eye_coords = eyes

    def calibrateFaceDetection(self):
        # Capture a frame from the camera
        _, self.imageBGR = self.cap.read()
        # Convert the colour format to grayscale and HSV
        self.imageGRAY = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2HSV)
        # Detect faces in the grayscale image
        self.faceDetect(self.imageGRAY)

        # If at least one face is detected
        if len(self.face_coords) > 0:
            # Extract the coordinates and dimensions of the detected face
            [x, y, w, h] = self.face_coords
            # Draw a rectangle around the detected face on the BGR image
            cv2.rectangle(self.imageBGR, (x, y), (x + w, y + h), (255, 0, 0))
            # Draw rectangles around the detected eyes on the BGR image using OpenCV's rectangle function
            self.featureDetect(self.imageGRAY[y:y + h, x:x + w])
            # Creating the rectangles to go around the eyes using openCV rectangle
            for [ex, ey, ew, eh] in self.eye_coords:
                cv2.rectangle(self.imageBGR, (ex + x, ey + y), (ex + x + ew, ey + y + eh), (0, 255, 0), 2)

            if len(self.eye_coords) != 2:
                print("Eye detection and counting error")

        return self.imageBGR

    # OLD calibrationSamples
    """def calibrationSamples(self):
        [x, y, w, h] = self.face_coords
        imageFace = self.imageHSV[y:y + h, x:x + w]
        base_y = 0
        sx = 10000
        base_x = 0
        for [ex, ey, ew, eh] in self.eye_coords:
            if (ey + eh) > base_y:
                base_y = ey + eh
            if ex < sx:
                sx = ex
            if ex + ew > base_x:
                base_x = ex + ew
        for i in range(1, (base_x - sx) // 10 + 1):
            self.raw_samples.append(imageFace[base_y][sx + i * 10])
            upper, lower = [], []
            for x in range(len(self.tolerance)):
                upper.append(imageFace[base_y][sx + i * 10][x] + self.tolerance[x])
                lower.append(imageFace[base_y][sx + i * 10][x] - self.tolerance[x])
            # Colour tolerance for RGB, max 255, min 0
            print("Before:")
            print(upper)
            print(lower)
            for y in range(len(upper)):
                upper[y] = min(max(upper[y], 0), 255)
            for y in range(len(lower)):
                lower[y] = min(max(lower[y], 0), 255)
            print("\nAfter:")
            print(upper)
            print(lower)
            print()
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            print("Numpy:")
            print(upper)
            print(lower)
            self.samples.append([lower, upper])"""

    def calibrationSamples(self):
        # Extract the region of interest linked to the detected face from the HSV image
        [x, y, w, h] = self.face_coords
        imageFace = self.imageHSV[y:y + h, x:x + w]

        # Determine the base coordinates for sampling based on the eye coordinates
        base_y = max([ey + eh for (ex, ey, ew, eh) in self.eye_coords])
        start_x = min([ex for (ex, ey, ew, eh) in self.eye_coords])
        base_x = max([ex + ew for (ex, ey, ew, eh) in self.eye_coords])

        # Iterate over horizontal sampling points with a step size of 10 pixels
        for i in range(1, (base_x - start_x) // 10 + 1):
            sample_point = imageFace[base_y, start_x + i * 10]  # Get the HSV values when sampled
            self.raw_samples.append(sample_point)  # Add samples to the raw sample list

            # Calculate the upper and lower bounds of the color tolerance
            lower = np.clip(sample_point - self.tolerance, 0, 255).astype(np.uint8)
            upper = np.clip(sample_point + self.tolerance, 0, 255).astype(np.uint8)
            # Print for debugging purposes
            print("Lower", lower)
            print("Upper", upper)
            # Append the lower and upper bounds as a pair to the list of samples
            self.samples.append([lower, upper])

    def createMask(self):
        # Create a mask using the lower and upper bounds of the first sample
        self.mask = cv2.inRange(self.imageHSV, self.samples[0][0], self.samples[0][1])
        for i in self.samples:
            temp_mask = cv2.inRange(self.imageHSV, i[0], i[1])  # Make temporary mask with the upper nad lower bounds
            # Combine the temporary mask with the existing mask using OR operation
            self.mask = cv2.bitwise_or(self.mask, temp_mask)

    def findContours(self):
        # Convert the BGR to grayscale
        self.imageGRAY = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2GRAY)
        # Find contours in the mask image
        contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            largest = 0
            contour = None
            # Find the largest contour
            for cont in contours:
                x, y, w, h = cv2.boundingRect(cont)
                if w * h > largest:
                    largest = w * h
                    contour = cont
            # Draw the largest contour on the BGR image
            cv2.drawContours(self.imageBGR, [contour], 0, (0, 255, 0), 2)
            hx, hy, hw, hh = cv2.boundingRect(contour)  # Get the bounding rectangle of the largest contour
            self.hand_coords = [hx + hx // 2, hy + hh // 2, hw * hh]  # Calculate center coords and area of rectangle
            # Draw a circle at the center of the hand region, Users reference of where the mouse is moved from
            cv2.circle(self.imageBGR, (self.hand_coords[0], self.hand_coords[1]), 4, (255, 0, 0), -1)

    def loop(self):
        _, self.imageBGR = self.cap.read()  # Read a single frame from the camera
        self.imageHSV = cv2.cvtColor(self.imageBGR, cv2.COLOR_BGR2HSV)
        self.imageHSV = cv2.blur(self.imageHSV, (5, 5))  # Blur applied to reduce noise

        self.createMask()
        self.findContours()

        # Calculate the coordinates of the detection region rectangle
        x1 = int((self.CameraWidth - self.CameraWidth / self.xSF) / 2)
        x2 = int(self.CameraWidth - x1)
        y1 = int((self.CameraHeight - self.CameraHeight / self.ySF) / 2)
        y2 = int(self.CameraHeight - y1)
        cv2.rectangle(self.imageBGR, (x1, y1), (x2, y2), (0, 0, 255))  # Draw rectangle around the detection region
        cv2.putText(self.imageBGR, "Detection Region", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

    def changeTolerance(self, value):
        self.tolerance = [value, value, value]  # Update the tolerance values
        self.samples = []  # Reset the samples list of any old samples
        for i in self.raw_samples:
            upper, lower = [], []
            # Creating the bounds of tolerance by adding the assigned value to the
            upper.append(i[0] + self.tolerance[0])
            upper.append(i[1] + self.tolerance[1])
            upper.append(i[2] + self.tolerance[2])
            lower.append(i[0] + self.tolerance[0])
            lower.append(i[1] + self.tolerance[1])
            lower.append(i[2] + self.tolerance[2])
            # Checking the extremes of the colours and setting them to the max and min values if they go over it
            for y in range(len(upper)):
                upper[y] = min(max(upper[y], 0), 255)
            for y in range(len(lower)):
                lower[y] = min(max(lower[y], 0), 255)
            # Convert the lists to NumPy arrays of type uint8
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            self.samples.append([lower, upper])

    def moveMouse(self):
        # Gets coordinates/ hieght ot width, to find it in relation to the screen size
        x_normalised = self.hand_coords[0] / self.CameraWidth
        y_normalised = self.hand_coords[1] / self.CameraHeight
        # Find the difference in position
        # Convert normalized coordinates to screen coordinates by scaling to the screen resolution
        x = 1920 - int(x_normalised * 1920)
        y = int(y_normalised * 1200)
        print(self.hand_coords)
        win32api.SetCursorPos((int(x), int(y))) # Set the mouse cursor position to the calculated screen coordinates
