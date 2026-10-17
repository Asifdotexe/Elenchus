# Design philosophy and origins

> *"For the love of the game. I honestly enjoy debates, but there is a huge difference between a heated argument and a well-structured discussion, and it comes down to how someone puts out their statement."*
> Asif Sayyed, project creator in his [journal](https://asifdotexe.github.io/journals/fallacy-classifier/)

---

## What is Elenchus?

Elenchus takes its name from the ancient Greek term **ἔλεγχος** (*élenkhos*), the Socratic method of argumentative dialogue. In Socratic dialogue, the point is never to shout louder or win through theatrical rhetoric. The point is to test claims, pull apart premises, and see whether a conclusion actually holds up.

Elenchus is a small HUD tool that floats on your desktop. It listens to spoken statements from your microphone or audio loopback, breaks each sentence down into premises and conclusions, and checks whether a fallacy was committed, providing a quick explanation of why.

An additional nicety: it requires no token costs and runs completely offline in a lightweight manner.

---

## Why does this exist?

### For the love of the game

Good debates are rare. Most disagreements turn into shouting matches where both sides talk past each other, move goalposts, and attack character instead of evidence.

In debates, people can be disingenuous. Sometimes they do it on purpose to win an exchange, but just as often it happens by accident because human thinking naturally takes shortcuts. Having a clear, real-time read on whether a statement is structurally valid helps weed out poor arguments and debates with no end.

When you can see the logical structure underneath the emotion of an argument, two things happen:

1. **You make sounder, more robust arguments**: You catch your own unsupported leaps and shaky premises before you say them out loud.
2. **You smell unsound or half-baked arguments immediately**: You notice when an opponent swaps definitions, sets up a straw man, or forces a false dilemma, and you know exactly where their reasoning failed.

---

## A sparring partner, not a replacement brain

A central question that came up during early development was:

> *"The aim of the tool is to learn. Having an assist of this sort shouldn't lead to people offloading their cognitive ability."*

That distinction matters. If software generates your debate responses for you, your own rhetorical skills get worse. You become passive and dependent on an automated crutch.

Elenchus is built as an intellectual sparring partner, not an autonomous brain:

| Cognitive offloading (unhelpful) | Cognitive elevation (our approach) |
| :--- | :--- |
| AI generates entire speeches | You form your own argument |
| You become a passive reader | The HUD highlights logical fallacies |
| Rhetorical instincts atrophy over time | You read the rationale and understand the flaw |
| Creates reliance on external models | Your brain learns the pattern and reacts faster |

When boxers train on a heavy bag or work with a sparring partner, the partner does not step into the ring on fight night. The partner helps build reflexes so that during the real fight, muscle memory takes over. Elenchus works the same way for your thinking.

---

## What is under the HUD (pun intended)

### 1. Zero token cost, zero clouds

Debate practice should not carry an API bill, and private conversations should never leave your machine.

Every audio buffer stays strictly in volatile memory, speech transcription runs on CPU without using VRAM, and model inference executes entirely on your local GPU. For detailed memory allocations and latency telemetry, see the canonical [Hardware allocation budget](specifications.md#hardware-allocation-budget) and [Latency budget breakdown](specifications.md#latency-budget-breakdown).

### 2. Why a coder model? Brevity

General chat models tend to produce three-paragraph essays. While listening to someone in a live conversation, you do not have time to read an essay.

I chose `qwen2.5-coder:3b` specifically because coder models give concise, structured responses. The task of classifying a premise is simple enough for a coder model, and its rationale has brevity. Rebuttals stay under 30 words, formatted so you can glance at them in a fraction of a second without losing eye contact or your train of thought. For technical implementation details, see [Stage 3: Fallacy classification](architecture.md#stage-3-fallacy-classification).

### 3. A floating desktop HUD

Rather than burying the tool in a browser tab or terminal window, Elenchus uses a translucent PyQt6 overlay pinned over your active desktop apps (Zoom, Discord, browser, or terminal). It stays visible in your peripheral field of view when you need it and fades into the background when you do not.

For window controls, status LEDs, and shortcuts, see the [User guide](user-guide.md#operating-the-desktop-hud).

---

## How do I distribute? Simplicity and ease of use

Software should be as straightforward to install as it is to run. Rather than requiring everyone to configure Python environments or shell scripts, distribution is tiered across standalone binaries, quick-start commands, and editable source builds.

For command-line installers, manual verification hashes, and source setup, see [Installation and distribution](installation.md).

---

## Future evolution

The core release provides a baseline sparring loop for single statements. Exploratory capabilities from the development journal (such as extended session recordings, opponent audio isolation, and personal argument metrics) are planned as version milestones.

For scope boundaries and planned version targets, see [Version scopes and roadmap](blueprint.md).
