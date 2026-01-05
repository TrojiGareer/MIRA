# M.I.R.A.

**M.I.R.A.** (Motion Interpretation Remote Assistant) is a desktop assistive technology application built in **Python** using **PyQt6**, **OpenCV**, and **MediaPipe**. It enables full hands-free computer control and learns gestures.

---

## Features

- **Core Functionality**
  - **Touch-less Control**: Complete mouse navigation (move, click, drag) and keyboard shortcuts using hand gestures.
  - **Dynamic Modes**: Seamless switching between *Prediction Mode* and *Data Collection Mode*.
  - **Visual Feedback**: Real-time camera feed with overlays and prediction logging.

- **System Architecture**
  - Built with **PyQt6** for a responsive, event-driven GUI.
  - **Multithreaded Pipeline**: Video capture and inference run on dedicated threads to prevent UI freezing.
  - **Core Structure**:
    ```python
    class MainWindow(QMainWindow):
        # Connection of backend logic to UI
        def __init__(self):
            self.camera_thread = Camera()       # QThread for non-blocking capture
            self.predictor = Predictor()        # ML Inference Engine
            self.mapper = CommandMapper()       # Heuristic Logic Engine
            self.executor = Executor()          # OS Automation Bridge
            self.mode = AppMode.IDLE            # State Machine (Idle/Predict/Collect)
    ```
  - **Signal-Slot Communication**: Asynchronous data flow between the Camera thread and the GUI widgets using `pyqtSignal`.

- **User Experience**
  - **Interactive Manual**: Built-in, tabbed "Command Manual" for presenting default gestures to the user.
  - 

---

## Engine Highlights

- **Hand gesture commands**
  - Wrapper around **PyAutoGUI** to handle OS-level inputs.
  - **Coordinate Mapping**: Translates normalized camera coordinates (0.0 - 1.0) to screen resolution pixels (1920x1080) to prevent cursor drift.

---

# Individual Contributions

### Ianis Nicolau - Hand Gestures & UI/UX

- **System Architecture & Multithreading**: 
  - Designed the modular `PyQt6` structure with a clear separation between UI and backend logic
  - Implemented the **QThread-based Camera** to prevent UI blocking during heavy MediaPipe processing
  - Established **signal-slot communication** pattern between `Camera`, `MainWindow`, and processing engines (`Predictor`, `CommandMapper`)

- **Gesture Recognition**:
  - Developed the complete `CommandMapper` class with **distinct heuristic algorithms**:
    1. **Pinch Detection**: Euclidean distance (`CLICK_THRESHOLD = 0.05`) for left-click (thumb-index) and right-click (thumb-middle)
    2. **Mouse Freeze Mechanism**: `FREEZE_THRESHOLD = 0.10` prevents cursor jitter when preparing to click by freezing movement during pre-pinch approach
    3. **Dead Zone Mapping**: `FRAME_MARGIN = 0.2` excludes outer 20% of camera frame, mapping center 60% to full screen to eliminate edge-case tracking errors
    4. **Victory Sign Scroll**: Y-coordinate thresholds (< 0.4 = up, > 0.6 = down) with a 20% dead zone for stable scrolling
    5. **Two-Hand Volume Control**: Delta-based distance tracking (`±0.02` threshold) between index fingers to filter out noise
   - Switched tracking point from **index fingertip** to **index knuckle** to prevent cursor movement during pinch gestures

- **UI/UX**:
  - Designed and implemented the **interactive Command Manual** with tabbed gesture previews
  - Fixed camera aspect ratio issues to prevent distorted video feed
  - Added real-time visual feedback system (overlay rendering, prediction logs)
  - Implemented the "Ring Fold" gesture logic for Alt+Tab functionality with a 30-frame cooldown to prevent spam

- **Debugging**:
  - Added console logging for gesture state transitions (`MODE SWITCHED: ACTIVE/SLEEP`)
  - Fine-tuned all threshold values through empirical testing to balance sensitivity vs. false positives

### Ana Miron - Live Prediction, ML Integration, Data Processing, Data Acquisition and Live Integration Suite

- **Machine Learning & Gesture Recognition Pipeline**: 
  - Designed and engineered the real-time processing, classification and prediction pipeline, using a 20-frame sliding window buffer that performs heuristic mathematical calculations to distinguish between gesture types (static, dynamic, noise) and sends the processed data to one of the two pre-trained random forest models (one for static and one for dynamic input)
    1. **The Classifier**: 
      a. Analyzes data in real-time to classify it into noise, static gestures or dynamic movements
      b. Uses a 20-frame sliding window buffer to increase classification accuracy
      c. Mathematically calculates the movement type using a custom-made formula, based on wrist, palm, and finger movement, and returns the movement type
      d. Processes the data into the custom format needed for the model that will make the prediction, then passes it to receive the result
      e. Filters noise from gestures to reduce false predictions and cpu load
    2. **The Static Model**:
      a. Trained on 84 float array of vectors (21 mediapipe points x 2 coords x 2 hands)
      b. Takes the processed frame coordinates and returns a prediction using a random forest classifier
    3. **The Dynamic Model**:
      a. Takes the processed coordinates of 30 consecutive frames (30 arrays x 84 coordinates)
      b. Makes predictions using a random forest classifier trained on the dataset

- **Data Processing and Engineering**
  - Developed the normalization algorithms used to turn the raw mediapipe objects into a polished 1d array of [-1, 1] values representing the x and y coordinates of each point, achieved by making the wrist the (0, 0) point (the position of the hand on the screen does not affect the predictions) and by dividing each coordinate by the absolute maximum value (the scale or "closeness" to the screen doesnt matter)
  - Integrated 2-hand support by adding 0 padding to every input to integrate recognition across both models

- **Dynamic Data Acquisition & Retraining Sysytem**:
  - Built a full data acquisition and integration suite directly into the application, to allow custom gesture integration and pre-built gestures refinement
  - User selects what type of gesture they want to integrate (static or dynamic), the label for this new gesture, then records as many samples as needed (recommendation is 30)
  - Developed an automated retraining script, fully integrated in the ML lifecycle that ingests and processes the new data, then immediately swaps the models for the new ones

---

## Difficulties & Solutions

- **UI Freezing**: Running heavy computer vision tasks on the main thread made the GUI freeze/crash.
  - *Solution*: Moved the `Camera` class to a background thread, emitting `frame_captured` signals only when processing is complete.
- **Gesture Conflicts**: The "Left Click" gesture was often mistaken for cursor movement.
  - *Solution*: Changed the tracking point from the **index finger** to the **index knuckle**, therefore when pinching the index with the thumb, the **cursor** won't move.
- **Model inacuracy**: Predictions were wrong and accuracy was about 60%
  - *Solution*: Processed the data to eliminate discrepancies between the same gesture caused by physical distance or rotation of the hand, added noise filters, increased the training samples dataset

---

## Installation & Usage

**Requirements**:
- Python 3.10+
- `pip install -r requirements.txt`
- **Linux Users**: Must use an X11 session (Wayland is not supported).

**Run Instructions**:
- After creating the virtual environment and installing the requirements, clone the repository and do the following:
```bash
cd src
python main.py
```

---

## Repository

**GitHub**: [https://github.com/TrojiGareer/MIRA](https://github.com/TrojiGareer/MIRA)