import os
import io

# Imports the Google Cloud client library
#from google.api_core import protobuf_helpers as protobuf
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
    '/Users/thomasedwards/PycharmProjects/persistence-landscapes/Flickr_Images/2-spot Ladybird/2631483315.jpg')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)
    print(label.score)