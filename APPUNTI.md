# Appunti

## Panoramica Clef

### Cos'è Clef

Clef è un **"decision model"** multimodale da **27B parametri**. Riceve due cose:

1. uno **stato**, cioè la situazione da valutare: testo, JSON, immagini o video;
2. uno **schema di domande tipizzate**.

Restituisce una **probabilità per ogni opzione ammessa di ogni domanda**, tutto in un **solo forward pass**.
Non genera testo libero, quindi non c'è output da interpretare con un parser.

In pratica: un LLM classico "scrive" una risposta, che poi va interpretata. Clef invece
**assegna un punteggio a un insieme chiuso di opzioni** e produce subito una distribuzione di probabilità.

Fa parte della collezione open-weight **Clef**, insieme alla variante più piccola e veloce
[**Clef-Flash**](https://huggingface.co/Cloudflare/clef-flash): 9B parametri, ottenuta con un post-training di Qwen/Qwen3.5-9B.

### Architettura

| Componente | Descrizione |
|---|---|
| **Backbone** | [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), compreso il suo vision encoder. Clef è un *post-training* di questo modello. |
| **Joint schema head** | Un piccolo transformer posto sopra gli hidden state finali del backbone. Instrada le informazioni dello stato verso ogni domanda e assegna un punteggio a tutte le opzioni di tutte le domande **insieme** (*jointly*). |
| **Output** | Un logit per ogni opzione di ogni domanda. Una softmax **per domanda** trasforma i logit in probabilità. |

- Pesi in formato **BF16**, file **safetensors** suddivisi in più parti (*sharded*).
- La card cita il tag `qwen3_5`, ma dichiara come base Qwen3.8: è un'incongruenza da tenere presente.

### Formato di input

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

### Formato di output

La risposta, in stile Jev/SystemOne, contiene `model`, `answers` (indicizzato per ID domanda) e `usage`.
Il contenuto di ogni risposta dipende dal tipo di domanda:

| Tipo | Contenuto della risposta |
|---|---|
| `choice` | `choice` (l'opzione scelta), `confidence`, `probabilities` |
| `score` | `score` (valore atteso), `confidence`, `legend`, `probabilities` |
| `noul` | probabilità di *true* |

## Parametri

I parametri sono tutti i numeri che il modello impara durante l'addestramento. La grande maggioranza sono i pesi delle connessioni della rete, ma "parametri" è un termine un po' più ampio. Comprende anche:

- i **bias**: piccoli valori aggiunti al risultato di ogni moltiplicazione;
- gli **embedding**: la tabella che traduce ogni token, cioè ogni pezzo di parola, in una lista di numeri;
- i parametri delle **normalizzazioni**: pochi numeri che tengono "in scala" i valori interni.

## SystemOne

SystemOne non è un modello. È il protocollo, cioè le regole con cui un programma chiede una decisione a un modello e riceve la risposta, nato con Jev. In concreto:

- si fa una richiesta `POST` all'indirizzo `/v1/systemone`;
- il body della richiesta contiene `state` e `questions`. Non c'è un elenco di `messages` come nelle chat, e infatti non è compatibile con l'API di OpenAI;
- la risposta contiene `answers` (con le chiavi che hai scelto tu per le domande) e `usage`.

## Chiamata di esempio

State

```text
A user shared this mobile phone screenshot.
```

Question

```json
{
  "platform": {
    "type": "choice",
    "instructions": "Which mobile operating system is shown in this screenshot?",
    "criteria": {
      "android": "Android UI: Material status bar, Android navigation bar or gesture pill, Google apps",
      "iphone": "iOS UI: Dynamic Island or notch, iOS status bar icons, home indicator, Apple apps"
    }
  }
}
```

```json
{
  "is_iphone": {
    "type": "noul",
    "instructions": "Is this a screenshot of an iPhone (iOS) screen?"
  },
  "is_android": {
    "type": "noul",
    "instructions": "Is this a screenshot of an Android phone screen? "
  }
}
```