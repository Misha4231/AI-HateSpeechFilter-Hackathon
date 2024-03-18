# Hate, Scam, and Spam Filter for Discord

The bot filters messages containing hate speech, potential scams, and spam using AI. Our bot also allows administrators to customize it completely to their preferences. The bot utilizes AI to detect the context of messages.

## Project was created at Bydgoszcz Hackathon 2024 in 24 hours with 6 developers:
* @Misha4231
* @Mirvik
* @rrrkkkvvv
* @A3rson
* @yuk1ko-chan

## Main Advantages:
* The bot works for every language.
* It can handle both text and images.
* The bot is not dependent on third-party APIs (we do not use ChatGPT or similar AI for detecting hate speech, scams, and spam).
* It can be customized for various purposes (administrators can choose categories of inappropriate words to detect and decide what to filter, for example, filter scams but not filter images).
* The bot can blur every inappropriate word on images.

## Installation
```bash
pip install -r requirements.txt
```
Add an environment (.env) file with the Discord bot token. For example:

```bash
# .env
BOT_TOKEN="Your bot token here"
```

If you are using Windows, provide the path to the pytesseract executable in the `imageHateDetection.py` file:
```python
pytesseract.pytesseract.tesseract_cmd = r"path to tesseract.exe"
```
Then, add it to the PATH variables.

If you are using Linux or MacOS, simply install it using the terminal.

The project utilizes the following libraries:
* discord.py
* sklearn, pandas, numpy
* googletrans
* nltk
* pytesseract

