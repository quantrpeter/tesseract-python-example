import pytesseract
from PIL import Image, ImageDraw
import json
import os
from PIL import ImageEnhance
from PIL import ImageFont

testcase_dir = 'testcase'
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(testcase_dir):
	if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
		image_path = os.path.join(testcase_dir, filename)
	image = Image.open(image_path)
	# Preprocess: convert to grayscale
	image = image.convert('L')
	# Enhance contrast
	enhancer = ImageEnhance.Contrast(image)
	image = enhancer.enhance(2.0)  # Increase contrast, adjust factor as needed
	# Load a Unicode font that supports Chinese and English
	font_path = 'font/NotoSansTC-VariableFont_wght.ttf'  # Update path if needed
	font_size = 20
	try:
		font = ImageFont.truetype(font_path, font_size)
	except Exception as e:
		print(f"Font load error: {e}. Using default font.")
		font = None
	for lang, suffix in [('eng', 'eng'), ('chi_sim', 'sim'), ('chi_tra', 'tra')]:
		# Use optimized Tesseract config for accuracy
		custom_config = r'--oem 3 --psm 6'
		boxes = pytesseract.image_to_boxes(image, lang=lang, config=custom_config)
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
		json_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_char_boxes_{suffix}.json')
		with open(json_path, 'w') as f:
			json.dump(result, f, ensure_ascii=False, indent=2)
		# Draw blue rectangles for each character box and save a new image
		image_copy = image.copy()
		draw = ImageDraw.Draw(image_copy)
		for item in result:
			box = item['box']
			draw.rectangle([
				(box['x1'], box['y1']),
				(box['x2'], box['y2'])
			], outline='blue', width=2)
		out_img_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_boxes_blue_{suffix}.png')
		image_copy.save(out_img_path)
		print(f'Processed {filename}: saved {json_path} and {out_img_path}')
		print(f'Processed {filename} ({lang}): saved {json_path} and {out_img_path}')

		# Create a new blank image and draw recognized text at correct positions
		text_img = Image.new('RGB', (width, height), color='white')
		text_draw = ImageDraw.Draw(text_img)
		for item in result:
			box = item['box']
			char = item['char']
			# Draw character at top-left of its bounding box
			if font:
				text_draw.text((box['x1'], box['y1']), char, fill='black', font=font)
			else:
				text_draw.text((box['x1'], box['y1']), char, fill='black')
		text_img_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_text_{suffix}.png')
		text_img.save(text_img_path)
		print(f'Processed {filename} ({lang}): saved {text_img_path}')

