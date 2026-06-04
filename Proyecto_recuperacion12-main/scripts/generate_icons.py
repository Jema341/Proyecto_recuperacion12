from PIL import Image, ImageDraw, ImageFont
import os

out_dir = os.path.join(os.path.dirname(__file__), '..', 'inicio', 'static', 'private', 'assets', 'images')
out_dir = os.path.normpath(out_dir)
os.makedirs(out_dir, exist_ok=True)

# logo-icon.png (128x128)
img = Image.new('RGBA', (128, 128), (78, 115, 223, 255))
draw = ImageDraw.Draw(img)
text = 'D'
font = ImageFont.load_default()
bbox = draw.textbbox((0, 0), text, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((128 - w) / 2, (128 - h) / 2), text, fill=(255, 255, 255, 255), font=font)
img.save(os.path.join(out_dir, 'logo-icon.png'))

# avatar-placeholder.png (96x96)
img = Image.new('RGBA', (96, 96), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
draw.ellipse((16, 8, 80, 72), fill=(108, 117, 125, 255))
draw.rectangle((16, 56, 80, 88), fill=(173, 181, 189, 255))
img.save(os.path.join(out_dir, 'avatar-placeholder.png'))

# favicon.png (64x64)
img = Image.new('RGBA', (64, 64), (244, 98, 58, 255))
draw = ImageDraw.Draw(img)
text = 'D'
bbox = draw.textbbox((0, 0), text, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((64 - w) / 2, (64 - h) / 2), text, fill=(255, 255, 255, 255), font=font)
img.save(os.path.join(out_dir, 'favicon.png'))

print('Icons written to', out_dir)
