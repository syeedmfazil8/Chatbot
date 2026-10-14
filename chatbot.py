from groq import Groq

client = Groq(api_key="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")

SYSTEM_PROMPT = "You are a friendly, helpful chatbot. Keep replies short and casual."
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("Chatbot ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["quit", "exit"]:
        print("Bot: Bye!")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )

    reply = response.choices[0].message.content
    print(f"Bot: {reply}\n")

    messages.append({"role": "assistant", "content": reply})