# Clef walkthrough

Percorso di studio personale del modello **Clef** di Cloudflare.

- Pagina del modello: https://huggingface.co/Cloudflare/clef
- Annuncio sul blog Cloudflare: https://blog.cloudflare.com/clef-decision-models

> Le informazioni qui sotto vengono dalla model card su Hugging Face (consultata il 2026-11-16).
> Numeri e affermazioni sono quelli dichiarati da Cloudflare: non li ho verificati in modo indipendente.

---

## Cos'è Clef

Clef è un **"decision model"** multimodale da **27B parametri**. Riceve due cose:

1. uno **stato**, cioè la situazione da valutare: testo, JSON, immagini o video;
2. uno **schema di domande tipizzate**.

Restituisce una **probabilità per ogni opzione ammessa di ogni domanda**, tutto in un **solo forward pass**.
Non genera testo libero, quindi non c'è output da interpretare con un parser.

In pratica: un LLM classico "scrive" una risposta, che poi va interpretata. Clef invece
**assegna un punteggio a un insieme chiuso di opzioni** e produce subito una distribuzione di probabilità.

Fa parte della collezione open-weight **Clef**, insieme alla variante più piccola e veloce
[**Clef-Flash**](https://huggingface.co/Cloudflare/clef-flash): 9B parametri, ottenuta con un post-training di Qwen/Qwen3.5-9B.

## Architettura

| Componente | Descrizione |
|---|---|
| **Backbone** | [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), compreso il suo vision encoder. Clef è un *post-training* di questo modello. |
| **Joint schema head** | Un piccolo transformer posto sopra gli hidden state finali del backbone. Instrada le informazioni dello stato verso ogni domanda e assegna un punteggio a tutte le opzioni di tutte le domande **insieme** (*jointly*). |
| **Output** | Un logit per ogni opzione di ogni domanda. Una softmax **per domanda** trasforma i logit in probabilità. |

- Pesi in formato **BF16**, file **safetensors** suddivisi in più parti (*sharded*).
- La card cita il tag `qwen3_5`, ma dichiara come base Qwen3.8: è un'incongruenza da tenere presente.

## Formato di input

Un "record" contiene questi campi:

| Campo | Significato |
|---|---|
| `state` | Stringa o valore JSON che descrive la situazione. |
| `images`, `videos` | Opzionali: liste di immagini o di array di frame video. |
| `media_kwargs` | Opzionale: parametri per il processor di immagini e video. |
| `questions` | Mappa *ID domanda → domanda*. |

Ogni domanda ha:

- **`type`**, uno fra:
  - `noul`: vero/falso;
  - `choice`: opzioni con un nome;
  - `score`: opzioni ordinate, cioè una scala.
- **`instructions`** (opzionale): se manca, il modello usa l'ID della domanda.
- **`criteria`**: dipende dal tipo.
  - `choice`: mappa *ID opzione → descrizione*;
  - `score`: lista di descrizioni, indicizzata da 0;
  - `noul`: descrizioni opzionali per *true* e *false*.

Limiti di lunghezza: `max_length` vale 16.384 token di default; `max_state_tokens` limita la parte dedicata allo stato.

## Formato di output

La risposta, in stile Jev/SystemOne, contiene `model`, `answers` (indicizzato per ID domanda) e `usage`.
Il contenuto di ogni risposta dipende dal tipo di domanda:

| Tipo | Contenuto della risposta |
|---|---|
| `choice` | `choice` (l'opzione scelta), `confidence`, `probabilities` |
| `score` | `score` (valore atteso), `confidence`, `legend`, `probabilities` |
| `noul` | probabilità di *true* |

## Come si usa (panoramica)

La card dichiara di aver testato il modello con `torch` 2.11, `transformers` 5.10.2 e una **singola GPU H200**.
Per immagini e video serve anche `pillow`.

Il percorso indicato dalla card usa un modulo Python incluso nel repository del modello, `joint_schema_model.py`:

1. scaricare il modello con `snapshot_download("Cloudflare/clef")` e aggiungere il percorso a `sys.path`;
2. caricarlo con `load_release_model(path, device="cuda")`, che restituisce `model, processor`;
3. costruire un record con `state` e `questions`;
4. codificarlo con `encode_record` e metterlo in un batch con `collate_records`;
5. eseguire il modello in `torch.inference_mode()`;
6. applicare una softmax per ogni domanda.

Nello stesso batch si possono mescolare record solo testuali e record multimodali.

### Opzioni di serving

- **SGLang**: immagine Docker `lmsysorg/sglang:dev-clef` con `sglang serve --model-path Cloudflare/clef`, sulla porta 30000.
  Espone l'endpoint `/v1/systemone`. C'è un [cookbook](https://docs.sglang.io/cookbook/autoregressive/Cloudflare/clef) per H200, B200 e B300.
- **API Jev/SystemOne**: l'helper `systemone(model, processor, request)` accetta il body di una `POST /v1/systemone`.
  Secondo la card, l'API di Clef è pienamente compatibile con Jev e SystemOne.
- Il pannello "Use this model" di Hugging Face propone anche `pipeline` di Transformers, vLLM e Docker Model Runner.
  Sono però interfacce generiche in stile chat: la card **non dice** se producono le stesse probabilità del percorso ufficiale.

## Benchmark (Decision Index 0.2.1, run interna di Cloudflare)

Una selezione dei risultati. I valori sono percentuali, tranne ForecastBench (Brier, più basso è meglio) e la latenza.

| Benchmark | Clef | Clef-Flash | Jev |
|---|---|---|---|
| BFCL (case exact acc.) | 98.5 | 98.8 | 95.8 |
| ToolRet (nDCG@10) | 69.2 | 66.4 | 65.3 |
| API-Bank (acc.) | 91.9 | 93.1 | 88.2 |
| BANKING77 (macro-F1) | 94.2 | 90.9 | 79.7 |
| CLINC150+OOS (macro-F1) | 97.4 | 66.8 | 89.3 |
| ContractNLI (macro-F1) | 81.4 | 84.3 | 71.7 |
| ANLI (macro-F1) | 69.8 | 59.1 | 74.8 |
| MMLU (acc.) | 90.3 | 91.8 | 91.7 |
| GPQA Diamond (acc.) | 48.0 | 51.0 | 78.3 |
| GSM8K (acc.) | 80.8 | 67.3 | 79.9 |
| MMLU-Pro (acc.) | 65.9 | 65.3 | 82.7 |
| BBH (acc.) | 73.7 | 68.9 | 92.9 |
| RAGTruth (halluc. F1) | 79.4 | 35.6 | 76.5 |
| ForecastBench (Brier ↓) | 13.9 | 10.6 | 17.4 |
| CRUXEval (acc.) | 86.7 | 86.1 | 73.0 |
| Latenza mediana (ms) | 209.3 | 38.8 | 524.1 |
| Latenza p95 (ms) | 238.6 | 122.4 | 536.0 |

**Come leggerla:** Clef va forte su tool calling, classificazione degli intenti e rilevamento delle allucinazioni.
È invece indietro rispetto a Jev nel ragionamento complesso (GPQA, MMLU-Pro, BBH).
Clef-Flash è molto più veloce.

### Workflow aziendali (Typesafe Evals)

| Workflow | Metrica | Clef | Clef-Flash | Jev |
|---|---|---|---|---|
| Elaborazione fatture | Exact actions | 64.7 | 57.1 | 61.8 |
| Elaborazione fatture | Primary action | 86.2 | 73.3 | 83.1 |
| Customer service | Exact actions | 76.3 | 77.0 | 76.0 |
| Incidenti di sicurezza | Exact actions | 62.9 | 61.7 | 61.7 |
| Osservabilità delle trace degli agenti | Primary action | 68.5 | 69.8 | 71.6 |

La classifica completa è sul [Decision Index leaderboard](https://clef-evals.workers-ai-mle.workers.dev).

## Licenza

**Apache-2.0**, la stessa del modello base.

## Cosa manca nella model card

- Dati e procedura di training
- Limitazioni, rischi e bias
- Una sezione esplicita sugli usi previsti
- Un paper o una citazione
- Requisiti hardware oltre a "testato su una H200"

## Risorse utili

- Model card: https://huggingface.co/Cloudflare/clef
- Clef-Flash: https://huggingface.co/Cloudflare/clef-flash
- Blog: https://blog.cloudflare.com/clef-decision-models
- Leaderboard: https://clef-evals.workers-ai-mle.workers.dev
- Cookbook SGLang: https://docs.sglang.io/cookbook/autoregressive/Cloudflare/clef
- Typesafe Evals: https://evals.typesafe.ai/
- Space di prova su Hugging Face (gli indirizzi degli Space contengono `/spaces/`):
  - https://huggingface.co/spaces/hugging-apps/clef-decision-model
  - https://huggingface.co/spaces/hugging-apps/clef-flash
  - https://huggingface.co/spaces/burhanyilmaz/clef-playground
  - https://huggingface.co/spaces/multimodalart/jev-decision-index

---

## Il mio percorso di studio

Da completare man mano.

- [ ] Capire la differenza fra un "decision model" e un LLM generativo
- [ ] Capire i tre tipi di domanda (`noul`, `choice`, `score`) e quando usare ciascuno
- [ ] Leggere `joint_schema_model.py` nel repository del modello
- [ ] Provare il modello in uno Space di Hugging Face
- [ ] Decidere dove eseguirlo: GPU locale, cloud oppure Clef-Flash
- [ ] Progettare un primo schema di domande per un caso d'uso reale
