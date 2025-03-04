import os
import json
import numpy as np
import tensorflow as tf
import streamlit as st
from PIL import Image
import io
import base64
import piexif
import pydeck as pdk
import mysql.connector
from mysql.connector import Error

# Custom CSS with nature-inspired green shades and white space 
custom_css = """
<style>
    .stApp {
      
           background: linear-gradient(to right, rgba(52, 152, 219, 0.3), rgba(46, 204, 113, 0.7), rgba(230, 126, 34, 0.4)); /* Gradient with reduced opacity */
            color: #000000 ;
    }
    .title {
        color: #1B5E20; /* Dark forest green for titles */
        font-size: 40px;
        text-align: center;
        margin-bottom: 20px;
    }
        .text {
        color: #FFFFFF; /* Medium green for text */
        font-size: 18px;
    }
    .footer {
        background-color: #A5D6A7; /* Pale green footer */
        padding: 10px;
        text-align: center;
        border-radius: 10px;
        margin-top: 20px;
    }
    .btn-green {
        background-color: #76FF03; /* Vibrant lime green for buttons */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px; /* Curved rectangular button */
        font-size: 16px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); /* Drop shadow */
    }
</style>
"""
# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)


# Load the pre-trained model
working_dir = os.path.dirname(os.path.abspath(__file__))
model_path = f"{working_dir}/plant_disease_prediction_model.h5"
model = tf.keras.models.load_model(model_path)

# Load the class names
class_indices1 = json.load(open(f"{working_dir}/class_indices.json", encoding='utf-8'))

# Function to establish connection to MySQL database
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host='sql12.freesqldatabase.com',
            database='sql12732889',
            user='sql12732889',
            password='ICHNYsEvLz',
            port=3306
        )
        if conn.is_connected():
            return conn
    except Error as e:
        st.error(f"Error: {e}")
        return None
    
# Function to insert data into MySQL table
def insert_data(lat, long, prediction, notes=None):
    try:
        conn = connect_to_mysql()
        if conn:
            cursor = conn.cursor()
            insert_query = """INSERT INTO herbify (Lat, Long1, Prediction, Notes) VALUES (%s, %s, %s, %s)"""
            cursor.execute(insert_query, (lat, long, prediction, notes))
            conn.commit()
            st.success("Data inserted successfully")
            cursor.close()
            conn.close()
    except Error as e:
        st.error(f"Error: {e}")    


# Function to extract geolocation from EXIF data
def get_geolocation(exif_data):
    gps_info = exif_data.get('GPS', {})
    if not gps_info:
        return None

    def convert_to_degrees(value):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    gps_latitude = gps_info.get(piexif.GPSIFD.GPSLatitude)
    gps_latitude_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
    gps_longitude = gps_info.get(piexif.GPSIFD.GPSLongitude)
    gps_longitude_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != b'N':
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != b'E':
            lon = -lon

        return lat, lon
    return None

# Function to Load and Preprocess the Image using Pillow
def load_and_preprocess_image(image):
    img = Image.open(image)
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array.astype('float32') / 255.
    return img_array

# Function to Predict the Class of an Image
def predict_image_class(model, image):
    preprocessed_img = load_and_preprocess_image(image)
    predictions = model.predict(preprocessed_img)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_class_name = class_indices1[str(predicted_class_index)]
    return predicted_class_name

# Sidebar
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Leaves Recognition"])

