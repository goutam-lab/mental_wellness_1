from flask import Blueprint, request, jsonify
from services import community_service

community_bp = Blueprint("community", __name__)

@community_bp.route("/posts", methods=["POST"])
def create_post():
    try:
        data = request.get_json()
        if not data or "user_id" not in data or "content" not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        post = community_service.create_post(
            user_id=data.get("user_id"),
            content=data.get("content"),
            media_url=data.get("media_url")
        )
        return jsonify({"status": "success", "post": post}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@community_bp.route("/posts", methods=["GET"])
def get_posts():
    try:
        posts = community_service.get_all_posts()
        return jsonify({"status": "success", "posts": posts}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@community_bp.route("/posts/<post_id>", methods=["GET"])
def get_single_post(post_id):
    try:
        post = community_service.get_post(post_id)
        if post:
            return jsonify({"status": "success", "post": post}), 200
        return jsonify({"status": "error", "message": "Post not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@community_bp.route("/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    try:
        post = community_service.like_post(post_id)
        if post:
            return jsonify({"status": "success", "post": post}), 200
        return jsonify({"status": "error", "message": "Post not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@community_bp.route("/posts/<post_id>/comment", methods=["POST"])
def comment_post(post_id):
    try:
        data = request.get_json()
        if not data or "text" not in data or "user_id" not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        post = community_service.add_comment(post_id, data.get("text"), data.get("user_id"))
        if post:
            return jsonify({"status": "success", "post": post}), 200
        return jsonify({"status": "error", "message": "Post not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500