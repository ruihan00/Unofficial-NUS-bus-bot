import os 
import base64 
 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/etc/secrets/auth.json' 
 
from vertexai.preview.generative_models import GenerativeModel, Part 

from PIL import Image
from io import BytesIO


# Mirror the image
# To fix the issue where the llm thinks that the image left is real world left
def mirror_image(image_bytes):
    # Open the image from bytes
    image = Image.open(BytesIO(image_bytes))

    # Mirror the image
    mirrored_image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # Convert the mirrored image to bytes
    mirrored_image_bytes = BytesIO()
    mirrored_image.save(mirrored_image_bytes, format='JPEG')
    mirrored_image_bytes = mirrored_image_bytes.getvalue()

    return mirrored_image_bytes

# Convert the image to a b64 string 
def file_to_b64string(path): 
    with open(path, 'rb') as file: 
        data = base64.b64encode(mirror_image(file.read())).decode('utf-8') 
     
    return data
 
# Function to recognise the image given a file path
def recognise_image(file_path):
    model = GenerativeModel("gemini-pro-vision")
    responses =  model.generate_content( 
        [Part.from_data(data=file_to_b64string(file_path),mime_type="image/jpeg") , 
         "Describe what injury has happened and the extent of the injury and where it occured, Please be conservative in your prediction of the injury, reject the image if it is not a injury or if it is not clear enough to make a prediction"]
    ) 
 
    return responses.candidates[0].content.parts[0].text.strip()
def recognise_image_from_data(data):
    model = GenerativeModel("gemini-pro-vision")
    print('data obtained')
    responses =  model.generate_content( 
        [Part.from_data(data=base64.b64encode(mirror_image(data)).decode('utf-8')
                        ,mime_type="image/jpeg") , 
         "Describe what injury has happened and the extent of the injury and where it occured, Please be conservative in your prediction of the injury, reject the image if it is not a injury or if it is not clear enough to make a prediction"]
    ) 
 
    return responses.candidates[0].content.parts[0].text.strip()
