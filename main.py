from flask import Flask, abort, make_response, request
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
from flask_cors import CORS, cross_origin
import requests
import datetime
import json
import random


app = Flask(__name__)
CORS(app)


def getGame(id):

    url = "https://api.turftown.in/api/v2/game/share/"+id
    
    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data["data"]["type"])
    vs_Data = data["data"]["type"]
    date = data["data"]["start_time"]
    start_time = data["data"]["start_time"]
    end_time = data["data"]["end_time"]
    gameKind = data["data"]["sport_name"]
    courtImage = data["data"]["image"]
    # convert the date format from 2020-08-21T19:00:00.000Z to Wed . Aug 21st
    date = date.split("T")
    date = date[0]
    date = date.split("-")
    date = date[2]+" . "+date[1]+" "+date[0]
    start_time = start_time.split("T")
    start_time = start_time[1]
    start_time = start_time.split(":")
    start_time = start_time[0]+":"+start_time[1]
    end_time = end_time.split("T")
    end_time = end_time[1]
    end_time = end_time.split(":")
    end_time = end_time[0]+":"+end_time[1]
    if int(start_time.split(":")[0]) < 12:
        start_time = start_time+" am"
    else:
        start_time = start_time+" pm"
    if int(end_time.split(":")[0]) < 12:
        end_time = end_time+" am"
    else:
        end_time = end_time+" pm"
    time = start_time+" - "+end_time
    
    # start_time should be in 12 hour format example 17:30 pm to 5:30 pm

    start_time = datetime.datetime.strptime(start_time, '%H:%M %p')

    # end_time should be in 12 hour format example 17:30 pm to 5:30 pm
    end_time = datetime.datetime.strptime(end_time, '%H:%M %p')

    # convert from utc to ist
    start_time = start_time + datetime.timedelta(hours=5, minutes=30)
    end_time = end_time + datetime.timedelta(hours=5, minutes=30)

    time  = start_time.strftime('%I:%M %p') + " - " + end_time.strftime('%I:%M %p')


    # 09 . 02 2023 to Day Month Date
    
    date_str = date
    date_object = datetime.datetime.strptime(date_str, "%d . %m %Y")
    
    day_suffix = "th" if 4 <= date_object.day <= 20 or 24 <= date_object.day <= 30 else ["st", "nd", "rd"][date_object.day % 10 - 1]
    
    date = date_object.strftime("%a %b %-d" + day_suffix)

    data = {
        "date": date,
        "time": time,
        "vs": vs_Data,
        "courtImage": courtImage,
        "gameKind": gameKind
    }

    return data

