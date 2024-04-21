import openai
import time
from typing import Any, Mapping
import flask
#import functions_framework

# Initialisez la clé API d'OpenAI
openai.api_key = "YOUR API TOKEN HERE"

# Dictionnaire pour stocker l'historique des échanges pour chaque utilisateur
user_histories = {}

def send_to_openai_and_get_response(history):
    end_time = time.time() + 5  # Fin de la période d'attente de 5 secondes
    while time.time() < end_time:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=history
            )
            return completion.choices[0].message['content']

        except openai.error.OpenaiError as e:
            time.sleep(1)  # Attendre 1 seconde avant d'essayer à nouveau
            continue

    # Si le code atteind ce point, cela signifi que la tentative de 5 secondes a échouée
    return "Désolé, une erreur est survenue lors de la communication avec OpenAI. Veuillez réessayer plus tard."

@functions_framework.http
def google_chat(req: flask.Request) -> Mapping[str, Any]:
    if req.method == 'GET':
        return 'Sorry, this function must be called from a Google Chat.'

    request_json = req.get_json(silent=True)
    user_input_text = request_json["message"]["text"]
    user_id = request_json["message"]["sender"]["name"]

    # Optional : Slash command / Gérer l'événement de commande à barre oblique
    if slash_command := request_json.get('message', {}).get('slashCommand'):
        command_id = slash_command['commandId']
        if command_id == 1:
            user_input_text = "translate to english: " + user_input_text
        elif command_id == 2:
            user_input_text = "translate to spanish: " + user_input_text
        elif command_id == 3:
            user_input_text = "translate to german: " + user_input_text
        elif command_id == 4:
            user_input_text = "translate to french: " + user_input_text
        elif command_id == 5:
            user_input_text = "translate the following text in this four languages : french, english, spanish and german (and write each translation on a separate line), here is my text: " + user_input_text
        elif command_id == 6:
            user_input_text = "Summarize this text with a markdown list of the key points. Finally, list the next steps or action items suggested, if any. here is the text : " + user_input_text
        elif command_id == 7:
            user_input_text = "you are a professional web developer with 20 years of work experience in ,php, python, javascript, node.js, in back-end and front-end development, please help me with my problem : " + user_input_text
        elif command_id == 8:
            user_input_text = "you are a highly experienced hardware engineer, in electonic engineering, embedded software (mainly with C language), and mechanical engineering, please help me with this problem : " + user_input_text
        elif command_id == 9:
            user_input_text = "You are a highly experienced marketing professionnal with great writing skills, please help me write on this subject : " + user_input_text


    # Récupérez l'historique de l'utilisateur ou initialisez un nouvel historique
    history = user_histories.get(user_id, [
        {"role": "system", "content": "You are a helpful assistant."}
    ])
    history.append({"role": "user", "content": user_input_text})

    # Envoyez l'historique complet à OpenAI
    response_text = send_to_openai_and_get_response(history)

    # Mettez à jour l'historique de l'utilisateur avec le message de l'utilisateur ET la réponse d'OpenAI
    history.append({"role": "assistant", "content": response_text})
    user_histories[user_id] = history

    # Limitez la longueur de l'historique pour éviter de dépasser les limites de l'API
    if len(history) > 10:
        del history[0]

    return {"text": response_text}
