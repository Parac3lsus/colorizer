import time
import redis
import settings
import json
import numpy as np
import os
import cv2 as cv

# Redis connection
db = redis.Redis( 
        host=settings.REDIS_IP,
        port=settings.REDIS_PORT, 
        db=settings.REDIS_DB_ID
        )



prototxt_path = 'Models/colorization_deploy_v2.prototxt'
model_path = 'Models/colorization_release_v2.caffemodel'
kernel_path = 'Models/pts_in_hull.npy'
#image_path ='Images/oz.jpg'


def predict(image_name):
    image_path = os.path.join(settings.UPLOAD_FOLDER, os.path.basename(image_name))
    print("Image path: {}".format(image_path), flush=True)
    net = cv.dnn.readNetFromCaffe(prototxt_path, model_path)
    points = np.load(kernel_path)


    points = points.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [points.astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]

    
    bw_image = cv.imread(image_path)
    normalized_img = (bw_image.astype(np.float32) / 255.0)

    # convert to Lab color space
    lab_img = cv.cvtColor(normalized_img, cv.COLOR_BGR2LAB)

    # resize to 224x224 for the network input
    resized_img = cv.resize(lab_img, (224, 224))

    L = cv.split(resized_img)[0]
    L -= 50
    # pass L channel through the network
    net.setInput(cv.dnn.blobFromImage(L))

    # this 'ab' array is the result of our colorization
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    # resize the ab channel to the same size as our input image
    ab = cv.resize(ab, (bw_image.shape[1], bw_image.shape[0]))

    # take L channel from original image
    L = cv.split(lab_img)[0]

    # concatenate original light channel with predicted color channels
    colorized_img = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    #convert from Lab to RGB
    colorized_img = cv.cvtColor(colorized_img, cv.COLOR_LAB2BGR)
    
    colorized_img_path = os.path.join(settings.COLORIZED_IMAGES_FOLDER,os.path.basename(image_path))
    cv.imwrite(colorized_img_path, colorized_img*255)
    
    return colorized_img_path

def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to generate colorized image.
    """
    while True:
        print("Waiting for new jobs...", flush=True)

        job_to_process =json.loads(db.brpop(settings.REDIS_QUEUE)[1])
        if(job_to_process):
            print("New job received: {}".format(job_to_process), flush=True)
            img_path = predict(job_to_process['image_name'])
            result_dict = {
                'image_path' : img_path
                }
            db.set(job_to_process['id'], json.dumps(result_dict))
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...", flush=True)
    classify_process()
