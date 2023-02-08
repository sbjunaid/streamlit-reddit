# Modules
import pyrebase
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
import base64
from streamlit_option_menu import option_menu
import os
from streamlit_cropper import st_cropper
import re

st.set_page_config(layout="wide")

# Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyA7Z8Os9zyEnPCh6U7Xxg0CAxM3tUiyPNY",
    'authDomain': "imagecomic-4b59f.firebaseapp.com",
    'databaseURL': "https://imagecomic-4b59f-default-rtdb.europe-west1.firebasedatabase.app",
    'projectId': "imagecomic-4b59f",
    'storageBucket': "imagecomic-4b59f.appspot.com",
    'messagingSenderId': "286944462712",
    'appId': "1:286944462712:web:c48a2494f5b04c22a66a8d",
    'measurementId': "G-0WSJM2P458"
}


# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
# if auth:
#     print("Firebase Connected")
# else:
#     print("Authentication Failed")

# Database
db = firebase.database()
storage = firebase.storage()

# Authentication
choice = st.sidebar.selectbox('login/Signup', ['--Select--','Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password', type='password')
st.sidebar.info("Password must be of Six or more letters.")
# App



def cartoonization(img, cartoon):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if cartoon == "Pencil Sketch":

        value = st.slider(
            'Tune the brightness of your sketch (the higher the value, the brighter your sketch)', 0.0, 300.0, 250.0)
        kernel = st.slider(
            'Tune the boldness of the edges of your sketch (the higher the value, the bolder the edges)', 1, 99, 25, step=2)

        gray_blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)

        cartoon = cv2.divide(gray, gray_blur, scale=value)

    if cartoon == "Detail Enhancement":

        smooth = st.slider(
            'Tune the smoothness level of the image (the higher the value, the smoother the image)', 3, 99, 5, step=2)
        kernel = st.slider(
            'Tune the sharpness of the image (the lower the value, the sharper it is)', 1, 21, 3, step=2)
        edge_preserve = st.slider(
            'Tune the color averaging effects (low: only similar colors will be smoothed, high: dissimilar color will be smoothed)', 0.0, 1.0, 0.5)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)

        color = cv2.detailEnhance(img, sigma_s=smooth, sigma_r=edge_preserve)
        cartoon = cv2.bitwise_and(color, color, mask=edges)

    if cartoon == "PencilEdges":

        kernel = st.slider(
            'Tune the sharpness of the sketch (the lower the value, the sharper it is)', 1, 99, 25, step=2)
        laplacian_filter = st.slider(
            'Tune the edge detection power (the higher the value, the more powerful it is)', 3, 9, 3, step=2)
        noise_reduction = st.slider(
            'Tune the noise effects of your sketch (the higher the value, the noisier it is)', 10, 255, 150)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.Laplacian(gray, -1, ksize=laplacian_filter)

        edges_inv = 255-edges

        dummy, cartoon = cv2.threshold(
            edges_inv, noise_reduction, 255, cv2.THRESH_BINARY)

    if cartoon == "Bilateral Filter":

        smooth = st.slider(
            'Tune the smoothness level of the image (the higher the value, the smoother the image)', 3, 99, 5, step=2)
        kernel = st.slider(
            'Tune the sharpness of the image (the lower the value, the sharper it is)', 1, 21, 3, step=2)
        edge_preserve = st.slider(
            'Tune the color averaging effects (low: only similar colors will be smoothed, high: dissimilar color will be smoothed)', 1, 100, 50)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)

        color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
    if cartoon == 'Gray Image':
        converted_img = np.array(image.convert('RGB'))
        cartoon = cv2.cvtColor(converted_img, cv2.COLOR_RGB2GRAY)
        
    if cartoon == 'Black and White':
        converted_img = np.array(image)
        gray_scale = cv2.cvtColor(converted_img, cv2.COLOR_RGB2GRAY)
        slider = st.slider('Adjust the intensity', 1, 255, 127, step=1)
        (thresh, blackAndWhiteImage) = cv2.threshold(gray_scale, slider, 255, cv2.THRESH_BINARY)
        cartoon =blackAndWhiteImage
        
        
    if cartoon == 'Blur Effect':
        converted_img = np.array(image)
        slider = st.slider('Adjust the intensity', 5, 81, 33, step=2)
        converted_img = cv2.cvtColor(converted_img, cv2.COLOR_RGB2BGR)
        blur_image = cv2.GaussianBlur(converted_img, (slider,slider), 0, 0)
        cartoon = blur_image 
        cartoon=cv2.cvtColor (cartoon,cv2.COLOR_RGB2BGR)
    return cartoon

