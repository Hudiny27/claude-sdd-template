# Questionnaire for someone else

Used by the `grill` skill when a question needs another person's answer.

When a question needs another person, write `kerdoiv-<kinek>.md` next to
the plan, following the project's file naming (or in the project's folder
for that audience, e.g. `docs/legal/` for the lawyer):

- formal Hungarian (magázás), for a reader who has not seen the chat;
- 2-4 sentences of context: what we are building and why their answer
  matters;
- numbered questions; for each, the options we see, our recommendation and
  why, and a blank "Válasz:" line;
- what we do until they answer (the default we will assume);
- if the project has a Markdown-to-Word helper (for example
  `scripts/legal_docx.py`), produce the .docx copy with it.

Record in the plan that the question is waiting on that person, and keep
going with the rest of the frontier.