# Main Page
if app_mode == "Home":
    image = Image.open("LG.png")  # Ensure the path is correct
    resized_img = image.resize((100, 100))

    # Convert the resized image to a base64 string
    buffered = io.BytesIO()
    resized_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Use HTML to display the title and the image
    st.markdown(
       f'''
    <div style="width: 800px; margin: 0 auto; display: flex; align-items: center;">
        <h1 class="title" style="margin: 0; padding-right: 0;">PLANT LEAF RECOGNITION SYSTEM</h1>
        <img src="data:image/png;base64,{img_str}" width="100" height="100" style="display: block;">
        
    </div>
    ''',
    unsafe_allow_html=True)
        
    st.image("BGNL.png", use_column_width=True)
    
    st.markdown("""
    <h3 style="text-align:lefft; color: #013a61; padding: 10px; margin: 0;">
        Welcome to the Plant Leaf Recognition System! 🌿🔍
    </h3>
    
    <h6>Our mission is to help in identifying plant leaf efficiently. Upload an image of a plant, and our system will analyze it to detect any signs of leaves. Together, let's identify the medical leaves of plants!</h6>

    <h3 style="text-align:left; color: #013a61; padding: 10px; margin: 0;">
        How It Works
    </h3>
    <ol>
    <li><strong>Upload Your Image:</strong> Head to the <em>Leaf Upload</em> section and share a photo of the plant leaf.</li>
    <li><strong>Smart Analysis:</strong> Our advanced algorithms will process the image to accurately identify the medicinal plant's name.</li>
    <li><strong>View Results:</strong> Check out the findings and receive personalized recommendations.</li>
    </ol>

    <h3 style="text-align: left; color: #013a61; padding: 10px; margin: 0;">
        Why Trusting Us?
    </h3>
    <ul>
    <li><strong>Rapid Results:</strong> Get your results in seconds for quick decision-making.</li>
    <li><strong>Intuitive Design:</strong> Enjoy a seamless experience with our user-friendly interface.</li>
    <li><strong>Precision:</strong> We use cutting-edge machine learning techniques for accurate plant identification.</li>
    </ul>
    
    <h3 style="text-align: left; color: #013a61; padding: 10px; margin: 0;">
        Start Exploring
    </h3>
    <p>Click on the**Plant Leaf Recognition**page in the sidebar to upload an image and experience the power of our Plant Leaf Name Recognition System!</p>
        <marquee> <h5>Like the medicinal herb striking the foot of him who is seeking it !</h5>
         "தேடப்போன மருந்து, காலிலே தட்டினதுபோல "</marquee>


   <h3 style="text-align: left; color: #013a61; padding: 10px; margin: 0;">
        Discover Our Story
    </h3>
     
    <p>Learn about our project, meet our team, and understand our goals on the Our About page.</p>
    



    """, unsafe_allow_html=True)






# About Project
elif app_mode == "About":
    st.header("About Us")
    #st.markdown("#### About Dataset\nThis dataset is recreated using offline augmentation from the original dataset.")
    st.markdown(
    '''
    <h3 style="color: #013a61;">Herbify - Herbal Plant Identification System</h3>
    <p>Herbify is an innovative platform designed to identify medicinal plants using advanced image recognition and machine learning. Our goal is to blend nature and technology, offering accurate plant identification while ensuring authenticity in the herbal supply chain.</p>
    
    <h3 style="color: #013a61;">Our Mission</h3>
    <p>We simplify plant identification, making it accessible and reliable, empowering individuals to make informed choices for health and sustainability.</p>
    <blockquote>"The greatest wealth is health." – Virgil</blockquote>
    
    <h3 style="color: #013a61;">Key Features</h3>
    <ul>
        <li><strong>AI-Powered Plant Identification:</strong> Upload a plant image, and our AI-driven system quickly identifies the plant and its medicinal benefits, powered by Convolutional Neural Networks (CNN).</li>
        <li><strong>Interactive Map:</strong> Discover nearby locations offering identified medicinal plants using our integrated map, powered by Pydeck.</li>
        <li><strong>User-Friendly Interface:</strong> Designed with Streamlit for an intuitive, seamless user experience.</li>
    </ul>
    <blockquote>"Look deep into nature, and then you will understand everything better." – Albert Einstein</blockquote>
    <center><p>-----------------------------------------------------------------------------------------------------------------</p></center>
    <h3 style="color: #013a61;">Our Journey</h3>
    ''', unsafe_allow_html=True
    )
    
    st.image("group.jpg", use_column_width=True)
    
    st.markdown(
    '''
    <p>We honed Herbify through field trips to <b>Tamil Nadu Agricultural College Madurai, Aravindh Ayush Herbal Farm, Bee & Honey Factory<b>, and collaborations with local Botanical ,live stock & other entrepreneurs. These experiences, combined with training in <b>TLC (Thin Layer Chromatography) , Herbal Identification and Water-Soluble Ash methods<b>, provided us with key insights into herbal authenticity and quality control.</p>
    <blockquote>"Tell me and I forget. Teach me and I remember. Involve me and I learn." – Benjamin Franklin</blockquote>
    
    <h3 style="color: #013a61;">Technology</h3>
    <ul>
        <li>TensorFlow for plant identification models.</li>
        <li>NumPy for efficient data handling.</li>
        <li>Piexif for image metadata processing.</li>
        <li>Pydeck for interactive mapping features.</li>
        <li>Streamlit for a smooth user interface.</li>
    </ul>
    
    <h3 style="color: #013a61;">Recognition</h3>
    <p>Herbify was awarded Best Innovative Project at K.L.N College of Engineering. Additionally, we were shortlisted in the Tamil Nadu Niral Thiruvizha event, placing among the top 150 teams out of 1,000 for our unique combination of plant identification and real-time product mapping.</p>
    <blockquote>"Innovation is seeing what everybody has seen and thinking what nobody has thought." – Albert Szent-Györgyi</blockquote>
    ''',
    unsafe_allow_html=True)












