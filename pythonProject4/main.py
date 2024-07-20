import cv2
import streamlit as st
from skimage.metrics import structural_similarity as ssim
import numpy as np


def compare_images(imageA, imageB):
    # Convert images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between two images
    score, diff = ssim(grayA, grayB, full=True)

    # The score is a value between -1 and 1, with 1 being a perfect match
    st.write(f"SSIM: {score}")

    # Threshold SSIM to decide if images are similar
    if score > 0.45:  # You can adjust this threshold based on your requirement
        st.write("The images are largely the same.")
    else:
        st.write("The images are different.")

    # Display the difference image
    diff = (diff * 255).astype("uint8")
    st.image(diff, caption="Difference Image")


st.title("Image Comparison using SSIM")

uploaded_file1 = st.file_uploader("Choose the first image", type=["jpg", "jpeg", "png"])
uploaded_file2 = st.file_uploader("Choose the second image", type=["jpg", "jpeg", "png"])

if uploaded_file1 is not None and uploaded_file2 is not None:
    image1 = np.array(cv2.imdecode(np.frombuffer(uploaded_file1.read(), np.uint8), cv2.IMREAD_COLOR))
    image2 = np.array(cv2.imdecode(np.frombuffer(uploaded_file2.read(), np.uint8), cv2.IMREAD_COLOR))

    # Ensure images are the same size
    min_height = min(image1.shape[0], image2.shape[0])
    min_width = min(image1.shape[1], image2.shape[1])
    image1 = cv2.resize(image1, (min_width, min_height))
    image2 = cv2.resize(image2, (min_width, min_height))

    compare_images(image1, image2)

    st.image([image1, image2], caption=["Image 1", "Image 2"], use_column_width=True)
