
# # налаштування бота
# bot = telebot.TeleBot('6169616446:AAGlla-Ln4SrhTVVmrCCKbTc_pmp6BS-348')


# # налаштування OpenAI
# openai.api_key = os.environ['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']

import os
import telebot
import speech_recognition as sr
from deepspeech import Model, version
from pydub import AudioSegment
from pydub.playback import play
import openai_secret_manager

# get secrets
assert "telegram" in openai_secret_manager.get_services()
secrets = openai_secret_manager.get_secret("telegram")

# create a bot instance
bot = telebot.TeleBot("6169616446:AAGlla-Ln4SrhTVVmrCCKbTc_pmp6BS-348")

# initialize DeepSpeech model
model_file_path = 'deepspeech-0.9.3-models.pbmm'
lm_file_path = 'deepspeech-0.9.3-models.scorer'
beam_width = 500
lm_alpha = 0.75
lm_beta = 1.85

ds = Model(model_file_path)
ds.enableExternalScorer(lm_file_path)
ds.setBeamWidth(beam_width)
ds.setScorerAlphaBeta(lm_alpha, lm_beta)

# define function for processing voice messages
def process_voice_message(message):
    # download voice message
    voice = bot.download_file(bot.get_file(message.voice.file_id).file_path)

    # convert voice message to wav format
    audio = AudioSegment.from_file(io.BytesIO(voice), format="ogg")
    audio.export("voice.wav", format="wav")

    # recognize speech with DeepSpeech
    r = sr.Recognizer()
    with sr.AudioFile("voice.wav") as source:
        audio = r.record(source)
    text = ds.stt(audio.get_raw_data())

    # process text with GPT-3 API
    # (replace this with your own GPT-3 API credentials and implementation)
    response = openai.Completion.create(
        engine="davinci",
        prompt=text,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )
    text_processed = response.choices[0].text

    # convert processed text to speech with pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(text_processed, "response.mp3")
    engine.runAndWait()

    # send response as voice message
    with open("response.mp3", "rb") as f:
        bot.send_voice(message.chat.id, f)

# handle voice messages
@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    process_voice_message(message)

# start the bot
bot.polling()
