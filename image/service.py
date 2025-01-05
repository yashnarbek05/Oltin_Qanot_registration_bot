from datetime import datetime

from PIL import ImageFont, ImageDraw, Image

IMAGE_PATH_NAME = "images/default_badge.jpg"
FONT_PATH = "image/font/GarnetCapitals-Bold (1).ttf"


async def write_name_and_second_name_to_badge(fullname, vol_id):
    photo_name = ""
    with Image.open(IMAGE_PATH_NAME) as im:
        draw = ImageDraw.Draw(im)

        names = fullname.split(" ")  # Sattorov Yashnarbek Quvonchbek o'g'li
        name = names[0]
        second_name = names[1]

        font = ImageFont.truetype(FONT_PATH, 160)

        width, height = im.size

        n_len = draw.textlength(name if len(name) > len(second_name) else second_name, font=font)

        draw.multiline_text(((width - n_len) / 2, height / 2 + 200),
                            name + "\n" + second_name,
                            "#ffe978",
                            font=font,
                            align="center")


        photo_name = f"images/{name}_{second_name}.png"

        draw.text(((width / 4) + 350, (height * 3 / 4) - 300), str(vol_id), font=ImageFont.truetype(FONT_PATH, 120))


        draw.text(((width / 4) + 250, (height * 3 / 4) + 50), datetime.now().strftime("%d.%m.%Y"),
                  font=ImageFont.truetype(FONT_PATH, 120))


        im.save(photo_name)

    return photo_name


async def add_photo_to_badge(name_written_photo, user_photo):
    # Open the original image and the target background image
    original_image = Image.open(user_photo)
    background_image = Image.open(name_written_photo)


    # Ensure both images are of the same mode (e.g., RGB) for compatibility
    original_image = original_image.convert('RGBA')
    background_image = background_image.convert('RGBA')

    width, height = original_image.size
    mask = Image.new("L", (width, height), 0)  # "L" mode creates a grayscale image
    draw = ImageDraw.Draw(mask)
    r = width if width < height else height
    draw.ellipse((0, 0, r, r), fill=255)  # Draw a white circle on the mask

    # Step 3: Apply the mask to the original image
    circular_cutout = Image.new("RGBA", (r, r))
    circular_cutout.paste(original_image, (0, 0), mask=mask)  # Paste the image with the mask


    # Step 4: Paste the circular cutout onto the background image
    bg_width, bg_height = background_image.size
    circular_cutout = circular_cutout.resize(
        (int(bg_width / 2) - 180, int(bg_width / 2) - 180))  # Resize cutout if needed
    x_offset = int((bg_width + 290) // 4)  # Center horizontally
    y_offset = int((bg_width + 1000) // 4)  # Center vertically
    background_image.paste(circular_cutout, (x_offset, y_offset), circular_cutout)


    # Step 5: Save the result
    resized_image = background_image.resize((860,1200))

    resized_image.save(name_written_photo)

    background_image.close()

    return name_written_photo


async def prepare_badge(fullname, vol_id, photo):
    photo_path = await write_name_and_second_name_to_badge(fullname, vol_id)
    photo_path = await add_photo_to_badge(photo_path, photo)

    return photo_path
