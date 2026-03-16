# Speaker Notes

Verbatim presentation script, delivered via `set-notes` in the build script.
The audience sees the slide; the speaker tells the story around it.

## CORE RULE

Slide = visual channel (data, structure, images).
Script = auditory channel (context, interpretation, narrative).
Never duplicate. If the slide shows "34% growth," the script explains
WHY — not "we grew 34%." ~80% of spoken content is NOT on the slide.
Lead with the "so what," not the "what" — audience read the slide in 3 seconds.

The script is the ACTUAL WORDS to say. Not coaching ("try telling a story here"),
not suggestions ("you could mention..."), not bullet points. Verbatim sentences
the presenter reads in Presenter View.

## PER-SLIDE STRUCTURE

```
hook:       1-2 sentences framing what the audience is about to see.
            NEVER "so on this slide" or "next we have."
            Types: question, surprising fact, bold claim, callback to earlier slide.

core:       2-4 points. Each: state -> evidence/example -> "so what."
            Reference visible elements by MEANING not POSITION.
            "The bar chart tracks monthly churn" not "on the left."
            Interpret, don't read: what it MEANS, not what it SHOWS.

transition: 1-2 sentences bridging to next slide. Closes current takeaway
            AND opens curiosity for what's next.
            Every slide MUST end with a transition. No dead stops.
            Last slide: closing statement or call to action instead.
```

## DELIVERY CUES

Sparse: ~1 cue per 30-50 words. Cluster at high-impact moments
(after stats, before reveals, at transitions). Thin out during narrative.

```
(pause)       2-3s silence. After key stats, before reveals,
              at section transitions, after rhetorical questions.
(long pause)  3-5s. After a major reveal or emotional statement.
(beat)        sub-second shift in energy/direction. The gear change
              between "We tried everything. (beat) Nothing worked."
CAPS          emphasis on a single word. "This isn't good — it's RECORD."
```

No physical gesture cues — presentations are delivered digitally/remote.

Density by section:
- Opening/closing: higher (~1 per 15-25 words)
- Narrative middle: lower (~1 per 40-60 words)
- Data/statistics: (pause) around every key number

## TIMING

```
default_wpm:     130 (adjust per direction voice)
section_divider: 10-20s  (~20-40 words)
content_slide:   45-90s  (~100-200 words)
data_heavy:      60-120s (+10-15s for chart/diagram processing)
```

Per-slide marker: `[~Xs | M:SS]` (slide estimate | running total).
Overhead: +2-3s per slide transition, +3s per (pause), +5s per (long pause).

## VISUAL REFERENCING

```
reference_ratio: ~60-70% of visible content explicitly narrated.
                 Rest = context audience absorbs on their own.
eye_flow:        narrate in natural scan order (Z-pattern: top-left ->
                 top-right -> bottom-left -> bottom-right).
read_ahead_gap:  quickly acknowledge visible content, then slow down
                 for interpretation the slide doesn't contain.
```

Name elements by content: "the trend line," "these three metrics,"
"the comparison." Avoid "as you can see." Tell them what it means.

## FACTUAL ACCURACY

Use: slide content, source material, user-provided context,
well-established general knowledge.

Missing specifics (metrics, dates, names, citations): ask the user.
Do not fabricate or infer numbers. General directional claims
supported by slide content are fine ("significant growth").

## DIRECTION VOICE

Modifiers on top of universal rules. The script's register shifts
per direction; the structural rules (hook/core/transition, cue
notation, timing) stay the same.

```
business:     measured, data-first, understated authority. Numbers before
              narrative. No exclamation energy. Formal transitions.
              (pause) after key metrics. Register: boardroom.

creative:     confident, expressive, room for drama. Rhetorical questions
              welcome. (beat) before reveals. Emotional register shifts
              between slides. Register: gallery opening.

educational:  warm, guiding, explicit signposting. "Let's look at..."
              "Notice how..." Progress cues ("halfway through now").
              More orientation phrases. Register: favorite professor.

technical:    dense, precise, peer-to-peer. Assumes knowledge, skips
              motivation. Focuses on mechanism. Fewer cues — content
              carries weight. Register: senior engineer in design review.
```
