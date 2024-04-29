
# II-Industrial Vision Technology: Image Stitcher

## Description
This project is developed as part of the coursework for II-Industrial Vision Technology. It features an advanced image stitcher that uses state-of-the-art computer vision techniques for feature detection and extraction. The image stitcher is equipped with a user-friendly graphical user interface (GUI), enabling users to effortlessly stitch multiple images to produce a seamless high-resolution panorama.

## Features
- **Feature Detection**: Utilizes SIFT/ORB/AKAZE/BRISK for robust feature detection.
- **Feature Extraction**: Implements SIFT/ORB/AKAZE/BRISK to accurately extract relevant features from images.
- **Image Stitching**: Efficiently stitches multiple images by aligning and blending them seamlessly.
- **Graphical User Interface**: Simple and intuitive GUI for easy operation by users of all skill levels.

## Installation

### Prerequisites
- Python 3.x
- Please refer to `requirements.txt` for a list of required libraries.

### Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ahmadshakleya/FeatureExtraction.git
   ```
   
2. **Create a Virtual Environment**
   Navigate to the project directory and create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   Install the required libraries with pip:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

You have two options to run the application:

- **Using Python Script:**
  After installing dependencies, run the following command within the activated virtual environment:
  ```bash
  python gui.py
  ```

- **Using Executable:**
  If you don't have python installed, simply navigate to the directory containing `gui.exe` and run it:
  ```bash
  ./gui.exe
  ```

### Usage
1. Launch the application using one of the methods described above.
2. Use the GUI to upload the images you wish to stitch.
3. Adjust settings as necessary and click the 'Stitch Images' button.
4. Save or view the resulting panoramic image.

### Authors
- Ahmad Shakleya
- Ken Van Laer
- Toon Smets

### Acknowledgments
- Thanks to Prof. dr. Steve Vanlanduit for guidance and course materials.
- Gratitude to anyone whose code was used.
