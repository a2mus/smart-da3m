# UX Writing Reference

## Button Labels — Verb + Object

| Bad | Good | Why |
|-----|------|-----|
| OK | Save changes | Says what happens |
| Submit | Create account | Outcome-focused |
| Yes | Delete message | Confirms the action |
| Cancel | Keep editing | Clarifies "cancel" |
| Click here | Download PDF | Describes destination |

**Destructive actions**: Name the destruction. "Delete 5 items" not "Delete selected".

## Error Message Formula
Every error answers: (1) What happened? (2) Why? (3) How to fix?

| Situation | Template |
|-----------|----------|
| Format error | "[Field] needs to be [format]. Example: [example]" |
| Missing required | "Please enter [what's missing]" |
| Permission denied | "You don't have access to [thing]. [What to do]" |
| Network error | "We couldn't reach [thing]. Check connection and [action]." |
| Server error | "Something went wrong on our end. [Alternative action]" |

**Never blame the user.** "Please enter MM/DD/YYYY format" not "You entered invalid date".

## Empty States Are Opportunities
1. Acknowledge briefly
2. Explain the value
3. Provide clear action

"No projects yet. Create your first one to get started." NOT "No items".

## Voice vs Tone
Voice = consistent personality. Tone = adapts to moment.

| Moment | Tone |
|--------|------|
| Success | Celebratory, brief: "Done! Changes are live." |
| Error | Empathetic, helpful: "That didn't work. Here's what to try…" |
| Loading | Reassuring: "Saving your work…" |
| Destructive | Serious, clear: "Delete this project? Can't be undone." |

**Never humor for errors.** Users are already frustrated.

## Translation Planning

| Language | Expansion |
|----------|-----------|
| German | +30% |
| French | +20% |
| Arabic | Variable (RTL) |

Keep numbers separate. Use full sentences. Avoid abbreviations.

## Consistency
Pick one term: Delete (not Remove/Trash). Settings (not Preferences/Options). Sign in (not Log in).

## Confirmation Dialogs
Most are design failures — consider undo instead. When must confirm: name action, explain consequences, specific labels ("Delete project" / "Keep project").
