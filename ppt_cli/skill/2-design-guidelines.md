# Design Guidelines

How to make a presentation that looks intentional rather than generated. Read this file when the task involves creating or significantly restyling a presentation. Do not skip it — design decisions made after content is laid out are expensive to retrofit.

Before building any slides or even reaching an agreement on exact presentation content, you need two things: the universal design rules (which apply to every deck regardless of style) and a design direction (which determines the specific aesthetic choices). The direction influences content decisions — how much text per slide, whether to use stat callouts or tables, how many slides a topic warrants — so it must be established before the content plan, not after.

---

## Universal rules

Read `3-design-universal.md` first, before choosing a direction. It covers color dominance, typography hierarchy, layout vocabulary, spacing, content structure, and visual motifs. Every direction assumes you have internalized these principles. They are the floor, not the ceiling.

---

## Choosing a direction

A design direction is a coherent set of aesthetic choices — palette character, typography personality, layout density, use of imagery, decorative approach — tuned to a specific kind of presentation. The direction determines what "good" looks like for this particular deck.

Ask the user about the context: who is the audience, what is the purpose, what tone do they want? Then recommend a direction. If the user's needs span two directions, blend them — but read both files before starting, and be explicit with the user about which elements you are drawing from each.

Always read at least one direction file before building slides. Do not wing it with no direction.

### Business

Conservative, credible, and data-forward. For quarterly reports, board decks, investor updates, internal communications, and any context where the audience expects professionalism over personality. The ideal reaction is trust and clarity — the audience leaves knowing the numbers and the narrative, without once thinking about the slides themselves.

Safe palette choices (navy, charcoal, teal ranges), clean font pairings (serif or strong sans headers, readable sans body), data-heavy layouts with stat callouts and comparison columns. Heavy on whitespace and alignment precision. Photography is sparse and supporting — visual weight is carried by data, shapes, and color, not imagery. Think: dark title and conclusion slides sandwiching light content slides, muted chart visualizations with a single accent color highlighting the key metric, executive summary slides with three large numbers and short labels, a small company logo anchored in the corner of every slide. The design should be invisible — the audience notices the content, not the slides.

Read `3-design-business.md` for full guidance.

### Technical

Structured, dense, and functional. For architecture reviews, engineering presentations, developer talks, system documentation, and technical walkthroughs. The ideal reaction is "I understand the system now" — the audience follows the logic, sees how the pieces connect, and retains the structure.

Dark backgrounds are acceptable throughout. Monospace typefaces enter the mix for headers or inline references. High information density, but organized with a clear grid and strong hierarchy. Think: architecture flow diagrams with labeled components, code snippets in styled containers with a dark fill and monospace font, numbered step breakdowns where each step is a distinct visual block, comparison columns showing before/after states. Decoration is minimal — structure does the work.

Read `3-design-technical.md` for full guidance.

### Creative

Expressive, bold, and visually assertive. For design showcases, portfolio presentations, brand launches, event decks, and any context where the presentation itself is part of the message. The ideal reaction is impact — the audience remembers the feeling and the imagery, not just the information.

High typographic contrast, unconventional font pairings, full-bleed imagery, asymmetric layouts, and generous negative space used as a compositional element. Color choices are confident and topic-specific. The full range of visual genres is available here — editorial photography, manga, comic, retro poster, stylized illustration — used as communicative tools, not decoration. Think: a title slide that is a single full-bleed photograph with a large word overlaid, content slides where text occupies one third and a striking image fills the rest, a section divider rendered as a vintage travel poster, stat callouts with oversized numbers in an expressive typeface. The design makes a statement — restraint is selective, not default.

Read `3-design-creative.md` for full guidance.

### Educational

Clear, progressive, and approachable. For workshops, tutorials, onboarding sessions, training materials, and any context where the audience is learning something. The ideal reaction is confidence — the audience feels they followed each step and can apply what they learned.

Strong sequential structure (numbered sections, consistent "here is what we will cover" framing), visual aids on every slide (icons, simple illustrations, callout boxes), friendly typography, and approachable palettes. Images serve explanation, not atmosphere — diagrams, annotated screenshots, and teaching-oriented charts over photography. Think: a progress indicator or section number on every slide, icon-and-text rows breaking a concept into three digestible points, callout boxes that highlight key takeaways or definitions, step-by-step layouts where each step has a number, a bold label, and a short explanation. Repetitive layout patterns are acceptable here — consistency aids learning. Higher text density per slide is fine if the text is well-structured with clear hierarchy.

Read `3-design-educational.md` for full guidance.

---

## Working with existing templates

When the user provides an existing template or branded deck, the task is not to impose a design direction — it is to understand and follow the one that is already there.

Before proposing or agreeing on exact presentation content, analyze the template: inspect its layouts, extract the palette from existing shapes, identify the font hierarchy, and find the visual motifs (recurring shapes, accent elements, background treatments). The template *is* the design system. Your job is to derive the rules from what you see and then apply them consistently to new content.

Extend the template's patterns when needed (a new slide type that the template doesn't have a layout for), but stay within its visual language. Match its fonts, its colors, its spacing conventions, its approach to imagery. When in doubt, be conservative — a new slide that looks slightly plain but consistent with the template is better than one that looks polished but foreign.
