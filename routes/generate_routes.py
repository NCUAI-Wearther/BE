import os
import tempfile
from flask import Blueprint, jsonify, request
from config import Config
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
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


@generate_bp.route("/", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400

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

        upload_result = cloudinary.uploader.upload(temp_file_path,
            folder="generate_results",
            overwrite=True)

        image_url = upload_result.get("secure_url")

        os.remove(temp_file_path)

        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
