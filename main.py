import tkinter as tk
from PIL import Image, ImageTk
import cv2
import processing
import win32api
import win32con

calibrated = 0  # Is programme calibrated
cameraFeed = processing.Detection()


class MainClass:
    def __init__(self, master):
        # Initialise main window and attributes
        self.master = master
        self.master.title("main")

        # Initialise variables and widgets
        self.running = 0
        self.font = "Arial"
        self.img = ImageTk.PhotoImage(Image.open("CalibrationNeeded.png"))
        self.image_label = tk.Label(master, image=self.img)
        self.image_label.grid(row=0, column=0, rowspan=5)
        self.imageLoop()

        # Button to initiate calibration
        self.calibrate_button = tk.Button(master, text="Calibrate", command=self.calibrateWindow, height=5, width=50)
        self.calibrate_button.grid(row=0, column=1, columnspan=2)

        # Button to display instructions page
        self.info_button = tk.Button(master, text="Instructions", command=self.instructionWindow, height=5, width=50)
        self.info_button.grid(row=1, column=1, columnspan=2)

        # Button to start or stop the program
        self.stop_button = tk.Button(master, text="Start", height=10, width=50, command=self.startStop)
        self.stop_button.grid(row=2, column=1, columnspan=2)

        # Text to show push-to-stop feature
        self.stop_label = tk.Label(master, text="Push to Stop:", font=(self.font, 16))
        self.stop_label.grid(row=4, column=1)

        # Button to access settings page
        self.settingsButton = tk.Button(master, text="Settings", command=self.settingsWindow, height=5, width=50)
        self.settingsButton.grid(row=3, column=1, columnspan=2)

        # Text to indicate if the program is running or not
        self.runningLabel = tk.Label(master, text="OFF", font=(self.font, 16), bg="RED")
        self.runningLabel.grid(row=5, column=1, columnspan=2)

        # Update the stop key status
        self.stopKeyUpdate()

    def stopKeyUpdate(self):
        try:
            # To change the Push to Stop key but making sure it is a function key
            self.stopKeyLabel = tk.Label(self.master, text=self.app.stopKeyVar, font=(self.font, 16))
            self.stopKeyLabel.grid(row=4, column=2)

            # Define dictionary to map function key strings to virtual key codes
            stopKeys = {"F1": win32con.VK_F1, "F2": win32con.VK_F2, "F3": win32con.VK_F3, "F4": win32con.VK_F4,
                        "F5": win32con.VK_F5, "F6": win32con.VK_F6, "F7": win32con.VK_F7, "F8": win32con.VK_F8,
                        "F9": win32con.VK_F9}
            # Get the virtual key code corresponding to the stop key
            self.stopKey = stopKeys[self.app.stopKeyVar.upper()]
            print(self.stopKey)  # For debugging

        except AttributeError:
            # If the stopKeyVar attribute is not found, set default stop key to F2
            self.stopKeyLabel = tk.Label(self.master, text="F2", font=(self.font, 16))
            self.stopKeyLabel.grid(row=4, column=2)
            self.stopKey = win32con.VK_F2  # Set default stop key to F2

    def calibrateWindow(self):
        # Open calibration window
        self.new_window = tk.Toplevel(self.master)
        self.app = Calibration(self.new_window)

    def instructionWindow(self):
        # Open instructions window
        self.new_window = tk.Toplevel(self.master)
        self.app = Instruction(self.new_window)

    def settingsWindow(self):
        # Open settings window
        self.new_window = tk.Toplevel(self.master)
        self.app = Settings(self.new_window)

    def imageLoop(self):
        global calibrated
        if calibrated:  # Calibrated value does not equal 0 to indicate it has been calibrated
            # If calibrated, continue processing camera feed
            cameraFeed.loop()
            # Convert BGR image to RGBA format
            image = cameraFeed.imageBGR
            cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

            img = Image.fromarray(cv2image)  # Convert numpy array to PIL Imag
            imgtk = ImageTk.PhotoImage(image=img)  # Convert PIL Image to ImageTk format
            # Update image in the label
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)
            if self.running:
                cameraFeed.moveMouse()
                if win32api.GetAsyncKeyState(self.stopKey) != 0:
                    self.startStop()
        else:
            # If not calibrated, display calibration needed image
            self.image_label.configure(image=self.img)
        # The next iteration of imageLoop after 10 milliseconds
        self.image_label.after(10, self.imageLoop)

    def startStop(self):
        if calibrated:
            self.running = not self.running  # Toggles the value of self.running
            if self.running:
                # Button turns from a start button to a stop button
                self.stop_button.configure(bg="Red", text="Stop")
                # Text to indicate the programme is running changes
                self.runningLabel.configure(bg="GREEN",
                                            text="ON")
            else:
                # Keep/create the start button
                self.stop_button.configure(bg="GREEN", text="Start")
                # Shows programme is off
                self.runningLabel.configure(bg="RED", text="OFF")


