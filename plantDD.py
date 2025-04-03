#  install the dependicies
# pip install transformers torch pillow

import argparse
from PIL import Image
from transformers import pipeline, AutoImageProcessor, AutoModelForImageClassification

# give the path of the jpeg image
image_path = "download (11).jpg"

#give the path of the model
model_path = "ViT-Base-model-20250401T195059Z-001/ViT-Base-model" # importing trained Vit-base model
image_processor = AutoImageProcessor.from_pretrained(model_path)
model = AutoModelForImageClassification.from_pretrained(model_path)

classifier = pipeline("image-classification", image_processor = image_processor, model=model)

try:
  image = Image.open(image_path).convert("RGB")
except Exception as e:
  print(f"Error opening the image: {e}")

results = classifier(image)
print("Classification Results")
for res in results:
  print(f"Label: {res['label']}, Score: {res['score']:.4f}")

""""
Sample output

Device set to use cpu

Classification Results
Label: leaf curl, Score: 0.8194
Label: whitefly, Score: 0.1033
Label: healthy, Score: 0.0361
Label: yellowish, Score: 0.0311
Label: leaf spot, Score: 0.0102

"""