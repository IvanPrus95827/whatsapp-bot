import google.generativeai as genai
import config
import time

message_texts= [
    "📣 Remember to post up when done. We love to see how people are getting on and we mark you off for the week! We'll do shout outs later tonight",
    "Week 4 done ✔️ 🥵",
    "Pilates class done ✔️",
    "Week 6 ✅",
    "Week 7 done",
    "Week 7 done, in hotel gym with the squishiest most useless foam roller🙄🗑️",
    "Week 7 done ☑️ I like the foam roller classes.",
    "Week 7 done , have to catch up on week 6",
    "Week 8 done. Great class 👌",
    "I’ve done the blitz, I’ll try another class on Saturday",
    "20min blitz + foam rolling done",
    "20 minutes of week 5 done. Will finish at the weekend",
    "Hip and groin class done✅ great exercises to help with my niggles 👏",
    "Q and A (12 August 2025) Spotify: https://open.spotify.com/episo...Facebook Group: https://www.facebook.com/group... YouTube: https://youtu.be/ViM1U5HQYw0",
    "can you create virtual pilates group that contains me named 'Virtual Sport Pilates'?",
    "I got it.",
    "Pilates class done ✔️",
    "Well done, Brian, Vera and Margaret. 🙌🏻"
]

for message_text in message_texts:
    gemini_api_key = config.GEMINI_API_KEY
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = config.GEMINI_ANALYSIS_PROMPT.format(message_text=message_text)

    response = model.generate_content(prompt)
    result = response.text.strip()

    print(f"Gemini analysis for '{message_text[:50]}...': {result}")
    print(result == "YES")

    time.sleep(5)