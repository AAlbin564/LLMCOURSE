from transformers import pipeline

pipe = pipeline("text-generation", model="janhq/Jan-v1-4B")
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)