# Prediction Page
elif app_mode == "Leaves Recognition":
    st.title('PLANT LEAF RECOGNITION SYSTEM')
    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        try:
            predicted_class = predict_image_class(model, uploaded_image)
            st.success(f'Prediction: {predicted_class}')

            image = Image.open(uploaded_image)
            resized_img = image.resize((450, 450))
            st.image(resized_img)

            exif_data = {}
            if "exif" in image.info:
                exif_data = piexif.load(image.info["exif"])
            geo_coordinates = get_geolocation(exif_data)

            if geo_coordinates:
                lat, lon = geo_coordinates
                st.write("### Geolocation Coordinates:")
                st.write(f"**Latitude**: {lat}, **Longitude**: {lon}")

                # Automatically save data to MySQL
                insert_data(lat, lon, predicted_class)

                view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=13)
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=[{"position": [lon, lat], "text": "Uploaded Image"}],
                    get_position="position",
                    get_radius=100,
                    get_fill_color=[255, 0, 0],
                    pickable=True
                )

                st.pydeck_chart(pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=view_state,
                    layers=[layer]
                ))
            else:
                st.write("### No geolocation data found in the image.")
                lat = st.number_input("Enter Latitude:", format="%.13f")
                lon = st.number_input("Enter Longitude:", format="%.13f")
                if st.button("Show Map"):
                    if lat and lon:
                        view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=13)
                        layer = pdk.Layer(
                            "ScatterplotLayer",
                            data=[{"position": [lon, lat], "text": "Manually Entered Coordinates"}],
                            get_position="position",
                            get_radius=100,
                            get_fill_color=[255, 0, 0],
                            pickable=True
                        )

                        st.pydeck_chart(pdk.Deck(
                            map_style="mapbox://styles/mapbox/light-v9",
                            initial_view_state=view_state,
                            layers=[layer]
                        ))
                    else:
                        st.error("Please enter valid coordinates.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
# Additional notes input
st.markdown("""
    <h4 style="color: #013a61;   
               padding: 10px;">
        Connect With Us
        </h4>
    """, unsafe_allow_html=True)

notes = st.text_area("")
if notes and st.button("Save Notes"):
    st.write("### Notes:")
    st.write(notes)
    if notes:
        insert_data(lat, lon, predicted_class, notes)  # Save notes along with other data
        st.success("Notes saved successfully.")



st.markdown(
    '''
    <marquee direction="right">
        <h1>🍂</h1>
    </marquee>
    ''',
    unsafe_allow_html=True
)

