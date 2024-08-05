import streamlit as st
from PIL import Image 
from streamlit_image_coordinates import streamlit_image_coordinates as im_coordinates 
from streamlit_dimensions import st_dimensions
import os
import cv2 
import requests
import base64
import numpy as np 

st.set_page_config(layout='wide')

def set_background(image_file):

    with open(image_file, "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)


api_endpoint = 'https://haileyesusbeyene.app.modelbit.com/v1/background_removal/latest'

st.subheader('Automatic background removal')

col01, col02 = st.columns(2)

file = col01.file_uploader('', type = ['jpeg', 'png', 'jpg'])

if file is not None: 
    image = Image.open(file).convert('RGB')

    image = image.resize((352, int(image.height*352/image.width)))

    col1, col2 = col01.columns(2)
    placeholder0 = col02.empty()
    

    with placeholder0: 
        value = im_coordinates(image)
        if value is not None:
           print(value)

    if col1.button('original', use_container_width=True): 
        placeholder0.empty()
        placeholder1 = col01.empty()
        with placeholder1: 
            col02.image(image, use_column_width=True)

    if col2.button('remove background', type ='primary', use_container_width=True):
        placeholder0.empty()
        placeholder2 = col02.empty()
        
        if value is not None:
           filename = '{}_{}_{}.png'.format(file.name, value['x'], value['y'])

        if os.path.exists(filename):
            result_image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        else:
            _, image_bytes = cv2.imencode('.png', np.asarray(image))

            image_bytes = image_bytes.tobytes()

            image_bytes_encoded_base64 = base64.b64encode(image_bytes).decode('utf-8')

            api_data = {"data": [image_bytes_encoded_base64, value['x'], value['y']]}
            response = requests.post(api_endpoint, json=api_data)

            result_image = response.json()['data']

            result_image_bytes = base64.b64decode(result_image)

            result_image = cv2.imdecode(np.frombuffer(result_image_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

            cv2.imwrite(filename, cv2.cvtColor(result_image, cv2.COLOR_BGRA2RGBA))

        with placeholder2:
            col02.image(result_image, use_column_width=True)