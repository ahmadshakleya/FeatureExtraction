import cv2
from stitching.feature_detector import FeatureDetector

finder = FeatureDetector(detector='orb', nfeatures=500)

img = cv2.imread('.\\images\\1.jpg')

features = finder.detect_features(img)
keypoints_center_img = finder.draw_keypoints(img, features)

# Display the result
cv2.imshow('Image with keypoints', keypoints_center_img)
cv2.waitKey(0)
cv2.destroyAllWindows()