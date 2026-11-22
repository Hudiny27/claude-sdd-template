# Critical pass

Used by the `grill` skill: before the first round, and again over the
settled plan before finishing.

Read the plan as a sceptic, even when it looks complete: a plan with no
open question is the one most likely to hide an assumption. Look things up
yourself; ask only the decisions. The second pass runs the same checks over
the settled plan: the answers themselves often open new edge cases.

- **Check claims against reality.** Every statement about how things work
  today ("there is no such action", "the file is always UTF-8") is checked
  in the code, the running app, the data and the baseline document. A
  contradiction becomes a question: "You said X; the code does Y. Which is
  right?"
- **Concrete scenarios.** Invent 3–5 specific cases at the edges (empty,
  huge, twice, at the same time, interrupted halfway, the wrong user,
  offline, an old file or format) and walk the plan through each. Where the
  plan has no answer, that is a question.
- **Pre-mortem.** "It shipped and went wrong: what happened?" The 2–3 most
  likely causes become questions, or checks the spec must contain.
- **Fuzzy words.** A word that can mean two things in this project (check
  the glossary) becomes a question proposing one term; never a silent
  choice.

**Break-it subagent.** When the plan is hard to reverse or reaches far (data
leaving the machine, deletion, migration, auth, payment, sent mail, a
format users' files depend on; in an SDD spec `ajtó: egyirányú` or
`hatósugár: nagy`), also spawn one fresh subagent with only the plan text
and the files it touches, asked how the plan fails. Check each of its
points before it enters the frontier.
