import cv2
from PIL import Image
from skimage import io

IMAGE_WIDTH = 1720
IMAGE_HEIGHT = 1080

def create_collage(images):
    images = [io.imread(img) for img in images]
    images = [cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT)) for image in images]
    if len(images) > 2:
        half = len(images) // 2
        h1 = cv2.hconcat(images[:half])
        h2 = cv2.hconcat(images[half:])
        concat_images = cv2.vconcat([h1, h2])
    else:
        concat_images = cv2.hconcat(images)
    image = Image.fromarray(concat_images)

    # Image path
    image_name = "result_CL36.jpg"
    image = image.convert("RGB")
    image.save(f"{image_name}")
    return image_name
images=["figures/eliade_CL36_resolution.png","figures/eliade_CL36_efficiency.png","figures/eliade_CL36_peaktotal.png","figures/eliade_CL36_calibration.png"]
#image1 on top left, image2 on top right, image3 on bottom left,image4 on bottom right
create_collage(images)