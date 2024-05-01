import base64
import textwrap
from inspect import cleandoc

import cv2
import moviepy.editor as mp
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Loads your API key from the .env file
oai = OpenAI()

MODEL = "gpt-4-vision-preview"
FPS = 2
FRAME_SIZE = 512
TEMPERATURE = 0.3
MAX_TOKENS = 500
SEED = 42


def deindent(text: str) -> str:
    return textwrap.dedent(cleandoc(text))


SYSTEM_MESSAGE = {
    "role": "system",
    "content": deindent(
        """
        As an expert fitness insctructor, your job is to give feedback on the form of the person in the video.

        If they are doing the exercise incorrectly:
            - List the mistakes. (At most 5 mistakes.)
            - For each mistake:
                - Teach them how to do it correctly. Just one line.
            - Don't mention the video or the frames.
            - No preamble or conclusion. Just the feedback.
            - Markdown format.

        If they are doing the exercise correctly:
            - Praise them and let them know they are doing a good job. Just one line.

        Address the person in the video as if they were your client. Don't be too verbose. Get to the point.
        Be strict in your analysis but have a positive attitude and be encouraging!
        """
    ),
}


def get_frames(vid_path: str, fps: int = FPS) -> list:
    vid = mp.VideoFileClip(vid_path)
    vid_fps = vid.fps
    return [
        base64.b64encode(cv2.imencode(".jpg", frame)[1]).decode("utf-8")
        for i, frame in enumerate(vid.iter_frames())
        if i % int(vid_fps / fps) == 0
    ]


def create_frames_message(frames: list, frame_size: int = FRAME_SIZE) -> dict:
    return {
        "role": "user",
        "content": [
            "These are frames from the same video. 1 frame per second. Please review them and provide feedback.",
            *map(lambda x: {"image": x, "resize": frame_size}, frames),
        ],
    }


def create_messages(
    video_path: str, fps: int = FPS, frame_size: int = FRAME_SIZE
) -> list:
    frames = get_frames(video_path, fps=fps)
    frames_message = create_frames_message(frames, frame_size=frame_size)
    return [SYSTEM_MESSAGE, frames_message]


def stream_response(res) -> str:
    feedback = ""
    for chunk in res:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")
            feedback += content
    return feedback


def get_feedback(
    messages: list,
    model: str = MODEL,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
    seed: int = SEED,
):
    
    result = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    feedback = result.choices[0].message.content
    return feedback
