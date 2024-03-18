import re
from scamDetection import is_scam
from spamDetection import onMessageScamCheck
import io
from imageHateDetection import redactImage
import discord
from langdetect import detect
from googletrans import Translator
from detection import detectHate
from allowedCategories import AllowedCategories

# ================================= BLUR TEXT ===================================
def translate_text(text):
    translator = Translator()
    translated_text = translator.translate(text, dest="en")

    return translated_text.text

def blur_word(text, target_words):
 
    def childrenFn(text, target_word):
        original_language = detect(text)
        
        translator = Translator()
        translated_target_word = translator.translate(target_word, src="en", dest=original_language).text

        blurred_text = re.sub(rf'{translated_target_word}', lambda match: '#' * len(match.group()), text, flags=re.IGNORECASE)

        return blurred_text
 
    for target_word in target_words:
        text = childrenFn(text, target_word)

    return text

def blurText(text: str, guildId):
    hate_detections = detectHate(translate_text(text.lower()))

    arr_bad_word = []
    allowed_categories = AllowedCategories(guildId)

    toBlur = allowed_categories.filterWords(hate_detections[1]) 

    if (len(toBlur) != 0):
        for word_and_category in toBlur:
            arr_bad_word.append(word_and_category[0])

    else:
        return text

    return blur_word(text, arr_bad_word)

# ================================= bot helper functions ===================================
def get_categories_str(hate_detections):
    str = ''

    for word in hate_detections[1]:
        str += f'\n **{word[1]}**'

    return str

async def is_admin_role(guild: discord.Guild, requiredPermissons):
    for role in guild.roles:
        if role.permissions >= requiredPermissons:
            return role
    return None

# ================================= main checks ===================================
async def hateCheck(message):
    hate_detections = detectHate(translate_text(message.content.lower()))

    if (hate_detections[0] != 2):
        censored_message = blurText(message.content, message.guild.id)

        await message.delete()
        if (censored_message != message.content):
            await message.channel.send(f'***{message.author.name}*** : {censored_message}')
        else:
            await message.channel.send(f'***{message.author.name}*** : **message was removed**')

        hateDescription = "Hate Speech"
        if hate_detections[0] == 1:
            hateDescription = "Offensive Language"
        elif hate_detections[0] == 2:
            hateDescription = "No Hate and Offensive"

        await message.author.send(f'***{message.author.name}***  Your message was removed, because you used {hateDescription}:\n {get_categories_str(hate_detections)}')
        
async def imageHateCheck(message):
    image_url = message.attachments[0].url
    censored_image_url = redactImage(image_url, message.guild.id)
    await message.delete()
    with io.BytesIO() as image_binary:
        censored_image_url.save(image_binary, 'PNG')
        image_binary.seek(0)
        await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
    
async def scamCheck(message):
    if is_scam(translate_text(message.content)):
        await message.delete()
        await message.channel.send('Warning! It\'s a scam')
    
async def spamCeck(message):
    await onMessageScamCheck(message)

