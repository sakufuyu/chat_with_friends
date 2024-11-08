# setup.py
from app import create_app
import os

app = create_app()
img_folder = "app/static/user_img/"

if __name__ == "__main__":
    app.run(debug=True)

    for filename in os.listdir(img_folder):
        file_path = os.path.join(img_folder, filename)
        if (os.path.isfile(file_path)):
            os.remove(file_path)
    print(" Finish App Runnig")
