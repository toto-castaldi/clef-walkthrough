# Appunti Clef

Appunti personali per lo studio del modello [Cloudflare/clef](https://huggingface.co/Cloudflare/clef).

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

## Prove sullo Space

Space: https://huggingface.co/spaces/hugging-apps/clef-decision-model (Clef 27B, su ZeroGPU)

### Prova 1 — "È un telefono Android?" (2026-11-16)

**Input**

- State: `this is a screenshot`
- Immagine: screenshot della home di un telefono (barra di ricerca Google, icone delle app, sfondo con un pontile sul mare)
- Domanda:
  - ID: `market`
  - type: `choice`
  - instructions: "Is it and Android phone?"
  - criteria: `yes` → "yes", `no` → "no"

**Output**

- Scelta: `yes`, con probabilità 99,6% (`no` 0,4%)
- 580 token di input · forward pass 2506 ms

**Osservazioni**

- La risposta è corretta: la schermata ha l'aspetto di Android.
- **Tipo di domanda**: per un sì/no esiste il tipo `noul`. `choice` è più utile quando le opzioni sono più di due.
- **ID della domanda**: senza `instructions`, il modello usa l'ID come testo della domanda, quindi l'ID ha un significato anche per il modello. `market` non descrive la domanda; un nome come `is_android` è più chiaro.
- **Refuso**: "and" invece di "an". Il modello ha capito lo stesso.
- **Token**: quasi tutti i 580 token vengono dall'immagine. Il vision encoder la trasforma in token che occupano spazio nel contesto, come se fossero parole.
- **Latenza**: 2,5 s, contro i circa 209 ms di latenza mediana dichiarati nella card. La differenza dipende probabilmente da ZeroGPU, che assegna la GPU al momento, e dall'immagine.

**Prossime prove**

- [ ] Rifare la stessa domanda come `noul` e confrontare risposta e probabilità
- [ ] Rinominare la domanda (`is_android`) e correggere il refuso: cambia qualcosa?
- [ ] Rilanciare senza immagine: quanto scendono i token?
- [ ] Rilanciare due volte di fila: la seconda è più veloce?
- [ ] Aprire il pannello "SystemOne JSON response" e confrontarlo con la sezione SystemOne di questi appunti
- [ ] `choice` sulla marca del telefono, con 4–5 opzioni: le probabilità si distribuiscono?
- [ ] `score` da 0 a 4 su quanto è "ordinata" la schermata, con una descrizione per ogni livello
