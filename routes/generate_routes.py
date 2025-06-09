import os
import random
import tempfile
import cv2
from flask import Blueprint, jsonify, request
from config import Config
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from rembg import remove

import cloudinary
import cloudinary.uploader

generate_bp = Blueprint('generate_bp', __name__)

PROJECT_ID = Config.PROJECT_ID
vertexai.init(project=PROJECT_ID, location="us-central1")

cloudinary.config(
    cloud_name=Config.cloud_name,
    api_key=Config.api_key,
    api_secret=Config.api_secret,
    secure=True
)

gender = ['man','woman']

@generate_bp.route("/", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        gender_str = data.get("gender")
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        if  not gender_str:
            if random.randint(0, 1):
                gender_str = gender[0]
            else:
                gender_str = gender[1]
        
        prompt = (
            "highly detailed illustration, full body portrait, front view, a young" + gender_str + "standing, " 
            "wearing: " + prompt + ", "
            "clear line art, realistic clothing texture, knitted fabric, soft shading, "
            "white or transparent background, fashion illustration style"
        )
        generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")

        images = generation_model.generate_images(
            prompt=prompt,
            number_of_images=1,
            # aspect_ratio="9:16",
            language="zh-TW",
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            images[0].save(location=temp_file.name, include_generation_parameters=False)
            temp_file_path = temp_file.name

        input = cv2.imread(temp_file_path)
        output = remove(input)
        cv2.imwrite(temp_file_path, output)
        
        upload_result = cloudinary.uploader.upload(temp_file_path,
            folder="generate_results",
            overwrite=True)

        image_url = upload_result.get("secure_url")

        os.remove(temp_file_path)

        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
