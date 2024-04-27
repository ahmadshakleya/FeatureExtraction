import cv2 as cv
import numpy as np
import logging
from PIL import Image
from stitching.feature_matcher import FeatureMatcher
# Import FeatureDetector from the corresponding module
from stitching.feature_detector import FeatureDetector, StitchingError

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process_and_display_matches(imgs, feature_sets, matcher_type='homography', conf_thresh=0.3, draw_matches=True, **matcher_params):
    try:
        # Initialize the FeatureMatcher with the specified type and parameters
        matcher = FeatureMatcher(matcher_type=matcher_type, **matcher_params)
        
        # Match features across images
        matches = matcher.match_features(feature_sets)
        
        if draw_matches:
            result_images = []
            # Draw matches and yield results for visualization
            for idx1, idx2, match_img in FeatureMatcher.draw_matches_matrix(imgs, feature_sets, matches, conf_thresh):
                result_images.append(match_img)
                logging.info(f"Match between image {idx1} and image {idx2} drawn successfully.")
            return result_images
        else:
            return matches

    except Exception as e:
        logging.error("Failed to process and display matches: %s", e)
        return None

# Example usage:
if __name__ == '__main__':
    images = [cv.imread('.//images//1.jpg'), cv.imread('.//images//2.jpg')]
    feature_detector = FeatureDetector(detector='sift', nfeatures=1000)
    feature_sets = [feature_detector.detect_features(img) for img in images] # Assuming feature_detector is defined
    matched_images = process_and_display_matches(images, feature_sets, 'affine', 0.5)
    for img in matched_images:
        cv.imshow('Matched Image', img)
        cv.waitKey(0)
    cv.destroyAllWindows()
