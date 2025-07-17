import numpy as np
import io
import cv2
import uuid
import tempfile
import os
from PIL import Image
from datetime import datetime
from app import face_collection, face_model

def extract_embedding(image_bytes):
    """Extract face embedding from image bytes"""
    try:
        img = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
        faces = face_model.get(img)
        if not faces:
            return None
        
        # Get the largest face if multiple faces detected
        if len(faces) > 1:
            face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        else:
            face = faces[0]
            
        emb = face.embedding
        emb = emb / np.linalg.norm(emb)  # normalize
        return emb.astype(np.float32)
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None

def extract_frames_from_video(video_bytes, max_frames=10, frame_interval=5):
    """Extract frames from video bytes"""
    try:
        # Save video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_bytes)
            temp_video_path = temp_video.name
        
        cap = cv2.VideoCapture(temp_video_path)
        frames = []
        frame_count = 0
        
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Extract frame at intervals
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            
            frame_count += 1
        
        cap.release()
        os.unlink(temp_video_path)  # Clean up temp file
        
        return frames
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []

def extract_embeddings_from_frames(frames):
    """Extract face embeddings from multiple frames"""
    embeddings = []
    
    for frame in frames:
        try:
            faces = face_model.get(frame)
            if faces:
                # Get the largest face
                face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
                emb = face.embedding
                emb = emb / np.linalg.norm(emb)  # normalize
                embeddings.append(emb.astype(np.float32))
        except Exception as e:
            print(f"Error processing frame: {e}")
            continue
    
    return embeddings

def store_embeddings_in_chroma(ez_id, embeddings):
    """Store embeddings in ChromaDB with only ez_id"""
    try:
        embedding_ids = []
        embedding_metadatas = []
        
        for i, emb in enumerate(embeddings):
            embedding_id = f"{ez_id}_{i}_{uuid.uuid4().hex[:8]}"
            embedding_ids.append(embedding_id)
            
            embedding_metadata = {
                "ez_id": ez_id,
                "embedding_index": i,
                "created_at": datetime.utcnow().isoformat()
            }
            
            embedding_metadatas.append(embedding_metadata)
        
        # Convert embeddings to list format for ChromaDB
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        face_collection.add(
            embeddings=embeddings_list,
            metadatas=embedding_metadatas,
            ids=embedding_ids
        )
        
        return True
    except Exception as e:
        print(f"Error storing embeddings: {e}")
        return False

def search_similar_faces(query_embedding, n_results=10):
    """Search for similar faces in ChromaDB"""
    try:
        results = face_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=['metadatas', 'distances']
        )
        
        return results
    except Exception as e:
        print(f"Error searching faces: {e}")
        return None
