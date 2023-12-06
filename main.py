import streamlit as st
import base64
import os
from openai import OpenAI # openai version 1.1.1
import instructor
import requests
from pydantic.main import BaseModel
st.image("stravamsging.png")
st.title("🏃‍♀️🚴‍♀️🏊StravaDM-GPT💦❤️💧")

class RunDetail(BaseModel):
  WorkoutName: str
  Distance: str
  Pace: str
  Time: str
  Achievements: int

class RideDetail(BaseModel):
  WorkoutName: str
  Distance: str
  ElevGain: str
  Time: str
  Achievements: str

class SwimDetail(BaseModel):
  WorkoutName: str
  Distance: str
  Time: str
  Pace: str

class GenWorkout(BaseModel):
  WorkoutName: str

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

strava_img= st.file_uploader("Upload a screenshot of a friend's👀 Strava workout!🔥⤵️", type=["png", "jpg","jpeg"])
if strava_img is not None and st.button('enter'):
  st.image(strava_img)
  with st.spinner('Processing📈...'):
    base64_image = encode_image(strava_img)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "What’s in this image?"
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions",   headers=headers, json=payload)
    print(response)

    client = instructor.patch(OpenAI())

    response_json = response.json()
    content = response_json['choices'][0]['message']['content']

    detect_workout = client.chat.completions.create(
      model="gpt-4",
      response_model=GenWorkout,
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Extract the workout name from the following json:" + content}
      ]
    )
    resp_model = ''
    workout_prompt = ''
    if "run" in str(detect_workout):
      resp_model = RunDetail
      workout_prompt = "Extract distance, pace, time, and achievements from the following json"
    elif "swim" in str(detect_workout):
      resp_model = SwimDetail
      workout_prompt = "Extract distance, time, and pace from the following json" + content
    elif "ride" in str(detect_workout):
      resp_model = RideDetail
      workout_prompt = "Extract distance, time, and elevation gain from the following json" + content
    else:
      resp_model = RunDetail
      workout_prompt = "Extract distance, pace, time, and achievements from the following json"+ content

    workout_info = client.chat.completions.create(
      model="gpt-4",
      response_model=resp_model,
      messages=[
          {"role": "user", "content": workout_prompt
          }
      ]
    )
    st.write(workout_info)
    gen_dm = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a helpful wingwoman with success in flirting."},
        {"role": "user", "content": "Craft a slightly-flirty, fun, jokey, personal complimentary message ideally using a workout pun with no more than 20 words based on" + str(workout_info)}
      ]
    )
    fin_msg = gen_dm.choices[0].message.content
    html_str = f"""
    <p style="font-family:Arial; color:Pink; font-size: 16px;">Slide   into that athlete's DMs with: {fin_msg}</p>
    """
    st.markdown(html_str, unsafe_allow_html=True)

st.markdown(
    """
    <p style="text-align: center;font-family:Arial; color:Pink; font-size: 12px;">Made with ❤️ in SF w/ OpenAI GPT-4V, Replit, Streamlit, & Pydantic. ✅ out <a href="https://replit.com/@LizzieSiegle/strava-dm-ai">the repl!</a></p>
    """,
    unsafe_allow_html=True
)