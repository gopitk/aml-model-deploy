import os
import openai
import gradio as gr
from typing import List, Tuple

# Configuration
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
MODEL_NAME = os.getenv("VLLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Answer clearly and concisely."
)

# The OpenAI client pointed at the vLLM OpenAI-compatible server.
# vLLM does not require a real key; a placeholder is fine.
openai_client = openai.OpenAI(
    base_url=VLLM_BASE_URL,
    api_key=os.getenv("OPENAI_API_KEY", "EMPTY")
)


def build_messages(history: List[Tuple[str, str]], user_message: str):
    """
    Convert Gradio (user, assistant) history plus current user_message
    into OpenAI ChatCompletion messages format.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user, assistant in history:
        if user:
            messages.append({"role": "user", "content": user})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    if user_message:
        messages.append({"role": "user", "content": user_message})
    return messages


def stream_chat(history: List[Tuple[str, str]], user_message: str):
    """
    Gradio generator function that streams model response tokens.
    """
    messages = build_messages(history, user_message)

    # Start with an empty assistant reply; accumulate as tokens arrive.
    assistant_reply = ""
    try:
        stream = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                assistant_reply += delta.content
                # Yield updated history (including the in-progress assistant reply)
                yield assistant_reply
    except Exception as e:
        assistant_reply += f"\n[Error: {e}]"
        yield assistant_reply


def gradio_chat(user_message, chat_history: List[Tuple[str, str]]):
    """
    Wrapper for non-streaming mode (not used if we enable streaming interface).
    """
    messages = build_messages(chat_history, user_message)
    try:
        completion = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
            stream=False,
        )
        assistant_reply = completion.choices[0].message.content
    except Exception as e:
        assistant_reply = f"[Error: {e}]"
    chat_history.append((user_message, assistant_reply))
    return "", chat_history


def main():
    with gr.Blocks(title="vLLM Chat UI") as demo:
        gr.Markdown("# Chat with TinyLlama via vLLM\n"
                    "Backend: vLLM OpenAI-compatible server\n"
                    f"Model: `{MODEL_NAME}`\n"
                    f"Base URL: `{VLLM_BASE_URL}`")

        with gr.Row():
            with gr.Column():
                chat = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    height=500,
                    placeholder="Model replies will appear here."
                )
                user_input = gr.Textbox(
                    placeholder="Type your message and press Enter",
                    label="Your Message"
                )
                clear_btn = gr.Button("Clear")

        # Streaming: use Chatbot + generator
        def user_submit(message, history):
            # Append placeholder for assistant which will be filled via stream
            history = history + [[message, ""]]
            return "", history

        def bot_response(history):
            user_message = history[-1][0]
            prior = history[:-1]
            # Stream tokens updating the last assistant message
            assistant_accum = ""
            for partial in stream_chat(prior, user_message):
                history[-1][1] = partial
                yield history

        user_input.submit(
            user_submit,
            [user_input, chat],
            [user_input, chat],
            queue=False
        ).then(
            bot_response,
            [chat],
            [chat]
        )

        clear_btn.click(lambda: None, None, chat, queue=False)

    demo.queue()  # Enable queuing for concurrency
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()
