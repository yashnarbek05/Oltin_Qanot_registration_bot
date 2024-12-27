import os

from PIL import ImageFont, ImageDraw, Image

IMAGE_PATH_NAME = "images/default_badge.jpg"
FONT_PATH = "image/font/GarnetCapitals-Bold (1).ttf"

def write_name_and_second_name_to_badge(name, second_name, time, vol_id):
    photo_name = ""
    with Image.open(IMAGE_PATH_NAME) as im:

        print("photo opened for time and name")
        draw = ImageDraw.Draw(im)

        font = ImageFont.truetype(FONT_PATH, 180)

        width, height = im.size

        n_len = draw.textlength(name if len(name) > len(second_name) else second_name, font=font)

        draw.multiline_text(((width - n_len) / 2, height / 2 + 180),
                            name + "\n" + second_name,
                            "#ffe978",
                            font=font,
                            align="center")

        print("name are written!!!!!!!")

        photo_name = f"images/{name}_{second_name}.png"

        draw.text(((width/ 4) + 350, (height*3/4) - 300), str(vol_id), font=ImageFont.truetype(FONT_PATH, 120))
        print("id is written!!!!!!!")

        draw.text(((width/ 4) + 250, (height*3/4) + 50), time.split(" ").pop(0), font=ImageFont.truetype(FONT_PATH, 120))

        print("time is written!!!!!!!")

        im.save(photo_name)

    return photo_name


def add_photo_to_badge(name_written_photo, user_photo):
    # Open the original image and the target background image
    original_image = Image.open(user_photo)
    background_image = Image.open(name_written_photo)

    print("photo opened for avatar placement!!!")

    # Ensure both images are of the same mode (e.g., RGB) for compatibility
    original_image = original_image.convert('RGBA')
    background_image = background_image.convert('RGBA')

    width, height = original_image.size
    mask = Image.new("L", (width, height), 0)  # "L" mode creates a grayscale image
    draw = ImageDraw.Draw(mask)
    r = width if width < height else height
    draw.ellipse((0, 0, r, r), fill=255)  # Draw a white circle on the mask

    # Step 3: Apply the mask to the original image
    circular_cutout = Image.new("RGBA", (r,r))
    circular_cutout.paste(original_image, (0, 0), mask=mask)  # Paste the image with the mask

    print("photo is cutted!!!!!")

    # Step 4: Paste the circular cutout onto the background image
    bg_width, bg_height = background_image.size
    circular_cutout = circular_cutout.resize((int(bg_width/2) - 180, int(bg_width/2)-180))  # Resize cutout if needed
    x_offset = int((bg_width + 300) // 4)  # Center horizontally
    y_offset = int((bg_width + 1000) // 4)  # Center vertically
    background_image.paste(circular_cutout, (x_offset, y_offset), circular_cutout)

    # Step 5: Save the result
    background_image.save(name_written_photo)
    print("cutted photo was placed on back photo!!!")
    background_image.show()

    background_image.close()

    return name_written_photo

def prepare_badge(firstname, lastname, time, vol_id, photo):
    photo_path = write_name_and_second_name_to_badge(firstname,lastname, time, vol_id)
    return add_photo_to_badge(photo_path, photo)


