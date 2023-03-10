# face_detection
## about the project:
The described tool is a real-time face detection hobby tool that utilizes threading for concurrent model training and face detection. The tool performs face detection in real-time by utilizing a non-blocking approach for the detection process. The trained model is stored in a Redis database and updated continuously through concurrent operations. A GoLang upload server has been implemented for adding new faces, and a web page template is available for easy integration of the file uploader API.
___
to start the application all you need to do is to launch it using the setup.sh file
```bash
chmod +x setup.sh
./setup.sh
```

Note : if you are on a debian-based linux and run into problems while installing dlib, chances are these packages will solve the issue:
```bash
sudo apt-get install python3 python3-pip build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev -y
```

___

## Details:
there are 2 files in the image2Encoding directory. the default file is thread.py that uses the registered faces (via REST API) and saves the model in redis DB.
there is also another file in that directory which is unknown.py and you can replace the name of the running script in Makefile. 
if you decide to use the unknown file, it will add any unknown face it finds as a new user with a name defined as: [ Unknown + UUID.V4 ]
so it depends on what you want to do with the project and based on your use case you can choose which file to use.<br>
also note that inside code where you define video capture device for now it is by default set on the camera #0 (most likely /dev/video0) but you can change the 
input camera or use RTSP camera stream (which i have a sample comment inside the code that will help you get started)<br>
Note #1: after the launch process is completed you can access the panel for file upload on localhost:5555<br>
Note #2: remember that redis models is not Durable(as D in ACID) and if you need persistent data you need to persist data on disk<br>
Note #3: you may want to change redis password or model tolerance rate (currently 0.6)

___
## Disclaimer:
note that all the code inside this repository was developed using the free and open source software and the ML model used in this repo was based on the awesome work here: <https://github.com/ageitgey/face_recognition>
so all this project was developed as a hobby and there is absolutely no guarantee that it's precision will satisfy your needs so be extremely cautious if you want to use it in production environment.


___
### Contact me:
if you have any questions about the project you can contact me in various ways:

website : <https://geek4geeks.ir><br>
mail : <shafigh75@gmail.com>

