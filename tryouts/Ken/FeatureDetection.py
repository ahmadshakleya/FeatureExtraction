import cv2

# Load an image
image = cv2.imread(r'C:\Users\kenva\PycharmProjects\FeatureExtraction\images\1.jpg')

# Convert the image to grayscale (feature detection usually works on grayscale images)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Initialize a feature detector (for example, using ORB)
orb = cv2.ORB_create()

# Detect keypoints and compute descriptors
keypoints, descriptors = orb.detectAndCompute(gray, None)

# Draw keypoints on the original image
image_with_keypoints = cv2.drawKeypoints(image, keypoints, None)

# Display the result
cv2.imshow('Image with keypoints', image_with_keypoints)
cv2.waitKey(0)
cv2.destroyAllWindows()