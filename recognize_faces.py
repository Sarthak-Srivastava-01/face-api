import face_recognition
import os
import json
import sys

def find_matching_faces(known_image_path, target_folder):
    try:
        # Load the known image and get its face encoding
        known_image = face_recognition.load_image_file(known_image_path)
        known_face_encodings = face_recognition.face_encodings(known_image)

        if not known_face_encodings:
            return {
                "error": f"No face found in the known image: {known_image_path}. "
                         "Try using a clearer, front-facing photo."
            }

        # Take the first detected face (best for single-person reference images)
        known_face_encoding = known_face_encodings[0]

        matching_images = []
        for filename in os.listdir(target_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(target_folder, filename)
                try:
                    unknown_image = face_recognition.load_image_file(image_path)
                    unknown_face_encodings = face_recognition.face_encodings(unknown_image)

                    if not unknown_face_encodings:
                        # Skip images with no detectable faces
                        continue

                    # Check all faces in this image
                    for face_encoding in unknown_face_encodings:
                        matches = face_recognition.compare_faces([known_face_encoding], face_encoding, tolerance=0.5)
                        if True in matches:
                            matching_images.append(filename)
                            break  # Stop after first match in this image
                except Exception as e:
                    # Collect error but don't stop processing
                    print(f"Error processing image {filename}: {e}", file=sys.stderr)

        return {"matching_images": matching_images}

    except Exception as e:
        return {"error": f"An error occurred: {e}"}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python recognize_faces.py <known_image_path> <target_folder>")
        sys.exit(1)

    known_image_path = sys.argv[1]
    target_folder = sys.argv[2]

    results = find_matching_faces(known_image_path, target_folder)
    print(json.dumps(results))