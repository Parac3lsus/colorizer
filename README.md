## Image colorizer service based using Richard Zhang Image Colorization Model: 
https://richzhang.github.io/colorization/ 
## Based on OpenCV sample: 
https://github.com/opencv/opencv/blob/master/samples/dnn/colorization.py

# Models Download
Run fetch_models.py to download the models and paste them in a folder named Models inside /model


# Flask ML API
## Install and run

To run the services using compose:

```bash
$ docker-compose up --build -d
```
Then go to localhost:80

To stop the services:

```bash
$ docker-compose down

