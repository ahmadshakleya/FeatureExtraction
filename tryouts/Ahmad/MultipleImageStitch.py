import cv2
import os
import logging
from stitching import Stitcher

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def load_images(image_paths, scale=1.0):
    """
    Load and resize images from specified file paths.

    Parameters:
    - image_paths (list of str): List of file paths for the images to be loaded.
    - scale (float, optional): Scaling factor for resizing images, where 1.0 means no scaling.

    Returns:
    - list of np.array: List of images loaded and resized as per the scale factor.
    """
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

def stitch_images(images, stitcher_settings):
    """
    Stitch a list of images into a panorama using specified settings for the stitcher.

    Parameters:
    - images (list of np.array): List of images to stitch. Each image should be loaded as a NumPy array.
    - stitcher_settings (dict): Configuration settings for the Stitcher class, allowing for detailed customization of the stitching process. Possible settings include:
        - detector (str): Type of feature detector to use ('orb', 'sift', 'brisk', 'akaze'). Determines how features are detected in images.
        - nfeatures (int): Number of features to detect. Higher numbers can improve matching but affect performance.
        - matcher_type (str): Type of matcher ('homography', 'affine') to find correspondences between features.
        - range_width (int): Range width for matching features: higher values are more restrictive.
        - try_use_gpu (bool): Whether to try using GPU acceleration: can improve performance but may not be supported on all systems.
        - match_conf (float): Confidence setting for matching features: higher values are more restrictive.
        - confidence_threshold (float): Threshold for determining which matches to use, impacting the subset of images that proceed to stitching: higher values are more restrictive.
        - matches_graph_dot_file (str): File path to save the matches graph in DOT format, useful for debugging.
        - estimator (str): Type of camera estimator: 'homography' or 'affine'.
        - adjuster (str): Type of camera parameters adjuster: 'no', 'ray', 'affine' or 'reproj'.
        - refinement_mask (list of bool): Mask to define parameters to adjust during camera adjustment: 'xxxxx' for all, 'xxxxo' for all but the last.
        - wave_correct_kind (str): Type of wave correction to apply: 'horiz', 'vert', 'auto', 'no'.
        - warper_type (str): Type of warper to use for image warping: 'plane', 'cylindrical', 'spherical', 'fisheye', 'stereographic', 'compressedPlaneA2B1', 'compressedPlaneA1.5B1', 'compressedPlanePortraitA2B1', 'compressedPlanePortraitA1.5B1', 'paniniA2B1', 'paniniA1.5B1', 'paniniPortraitA2B1', 'paniniPortraitA1.5B1', 'mercator', 'transverseMercator'
        - low_megapix (float): Resolution for initial image resizing: higher values are more restrictive.
        - medium_megapix (float): Resolution for intermediate image resizing: higher values are more restrictive.
        - final_megapix (float): Resolution for final image output: higher values are more restrictive.
        - crop (bool): Whether to crop the result to the largest possible inner rectangle: can improve quality but may remove content.
        - blend (bool): Whether to blend the final result: can improve quality but may reduce speed.
        - compensator (str): Type of exposure compensator to use: 'no', 'gain', 'gain_blocks', 'channels', 'channels_blocks'.
        - nr_feeds (int): Number of feed images to exposure compensator: higher values can improve quality.
        - block_size (int): Block size for exposure compensation: higher values can improve quality.
        - finder (str): Type of seam finder used to determine the optimal cut between images.
        - blender_type (str): Type of blender used for combining images: 'multiband', 'feather', 'no'.
        - blend_strength (int): Strength of blending operation: higher values are more restrictive.
        - timelapse (bool): Whether to generate a timelapse instead of a static panorama: can improve visual quality.
        - timelapse_prefix (str): Prefix for output files if timelapse mode is enabled: useful for organizing timelapse frames.

    Returns:
    - np.array or None: The stitched panorama as an array, or None if stitching fails.

    Raises:
    - Exception: Captures and logs any exception that occurs during the stitching process, which could be related to feature detection, image alignment, or memory issues.
    """
    try:
        if stitcher_settings is None:
            stitcher_settings = {
                "detector": "sift",
                "nfeatures": 1000,
                "matcher_type": "homography",
                "confidence_threshold": 0.1,
                "try_use_gpu": True,
                "crop" : False,
            }
        stitcher = Stitcher(**stitcher_settings)
        panorama = stitcher.stitch(images)
        if panorama is not None:
            logging.info("Images stitched successfully")
            return panorama
        else:
            logging.error("Stitching failed to produce a panorama")
            return None
    except Exception as e:
        logging.error(f"Stitching failed: {e}")
        return None


def save_image(path, image, scale=1.0):
    """
    Save the provided image to a file, optionally resizing it.

    Parameters:
    - path (str): File path where the image will be saved.
    - image (np.array): Image data to save.
    - scale (float, optional): Scaling factor for resizing the image before saving.

    Returns:
    - None
    """
    try:
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
    except Exception as e:
        logging.error(f"Failed to save image {path}: {e}")

if __name__ == "__main__":
    folder_path = [os.path.join('images', filename) for filename in os.listdir('images')]
    logging.info("Starting to load images")
    images = load_images(folder_path, scale=0.75)

    logging.info("Starting to stitch images")
    stitcher_settings = {
        "detector": "sift",             # Detector type: 'orb', 'sift', etc.
        "nfeatures": 1000,              # Number of features to detect.
        "matcher_type": "homography",   # Matcher type: 'homography' or 'affine'.
        "confidence_threshold": 0.3,    # Confidence threshold for determining which matches to use.
        "try_use_gpu" : True
    }
    panorama = stitch_images(images, stitcher_settings)

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