@app.route('/image')
def image_endpoint():
    id = request.args.get('id')
    game = getGame(id)
    date = game['date']
    time = game['time']
    vs = game['vs']
    courtImage = game['courtImage']
    gameKind = game['gameKind']
    img = Image.new('RGB', (1200, 630), color='white')
    draw = ImageDraw.Draw(img)
    bg = Image.open('assets/image/BG.png')
    img.paste(bg, (0, 0))
    text = "Join my Game on"
    try:
     font = ImageFont.truetype('assets/fonts/Nexa-Trial-Heavy.ttf', 80)
    except:
        permission = oct(os.stat('assets/fonts/NexaDemo-Bold.ttf').st_mode)[-3:]
        font = ImageFont.load_default()
    
    
    draw.text((70, 50), text, fill='white', font=font)
    calender = Image.open('assets/image/Date.png')
    img.paste(calender, (70, 430), calender)
    timer = Image.open('assets/image/Time.png')
    img.paste(timer, (70, 530), timer)
    location = Image.open('assets/image/Court.png')
    court = Image.open(requests.get(courtImage, stream=True).raw)
    court = court.resize((274, 273))
    img.paste(court, (800, 120), location)
    game = Image.open('assets/image/TurfTownLogo.png')
    img.paste(game, (70, 180), game)
    micro = Image.open('assets/image/MicroBanner.png')
    img.paste(micro, (850, 350), micro)
    font = ImageFont.truetype('assets/fonts/NexaText-Trial-Bold.ttf', 37)
    text = vs if vs is not None else "6 v 6"
    #text_width, text_height = draw.textsize(text, font)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]  # Width of the text
    text_height = bbox[3] - bbox[1]  # Height of the text
    text_x = (micro.width - text_width) / 2 + 850
    text_y = (micro.height - text_height) / 2 + 340
    # Nexa-Text Regular
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    font = ImageFont.truetype('assets/fonts/NexaText-Trial-Regular.ttf', 47)
    if date is None:
        date = "Wed . Aug 21st"
    draw.text((150, 428), date, fill='white', font=font)
    font = ImageFont.truetype('assets/fonts/NexaText-Trial-Regular.ttf', 47)

    if time is None:
        time = "7:00 pm - 10:30 pm"
    draw.text((150, 528), time, fill='white', font=font)

    if gameKind is None:
        gameKind = "Football"
    icon_path = 'assets/image/' + gameKind.lower() + '.png'
    if not os.path.exists(icon_path):
        icon_path = 'assets/image/football.png'
    burn = Image.open(icon_path)
    img.paste(burn, (1040, 470), burn)
    #img = img.resize((int(img.width/2), int(img.height/2)), Image.ANTIALIAS)
    img = img.resize((int(img.width/2), int(img.height/2)), resample=Image.LANCZOS)
    os.makedirs('generated', exist_ok=True)
    img.save('generated/image.jpeg')
    response = make_response(open('generated/image.jpeg', 'rb').read())
    response.headers.set('Content-Type', 'image/jpeg')
    return response

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def getVenue(id):
    url = "https://devstage.turftown.in/api/v3/venue/get_venue_info/"+id
    payload={}
    headers = {
      'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVlMDIwNjk4MTdmNTE3NmRmZmZhNmNmNSIsInBob25lIjoiOTM0NzYwMzAxMyIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjc3NzI2NjUyfQ.mOa7eq4jKRvOripCXh74kJFjCo8KVOngdGHPb2bDb9E'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    # json parse and return
    return json.loads(response.text)

@app.route('/venue')
def venue_endpoint():
    id = request.args.get('id')
    venue = getVenue(id)
    spotlight_picture = venue['data']['venue']['spotlight_picture']
    rating = venue['data']['ratings_and_reviews']['rating']
    area = venue['data']['venue']['area']
    address = venue['data']['venue']['address']
    name = venue['data']['venue']['name']
    print(spotlight_picture, rating, area, address, name)
    img = Image.new('RGB', (1200, 630), color='white')
    draw = ImageDraw.Draw(img)
    bg = Image.open('assets/venue/venueBG.png')
    img.paste(bg, (0, 0))
    text_line1 = "Check this"
    text_line2 = "venue out on"
    try:
        font = ImageFont.truetype('assets/fonts/Nexa-Trial-Heavy.ttf', 100)
    except:
        permission = oct(os.stat('assets/fonts/NexaDemo-Bold.ttf').st_mode)[-3:]
        font = ImageFont.load_default()
    draw.text((70, 90), text_line1, fill='white', font=font)
    draw.text((70, 220), text_line2, fill='white', font=font)

    # logo below the text turfLogo
    turfLogo = Image.open('assets/venue/turfLogo.png')
    img.paste(turfLogo, (73, 390), turfLogo)

    venueImage = Image.open(requests.get(spotlight_picture, stream=True).raw).convert("RGBA")
    venueImage = venueImage.resize((320, 320))
    venueImage = add_corners(venueImage, 50)
    img.paste(venueImage, (800, 120), venueImage)

    # add emptyRatingsBanner under the venueImage
    emptyRatingsBanner = Image.open('assets/venue/emptyRatingsBanner.png')
    img.paste(emptyRatingsBanner, (820, 360), emptyRatingsBanner)

    # add rating on the emptyRatingsBanner where ratings is two decimal points
    rating  = float(rating)
    rating = str(rating)
    font = ImageFont.truetype('assets/fonts/Nexa-Trial-Heavy.ttf', 60)
    draw.text((890, 390), rating, fill='white', font=font)

    # add StarVenue.png after the rating
    starVenue = Image.open('assets/venue/StarVenue.png')
    img.paste(starVenue, (1000, 400), starVenue)

    font = ImageFont.truetype('assets/fonts/NexaText-Trial-Bold.ttf', 37)
    text = name
    os.makedirs('generated', exist_ok=True)
    img.save('generated/venue.jpeg')
    response = make_response(open('generated/venue.jpeg', 'rb').read())
    response.headers.set('Content-Type', 'image/jpeg')


    return response
    

def hex_mask_from_frame(frame_img, inset_ratio=0.922):
    w, h = frame_img.size
    alpha = frame_img.split()[-1]
    inset_w = int(w * inset_ratio)
    inset_h = int(h * inset_ratio)
    small = alpha.resize((inset_w, inset_h), Image.LANCZOS)
    mask = Image.new('L', (w, h), 0)
    mask.paste(small, ((w - inset_w) // 2, (h - inset_h) // 2))
    return mask


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


@app.route('/host')
def host_endpoint():
    name = request.args.get('name')
    image_url = request.args.get('image')
    subtitle = request.args.get('text', 'Come join my games!')

    if not name:
        abort(400, description="Missing required 'name' parameter.")
    if not image_url:
        abort(400, description="Missing required 'image' parameter.")
    if not image_url.startswith(('http://', 'https://')):
        abort(400, description="Invalid 'image' URL.")

    try:
        img = Image.open('assets/host/host_og_background.png').convert('RGB')
    except Exception as exc:
        abort(500, description=f"Failed to load background asset: {exc}")

    draw = ImageDraw.Draw(img)

    frame_color = random.choice(['blue', 'brown', 'violet', 'green', 'purple'])
    try:
        frame = Image.open('assets/host/frame_' + frame_color + '.png').convert('RGBA')
    except Exception as exc:
        abort(500, description=f"Failed to load frame asset: {exc}")

    pic_box = (952, 106, 500, 556)
    frame = frame.resize((pic_box[2], pic_box[3]), Image.LANCZOS)
    img.paste(frame, (pic_box[0], pic_box[1]), frame)

    try:
        photo_response = requests.get(image_url, stream=True, timeout=15)
        photo_response.raise_for_status()
        photo = Image.open(photo_response.raw).convert('RGB')
    except Exception as exc:
        abort(400, description=f"Failed to fetch or open image: {exc}")

    mask = hex_mask_from_frame(frame)

    target_w, target_h = pic_box[2], pic_box[3]
    photo = ImageOps.fit(photo, (target_w, target_h), method=Image.LANCZOS)
    img.paste(photo, (pic_box[0], pic_box[1]), mask)

    name_font = _load_font('assets/fonts/nexaandnexatextotf/Fontfabric - Nexa Extra Bold.otf', 128)
    name_box = (879, 710, 640, 180)
    bbox = draw.textbbox((0, 0), name, font=name_font)
    text_x = name_box[0] + (name_box[2] - (bbox[2] - bbox[0])) / 2
    text_y = name_box[1] + (name_box[3] - (bbox[3] - bbox[1])) / 2
    draw.text((text_x, text_y), name, fill='#E1E2E5', font=name_font)

    body_font = _load_font('assets/fonts/nexaandnexatextotf/Fontfabric - Nexa Text Bold.otf', 112)
    body_box = (642, 923, 1118, 156)
    bbox = draw.textbbox((0, 0), subtitle, font=body_font)
    text_x = body_box[0] + (body_box[2] - (bbox[2] - bbox[0])) / 2
    text_y = body_box[1] + (body_box[3] - (bbox[3] - bbox[1])) / 2
    draw.text((text_x, text_y), subtitle, fill='#B4B4B8', font=body_font)

    img = img.resize((int(img.width / 2), int(img.height / 2)), resample=Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers.set('Content-Type', 'image/jpeg')
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
