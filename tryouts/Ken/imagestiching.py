import cv2
import numpy as np

def stitch_images(img1, img2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Create SIFT detector object
    sift = cv2.SIFT_create()

    # Detect keypoints and descriptors
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)

    # Create matcher object
    matcher = cv2.BFMatcher()

    # Match descriptors
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    # Filter matches using the Lowe's ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # Extract location of good matches
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Find homography
    H, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

    # Use homography
    height, width, channels = img1.shape
    img2_transformed = cv2.warpPerspective(img2, H, (width, height))

    # Combine images
    result = cv2.addWeighted(img1, 0.5, img2_transformed, 0.5, 0)

    return result

# Load images
image1 = cv2.imread('images/1.jpg')
image2 = cv2.imread('images/2.jpg')

# Stitch images
result = stitch_images(image1, image2)

# Save or show the result
cv2.imshow('Stitched Image', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