def brighten_image(image, amount):
    img_bright = cv2.convertScaleAbs(image, beta=amount)
    return img_bright


def blur_image(image, amount):
    blur_img = cv2.GaussianBlur(image, (11, 11), amount)
    return blur_img


def enhance_details(img):
    hdr = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    return hdr

def get_image_download_link(img,filename,text):
    buffered = BytesIO()
    img.save(buffered, format="jpg")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href =  f'<a href="data:file/txt;base64,{img_str}" download="{filename}">{text}</a>'
    return href
if choice == '--Select--':
    st.title("Welcome to Comicmage ")
    st.header('Please Signup or Login')

# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input('Please input your name', value='Default')
    submit = st.sidebar.button('Create my account')
    e=1
    

    if submit:
        try:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if(re.fullmatch(regex, email)):
                print("Valid Email")
            else:
                st.warning("Invalid Email")
                e=0
            if len(password) >=6:
                print("valid Password")
            else:
                st.warning("Invalid Password")
                e=0
            user = auth.create_user_with_email_and_password(email, password)  
            st.success('Your account is created suceesfully!')
            st.balloons()
            # Sign in
            user = auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])
            st.title('Welcome ' + handle)
            st.info('Login via login drop down selection')
        except:
            if e==1:
                st.warning("Email is already in use.")
            

# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        e=1
        try:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if(re.fullmatch(regex, email)):
                print("Valid Email")
            else:
                st.warning("Invalid Email")
                e=0
            if len(password) >=6:
                print("valid Password")
            else:
                st.warning("Invalid Password")
                e=0
            user = auth.sign_in_with_email_and_password(email, password)
            # if user:
            #     print("Account is logged in")
            st.write(
                '<style>div.row-widget.stRadio > div{flex-direction:row;background-color: grey;text-transform: uppercase;}</style>', unsafe_allow_html=True)
            bio = option_menu(None, ['Home', 'ImageCartoon','Crop Image', 'Filter Image', 'Webcam', 'Comicmage Feeds', 'Settings'], icons=[
                              'NONE', 'NONE', 'NONE', 'NONE','NONE', 'NONE', 'NONE'], menu_icon="cast", default_index=0, orientation="horizontal")
            

    # SETTINGS PAGE
            if bio == 'Settings':  
                # CHECK FOR IMAGE
                nImage = db.child(user['localId']).child("Image").get().val()    
                # IMAGE FOUND     
                if nImage is not None:
                    # We plan to store all our image under the child image
                    Image = db.child(user['localId']).child("Image").get()
                    for img in Image.each():
                        img_choice = img.val()
                        #st.write(img_choice)
                    st.image(img_choice,width=150)
                    exp = st.expander('Change Bio and Image')  
                    # User plan to change profile picture  
                    with exp:
                        upload_new = st.file_uploader('Enter full path of your profile image')
                        # upload_new = st.button('Upload')
                        if upload_new:
                            uid = user['localId']
                            fireb_upload = storage.child(uid).put(upload_new,user['idToken'])
                            a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                            db.child(user['localId']).child("Image").push(a_imgdata_url)
                            st.success('Success!')       
                            # print("Profile successfully Updated.")
                # IF THERE IS NO IMAGE
                else:    
                    st.info("No profile picture yet")
                    upload_new = st.file_uploader('Enter full path of your profile image')
                    # upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        # Stored Initated Bucket in Firebase
                        fireb_upload = storage.child(uid).put(upload_new,user['idToken'])
                        # Get the url for easy access
                        a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                        # Put it in our real time database
                        db.child(user['localId']).child("Image").push(a_imgdata_url)
                        st.success('Success!')
                
    # ImageCartoon
            elif bio == "ImageCartoon":
                file = st.file_uploader("Please upload an image file", type=["jpg", "png"])
                if file is None:
                    st.text("You haven't uploaded an image file")
                else:
                    image = Image.open(file)
                    img = np.array(image)
                    color = cv2.bilateralFilter(img, 9, 9, 7)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    blur = cv2.medianBlur(gray, 7)
                    edges = cv2.adaptiveThreshold(blur, 255, cv2.
                                                ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
                    frame_edge = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                    cartoon = cv2.bitwise_and(color, frame_edge)
                    
                    col1,col2 = st.columns(2)
                    with col1:
                        st.image(img)
                    
                    with col2:
                        st.image(cartoon)
                        
                    col1,col2 = st.columns(2)
                    with col1:
                        imgname=st.text_input("Enter file name")
                        
                        
                    with col2:
                        st.write("Click Download")
                        im = Image.fromarray(cartoon)
                        im.save("Edge.png")
                        with open("Edge.png", "rb") as file:
                            btn = st.download_button(
                                label="Download Image",
                                data=file,
                                file_name=imgname+".png",
                                mime="image/png"
                                )
                    
                    if os.path.exists("Edge.png"):
                        os.remove("Edge.png")
                        print("Edge deleted successfully.")
                        
                    
                    
                            

    # EditImage
            elif bio == 'Filter Image':
                file = st.file_uploader("Please upload an image file", type=["jpg", "png"])
                if file is None:
                    st.text("You haven't uploaded an image file")
                else:
                    image = Image.open(file)
                    img = np.array(image)
                    option = st.selectbox('Which cartoon filters would you like to apply?', ('Gray Image','Pencil Sketch', 'Detail Enhancement', 'PencilEdges', 'Bilateral Filter','Black and White',  'Blur Effect'))
                    cartoon = cartoonization(img, option)
                    col1,col2 =st.columns(2)
                    with col1:
                        st.text("Your Original image")
                        st.image(image, use_column_width=True)
                    with col2:
                        st.text("Your Filtered image")
                        st.image(cartoon, use_column_width=True)
                        
                        
                    col1,col2 = st.columns(2)
                    with col1:
                        imgname=st.text_input("Enter file name")
                    
                    with col2:
                        st.write("Click Download")
                        
                        im = Image.fromarray(cartoon)
                        im.save("Edge.png")
                        with open("Edge.png", "rb") as file:
                            btn = st.download_button(
                                label="Download Image",
                                data=file,
                                file_name=imgname+".png",
                                mime="image/png"
                                )
                    
                    if os.path.exists("Edge.png"):
                        os.remove("Edge.png")
                        print("Edge deleted successfully.")
                    
                    
                        
    #Webcam
            elif bio=='Webcam':
                img_file_buffer = st.camera_input("Take a Photo")
                if img_file_buffer is not None:
                    # To read image file buffer with OpenCV:
                    st.subheader("Cartoonify Image")
                    bytes_data = img_file_buffer.getvalue()
                    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.
                                                            uint8), cv2.IMREAD_COLOR)
                    
                    color = cv2.bilateralFilter(cv2_img, 9, 9, 7)
                    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
                    blur = cv2.medianBlur(gray, 7)
                    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
                    frame_edge = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                    cartoon = cv2.bitwise_and(color, frame_edge)
                    cartoon=cv2.cvtColor (cartoon,cv2.COLOR_RGB2BGR)
                    
                    st.image(cartoon)
                    print(type(cartoon))
                    imgname=st.text_input("Enter file name")
            
                    im = Image.fromarray(cartoon)
                    im.save("Edge1.png")
                    with open("Edge1.png", "rb") as file:
                        btn = st.download_button(
                            label="Download Image",
                            data=file,
                            file_name=imgname+".png",
                            mime="image/png"
                            )
                        
                    if os.path.exists("Edge.png"):
                        os.remove("Edge.png")
                        print("Edge deleted successfully.")
            #crop
            elif bio == 'Crop Image':
                file = st.file_uploader("Please upload an image file", type=["jpg", "png"])
                if file is None:
                    st.text("You haven't uploaded an image file")
                else:
                    image = Image.open(file)
                    
                    col1,col2 = st.columns(2)
                    with col1:
                        st.subheader("Original Image")
                        c=st_cropper(image)
                        imgname=st.text_input("Enter file name")
                        c.save("Edge1.png")
                        st.write("Click Download")
                        with open("Edge1.png", "rb") as file:
                            btn = st.download_button(
                                label="Download Image",
                                data=file,
                                file_name=imgname+".png",
                                mime="image/png"
                                )
                            
                        if os.path.exists("Edge1.png"):
                            os.remove("Edge1.png")
                            print("Edge deleted successfully.")

                    with col2:
                        st.subheader("Cropped Image")
                        st.image(c)
                        
                        
                        
                        
            # HOME PAGE
            elif bio == 'Home':
                nImage = db.child(user['localId']).child("Image").get().val()
                if nImage is not None:
                    val = db.child(user['localId']).child("Image").get()
                    for img in val.each():
                        img_choice = img.val()
                    st.image(img_choice, width=150)
                else:
                    st.info("No profile picture yet. Go to Edit Profile and choose one!")
                    
                post = st.sidebar.text_input("Share Your Feedback!", max_chars=100)
                add_post = st.sidebar.button('Share your feedback')
                if add_post:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y")
                    tm_string = now.strftime("%H:%M:%S")
                    st.balloons()
                    post = {'Post': post,
                            'Date': dt_string,
                            'Time': tm_string}
                    results = db.child(user['localId']).child("Posts").push(post)
                    
                
                st.markdown('<h3 style="font-family:sans-serif;  font-size: 42px;">POSTS</h3>', unsafe_allow_html=True)
                all_posts = db.child(user['localId']).child("Posts").get()
                if all_posts.val() is not None:
                    for Posts in reversed(all_posts.each()):
                        st.markdown("---")
                        if "Post" in Posts.val():
                            col1,col2,col3 =st.columns(3)
                            with col1:
                                st.subheader((Posts.val())["Post"])
                            with col3:
                                st.caption((Posts.val())["Date"])
                                st.caption((Posts.val())["Time"])
                                
                    st.sidebar.markdown("---")
    # WORKPLACE FEED PAGE
            elif bio == "Comicmage Feeds":
                all_users = db.get()
                res = []
                # Store all the users handle name
                for users_handle in all_users.each():
                    k = users_handle.val()["Handle"]
                    res.append(k)
                # Total users
                nl = len(res)
                st.info('Total users here: ' + str(nl))

                # Allow the user to choose which other user he/she wants to see
                choice = st.selectbox('See Feedbacks of Users', res)
                push = st.button('Show Profile')

                # Show the choosen Profile
                if push:
                    for users_handle in all_users.each():
                        k = users_handle.val()["Handle"]
                        #
                        if k == choice:
                            lid = users_handle.val()["ID"]

                            handlename = db.child(lid).child("Handle").get().val()
                            
                            nImage = db.child(lid).child("Image").get().val()
                            if nImage is not None:
                                val = db.child(lid).child("Image").get()
                                for img in val.each():
                                    img_choice = img.val()
                                col1,col2 = st.columns(2)
                                with col1:
                                    
                                    
                                    st.markdown(f'<h1 style="font-family:sans-serif; color:Green; font-size: 42px;">{handlename}</h1>',unsafe_allow_html=True)
                                with col2:
                                    st.image(img_choice,width=150)
                            else:
                                st.info(
                                    "No profile picture yet. Go to Edit Profile and choose one!")

                            # All posts
                            all_posts = db.child(lid).child("Posts").get()
                            if all_posts.val() is not None:
                                st.markdown("---")
                                for Posts in reversed(all_posts.each()):
                                    if "Post" in Posts.val():
                                        col1,col2,col3 =st.columns(3)
                                        with col1:
                                            st.subheader((Posts.val())["Post"])
                                        with col3:
                                            st.caption((Posts.val())["Date"])
                                            st.caption((Posts.val())["Time"])
                                    st.markdown("---")
            

        except:
            if e==1:
                st.warning("Error")



hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)





all_users = db.get()
res = []
# Store all the users handle name
for users_handle in all_users.each():
    k = users_handle.val()["Handle"]
    res.append(k)
                # Total users
nl = len(res)
st.info('Total users here: ' + str(nl))
