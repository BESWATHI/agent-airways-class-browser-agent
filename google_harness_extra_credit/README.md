# Google AI Harness Extra Credit

## 1. Connection to Google's Harness Concept
Google describes a harness as the code around a model that gives it tools,
checks its decisions, runs actions, and decides when the task is done. My
browser agent is a harness. The Qwen3:8b model only proposes a JSON action.
Python parses it (`parse_model_reply`), validates it (`validate_proposal`),
runs it through `browser_tools` (`open_site`, `read_page`), and sends the
observation back to the model. The loop stops at `MAX_STEPS = 8`, and
Python, not the model, decides success (`check_goal`).

## 2. How Success Is Checked
When the model proposes `done`, Python ignores its explanation and re-reads
the live page. `check_goal` requires all three:
1. The URL exactly equals `SITE_URL`.
2. The page title is "Agent Airways Lab".
3. The main heading is "Agent Airways".

Failure types: `budget_exceeded` (8 steps without success), `model_error`
(Ollama problem), invalid JSON or action, and a `done` rejected as premature.

Limitation: this only confirms the correct page is open. There is no form,
so it cannot check submitted values.

## 3. Five-Run Results
| Run | Success or Failure | Notes |
|-----|--------------------|-------|
| 1 | Failure | budget_exceeded after 8 steps; done rejected __ times (URL mismatch) |
| 2 | Failure | budget_exceeded after 8 steps; done rejected __ times (URL mismatch) |
| 3 | Failure | budget_exceeded after 8 steps; done rejected __ times (URL mismatch) |
| 4 | Failure | budget_exceeded after 8 steps; done rejected __ times (URL mismatch) |
| 5 | Failure | budget_exceeded after 8 steps; done rejected __ times (URL mismatch) |

Evidence: run1.log, run1_trace.json, run1.png, ... through run5.
Each screenshot shows the correct page title and heading, with
`#search` added to the URL.

## 4. Findings and Limitations
All five runs failed with `budget_exceeded`, but the agent did reach the
correct page every time. The screenshots show the right title ("Agent
Airways Lab") and heading ("Agent Airways"). The problem is in my
success check, not the model. `check_goal` requires the URL to exactly
equal `SITE_URL` (`.../travel/`), but the site adds `#search`, so the
browser's URL is `.../travel/#search`. Python rejected every correct
`done`, and the model did not understand why, so it kept repeating
actions until it hit the 8-step limit. Because the failure was identical
in all five runs, it is a deterministic harness bug rather than random
model behavior. A fix would be to compare `observation["url"].split("#")[0]`
with `SITE_URL`, and to send a clearer rejection message back to the
model. This connects to the Google course's point about evaluation:
an automated check can be wrong, so you have to verify the checker
itself, not just the agent.

A limitation is that because the check never passed, these runs did not
measure how reliable the model is at the task. After fixing the URL
check, I would need to run new trials to measure that.