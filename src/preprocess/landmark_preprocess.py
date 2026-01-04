# have the wrist be the starting point, so the different positioning of the hand doesnt affect the prediction
# takes the 42 raw mediapipe coordinates (each for each point) and subtracts the wrist to make it the reference point (0,0)

def zero_wrist(hand_landmarks):
    wrist_x = hand_landmarks.landmark[0].x
    wrist_y = hand_landmarks.landmark[0].y

    new_landmarks = []

    for crt_lm in hand_landmarks.landmark:
        new_landmark_x = crt_lm.x - wrist_x
        new_landmark_y = crt_lm.y - wrist_y

        new_landmarks.append([new_landmark_x, new_landmark_y])

    return new_landmarks

# normalize all point values to be between -1 and 1, so the distance between the hand and the camera doesnt interfere
# pick the maximum absolute value of the points and use that as one, dividing everything by that

def normalize_size(landmarks):
    # find absolute max
    max_val = 0
    result = []
    for lm in landmarks:
        if (abs(lm[0]) > max_val):
            max_val = abs(lm[0])
        if (abs(lm[1]) > max_val):
            max_val = abs(lm[1])
    if max_val == 0:
        max_val = 1
    for lm in landmarks:
        result.append(lm[0] / max_val)
        result.append(lm[1] / max_val)

    return result

# this will be called to ensure all the operations are done on the dataset before storing
# returns a vector of 42 integers representing the processed x and y values of each point

def process_landmarks(hand_landmarks):
    landmarks = zero_wrist(hand_landmarks)
    processed_landmarks = normalize_size(landmarks)
    return processed_landmarks

# allow processing for either or both of the hands as input in a frame
# zeros out the missing hand(s)

def process_dataset(results):
    result = []
    left_hand_data = [0.0] * 42
    right_hand_data = [0.0] * 42

    if results.multi_hand_landmarks:
        for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            crt_label = handedness.classification[0].label
            flat_coords = process_landmarks(landmarks)
            if crt_label == "Right":
                left_hand_data = flat_coords
            else:
                right_hand_data = flat_coords

    final_vector = left_hand_data + right_hand_data
    return final_vector
                
