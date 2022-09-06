from genericpath import exists
import utils
import settings
import os
from middleware import model_predict
import redis

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify
)
import json

router = Blueprint("app_router", __name__, template_folder="templates")


@router.route("/", methods=["GET"])
def index():
    """
    Index endpoint, renders our HTML code.
    """
    return render_template("index.html")


@router.route("/", methods=["POST"])
def upload_image():
    """
    Function used in our frontend so we can upload and show an image.
    When it receives an image from the UI, it also calls our ML model to
    get and display the colorized image.
    """
    # No file received, show basic UI
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    # File received but no filename is provided, show basic UI
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)

    # File received and it's an image, we will show it in our UI
    if file and utils.allowed_file(file.filename):

        img_name = utils.get_file_hash(file)
        path = settings.UPLOAD_FOLDER + img_name
        if(not os.path.exists(path)):
            file.save(path, buffer_size=16384)
        file.close()
        
        colorized_image_path = model_predict(img_name)

        context = {
            "filename": 'static/'+colorized_image_path,
        }
        
        img_name = 'static/uploads/'+img_name

        return render_template(
            "index.html", filename=img_name, context=context
        )
    # File received and but it isn't an image
    else:
        flash("Allowed image types are -> png, jpg, jpeg, gif")
        return redirect(request.url)



