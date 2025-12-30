
def zero_wrist(hand_landmarks):
    """
    Makes the wrist the reference point for the hand, so the positioning of the hand doesn't affect the prediction

    :param hand_landmarks: mediapipe hand landmarks

    :return new_landmarks: list of translated landmarks with wrist at (0,0)
    """

    wrist_x = hand_landmarks.landmark[0].x
    wrist_y = hand_landmarks.landmark[0].y

    new_landmarks = []

    # Here, a landmark is a mediapipe Landmark object with x and y attributes
    for curr_landmark in hand_landmarks.landmark:
        new_landmark_x = curr_landmark.x - wrist_x
        new_landmark_y = curr_landmark.y - wrist_y

        new_landmarks.append([new_landmark_x, new_landmark_y])

    return new_landmarks


def normalize_size(landmarks):
    """
    Normalize point values to be between -1 and 1, so the distance between the hand and the camera doesn't affect the
    prediction

    :param landmarks: list of translated landmarks with wrist at (0,0) (list of [x,y] points).

    :return result: flattened list of normalized x and y values
    """

    # find absolute max
    max_abs_val = 0
    result = []

    # Here, a landmark is a [x,y] list of coordinates => landmark[0] is x, landmark[1] is y
    for landmark in landmarks:
        if (abs(landmark[0]) > max_abs_val):
            max_abs_val = abs(landmark[0])
        if (abs(landmark[1]) > max_abs_val):
            max_abs_val = abs(landmark[1])

    if max_abs_val == 0:
        max_abs_val = 1

    for landmark in landmarks:
        result.append(landmark[0] / max_abs_val) # normalize x
        result.append(landmark[1] / max_abs_val) # normalize y

    return result

def process_landmarks(hand_landmarks):
    """
    Preprocess the hand landmarks before feeding them to the classifier

    :param hand_landmarks: mediapipe hand landmarks

    :return processed_landmarks: a vector of 42 integers (21 points * x,y coordinates) representing the processed
    coordinates of each point of a hand
    """

    landmarks = zero_wrist(hand_landmarks)
    processed_landmarks = normalize_size(landmarks)
    return processed_landmarks

def process_dataset(results):
    """
    Allow processing for either or both hands of a frame. Pads out the missing hand(s) with zeros.
    
    :param results: mediapipe results object from a frame

    :return final_vector: a vector of 84 integers (2 hands * 21 points * x,y coordinates) representing the processed
    coordinates of each point of both hands in a frame
    """
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
