from flask import Flask, request, jsonify
import recognize_faces
import os
import tempfile
import zipfile
import shutil

app = Flask(__name__)

@app.route("/recognize", methods=["POST"])
def recognize():
    tmp_known = None
    tmp_target_dir = None

    try:
        # Validate incoming files
        if 'known' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing files. Upload both 'known' (image) and 'target' (ZIP of images)."}), 400

        # Save known image
        known_file = request.files['known']
        tmp_known = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        known_file.save(tmp_known.name)

        # Save and extract ZIP of target images
        target_file = request.files['target']
        tmp_target_dir = tempfile.mkdtemp()
        target_zip_path = os.path.join(tmp_target_dir, "targets.zip")
        target_file.save(target_zip_path)

        # Extract ZIP securely
        with zipfile.ZipFile(target_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_target_dir)

        # Run recognition logic
        results = recognize_faces.find_matching_faces(tmp_known.name, tmp_target_dir)
        return jsonify(results)

    except zipfile.BadZipFile:
        return jsonify({"error": "Invalid ZIP file uploaded."}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        # Cleanup temporary files/directories
        try:
            if tmp_known:
                os.unlink(tmp_known.name)
            if tmp_target_dir:
                shutil.rmtree(tmp_target_dir)
        except Exception:
            pass  # Ignore cleanup errors

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
