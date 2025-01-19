import json

def get_animation_data(animation_path):
    def load_lottie_json(path: str):
        with open(path, "r") as f:
            return json.load(f)

    animation_data = load_lottie_json(animation_path)
    return animation_data

