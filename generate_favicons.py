from PIL import Image, ImageDraw
import math

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

# 1. Draw rounded rectangle with vertical/diagonal gradient
# Gradient from #1e1b4b (top left) to #0284c7 (bottom right)
c_start = (30, 27, 75, 255)
c_mid = (30, 58, 138, 255)
c_end = (2, 132, 199, 255)

grad_img = Image.new("RGBA", (SIZE, SIZE))
for y in range(SIZE):
    for x in range(SIZE):
        t = (x + y) / (2.0 * SIZE)
        if t < 0.5:
            sub_t = t * 2.0
            r = int(c_start[0] + (c_mid[0] - c_start[0]) * sub_t)
            g = int(c_start[1] + (c_mid[1] - c_start[1]) * sub_t)
            b = int(c_start[2] + (c_mid[2] - c_start[2]) * sub_t)
        else:
            sub_t = (t - 0.5) * 2.0
            r = int(c_mid[0] + (c_end[0] - c_mid[0]) * sub_t)
            g = int(c_mid[1] + (c_end[1] - c_mid[1]) * sub_t)
            b = int(c_mid[2] + (c_end[2] - c_mid[2]) * sub_t)
        grad_img.putpixel((x, y), (r, g, b, 255))

# Mask for squircle
mask = Image.new("L", (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(mask)
margin = 40
radius = 230
mask_draw.rounded_rectangle([margin, margin, SIZE - margin, SIZE - margin], radius=radius, fill=255)

# Composite gradient on squircle
img.paste(grad_img, (0, 0), mask)
draw = ImageDraw.Draw(img)

# Subtle cyan border
border_draw = ImageDraw.Draw(img)
border_draw.rounded_rectangle([margin, margin, SIZE - margin, SIZE - margin], radius=radius, outline=(56, 189, 248, 140), width=12)

# 2. Draw Sun in top-right
sun_cx = 740
sun_cy = 260
sun_r = 75

# Glow
for r_glow in [140, 105]:
    draw.ellipse([sun_cx - r_glow, sun_cy - r_glow, sun_cx + r_glow, sun_cy + r_glow], fill=(251, 191, 36, 45))

# Sun rays
ray_len_inner = 95
ray_len_outer = 125
for angle_deg in range(0, 360, 45):
    rad = math.radians(angle_deg)
    x1 = sun_cx + ray_len_inner * math.cos(rad)
    y1 = sun_cy + ray_len_inner * math.sin(rad)
    x2 = sun_cx + ray_len_outer * math.cos(rad)
    y2 = sun_cy + ray_len_outer * math.sin(rad)
    draw.line([(x1, y1), (x2, y2)], fill=(253, 224, 71, 230), width=14)

# Sun Core
draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(250, 204, 21, 255), outline=(234, 88, 12, 255), width=6)

# 3. Draw Isometric Cardboard Moving Box
# Top face points: (top, right, bottom, left)
p_top = (512, 330)
p_right = (770, 470)
p_bottom = (512, 610)
p_left = (254, 470)

# Bottom points
box_h = 240
p_bottom_l = (254, 470 + box_h)
p_bottom_c = (512, 610 + box_h)
p_bottom_r = (770, 470 + box_h)

# Drop shadow behind box
shadow_poly = [
    (240, 480 + box_h),
    (512, 630 + box_h),
    (780, 480 + box_h),
    (800, 520 + box_h),
    (512, 670 + box_h),
    (220, 520 + box_h)
]
shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_layer)
s_draw.polygon(shadow_poly, fill=(0, 0, 0, 90))
img.alpha_composite(shadow_layer)
draw = ImageDraw.Draw(img)

# Left Face (Darker Kraft)
draw.polygon([p_left, p_bottom, p_bottom_c, p_bottom_l], fill=(180, 83, 9, 255), outline=(140, 60, 5, 255), width=3)

# Right Face (Medium Kraft)
draw.polygon([p_bottom, p_right, p_bottom_r, p_bottom_c], fill=(217, 119, 6, 255), outline=(160, 80, 5, 255), width=3)

# Top Face (Lighter Kraft)
draw.polygon([p_top, p_right, p_bottom, p_left], fill=(245, 158, 11, 255), outline=(253, 230, 138, 200), width=4)

# Packing Tape across top
tape_w = 60
draw.polygon([
    (512 - tape_w, 330 + 35),
    (512 + tape_w, 330 + 35),
    (512 + tape_w, 610 - 35),
    (512 - tape_w, 610 - 35)
], fill=(254, 243, 199, 230))

# Tape down center front crease
draw.polygon([
    (512 - 20, 600),
    (512 + 20, 600),
    (512 + 20, 610 + box_h),
    (512 - 20, 610 + box_h)
], fill=(254, 240, 138, 220))

# White Arrow on Left Face (Upward moving direction)
# Arrow points
arrow_cx = 380
arrow_cy = 650
draw.polygon([
    (arrow_cx, arrow_cy - 45),
    (arrow_cx + 35, arrow_cy - 10),
    (arrow_cx + 15, arrow_cy - 10),
    (arrow_cx + 15, arrow_cy + 45),
    (arrow_cx - 15, arrow_cy + 45),
    (arrow_cx - 15, arrow_cy - 10),
    (arrow_cx - 35, arrow_cy - 10)
], fill=(255, 255, 255, 235))

# Export to various standard favicon formats
sizes = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "favicon-192x192.png": 192,
    "apple-touch-icon.png": 180
}

for filename, sz in sizes.items():
    resized = img.resize((sz, sz), Image.Resampling.LANCZOS)
    resized.save(filename)
    print(f"Generated {filename} ({sz}x{sz})")

# Generate standard multi-resolution favicon.ico
ico_sizes = [(16, 16), (32, 32), (48, 48)]
img.save("favicon.ico", format="ICO", sizes=ico_sizes)
print("Generated favicon.ico (16x16, 32x32, 48x48)")
