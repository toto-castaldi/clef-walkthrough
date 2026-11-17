# /// script
# requires-python = ">=3.10"
# dependencies = ["gradio_client"]
# ///
"""Chiama il playground di Clef (Space Hugging Face) via API Gradio.

Non è l'API ufficiale di Cloudflare (`/v1/systemone`), ma lo Space demo
https://huggingface.co/spaces/hugging-apps/clef-decision-model, che restituisce
lo stesso formato di risposta SystemOne.

"""

import argparse
import json
import os
from pathlib import Path

from gradio_client import Client, handle_file

SPACE = "hugging-apps/clef-decision-model"


def load_questions(value: str) -> dict:
    """Accetta un percorso a un file JSON oppure il JSON scritto inline."""
    path = Path(value)
    text = path.read_text() if path.is_file() else value
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", required=True, help="stato: testo libero o JSON")
    parser.add_argument("--questions", required=True, help="file .json o JSON inline")
    parser.add_argument("--image", help="percorso locale o URL pubblico di un'immagine")
    args = parser.parse_args()

    questions = load_questions(args.questions)

    client = Client(SPACE, token=os.environ.get("HF_TOKEN"), verbose=False)
    _html, response = client.predict(
        state=args.state,
        questions=json.dumps(questions),
        image=handle_file(args.image) if args.image else None,
        api_name="/decide",
    )
    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