class Calibration:
    def __init__(self, master):
        # Call the global variable and set to zero/False
        global calibrated
        calibrated = 0

        self.master = master
        self.master.title("Calibration")

        # Create label to display calibration image
        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row=0, column=0, columnspan=2)
        self.showFrame()

        # Button to quit
        self.quitButton = tk.Button(self.master, text="Quit", width=25, command=self.close_windows)
        self.quitButton.grid(row=3, column=0)

        # Button to go to next stage of calibration
        self.nextButton = tk.Button(self.master, text="Next", command=self.stage2, width=25)
        self.nextButton.grid(row=3, column=1)

        # Instructions for calibration first step
        self.instructions = tk.Label(master, text="Make sure to have a clear background")
        self.instructions2 = tk.Label(master, text="Try not to wear anything short sleeved")
        self.instructions.grid(row=1, column=0, columnspan=2)
        self.instructions2.grid(row=2, column=0, columnspan=2)

    def showFrame(self):
        _, image = cameraFeed.cap.read()  # Captures a image
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)  # Convert the image to RGBA
        img = Image.fromarray(cv2image)  # Convert the image to a PIL Image
        imgtk = ImageTk.PhotoImage(image=img)  # Convert the PIL Image to ImageTk format
        # Update the image in the label
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image=imgtk)
        # Next iteration after 10 milliseconds
        self.imageLabel.after(10, self.showFrame)

    def showFace(self):
        image = cameraFeed.calibrateFaceDetection()  # Capture an image and detect face
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)  # Convert the image to RGBA
        img = Image.fromarray(cv2image)  # Convert the image to a PIL Image
        imgtk = ImageTk.PhotoImage(image=img)  # Convert the PIL Image to ImageTk format
        # Update the image in the label
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image=imgtk)
        # Next iteration after 10 milliseconds
        self.imageLabel.after(10, self.showFace)

    def close_windows(self):
        self.master.destroy()

    def stage2(self):
        # Destroy previous widgets
        self.instructions.destroy()
        self.instructions2.destroy()
        self.nextButton.destroy()
        self.quitButton.destroy()
        self.imageLabel.destroy()

        # Create a new label to display the calibrated face
        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row=0, column=0, columnspan=2)
        self.showFace()

        # Given instructions for stage 2
        self.instructions = tk.Label(self.master,
                                     text="Ensure tour face is within the blue box, and there is a green box around each eye.")
        self.instructions2 = tk.Label(self.master, text="Click 'Next' when there is.")
        self.instructions.grid(row=1, column=0, columnspan=2)
        self.instructions.grid(row=2, column=0, columnspan=2)

        # Create quit and next buttons for stage 2
        self.quitButton = tk.Button(self.master, text="Quit", width=25, command=self.close_windows)
        self.quitButton.grid(row=3, column=0)

        # Create Continue and next buttons for stage 2
        self.nextButton = tk.Button(self.master, text="Continue", width=25, command=self.stage3)
        self.nextButton.grid(row=3, column=1)

    def PreviousToStage2(self):
        # Destroy buttons for previous stage
        self.prev_button.destroy()
        self.cont_button.destroy()
        self.stage2()  # Go to stage 2 again

    def stage3(self):
        # Destroy previous widgets
        self.instructions.destroy()
        self.instructions2.destroy()
        self.nextButton.destroy()
        self.quitButton.destroy()
        self.imageLabel.destroy()

        # Create a new label to display the image, with the rectangles
        self.imageLabel = tk.Label(self.master)
        self.imageLabel.grid(row=0, column=0, columnspan=3)

        # Capture an image and convert it
        image = cameraFeed.imageBGR
        cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the image in the label
        self.imageLabel.imgtk = imgtk
        self.imageLabel.configure(image=imgtk)

        # Given instructions for stage 3
        self.instructions = tk.Label(self.master, text="Check if box around your face and eyes.")
        self.instructions2 = tk.Label(self.master, text="If so 'continue', if not press previous to try again.")
        self.instructions.grid(row=1, column=0, columnspan=3)
        self.instructions2.grid(row=2, column=0, columnspan=3)

        # Create buttons for stage 3
        self.prev_button = tk.Button(self.master, text="Previous", width=25, command=self.PreviousToStage2)
        self.cont_button = tk.Button(self.master, text="Continue", width=25, command=self.stage4)
        self.prev_button.grid(row=3, column=0)
        self.cont_button.grid(row=3, column=2)

    def stage4(self):
        # Destroy previous widgets
        self.instructions.destroy()
        self.instructions2.destroy()
        self.prev_button.destroy()
        self.cont_button.destroy()
        self.imageLabel.destroy()

        # Given instructions for stage 4
        self.instructions = tk.Label(self.master, text="All calibrated and set. Yippee!!!!")
        self.instructions2 = tk.Label(self.master, text="Press finish to go back to the home page.")
        self.instructions.grid(row=1, column=0, columnspan=3)
        self.instructions2.grid(row=2, column=0, columnspan=3)

        # Button to complete the calibration process
        self.finish_button = tk.Button(self.master, text="Finish", width=25, command=self.finish)
        self.finish_button.grid(row=4, column=0, columnspan=3)

        # Create calibration samples that will be used for detection
        cameraFeed.calibrationSamples()

    def finish(self):
        global calibrated
        calibrated = 1
        self.close_windows()


