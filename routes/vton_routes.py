import os
import tempfile
import base64
import requests
from flask import Blueprint, jsonify, request
from config import Config

import cloudinary
import cloudinary.uploader

vton_bp = Blueprint('vton_bp', __name__)

cloudinary.config(
    cloud_name=Config.cloud_name,
    api_key=Config.api_key,
    api_secret=Config.api_secret,
    secure=True
)

RAPIDAPI_VTON_URL = f"https://{Config.RAPIDAPI_HOST}/try-on-file"

@vton_bp.route("/", methods=["POST"])
def upload_vton_result():
    
    clothing_image_file = request.files.get('clothing_image')
    avatar_image_file = request.files.get('avatar_image')
    avatar_sex = request.form.get('avatar_sex','female') # 例如 'female' 或 'male'
    
    if not clothing_image_file or not avatar_image_file:
        return jsonify({"error": "請上傳 'clothing_image' 和 'avatar_image' 檔案。"}), 400
    
    try:
        rapidapi_headers = {
            'x-rapidapi-host': Config.RAPIDAPI_HOST,
            'x-rapidapi-key': Config.RAPIDAPI_KEY,
            # Content-Type: multipart/form-data 會由 requests 自動處理
        }

        rapidapi_files = {
            'clothing_image': (clothing_image_file.filename, clothing_image_file.read(), clothing_image_file.mimetype),
            'avatar_image': (avatar_image_file.filename, avatar_image_file.read(), avatar_image_file.mimetype),
        }

        rapidapi_data = {}
        rapidapi_data['avatar_sex'] = avatar_sex

        print("正在呼叫 RapidAPI Try-On Diffusion 服務...")

        rapidapi_response = requests.post(
            RAPIDAPI_VTON_URL,
            headers=rapidapi_headers,
            files=rapidapi_files,
            data=rapidapi_data
        )
        
        rapidapi_response.raise_for_status()

        image_data = rapidapi_response.content
        content_type_header = rapidapi_response.headers.get('Content-Type', 'image/png')
        
        if 'jpeg' in content_type_header or 'jpg' in content_type_header:
            file_suffix = ".jpg"
        elif 'png' in content_type_header:
            file_suffix = ".png"
        else:
            file_suffix = ".png"

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        upload_result = cloudinary.uploader.upload(temp_file_path,
            folder="vton_results",
            overwrite=True)

        final_image_url = upload_result.get("secure_url")

        os.remove(temp_file_path)

        if not final_image_url:
            return jsonify({"error": "無法從 Cloudinary 上傳結果中獲取圖片 URL"}), 500

        return jsonify({"image_url": final_image_url})

    except requests.exceptions.RequestException as e:

        print(f"呼叫 RapidAPI 服務失敗：{e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"狀態碼：{e.response.status_code}")
            print(f"響應內容：{e.response.text}")
            return jsonify({"error": f"Try-On Diffusion API 錯誤: {e.response.text}"}), e.response.status_code
        return jsonify({"error": f"呼叫 Try-On Diffusion API 失敗: {str(e)}"}), 500
    except Exception as e:

        print(f"處理請求過程中發生錯誤：{e}")
        return jsonify({"error": str(e)}), 500