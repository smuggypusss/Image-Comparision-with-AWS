import streamlit as st
from exif import Image
from geopy.geocoders import Nominatim


def get_exif_coordinates(image_path):
    with open(image_path, 'rb') as img_file:
        img = Image(img_file)
        if img.has_exif:
            try:
                lat = img.gps_latitude
                lon = img.gps_longitude
                lat_ref = img.gps_latitude_ref
                lon_ref = img.gps_longitude_ref

                latitude = lat[0] + lat[1] / 60 + lat[2] / 3600
                longitude = lon[0] + lon[1] / 60 + lon[2] / 3600

                if lat_ref != 'N':
                    latitude = -latitude
                if lon_ref != 'E':
                    longitude = -longitude

                return (latitude, longitude)
            except AttributeError:
                return None
        else:
            return None


st.title("Photo Capture and Geographical Coordinates")

# Capture photo
picture = st.camera_input("Take a picture")

if picture:
    st.image(picture, caption="Captured Image")

    # Save the image to a file
    with open("captured_image.jpg", "wb") as f:
        f.write(picture.getbuffer())

    # Get coordinates from the image's EXIF data
    coordinates = get_exif_coordinates("captured_image.jpg")
    if coordinates:
        st.write(f"Latitude: {coordinates[0]}")
        st.write(f"Longitude: {coordinates[1]}")
    else:
        st.warning("No GPS data found in the image EXIF data.")
else:
    st.warning("No image captured. Please enable the camera and try again.")
