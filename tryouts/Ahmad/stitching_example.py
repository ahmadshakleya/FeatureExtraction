import cv2
from stitching import Stitcher
stitcher = Stitcher(detector="sift", confidence_threshold=0.2)

# Stitch the images together to create a panorama
result = stitcher.stitch(["./images/?.jpg"])

# Resize the result to make it smaller and fit the window
scale_percent = 50
width = int(result.shape[1] * scale_percent / 100)
height = int(result.shape[0] * scale_percent / 100)
dim = (width, height)
result = cv2.resize(result, dim, interpolation=cv2.INTER_AREA)




cv2.imshow('Result', result)

cv2.waitKey(0)
cv2.destroyAllWindows()
