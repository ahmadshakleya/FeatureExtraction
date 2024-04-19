import cv2
import os
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def load_images(image_paths, scale=1.0):
    """Load and resize images from given paths."""
    images = []
    for img_path in image_paths:
        img = cv2.imread(img_path)
        if img is not None:
            if scale != 1.0:
                width = int(img.shape[1] * scale)
                height = int(img.shape[0] * scale)
                dim = (width, height)
                resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                images.append(resized_img)
                logging.info(f"Resized and loaded {img_path}")
            else:
                images.append(img)
                logging.info(f"Loaded {img_path}")
        else:
            logging.warning(f"Failed to load image: {img_path}")
    return images

def stitch_images(images):
    """Stitch a list of images into a panorama with adjusted settings."""
    stitcher = cv2.Stitcher_create()
    stitcher.setPanoConfidenceThresh(0.5)  # Lower this threshold if needed
    status, stitched = stitcher.stitch(images)
    if status != cv2.Stitcher_OK:
        logging.error(f"Can't stitch images, error code = {status}")
        return None
    logging.info("Images stitched successfully")
    return stitched

def save_image(path, image, scale=1.0):
    """Save the stitched image to the specified path, optionally resizing it."""
    if scale != 1.0:
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        dim = (width, height)
        resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        cv2.imwrite(path, resized_image)
        logging.info(f"Saved resized image to {path}")
    else:
        cv2.imwrite(path, image)
        logging.info(f"Saved image to {path}")

if __name__ == "__main__":
    folder_path = []
    for filename in os.listdir('images'):
        folder_path.append(f'./images/{filename}')
    logging.info("Starting to load images")
    images = load_images(folder_path, scale=0.75)

    logging.info("Starting to stitch images")
    panorama = stitch_images(images)

    if panorama is not None:
        final_scale_factor = 1.0
        save_image('panorama.jpg', panorama, scale=final_scale_factor)
        logging.info("Panorama saved as 'panorama.jpg'")
        displayed_image = cv2.imread('panorama.jpg')
        cv2.imshow('Panorama', displayed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        logging.error("Failed to create panorama")
