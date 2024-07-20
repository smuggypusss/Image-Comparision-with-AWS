import cv2
import streamlit as st
from skimage.metrics import structural_similarity as ssim

import numpy as np

def compare_images(imageA, imageB):
    # Convert images to grayscale
    image1 = cv2.imread(image_path1)
    image2 = cv2.imread(image_path2)
    image1 = cv2.resize(image1, (min(image1.shape[1], image2.shape[1]), min(image1.shape[0], image2.shape[0])))
    image2 = cv2.resize(image2, (min(image1.shape[1], image2.shape[1]), min(image1.shape[0], image2.shape[0])))
    grayA = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between two images
    score, diff = ssim(grayA, grayB, full=True)

    # The score is a value between -1 and 1, with 1 being a perfect match
    print(f"SSIM: {score}")

    # Threshold SSIM to decide if images are similar
    if score > 0.45:  # You can adjust this threshold based on your requirement
       st.write("The images are largely the same.")
    else:
        st.write("The images are different.")

    # Display the difference image
    diff = (diff * 255).astype("uint8")
    cv2.imshow("Difference", diff)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    # Load the two input images
image_path1 = "C:/Users/Asus/OneDrive/Pictures/Saved Pictures/PXL_20240716_182304878.jpg"
image_path2 = "C:/Users/Asus/OneDrive/Pictures/Saved Pictures/PXL_20240716_182316457.jpg"

    # Compare the images
compare_images(image_path1, image_path2)
st.image(["C:/Users/Asus/OneDrive/Pictures/Saved Pictures/PXL_20240716_182304878.jpg"],["C:/Users/Asus/OneDrive/Pictures/Saved Pictures/PXL_20240716_182316457.jpg"])