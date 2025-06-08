import os
import tempfile
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

RAPIDAPI_VTON_URL = f"https://{Config.RAPIDAPI_HOST}/try-on-url"

@vton_bp.route("/", methods=["POST"])
def upload_vton_result():
    clothes_url = request.form.get('clothes_url') 
    avatar_image_file = request.files.get('avatar_image')
    avatar_sex = request.form.get('avatar_sex', 'female')

    if not clothes_url or not avatar_image_file:
        return jsonify({"error": "請提供 'clothes_url' 及上傳 'avatar_image'。"}), 400

    avatar_public_id = None 
    temp_vton_result_filepath = None

    try:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{avatar_image_file.mimetype.split('/')[-1]}") as temp_avatar_file:
                avatar_image_file.save(temp_avatar_file)
                temp_avatar_filepath = temp_avatar_file.name

            avatar_upload_result = cloudinary.uploader.upload(
                temp_avatar_filepath,
                folder="vton_avatars", 
                resource_type="image"
            )
            avatar_image_url = avatar_upload_result.get("secure_url")
            avatar_public_id = avatar_upload_result.get("public_id")

            os.remove(temp_avatar_filepath)

            if not avatar_image_url:
                raise Exception("Cloudinary 頭像上傳失敗，未獲取到 URL。")

            print(f"使用者頭像已上傳至 Cloudinary: {avatar_image_url}")

        except Exception as e:
            print(f"Cloudinary 頭像上傳失敗：{e}")
            return jsonify({"error": f"使用者頭像上傳失敗: {str(e)}"}), 500

        rapidapi_headers = {
            'x-rapidapi-host': Config.RAPIDAPI_HOST,
            'x-rapidapi-key': Config.RAPIDAPI_KEY,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        rapidapi_payload = {
            'clothing_image_url': clothes_url,
            'avatar_image_url': avatar_image_url, 
            'avatar_sex': avatar_sex,
        }

        rapidapi_response = requests.post(
            RAPIDAPI_VTON_URL,
            headers=rapidapi_headers,
            data=rapidapi_payload 
        )
        
        rapidapi_response.raise_for_status() 

        vton_image_data = rapidapi_response.content

        vton_content_type_header = rapidapi_response.headers.get('Content-Type', 'image/png').lower()
        vton_file_suffix = ".jpg" if 'jpeg' in vton_content_type_header or 'jpg' in vton_content_type_header else ".png"

        with tempfile.NamedTemporaryFile(delete=False, suffix=vton_file_suffix) as temp_file:
            temp_file.write(vton_image_data)
            temp_vton_result_filepath = temp_file.name 
        
        upload_result = cloudinary.uploader.upload(
            temp_vton_result_filepath,
            folder="vton_results", 
            overwrite=True, 
            resource_type="image"
        )
        final_image_url = upload_result.get("secure_url")

        os.remove(temp_vton_result_filepath)
        temp_vton_result_filepath = None 

        if not final_image_url:
            raise Exception("Cloudinary 結果圖片上傳失敗。")

        print(f"最終 VTON 結果圖片已上傳至 Cloudinary: {final_image_url}")

        if avatar_public_id: 
            try:
                cloudinary.uploader.destroy(avatar_public_id, resource_type="image")
                print(f"原始頭像 {avatar_public_id} 已從 Cloudinary 刪除。")
            except Exception as e:
                print(f"刪除原始頭像 {avatar_public_id} 失敗：{e}")

        return jsonify({"image_url": final_image_url}), 200

    except requests.exceptions.RequestException as e:
        print(f"呼叫 RapidAPI 失敗：{e}")
        if e.response is not None:
            print(f"狀態碼：{e.response.status_code}")
            print(f"響應內容：{e.response.content[:500]}..." if e.response.content else "無回應內容")
            return jsonify({"error": f"Try-On API 錯誤: {e.response.text}"}), e.response.status_code
        return jsonify({"error": f"呼叫 Try-On API 失敗: {str(e)}"}), 500
    except Exception as e:
        print(f"處理過程中發生錯誤：{e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_vton_result_filepath and os.path.exists(temp_vton_result_filepath):
            try:
                os.remove(temp_vton_result_filepath)
            except Exception as e:
                print(f"清理暫存 VTON 結果檔案失敗: {e}")