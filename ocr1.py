import pytesseract
from PIL import Image, ImageDraw
import json
import os

testcase_dir = 'testcase'
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(testcase_dir):
	if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
		image_path = os.path.join(testcase_dir, filename)
		image = Image.open(image_path)
		boxes = pytesseract.image_to_boxes(image)
		width, height = image.size
		result = []
		for line in boxes.splitlines():
			parts = line.split(' ')
			if len(parts) == 6:
				char, x1, y1, x2, y2, _ = parts
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
		# Save char boxes JSON
		json_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_char_boxes.json')
		with open(json_path, 'w') as f:
			json.dump(result, f, ensure_ascii=False, indent=2)
		# Draw blue rectangles for each character box and save a new image
		draw = ImageDraw.Draw(image)
		for item in result:
			box = item['box']
			draw.rectangle([
				(box['x1'], box['y1']),
				(box['x2'], box['y2'])
			], outline='blue', width=2)
		out_img_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_boxes_blue.png')
		image.save(out_img_path)
		print(f'Processed {filename}: saved {json_path} and {out_img_path}')