class Settings:
    def __init__(self, master):
        # Set up the settings window
        self.master = master
        self.master.title("Settings")

        # Text for the PTS key
        self.PTSKeyText = tk.Label(self.master, text="""Push to stop key(F1-9):""")
        self.PTSKeyText.grid(row=0, column=0)

        # Entry field to input the new PTS key
        self.stopKeyVar = tk.StringVar()
        self.PTSKeyEntry = tk.Entry(self.master, textvariable=self.stopKeyVar)
        self.PTSKeyEntry.grid(row=0, column=1)

        # Button to set the PTS key
        self.PTSKeyButton = tk.Button(self.master, text="Set", command=self.stopKeyGet)
        self.PTSKeyButton.grid(row=0, column=2)

        # Slider for the X axis -> linked with xSF in the processes.py to scale up the movement of mouse
        self.xSpeedText = tk.Label(self.master, text="Horizontal Speed:")
        self.xSpeedText.grid(row=1, column=0)
        self.xSpeedSlider = tk.Scale(self.master, from_=1, to=10, orient=tk.HORIZONTAL, length=400)  # Slider creation
        self.xSpeedSlider.set(cameraFeed.xSF * 10 - 9)  # Increase the speed of camera
        self.xSpeedSlider.grid(row=1, column=1)

        # Slider for the Y axis -> linked with ySF
        self.ySpeedText = tk.Label(self.master, text="Vertical Speed:")
        self.ySpeedText.grid(row=2, column=0)
        self.ySpeedSlider = tk.Scale(self.master, from_=1, to=10, orient=tk.HORIZONTAL, length=400)  # Slider creation
        self.ySpeedSlider.set(cameraFeed.ySF * 10 - 9)  # Increase the speed of camera
        self.ySpeedSlider.grid(row=2, column=1)

    def stopKeyGet(self):
        # Get the stop key from the entry field
        stop_key_entry = self.PTSKeyEntry.get()
        if len(stop_key_entry) == 2:
            if stop_key_entry[0].upper() == "F" and 1 <= int(stop_key_entry[1]) <= 9:
                # Set the PTS key variable and update the UI
                self.stopKeyVar = stop_key_entry
                print(self.stopKeyVar)
                mainApp.stopKeyUpdate()
                self.PTSKeyButton.configure(bg="WHITE")
                self.PTSKeyText.configure(fg="BLACK")
                return
        # Print error message if the input is invalid
        print("Input Error")

    def stopKeyInputError(self):
        self.PTSKeyButton.configure(bg="RED")
        self.PTSKeyText.configure(fg="DARK RED")

    def close_window(self):
        # Update the horizontal and vertical speed factors based on slider values
        cameraFeed.xSF = (self.xSpeedSlider.get() * 10) / 10.0
        cameraFeed.ySF = (self.ySpeedSlider.get() * 10) / 10.0


