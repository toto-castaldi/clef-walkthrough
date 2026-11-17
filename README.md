# Clef walkthrough

Percorso di studio personale del modello **Clef** di Cloudflare.

usa APPUNTI.md e DA_APPROFONDIRE.md su richiesta dell'utente

- Pagina del modello: https://huggingface.co/Cloudflare/clef
- Annuncio sul blog Cloudflare: https://blog.cloudflare.com/clef-decision-models
- Demo https://huggingface.co/spaces/hugging-apps/clef-decision-model

## Esempi di chiamata API al playground

```bash
export HT_TOKEN=[hf-token]
uv run clef_playground.py --state "A user shared this mobile phone screenshot." --questions questions/platform_choice.json --image resources/phone-screenshot.png
```
