import pytesseract
from PIL import Image, ImageFilter
import requests
from io import BytesIO
import services

pytesseract.pytesseract.tesseract_cmd = r"E:\Tesseract\tesseract.exe"

def get_text_and_coordinates(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
   
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='eng+pol')

    textData = []
    for i, word in enumerate(data['text']):
        if word.strip():
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            coordinates = (x, y, x + w, y + h)  # (left, top, right, bottom)
            textData.append([word, coordinates])

    return image, textData

def blurBadWords(image: Image, wordsToBlur):
    for tD in wordsToBlur:
        croppedImage = image.crop(tD[1])

        blurredImage = croppedImage.filter(ImageFilter.GaussianBlur(radius=15))
        image.paste(blurredImage, tD[1])

    return image

def redactImage(url, guildId) -> Image:
    image, textData = get_text_and_coordinates(url)

    fullText = ""
    for t in textData:
        fullText += f'{t[0]} '
    
    bluredText = services.blurText(fullText, guildId) #blure(fullText)
    fullTextSp = fullText.split(' ')
    bluredTextSp = bluredText.split(' ')


    wordsToBlur = []
    for i in range(len(fullTextSp)):
        if fullTextSp[i] != bluredTextSp[i]:
            for tD in textData:
                if tD[0] == fullTextSp[i]:
                    wordsToBlur.append(tD)
                    break

    resImage = blurBadWords(image, wordsToBlur)

    return resImage



