from PIL import Image, ImageEnhance, ImageFilter

im = Image.open('logotipo-original.webp').convert('RGBA')
width, height = im.size

new_im = Image.new('RGBA', (width, height), (0, 0, 0, 0))
pixels = im.load()
new_pixels = new_im.load()

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        
        # Check if white or near white background
        if r > 220 and g > 220 and b > 220:
            new_pixels[x, y] = (0, 0, 0, 0)
        elif r > 180 and g > 180 and b > 180:
            # Soft edge
            alpha = int(255 * (1.0 - (r - 180) / 40.0))
            new_pixels[x, y] = (r, g, b, alpha)
        else:
            # Check if this is the blue icon (left side x < 70 and blueish)
            if x < 65:
                # Enhance the blue to vibrant cyan / electric blue
                cyan_r = min(255, int(r * 0.8))
                cyan_g = min(255, int(g * 1.5 + 50))
                cyan_b = min(255, int(b * 1.8 + 80))
                new_pixels[x, y] = (cyan_r, cyan_g, cyan_b, 255)
            else:
                # This is the text! Invert dark text to crisp white / platinum
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                # Dark gray should become bright white
                bright = 255 - gray
                # Clamp to high brightness
                text_val = max(220, min(255, bright + 180))
                new_pixels[x, y] = (text_val, text_val, text_val, 255)

# Scale up 2x with high-quality resampling for crisp retina display
new_im_retina = new_im.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
new_im_retina.save('logotipo-ms-dark.webp', 'WEBP', quality=95)
new_im_retina.save('logotipo-ms-dark.png', 'PNG')
print("Logotipo creado con éxito: logotipo-ms-dark.webp y .png")