class Instruction():
    def __init__(self, master):
        self.master = master
        self.width = 600  # Setting up the width for the window screens for the instructions

        # Display the next instruction image
        self.img = ImageTk.PhotoImage(Image.open("InstructionPic1.png"))
        self.imgLabel = tk.Label(self.master, image=self.img)
        self.imgLabel.grid(row=0, column=0)

        # Display the instruction text
        self.textLabel = tk.Label(self.master,
                                  text="Make sure the camera is facing you.\nThis program will detect your skin and skin colout so if possible try to wear long sleeves, to prevent it from registering your arm instead of your hand.\nMake sure your baground is fairly clean and uncluttered.",
                                  wraplength=self.width,
                                  font=("Calibri", 10))
        self.textLabel.grid(row=1, column=0)

        # Create the 'Continue' button for the next step
        self.nextButton = tk.Button(self.master, text="Step 2->", command=self.step2, width=40)
        self.nextButton.grid(row=2, column=0)

    def step2(self):
        # Destroy previous widgets
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        # Display the next instruction image
        self.img = ImageTk.PhotoImage(Image.open("InstructionPic2.png"))
        self.imgLabel = tk.Label(self.master, image=self.img)
        self.imgLabel.grid(row=0, column=0)

        # Display the instruction text
        self.textLabel = tk.Label(self.master,
                                  text="There should be a box around your face and eyes, this is the program finding your face.\nOnce you see the it,make sur only your face and eyes are boxed and nothing else.\nWait a few seconds and then press 'Continue'.",
                                  wraplength=self.width,
                                  font=("Calibri", 10))
        self.textLabel.grid(row=1, column=0)

        # Create the 'Continue' button for the next step
        self.nextButton = tk.Button(self.master, text="Step 3->", command=self.step3, width=40)
        self.nextButton.grid(row=2, column=0)

    def step3(self):
        # Destroy previous widgets
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        # Display the next instruction image
        self.img = ImageTk.PhotoImage(Image.open("InstructionPic3.png"))
        self.imgLabel = tk.Label(self.master, image=self.img)
        self.imgLabel.grid(row=0, column=0)

        # Display the instruction text
        self.textLabel = tk.Label(self.master,
                                  text="The program will take a picture of your face with the boxes, double chack if nothing is off or if the boxes are not fully detecting your face.\nIf so press 'Previous' otherwise 'Continue'.",
                                  wraplength=self.width,
                                  font=("Calibri", 10))
        self.textLabel.grid(row=1, column=0)

        # Create the 'Continue' button for the next step
        self.nextButton = tk.Button(self.master, text="Step 4->", command=self.step4, width=40)
        self.nextButton.grid(row=2, column=0)

    def step4(self):
        # Destroy previous widgets
        self.imgLabel.destroy()
        self.textLabel.destroy()
        self.nextButton.destroy()

        # Display the instruction text
        self.textLabel = tk.Label(self.master,
                                  text="YAAAAY, we're all done now, all you need to do is Click 'Finish', and we've succesfully calibrated.\nWhippeee!!!",
                                  wraplength=self.width,
                                  font=("Calibri", 14))
        self.textLabel.grid(row=1, column=0)

        # Create the 'Finish' button to end the instructions pages
        self.nextButton = tk.Button(self.master, text="Finish", command=self.close_window, width=40)
        self.nextButton.grid(row=2, column=0)

    def close_window(self):
        self.master.destroy()


if __name__ == '__main__':
    # main()
    root = tk.Tk()
    mainApp = MainClass(root)
    root.mainloop()
