import os 
import base64
import json
from io import BytesIO

from PIL import Image

from vertexai.preview.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold


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
def extract_injury_details(file_path):
    model = GenerativeModel("gemini-pro-vision")
    responses =  model.generate_content( 
        [Part.from_data(data=base64.b64encode(file_path).decode('utf-8'),mime_type="image/jpeg") , 
         "Describe what injury has happened and the extent of the injury and where it occured, Please be conservative in your prediction of the injury."]
    )
    return responses.candidates[0].content.parts[0].text.strip()

def extract_user_details(file_path):
    model = GenerativeModel("gemini-pro-vision")
    safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    } 
    responses = model.generate_content( 
        [Part.from_data(data=base64.b64encode(file_path).decode('utf-8'),mime_type="image/jpeg"),
        '''Image is suppose to be an identification document of a person, if the image is not an identification document, reply with "Not an identification document"

Otherwise, please extract the name, date_of_birth and id_number in json format. Missing fields are left as null. please note that id_number is also called identity card number'''
        ],
        stream=False,
        safety_settings=safety_config
    )

    response_text = responses.candidates[0].content.parts[0].text.strip().replace('```json', '').replace('```', '').strip()

    json_data = json.loads(response_text)

    return json_data['name'], json_data['date_of_birth'], json_data['id_number']

