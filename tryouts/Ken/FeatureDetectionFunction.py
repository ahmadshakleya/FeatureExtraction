import cv2
import numpy as np
from PIL import Image

def process_image_with_keypoints(pil_img, draw_keypoints=True):
    img = np.array(pil_img)  # Convert PIL Image to numpy array
    img = img[:, :, ::-1].copy()  # Convert RGB to BGR, which OpenCV expects

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if draw_keypoints:
        img = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DrawMatchesFlags_DRAW_RICH_KEYPOINTS)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert back to RGB
    return Image.fromarray(img)



# Example usage:
# image = cv2.imread(r'C:\Users\kenva\PycharmProjects\FeatureExtraction\images\1.jpg')
# process_image_and_display_keypoints(image)