import pytesseract
from PIL import Image
import json

image_path = '1.jpeg'
image = Image.open(image_path)

# Get character-level bounding boxes
boxes = pytesseract.image_to_boxes(image)
width, height = image.size

result = []
for line in boxes.splitlines():
	parts = line.split(' ')
	if len(parts) == 6:
		char, x1, y1, x2, y2, _ = parts
		# Tesseract's y origin is bottom-left, Pillow's is top-left
		y1_flipped = height - int(y2)
		y2_flipped = height - int(y1)
		result.append({
			'char': char,
			'box': {
				'x1': int(x1),
				'y1': y1_flipped,
				'x2': int(x2),
				'y2': y2_flipped
			}
		})

with open('ocr_char_boxes.json', 'w') as f:
	json.dump(result, f, ensure_ascii=False, indent=2)

# Draw blue rectangles for each character box and save a new image
from PIL import ImageDraw

with open('ocr_char_boxes.json', 'r') as f:
	char_boxes = json.load(f)

draw = ImageDraw.Draw(image)
for item in char_boxes:
	box = item['box']
	draw.rectangle([
		(box['x1'], box['y1']),
		(box['x2'], box['y2'])
	], outline='blue', width=2)

image.save('1_boxes_blue.png')
print('New image with blue boxes saved as 1_boxes_blue.png')

