# Hand Tracking App 👋

Welcome to the Hand Tracking App repository! This project was created for my A-Level Computer Science NEA project it offers a simple yet effective solution for hand tracking using computer vision techniques. The repository contains the code for the project and the full documentaion for the NEA will be posted soon.

This project aims to provide a simple yet powerful solution for hand tracking as a way of making the use of a mouse obselete. Alongside making it usable for all people regardless of their technical skill.

## Overview
The programme is made with *OpenCV* and the hand and eye *Haar Cascade Clasifier*. It works with the premise of collecting the users skin colour data and using that to identifiy there hand, of which the movemnt would be relayed to the cursor.

### Features
1. **Calibration** to be able to get the skin colour. This is done by detecting both the eyes and the face and then the colour of the skin is found. Then to it a tolerance is added to make account for the changes in light or different skin complection. On the users end it is hassle free all they need to do is just keep clicking *"continue"* when the requirements of each page are met.
2. **Live Tracking** of the hand which corresponds to the movement of the hand.
3. **Settings Page** to be able to adjust the speed and push to stop keys (PTS) for when using the programme. Using the `win32api` keys on the keyboard when pressed and if they are corresponidng to the PTS it would stop the tracking and return the control from the application back to the mouse.
4. **Responsive User Interface** which shows an overlay/contour  around the hand in realtime as a visual aide to the user.
5. **Instructions Page** to show the user how to use the programme and the *calibration* process.

## Getting Started
To get up and running with the app, follow these steps:
1. Clone Repository:
   ```
   git clone https://github.com/rudrapatel08/Hand-Tracking-App.git
   ```
2. Install the required dependencies in the rquirements page:
   ```
   pip install -r requirements.txt
   ```
3. Finally run the programme and have fun:
   ```
   python hand_tracking_app.py
   ```

## Notes
When using the application make sure your webcam is connected properly and accessible by the programme.
The code is also commented, maybe a bit too much, so feel free to walk yourself through the code. 🙂
