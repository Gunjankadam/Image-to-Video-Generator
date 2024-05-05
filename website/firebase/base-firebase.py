import pyrebase

config ={
    "apiKey": "AIzaSyCpIxSXnDDd0woyZvSsMQrVbzclLcXQM28",
    "authDomain": "alumini8-3fd16.firebaseapp.com",
    "databaseURL": "https://alumini8-3fd16-default-rtdb.firebaseio.com",
    "projectId": "alumini8-3fd16",
    "storageBucket": "alumini8-3fd16.appspot.com",
    "messagingSenderId": "662379845396",
    "appId": "1:662379845396:web:95a001d7233827e3d89401",
    "measurementId": "G-H8ERJ8QPFG"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
path_on_cloud = "images/first.jpg"
path_local = "C:/Users/Gunjan/Desktop/minor-pro/website/firebase/bro.jpg"
#upload
storage.child(path_on_cloud).put(path_local)
#download
storage.download(path_on_cloud,"test.jpg")