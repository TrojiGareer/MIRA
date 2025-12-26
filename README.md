# M.I.R.A. - Motion Interpretation Remote Assistant

A program that reads hand signals and gestures by temporarily accessing the device's camera, with an intuitive GUI and a ML model that can be trained to learn more or perfect the already existing recognized signals.

## Features

Last update: 26/12/25
At this current time, the features of the app are:
+ gesture recognition mode
+ data collection mode
+ a model that trains itself on the new sets of data provided
+ intuitive GUI for a smooth UX

## Running the program
After cloning the project, creating the virtual environment and installing the dependancies, go to MIRA/src and run `python main.py`. Everything else can be done from buttons in the UI.

To manually retrain the model, after stopping everything, in MIRA/src run `python train.py`.

### Prediction mode
Run the app using the steps above, press 'Start M.I.R.A.' and put your hands in the device camera's view. To stop this, click on the same button, which now says 'Stop M.I.R.A.'.

### Data collection mode
Run the app using the steps above, press 'Start Data Collection', type the name of the sign or gesture you want to record, then press enter. Show the sign to the camera and when you are ready press enter, which will collect the data about your hand position in the current frame. Repeat this process, slightly changing your hand positioning each time, until a big enough dataset has been gathered (around 50-100 snaps should suffice). Taking these snaps in various locations with different lightings and heights will significantly help with prediction accuracy. When enough data has been gathered, press the button again to exit data collection mode.

Close the window to stop the project and manually retrain the model as instructed above, you'll see a message about your new model accuracy in the console. You can now test and use your new gesture when running MIRA again.