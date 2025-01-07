from PIL import Image, ImageFont, ImageDraw

def build_thumbnail(episode_data):
    image = None
    for image_step in episode_data['thumbnail_processor']['image_steps']:
        image = process_image_step(image_step['key'], image_step['values'], image, episode_data)
    image.show()
    image.save(episode_data['thumbnail_processor']['thumbnailOutputFormat'].format(**episode_data))

def process_image_step(key, values, image, episode_data):
    if (key == 'BackgroundImage'):
        return background_image(values)
    elif (key == 'CropCenterIdealThumbnailSize'):
        return crop(image, get_ideal_crop_size(image))#.resize((1280, 720)).convert("RGBA")
    elif (key == 'AddScaledImage'):
        return add_image(image, scale_image(values), values)
    elif (key == 'AddText'):
        add_text(image, values, episode_data)
    return image

def add_text(image, values, episode_data):
    font = ImageFont.truetype(values['font']['path'], values['font']['size'])

    fill_color = (values['fill']['r'], values['fill']['g'], values['fill']['b'])
    stroke_color = (values['stroke']['fill']['r'], values['stroke']['fill']['g'], values['stroke']['fill']['b'])

    I1 = ImageDraw.Draw(image)

    I1.text(
        (values['location']['x'], values['location']['y']),
        values['text'].format(**episode_data),
        font=font,
        fill=fill_color,
        stroke_width=values['stroke']['width'],
        stroke_fill=stroke_color,
        spacing = values['spacing'])
    return image

def add_image(image, image_to_add, values):
    img = image.copy().convert("RGBA")
    img.paste(image_to_add, (values['location']['x'], values['location']['y']), image_to_add)
    return img

def scale_image(values):
    image = Image.open(values['image_path'])
    width, height = image.size
    scale = values['scale']
    new_size = (int(width / scale), int(height / scale))
    return image.resize(new_size).convert("RGBA")

def get_ideal_crop_size(image):
    width, height = image.size
    left = (width - 1280) / 2
    right = 1280 + left
    upper = (height - 720) / 2
    bottom = 720 + upper
    return (left, upper, right, bottom)

def crop(image, crop_size):
    print(image.size)
    img = image.crop(crop_size)
    print(img.size)
    return img

def background_image(values):
    return Image.open(values['image_path'])