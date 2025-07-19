from flask import Blueprint, request, jsonify, abort
from ..utils.embedding_func import *
from ..models import SenInfo

lookup = Blueprint('lookup', __name__)

@lookup.route('/register', methods=['POST'])
def register():
    """Register user using video only"""
    try:
        video = request.files.get('video')
        ez_id = request.form.get('ez_id')
        
        senior = SenInfo.query.filter_by(ez_id = ez_id).one_or_none()
        if not senior:
            abort(404, description="User not Found!")

        if not video or video.filename == '':
            return jsonify({"error": "No video uploaded"}), 400

        try:
            video_bytes = video.read()
            frames = extract_frames_from_video(video_bytes, max_frames=15, frame_interval=3)
            embeddings = extract_embeddings_from_frames(frames)
            
            if not embeddings:
                return jsonify({"error": "No valid faces detected in the video. Please ensure the video contains clear, visible faces"}), 400

            if len(embeddings) < 3:
                return jsonify({"error": "At least 3 frames with valid faces are required for registration from video"}), 400

            # Clear existing embeddings for this ez_id in ChromaDB
            try:
                existing_results = face_collection.get(where={"ez_id": senior.ez_id})
                if existing_results['ids']:
                    face_collection.delete(ids=existing_results['ids'])
            except Exception as e:
                print(f"Error clearing existing embeddings: {e}")

            # Store embeddings in ChromaDB
            success = store_embeddings_in_chroma(senior.ez_id, embeddings)

            if not success:
                return jsonify({"error": "Failed to store face embeddings"}), 500

            return jsonify({
                "message": f"User registered successfully from video with {len(embeddings)} face embeddings",
                "ez_id": senior.ez_id,
                "total_embeddings": len(embeddings),
                "frames_processed": len(frames)
            }), 200

        except Exception as e:
            print(f"Error processing video {video.filename}: {e}")
            return jsonify({"error": f"Failed to process video!"}), 500

    except Exception as e:
        return jsonify({"error": f"Video registration failed! Try Again Later."}), 500

@lookup.route('/recognize', methods=['POST'])
def recognize():
    """Recognize user using photo only and return matching ez_id(s)"""
    try:
        file = request.files.get('photo')
        
        if not file or file.filename == '':
            return jsonify({"error": "No photo uploaded"}), 400
        
        # Process image
        emb = extract_embedding(file.read())
        if emb is None:
            return jsonify({"error": "No face detected in the uploaded photo. Please upload a clear image with a visible face"}), 400

        # Search in ChromaDB
        search_results = search_similar_faces(emb, n_results=50)
        
        if not search_results or not search_results['metadatas'][0]:
            return jsonify({
                "error": "No matching user found",
                "message": "The face in the photo doesn't match any registered users"
            }), 404

        THRESHOLD = 0.7  # ChromaDB uses distance, lower is better
        user_scores = {}  # ez_id -> best similarity (1 - distance)

        for metadata, distance in zip(search_results['metadatas'][0], search_results['distances'][0]):
            if distance > THRESHOLD:  # Skip if distance too high
                continue
                
            ez_id = metadata.get('ez_id')
            similarity = 1 - distance  # Convert distance to similarity
            
            if ez_id not in user_scores or similarity > user_scores[ez_id]:
                user_scores[ez_id] = similarity

        # Sort users by similarity
        top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        if not top_users:
            return jsonify({
                "error": "No matching user found",
                "message": "The face in the photo doesn't match any registered users with sufficient confidence",
                "min_distance": float(min(search_results['distances'][0])) if search_results['distances'][0] else 1.0
            }), 404

        results = []
        for ez_id, similarity in top_users:
            results.append({
                "ez_id": ez_id,
                "similarity": float(similarity),
                "confidence": "High" if similarity > 0.8 else "Medium" if similarity > 0.6 else "Low"
            })

        return jsonify({
            "matches": results
        })
        
    except Exception as e:
        return jsonify({"error": f"Recognition failed! Try Again."}), 500
