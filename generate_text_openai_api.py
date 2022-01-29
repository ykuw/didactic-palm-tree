import os
import openai

openai.api_key = ""

text = input("Enter something and the AI will continue to complete it: ")

request = openai.Completion.create(
	engine="davinci",
	prompt=f"{text}",
	max_tokens=50,
	n=4,
	best_of=25,
	temperature=0.9
)


def api_result():
	for response in request["choices"]:
		result = response["text"]
		return result


print(text + api_result())
