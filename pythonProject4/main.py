import streamlit as st
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import boto3
import tempfile
from PIL import Image
from io import BytesIO

# AWS S3 Configuration
AWS_ACCESS_KEY = 'AKIAW3MEE26ZFEGENAFU'
AWS_SECRET_ACCESS_KEY = '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'
S3_BUCKET_NAME = 'envosafe1'
AWS_REGION_NAME = 'ap-southeast-2'

# Initialize Boto3 S3 client
s3 = boto3.client(service_name='s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION_NAME)


def upload_to_s3(file, user_id, filename):
    # Reset file pointer to the beginning
    file.seek(0)
    s3.upload_fileobj(file, S3_BUCKET_NAME, f"{user_id}/{filename}")
    return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id}/{filename}"


def download_from_s3(user_id, filename):
    _, temp_local_filename = tempfile.mkstemp()
    s3.download_file(S3_BUCKET_NAME, f"{user_id}/{filename}", temp_local_filename)
    return temp_local_filename


def compress_image(image, quality=85):
    output = BytesIO()
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img.save(output, format="JPEG", quality=quality)
    output.seek(0)
    return output


def rotate_image(image, angles=[0, 90, 180, 270]):
    rotated_images = []
    for angle in angles:
        if angle == 90:
            rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated_image = cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated_image = image
        rotated_images.append(rotated_image)
    return rotated_images


def compare_images(imageA, imageB):
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    score, diff = ssim(grayA, grayB, full=True)
    return score


def feature_based_comparison(imageA, imageB):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(imageA, None)
    kp2, des2 = orb.detectAndCompute(imageB, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches) / min(len(kp1), len(kp2))


# Streamlit App
st.title("Image Comparison")

# Hardcoding the user_id for testing purposes
user_id = 'test_user'

# Camera input for taking a photo
photo = st.camera_input("Take a photo")

if photo is not None:
    image = np.array(Image.open(photo))
    compressed_image_file = compress_image(image)
    photo_url = upload_to_s3(compressed_image_file, user_id, "uploaded_photo.jpg")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    existing_photos = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=f"{user_id}/")
    original = True

    if 'Contents' in existing_photos:
        for obj in existing_photos['Contents']:
            if obj['Key'] == f"{user_id}/uploaded_photo.jpg":
                continue  # Skip comparing the image with itself

            existing_photo_path = download_from_s3(user_id, obj['Key'].split('/')[-1])
            existing_image = cv2.imread(existing_photo_path)

            rotated_images = rotate_image(image)
            comparison_scores = []

            for rotated_image in rotated_images:
                min_height = min(rotated_image.shape[0], existing_image.shape[0])
                min_width = min(rotated_image.shape[1], existing_image.shape[1])
                rotated_image_resized = cv2.resize(rotated_image, (min_width, min_height))
                existing_image_resized = cv2.resize(existing_image, (min_width, min_height))

                score = compare_images(rotated_image_resized, existing_image_resized)
                comparison_scores.append(score)

            # Using feature-based comparison
            feature_score = feature_based_comparison(image, existing_image)
            comparison_scores.append(feature_score)

            if max(comparison_scores) > 0.45:
                st.write("The uploaded image is similar to an existing image.")
                original = False
                break

    if 'Contents' not in existing_photos or original:
        st.write("The uploaded image is original.")
    else:
        st.write("The uploaded image is not original.")
