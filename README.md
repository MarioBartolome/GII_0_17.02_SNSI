# GII_0_17.02_SNSI
![Status](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=alert_status)
![maintainability](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=sqale_rating)
![TechDebt](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=sqale_index)
![Reliability](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=reliability_rating)
![Coverage](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=coverage)
![Bugs](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=bugs)
![Lines](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=ncloc)
![DuplicatedLines](https://sonarcloud.io/api/project_badges/measure?project=GII_0_17.02_SNSI&metric=duplicated_lines_density)



This project aims to design a semi-autonomous navigation system for indoor use,
destined to aid security vigilance using drones. 

Given an enclosed space, the drone should be able to make its path through it recording video,
which will be streamed to a server, and updating its position inside of it to the security guard in charge. 

This project comprises two distributed systems:
- A backend system. Usually a RaspberryPi-like computer. Small, not so power hungry and most importantly, lightweight.
- A frontend system. Giving the user a  WebUI to access the backend system.

![Drone Image](https://github.com/mbm0089/GII_0_17.02_SNSI/blob/5e03572352750919cc015e59bdead2220eca5f19/frontend/view/static/droneLogo.png "I know... it's beautiful. It's the stallion of the pictures")

## BackEnd



Files under the <code>backend</code> directory are supposed to be deployed on a Raspberry Pi. 
They contain the main wrapper system to control a drone making use of the [implementation](https://github.com/mbm0089/GII_0_17.02_SNSI/blob/5e03572352750919cc015e59bdead2220eca5f19/backend/MultiWiiProtocol.py) made of the [MultiWii Serial Protocol](http://www.multiwii.com/wiki/index.php?title=Multiwii_Serial_Protocol). Also they will create a socket server to handle the remote controller connection. 

Sending those files to a \*nix like system can be done with ease:

<code> scp -r backend USER@raspberry:/home/USER/ </code>

Or you can make use of any GUI tool of your choice, like [WinSCP](https://winscp.net/eng/download.php).

Obviously you must have access to the Raspberry Pi.

#### *Dependencies*
The Raspberry Pi must have installed the following Python >=3.5 packages: 
- Numpy
- PySerial
- PyCamera

Which could be installed with any Python packet manager, I suggest pip:

<code>pip3 install picamera numpy pyserial</code>

If Numpy gives a hard time trying to install, you could try:

<code>sudo apt-get install python3-numpy</code>

The Raspberry Pi is going to act as a WebRTC server to provide a real-time video feed to the client. So you will need to install also [UV4L](https://www.linux-projects.org/uv4l/). 

<code>sudo apt-get install uv4l uv4l-raspicam uv4l-raspicam-extras uv4l-server uv4l-webrtc </code>

UV4L places its configuration files under <code>/etc/uv4l/uv4l-raspicam.conf</code>

May you edit those as you please. A full reference manual can be found [here](https://www.linux-projects.org/documentation/uv4l-server/). But keep on mind to edit the database at <code>frontend/model/database.db</code> according to the changes you made, such as ports or hostnames.



## FrontEnd

The FrontEnd is the <small>~~ugly~~</small> cute part of this project, it conforms a WebUI that should be deployed on a system ready to become a web server.

#### *Dependencies*

The server must have installed the following Python >=3.5 packages:
- Numpy
- Flask
- Flask_login
- Flask_socketio
- Flask_sqlalchemy
- Flask_migrate
- Flask_wtf
- wtforms
- eventlet

Which could be installed with any Python packet manager, I suggest pip:

<code>pip3 install numpy flask flask_login flask_socketio flask_sqlalchemy flask_migrate flask_wtf wtforms eventlet</code>


## Putting everything together

You will need to connect a flight controller that supports MultiWiiSerialProtocol to receive channel inputs to the RaspberryPi. Just make use of any of the USB ports on the RaspberryPi.

Once you have everything on its right place is time to run it!

#### On the RaspberryPi: 

<code>user@raspberry~> sudo service uv4l start</code> Will get us the WebRTC video feed.
<code>user@raspberry~> python3 backend/ctrlWrapper.py</code> Will run the remote controller receiver and the comunication services with the drone, making use of <code>backend/MultiWiiProtocol.py</code>

#### On the web server:
Remember, WebRTC only works through HTTP**S** so you will need to get those fancy certs and keys to run this. Once you got them place them under root folder of the project, on a folder named <code>private</code>. 

***Note***: You can also play with the <code>frontend/droneControlWebUI.py</code> code to change the folders and names of the key-cert files.

<code>user@webserver~> python3 frontend/droneControlWebUI.py</code>

And now, if everything is working fine, you could point to your host and access the Drone Control System. 

To remote-control the drone, you need to connect a joystick or radio with, at least, 5 axis:
- Channel 1: Throttle
- Channel 2: Aileron (Roll)
- Channel 3: Elevation (Pitch)
- Channel 4: Rudder (Yaw/Heading)
- Channel 5: Arm/Disarm

```diff
- Make sure all your readings are correct prior to enabling manual control
```
