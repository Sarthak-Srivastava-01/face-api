from flask import Flask, request, jsonify
import recognize_faces
import os
import tempfile

app = Flask(__name__)

@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        if 'known' not in request.files or 'target' not in request.files:
            return jsonify({"error": "Missing files (need 'known' and 'target')"}), 400

        # Save uploaded known image
        known_file = request.files['known']
        tmp_known = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        known_file.save(tmp_known.name)

        # Save uploaded target folder (zipped)
        target_file = request.files['target']
        tmp_target_dir = tempfile.mkdtemp()
        target_zip_path = os.path.join(tmp_target_dir, "targets.zip")
        target_file.save(target_zip_path)

        # Extract images if it's a zip
        import zipfile
        with zipfile.ZipFile(target_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_target_dir)

        # Run your existing Python logic
        results = recognize_faces.find_matching_faces(tmp_known.name, tmp_target_dir)
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
