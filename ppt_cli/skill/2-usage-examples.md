# Usage Examples

─── 1. Reverse-engineer an existing deck ───

Got a .pptx someone sent you? Crack it open:

  ppt-cli internals analyze client-deck.pptx     # layouts, masters, media inventory
  ppt-cli internals fingerprint client-deck.pptx  # shape positions, sizes, colors per slide
  ppt-cli peek client-deck.pptx                   # quick shape/text overview
  ppt-cli screenshot client-deck.pptx 3 7 12       # render specific slides as PNG
  ppt-cli screenshot client-deck.pptx --all        # render every slide

This tells you which layouts are actually used, which are dead weight, and
whether slides were built cleanly from layouts or hacked together freehand.
The fingerprint command can spot patterns like "slides 5, 11, 23 all have the
same 3-card layout but nobody made it a real layout."

─── 2. Turn last month's deck into a reusable template ───

  ppt-cli internals stage quarterly-report.pptx
  ppt-cli internals delete slide <staged-dir> --slide 4   # gut content slides
  ppt-cli internals delete layout <staged-dir> --layout "unused-thing"
  ppt-cli internals build-template <staged-dir> \
    --name=quarterly --description="Q report template"

Now you have a registered template with your corporate theme, masters, and
layouts — minus the old content.

─── 3. Build a new deck from that template ───

  ppt-cli create q1-report.pptx --template quarterly
  ppt-cli add-slide q1-report.pptx --layout "Title Slide"
  ppt-cli set-title q1-report.pptx 1 "Q1 2026 Results"
  ppt-cli add-slide q1-report.pptx --layout "bg_white"
  ppt-cli set-text q1-report.pptx 2 --shape-id 3 "Revenue up 15% YoY"
  ppt-cli add-image q1-report.pptx 2 chart.png --x 1in --y 2in --w 8in
  ppt-cli add-table q1-report.pptx 3 data.csv --x 1in --y 1.5in
  ppt-cli set-notes q1-report.pptx 1 "Mention the new product line"

Slide by slide: pick layout, fill placeholders, drop in images/tables from
files, add speaker notes.

If a default template is set (ppt-cli template default quarterly), the create
simplifies to just: ppt-cli create q1-report.pptx

─── 4. Bulk find-and-replace across a deck ───

Rebranding, or fixing a typo that's on 30 slides:

  ppt-cli replace-text deck.pptx "Acme Corp" "NewCo Inc."
  ppt-cli replace-text deck.pptx "FY2025" "FY2026"

Hits every slide, every shape.

─── 5. Restructure slide order, duplicate, delete ───

  ppt-cli list deck.pptx                    # see slide titles + positions
  ppt-cli duplicate-slide deck.pptx 3       # clone slide 3
  ppt-cli reorder deck.pptx 4 --to 2        # move slide 4 to position 2
  ppt-cli delete-slide deck.pptx 7          # remove slide 7

─── 6. Fine-tune styling without opening PowerPoint ───

  ppt-cli set-font deck.pptx 1 --shape-id 5 --bold --size 28 --color "#FF0000"
  ppt-cli set-fill deck.pptx 2 --shape-id 8 --color "#1A1A2E"
  ppt-cli set-position deck.pptx 1 --shape-id 5 --x 2in --y 1in --w 6in

─── 7. Evolve your template when branding changes ───

  ppt-cli template show quarterly                  # get path
  ppt-cli internals stage /path/to/template.pptx   # extract
  # edit theme1.xml for new colors, tweak layout XML for new placeholder positions
  ppt-cli internals duplicate layout <staged-dir> \
    --source "finance-green" --name "finance-red"
  ppt-cli internals build-template <staged-dir> --name=quarterly -f

For single-file edits, work directly on the XML in the staged directory:
rename a layout (<p:cSld name="...">), reposition placeholders (<a:off>,
<a:ext>), change theme colors (theme1.xml). For multi-file structural changes
that require cross-reference syncing, use internals commands:

  ppt-cli internals add layout <staged-dir> --name "new-section" --master 1
  ppt-cli internals delete layout <staged-dir> --layout "old-thing"
  ppt-cli internals duplicate master <staged-dir> --master 1 --name "dark-variant"

─── 8. Audit a deck: layout usage vs. freehand overrides ───

You're given a deck as a visual guide. Before rebuilding, check how faithfully
slides follow their layouts:

  ppt-cli internals analyze source.pptx
  ppt-cli internals stage source.pptx

Then read specific slide XMLs alongside their layout XMLs. Every shape on a
slide is either a placeholder (<p:ph> element — inherited from the layout) or
a freehand shape (no <p:ph> — manually added). If 12 slides share the same
freehand pattern, it's worth promoting to a real layout.

─── 9. Promote implicit templates to real layouts ───

Fingerprinting reveals several slides share the same freehand structure but
all use Blank or a minimal layout:

  ppt-cli internals fingerprint deck.pptx --slide 5    # get structural detail
  ppt-cli internals stage deck.pptx
  ppt-cli internals add layout <staged-dir> --name "metric-cards" --master 1
  # edit the new layout's XML: add placeholder shapes matching the fingerprint

Now future slides can use add-slide --layout "metric-cards" and fill
placeholders instead of placing shapes freehand each time.

─── 10. Template management ───

Day-to-day housekeeping of the template registry.

  ppt-cli template list                       # all templates
  ppt-cli template show <name>                # path, description, layouts
  ppt-cli template rename <old> <new>         # optionally --description="..."
  ppt-cli template delete <name>              # remove from registry and disk
  ppt-cli template default                    # print current default
  ppt-cli template default <name>             # set default
  ppt-cli template default --unset            # clear default

These examples don't show every option. Run ppt-cli <command> -h to see the
full set of flags and arguments for any command.
