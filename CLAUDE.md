# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A personal study path ("walkthrough") of Cloudflare's **Clef** decision model written in **Italian**.

Primary sources:
- Model card: https://huggingface.co/Cloudflare/clef
- Announcement: https://blog.cloudflare.com/clef-decision-models

## Files

- `README.md`: short entry point with links to the sources.
- `APPUNTI.md`: the notes. Organized by `##` topic sections (e.g. overview of Clef, parameters, SystemOne protocol), with `###` subsections.
- `DA_APPROFONDIRE.md`: checklist (`- [ ]`) of topics to study in more depth, each with a bold title and a one-line description of what to understand.

Only edit `APPUNTI.md` and `DA_APPROFONDIRE.md` when the user asks (the README states this explicitly).

## Writing conventions (match the existing notes)

- Write in Italian, in plain explanatory prose aimed at someone learning the topic: define terms the first time they appear (e.g. "il protocollo, cioè le regole con cui…").
- **Bold** for key concepts; *italics* for English technical terms kept in the text (*post-training*, *sharded*, *residual stream*); backticks for field names, types, endpoints (`state`, `choice`, `/v1/systemone`).
- Use tables for structured comparisons (components, input/output fields) and bullet lists ending with `;` / `.` for enumerations.
- Note inconsistencies found in the sources explicitly rather than silently resolving them (e.g. the card's `qwen3_5` tag vs. the declared Qwen3.8 base).
- When a new topic worth deepening comes up while studying, add it as an unchecked item to `DA_APPROFONDIRE.md`.
