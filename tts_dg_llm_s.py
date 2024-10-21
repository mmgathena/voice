# Copyright 2024 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

import time
# from deepgram.utils import verboselogs
from dotenv import load_dotenv
load_dotenv()

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)
import openai
import os

TTS_TEXT = "Hello, this is a text to speech example using Deepgram."

client = openai.OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# client = openai.OpenAI(
#     base_url = 'http://localhost:11434/v1',
#     api_key='ollama', # required, but unused
# )
global warning_notice
warning_notice = True

config: DeepgramClientOptions = DeepgramClientOptions(
    options={
        # "auto_flush_speak_delta": "500",
        "speaker_playback": "true",
    },
    # verbose=verboselogs.DEBUG,
)
deepgram_tts: DeepgramClient = DeepgramClient("", config)


def tts_dg(TTS_TEXT):
    try:
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM

        # completion = client.chat.completions.create(
        #     model="llama3-8b-8192",
        #     messages=[
        #         {"role": "system", "content": "You are an famous Youtube podcaster named Mr. Beast. You have an engaging and energetic style. Please respond in two lines only"},
        #         {
        #             "role": "user",
        #             "content": TTS_TEXT
        #         }
        #     ]
        # )

        # llm_response_full = completion.choices[0].message.content
        # print(f"LLM: {llm_response_full}")
        # Create a websocket connection to Deepgram
        dg_connection_tts = deepgram_tts.speak.websocket.v("1")

        def on_open(self, open, **kwargs):
            print(f"\n\n{open}\n\n")

        def on_binary_data(self, data, **kwargs):
            global warning_notice
            if warning_notice:
                print("Received binary data")
                print("You can do something with the binary data here")
                print("OR")
                print(
                    "If you want to simply play the audio, set speaker_playback to true in the options for DeepgramClientOptions"
                )
                warning_notice = False

        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        def on_flush(self, flushed, **kwargs):
            print(f"\n\n{flushed}\n\n")

        def on_clear(self, clear, **kwargs):
            print(f"\n\n{clear}\n\n")

        def on_close(self, close, **kwargs):
            print(f"\n\n{close}\n\n")

        def on_warning(self, warning, **kwargs):
            print(f"\n\n{warning}\n\n")

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        def on_unhandled(self, unhandled, **kwargs):
            print(f"\n\n{unhandled}\n\n")

        dg_connection_tts.on(SpeakWebSocketEvents.Open, on_open)
        dg_connection_tts.on(SpeakWebSocketEvents.AudioData, on_binary_data)
        dg_connection_tts.on(SpeakWebSocketEvents.Metadata, on_metadata)
        dg_connection_tts.on(SpeakWebSocketEvents.Flushed, on_flush)
        dg_connection_tts.on(SpeakWebSocketEvents.Cleared, on_clear)
        dg_connection_tts.on(SpeakWebSocketEvents.Close, on_close)
        dg_connection_tts.on(SpeakWebSocketEvents.Error, on_error)
        dg_connection_tts.on(SpeakWebSocketEvents.Warning, on_warning)
        dg_connection_tts.on(SpeakWebSocketEvents.Unhandled, on_unhandled)

        # connect to websocket
        options = SpeakWSOptions(
            model="aura-asteria-en",
            encoding="linear16",
            sample_rate=16000,
        )

        print("\n\nPress Enter to stop...\n\n")
        if dg_connection_tts.start(options) is False:
            print("Failed to start connection")
            return

        messages = [
                {
                    "role": "system",
                    "content": "You are an famous Youtube podcaster named Mr. Beast. You have an engaging and energetic style. Please respond in two lines only",
                },
                {"role": "user", "content": TTS_TEXT},
            ]
        
        for response in client.chat.completions.create(
            model="llama3-8b-8192",
            # model="lstorm",
            messages=messages,
            stream=True,
        ):
            print(time.time())
            # here is the streaming response
            for chunk in response:
                if chunk[0] == "choices":
                    llm_output = chunk[1][0].delta.content
                    print(llm_output)

                    # skip any empty responses
                    if llm_output is None or llm_output == "":
                        continue

                    # send to Deepgram TTS
                    # send the text to Deepgram
                    dg_connection_tts.send_text(llm_output.lower())

        

        # if auto_flush_speak_delta is not used, you must flush the connection by calling flush()
        dg_connection_tts.flush()

        # Indicate that we've finished
        dg_connection_tts.wait_for_complete()

        # print("\n\nPress Enter to stop...\n\n")
        # input()

        # Close the connection
        dg_connection_tts.finish()

        print("Finished")

    except ValueError as e:
        print(f"Invalid value encountered: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    tts_dg(TTS_TEXT)