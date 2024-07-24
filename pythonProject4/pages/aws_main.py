import streamlit as st
import numpy as np
from skimage.metrics import structural_similarity as ssim
import boto3
from PIL import Image, ImageOps
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
    file.seek(0)
    s3.upload_fileobj(file, S3_BUCKET_NAME, f"{user_id}/{filename}")
    return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{user_id}/{filename}"

def download_from_s3(user_id, filename):
    file_obj = BytesIO()
    s3.download_fileobj(S3_BUCKET_NAME, f"{user_id}/{filename}", file_obj)
    file_obj.seek(0)
    return file_obj

def compress_image(image, quality=85):
    output = BytesIO()
    img = Image.fromarray(np.array(image))
    img.save(output, format="JPEG", quality=quality)
    output.seek(0)
    return output

def rotate_image(image, angles=[0, 90, 180, 270]):
    rotated_images = []
    for angle in angles:
        rotated_image = image.rotate(angle)
        rotated_images.append(rotated_image)
    return rotated_images

def compare_images(imageA, imageB):
    grayA = ImageOps.grayscale(imageA)
    grayB = ImageOps.grayscale(imageB)
    grayA = np.array(grayA)
    grayB = np.array(grayB)
    score, _ = ssim(grayA, grayB, full=True)
    return score

# Streamlit App
st.title("Image Comparison")

# Hardcoding the user_id for testing purposes
user_id = 'test_user'

# Camera input for taking a photo
photo = st.camera_input("Take a photo")

if photo is not None:
    image = Image.open(photo)
    compressed_image_file = compress_image(image)
    photo_url = upload_to_s3(compressed_image_file, user_id, "uploaded_photo.jpg")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    existing_photos = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=f"{user_id}/")
    original = True

    if 'Contents' in existing_photos:
        for obj in existing_photos['Contents']:
            if obj['Key'] == f"{user_id}/uploaded_photo.jpg":
                continue  # Skip comparing the image with itself

            existing_photo_file = download_from_s3(user_id, obj['Key'].split('/')[-1])
            existing_image = Image.open(existing_photo_file)

            rotated_images = rotate_image(image)
            comparison_scores = []

            for rotated_image in rotated_images:
                min_height = min(rotated_image.height, existing_image.height)
                min_width = min(rotated_image.width, existing_image.width)
                rotated_image_resized = rotated_image.resize((min_width, min_height))
                existing_image_resized = existing_image.resize((min_width, min_height))

                score = compare_images(rotated_image_resized, existing_image_resized)
                comparison_scores.append(score)

            if max(comparison_scores) > 0.45:
                st.write("The uploaded image is similar to an existing image.")
                original = False
                break

    if 'Contents' not in existing_photos or original:
        st.write("The uploaded image is original.")
    else:
        st.write("The uploaded image is not original.")