import time
import redis
import settings
import uuid
import json

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis( 
        host=settings.REDIS_IP,
        port=settings.REDIS_PORT, 
        db=settings.REDIS_DB_ID
        )

def model_predict(image_name):

    job_id = str(uuid.uuid4())

    job_data = {
        'id' : job_id,
        'image_name' : image_name
     }

    db.rpush(settings.REDIS_QUEUE, json.dumps(job_data))

    # Loop until we received the response from our ML model
    while True:
        # Attempt to get model predictions using job_id

        output = None
        if db.exists(job_id):
            output = json.loads(db.get(job_id))

            db.delete(job_id)
            return output['image_path']
        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)
    return None

