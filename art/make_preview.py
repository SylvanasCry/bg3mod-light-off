"""Build the Light Off preview image (1600x900).

Usage: python make_preview.py <Spell_Evocation_Light.png> <out.png>
The icon is the game's tooltip icon (Game.pak: Public/Game/GUI/Assets/Tooltips/Icons/
Spell_Evocation_Light.DDS) converted to PNG.
"""
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 900
GOLD = (217, 192, 138)
FONT_SERIF = "C:/Windows/Fonts/georgia.ttf"
FONT_SERIF_BOLD = "C:/Windows/Fonts/georgiab.ttf"


def background():
    """
    Dark radial gradient in the BG3 tooltip palette.
    """
    small = Image.new("RGB", (160, 90))
    px = small.load()
    cx, cy = 52, 45
    for y in range(90):
        for x in range(160):
            d = min(1.0, (((x - cx) / 95) ** 2 + ((y - cy) / 60) ** 2) ** 0.5)
            inner, outer = (46, 36, 52), (12, 9, 14)
            px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * d) for i in range(3))
    return small.resize((W, H), Image.BICUBIC).convert("RGBA")


def fade_edges(icon):
    """
    The tooltip DDS carries a faint fill over the whole square; fade alpha radially so no
    square edge shows on the dark background.
    """
    size = icon.size[0]
    mask = Image.new("L", icon.size, 0)
    px = mask.load()
    c = size / 2
    for y in range(size):
        for x in range(size):
            r = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / size
            px[x, y] = 255 if r < 0.40 else max(0, int(255 * (0.49 - r) / 0.09))
    r, g, b, a = icon.split()
    a = Image.composite(a, Image.new("L", icon.size, 0), mask)
    return Image.merge("RGBA", (r, g, b, a))


def glow(icon, color, radius):
    """
    Soft colored halo built from the icon's alpha channel.
    """
    alpha = icon.split()[3].filter(ImageFilter.GaussianBlur(radius))
    layer = Image.new("RGBA", icon.size, color + (0,))
    layer.putalpha(alpha)
    return layer


def switch(scale=1.0):
    """
    Toggle switch in the OFF position: dark track, gold rim, knob on the left.
    """
    w, h = int(380 * scale), int(180 * scale)
    pad = int(40 * scale)
    img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad + 8, pad + 14, pad + w + 8, pad + h + 14), radius=h // 2, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(14 * scale)))

    d = ImageDraw.Draw(img)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), radius=h // 2, fill=GOLD)
    rim = int(9 * scale)
    d.rounded_rectangle((pad + rim, pad + rim, pad + w - rim, pad + h - rim),
                        radius=h // 2 - rim, fill=(34, 30, 38))

    font = ImageFont.truetype(FONT_SERIF_BOLD, int(64 * scale))
    tx = pad + int(w * 0.70)
    d.text((tx, pad + h // 2), "OFF", font=font, fill=(150, 140, 150), anchor="mm")

    k = h - 2 * rim - int(16 * scale)
    kx, ky = pad + rim + int(8 * scale), pad + rim + int(8 * scale)
    d.ellipse((kx, ky, kx + k, ky + k), fill=(205, 205, 212))
    hl = int(k * 0.22)
    d.ellipse((kx + hl, ky + hl * 0.6, kx + k - hl * 1.6, ky + k * 0.45), fill=(240, 240, 245))
    d.ellipse((kx, ky, kx + k, ky + k), outline=(120, 120, 130), width=max(2, int(3 * scale)))
    return img


def main(icon_path, out_path):
    canvas = background()

    icon = fade_edges(Image.open(icon_path).convert("RGBA").resize((640, 640), Image.LANCZOS))
    ix, iy = 150, 110
    # Blur on a padded copy, otherwise the halo is clipped to the icon square.
    m = 160
    padded = Image.new("RGBA", (640 + 2 * m, 640 + 2 * m), (0, 0, 0, 0))
    padded.alpha_composite(icon, (m, m))
    canvas.alpha_composite(glow(padded, (120, 190, 230), 40), (ix - m, iy - m))
    canvas.alpha_composite(icon, (ix, iy))

    sw = switch(1.0)
    canvas.alpha_composite(sw, (ix + 330, iy + 430))

    d = ImageDraw.Draw(canvas)
    title = ImageFont.truetype(FONT_SERIF_BOLD, 132)
    sub = ImageFont.truetype(FONT_SERIF, 44)
    d.text((1180, 380), "Light Off", font=title, fill=GOLD, anchor="mm")
    d.line((930, 470, 1430, 470), fill=(GOLD[0], GOLD[1], GOLD[2], 160), width=2)
    d.text((1180, 530), "Douse the Light cantrip", font=sub, fill=(220, 214, 224), anchor="mm")
    d.text((1180, 590), "free action \u2022 keeps stealth", font=sub, fill=(170, 162, 176), anchor="mm")

    canvas.convert("RGB").save(out_path, quality=95)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
