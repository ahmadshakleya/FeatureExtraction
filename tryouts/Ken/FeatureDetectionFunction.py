import cv2
import numpy as np
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Import FeatureDetector from the corresponding module
from stitching.feature_detector import FeatureDetector, StitchingError

def process_image_with_keypoints(pil_img, detector='orb', draw_keypoints=True, **detector_params):
    """Process an image with the specified feature detector and draw keypoints on it.
    
    Args:
        pil_img (PIL.Image): The input image as a PIL Image.
        detector (str): The feature detector to use. One of 'orb', 'sift', 'brisk', 'akaze'.
        draw_keypoints (bool): Whether to draw keypoints on the image.
        **detector_params: Additional parameters to pass to the feature detector.

    Returns:
        PIL.Image: The processed image as a PIL Image.
    """
    try:
        # Convert PIL Image to numpy array and handle BGR conversion
        img = np.array(pil_img)
        img = img[:, :, ::-1].copy()  # Convert RGB to BGR, as expected by OpenCV

        # Initialize the feature detector with the specified detector and parameters
        feature_detector = FeatureDetector(detector=detector, **detector_params)

        # Detect features
        features = feature_detector.detect_features(img)

        # Optionally draw keypoints on the image
        if draw_keypoints:
            img = feature_detector.draw_keypoints(img, features)

        # Convert the image back to RGB and return as PIL Image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)

    except StitchingError as e:
        logging.error("Stitching error: %s", e)
        return None
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return None

# Example usage:
# from PIL import Image

if __name__ == '__main__':
    pil_img = Image.open('.\\images\\1.jpg')
    processed_image = process_image_with_keypoints(pil_img, 'sift', nfeatures=1000, draw_keypoints=True)
    processed_image.show()
