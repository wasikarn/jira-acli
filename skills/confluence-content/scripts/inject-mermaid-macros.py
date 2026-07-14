#!/usr/bin/env python3
"""inject-mermaid-macros — add the "Mermaid diagram" Forge render macro after
every mermaid code block on a Confluence page.

Why this exists: a ```mermaid fenced code block in Markdown (or a `codeBlock`
node with language=mermaid in ADF) only gets you syntax-highlighted TEXT —
Confluence Cloud has no native Mermaid renderer. This repo's sites have the
"Mermaid diagram" marketplace app installed (a Forge custom-UI macro,
extension-type `com.atlassian.ecosystem`), which DOES render the diagram, but
it is a *separate* macro instance that must sit immediately after each code
block — one macro renders one code block, not the whole page.

By default a freshly-decorated mermaid codeBlock is wrapped in a collapsible
ADF `expand` node (title "Diagram source" — override with --collapse-title),
so the page shows the rendered diagram with the raw source tucked behind a
click, not a wall of mermaid syntax above every diagram. `expand` stores no
open/closed state in the document (same as HTML `<details>` without an `open`
attribute) — every viewer sees it collapsed on load, there is nothing to set
for that. A codeBlock already followed by a matching extension (bare, from a
native /mermaid insert — e.g. TP-807's 7 diagrams) is left exactly as-is, not
retroactively wrapped; this only applies to newly-decorated code blocks.

Operates on ADF (contentFormat="adf"), not HTML. An earlier version of this
script transformed the HTML representation instead
(`<div data-type="extension">`), because that's the syntax
createConfluencePage/updateConfluencePage document for contentFormat="html".
That path is BROKEN: writing a codeBlock immediately followed by a matching
extension div through `updateConfluencePage(contentFormat="html")` makes
Confluence's html-format writer "helpfully" restructure it into three nodes —
an incomplete preview extension before the code, the code wrapped in a
collapsible `expand` macro, and the original extension after — and the
diagram renders TWICE with a useless collapsed accordion between them
(visually confirmed broken 2026-07-14 against a scratch page). Writing the
exact same macro as a proper `extension` ADF node via
`contentFormat="adf"` does NOT trigger that restructuring — confirmed by
reading the page back after write (structurally identical to what was sent,
byte for byte) AND by visual screenshot on the same scratch page, same day:
each diagram renders exactly once, no wrapping, no duplication. Use "adf",
never "html", for this.

Discovered 2026-07-14 against TP-807's spec page (100-stars.atlassian.net,
space BEP) by inserting the macro once by hand via the Confluence editor's
`/mermaid` slash command, then reading the page back with
`getConfluencePage(contentFormat="adf")` to see the real extension node shape
Confluence itself produces — confirmed identical in every field to this
script's hand-built node before trusting it. Verified present on 7 instances
on one page (all `codeBlock` -> `extension` pairs, no wrapping, no gaps).

What varies between instances (confirmed by diffing 7 real macro instances):
  - `localId` (appears twice per node: `attrs.localId` and
    `attrs.parameters.localId`, always equal) — any fresh UUID4, unique per
    instance.
  - `attrs.parameters.guestParams.index` — 0-based position of THIS
    extension's paired codeBlock among ALL codeBlock nodes on the page,
    counting every language, not just mermaid ones. Confirmed against the
    app's own source (github.com/atlassian-labs/mermaid-diagrams-viewer,
    custom-ui/src/confluence/code-blocks/index.ts,
    `getCodeFromCorrespondingBlock`): when `guestParams.index` is set, the
    renderer resolves the diagram source via
    `findCodeBlocks(adf).at(index)`, where `findCodeBlocks` collects every
    `codeBlock` node on the page regardless of `attrs.language` — it does
    NOT filter to mermaid-only, and it does NOT require the extension to sit
    next to its codeBlock (adjacency is a readability convention this
    script follows, not a technical requirement). A page mixing a
    non-mermaid code block (JSON, bash, ...) among the mermaid ones would
    silently misindex if you count mermaid blocks only — this script counts
    ALL codeBlock nodes to match. Empirically indistinguishable from
    mermaid-only counting on any page seen so far (TP-807 and the scratch
    test page both happen to have zero non-mermaid code blocks), so this
    was unverified against a live mixed-language page as of 2026-07-14 —
    the source reading above is what the fix is based on, not a repro.
  - Traversal is TOP-LEVEL ONLY (`content` array, one level) — matches the
    app's `traverse(adf, ...)` (which walks the full tree, including nested
    panels/expands/table cells) only for the flat structure this skill's
    templates actually produce. A codeBlock nested inside a table cell or
    expand would be invisible to this script's counting and insertion.
    # ponytail: flat traversal only; add recursive traversal if a spec page
    # ever nests a mermaid block inside a table/panel/expand.
Everything else (extension-key, cloud-id, account-id, workspace ARI,
`extensionData.content.version` which is a fixed macro-schema constant and
NOT the real page version) is a per-site/per-author constant — safe to reuse
across pages on the SAME site, wrong on a different Atlassian site or a
different Forge app install. Re-derive by inserting the macro once by hand
and re-running this discovery if the org/site changes.

Usage:
  # 1. Fetch the current page as ADF:
  #      getConfluencePage(cloudId, pageId, contentFormat="adf")  -> save the
  #      full JSON response to a file (this script reads either the full
  #      page object or a bare {"type":"doc",...} body).
  # 2. Run this script; it prints the updated doc JSON on stdout.
  # 3. Feed that JSON straight back as the `body` argument to
  #      updateConfluencePage(cloudId, pageId, body=<output>, contentFormat="adf")
  python3 inject-mermaid-macros.py page.json --page-id 217743376 > doc.json
  python3 inject-mermaid-macros.py - --page-id 217743376 < page.json > doc.json

Idempotent: a mermaid codeBlock immediately followed by a matching extension
node (from a prior run, or a manual /mermaid insert) is left untouched and
does not count twice — safe to re-run after adding more diagrams to a page
that already has some rendered.
"""
import argparse
import copy
import json
import sys
import uuid

# ── site-specific constants (100-stars.atlassian.net / TaThep) ─────────────
# Re-derive these if this script is ever pointed at a different Atlassian
# site: insert the macro once by hand via the editor, then diff the page's
# contentFormat="adf" body against this script's output.
DEFAULT_EXTENSION_KEY = (
    "23392b90-4271-4239-98ca-a3e96c663cbb/"
    "63d4d207-ac2f-4273-865c-0240d37f044a/static/mermaid-diagram"
)
DEFAULT_EXTENSION_TYPE = "com.atlassian.ecosystem"
DEFAULT_CLOUD_ID = "85ad5bd2-ef9c-477e-b000-062f1421d0c0"
DEFAULT_ACCOUNT_ID = "712020:64219948-720a-4925-a48c-d7a53557993c"
DEFAULT_WORKSPACE_ARI = (
    "ari:cloud:confluence:85ad5bd2-ef9c-477e-b000-062f1421d0c0:"
    "workspace/2f960cad-efff-4621-bb36-aa7f65cf74df"
)
DEFAULT_SPACE_KEY = "BEP"
DEFAULT_SPACE_ID = "1081347"
CONTENT_VERSION = 1  # observed constant across all instances — not the page version


def is_matching_extension(node, extension_key):
    return node.get("type") == "extension" and node.get("attrs", {}).get("extensionKey") == extension_key


def is_mermaid_code_block(node):
    return node.get("type") == "codeBlock" and node.get("attrs", {}).get("language") == "mermaid"


def wrapped_code_block(node):
    """If `node` is this script's own expand-wrapped code block (single
    codeBlock child), return that child; else None."""
    if node.get("type") != "expand":
        return None
    inner = node.get("content") or []
    if len(inner) == 1 and inner[0].get("type") == "codeBlock":
        return inner[0]
    return None


def build_expand_wrapper(code_block_node, title):
    return {
        "type": "expand",
        "attrs": {"title": title},
        "content": [code_block_node],
    }


def build_extension_node(index, args):
    local_id = str(uuid.uuid4())
    return {
        "type": "extension",
        "attrs": {
            "extensionType": args.extension_type,
            "extensionKey": args.extension_key,
            "parameters": {
                "layout": "extension",
                "guestParams": {"index": index},
                "forgeEnvironment": "PRODUCTION",
                "embeddedMacroContext": {
                    "accountId": args.account_id,
                    "cloudId": args.cloud_id,
                    "contextIds": [args.workspace_ari],
                    "extensionData": {
                        "type": "macro",
                        "content": {"id": args.page_id, "type": "page", "version": CONTENT_VERSION},
                        "space": {"id": args.space_id, "key": args.space_key},
                    },
                },
                "localId": local_id,
                "extensionId": f"ari:cloud:ecosystem::extension/{args.extension_key}",
                "extensionTitle": "Mermaid diagram",
            },
            "text": "Mermaid diagram",
            "layout": "default",
            "localId": local_id,
        },
    }


def inject(content, args):
    code_block_count = 0  # ANY language — see guestParams.index note above
    added = 0
    rewrapped = 0
    result = []
    for i, node in enumerate(content):
        next_node = content[i + 1] if i + 1 < len(content) else None
        already_decorated = next_node is not None and is_matching_extension(next_node, args.extension_key)

        if is_mermaid_code_block(node):
            this_index = code_block_count
            code_block_count += 1
            if already_decorated:
                if getattr(args, "wrap_existing", False):
                    # bare codeBlock + extension (native /mermaid insert) -> wrap the
                    # codeBlock; the unchanged extension node is appended by the loop's
                    # next iteration (it isn't a codeBlock/expand, so it falls through
                    # to the plain append below) — same localId/index, still valid,
                    # since wrapping doesn't move the codeBlock's traversal position.
                    rewrapped += 1
                    result.append(build_expand_wrapper(node, args.collapse_title))
                else:
                    result.append(node)  # native/old-style insert, leave as-is
                continue
            added += 1
            result.append(build_expand_wrapper(node, args.collapse_title))
            result.append(build_extension_node(this_index, args))
            continue

        inner = wrapped_code_block(node)
        if inner is not None and is_mermaid_code_block(inner):
            this_index = code_block_count
            code_block_count += 1
            result.append(node)
            if already_decorated:
                continue  # already wrapped AND already has a macro — untouched
            added += 1
            result.append(build_extension_node(this_index, args))
            continue  # wrapped but missing its macro (e.g. hand-wrapped) — add just the macro

        if node.get("type") == "codeBlock":
            code_block_count += 1  # non-mermaid — still counts toward the global index

        result.append(node)

    print(f"code blocks on page (any language): {code_block_count}, "
          f"mermaid macros added this run: {added}, "
          f"existing bare diagrams rewrapped this run: {rewrapped}", file=sys.stderr)
    return result


def extract_doc(data):
    """Accept either a full getConfluencePage response or a bare ADF doc."""
    if data.get("type") == "doc" and "content" in data:
        return data
    body = data.get("body")
    if body and body.get("type") == "doc":
        return body
    raise SystemExit("input JSON has no ADF doc (expected {'type':'doc',...} or a page object with .body)")


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="ADF JSON file (contentFormat=adf response), or '-' for stdin")
    p.add_argument("--page-id", required=True, help="target Confluence page id")
    p.add_argument("--space-key", default=DEFAULT_SPACE_KEY)
    p.add_argument("--space-id", default=DEFAULT_SPACE_ID)
    p.add_argument("--cloud-id", default=DEFAULT_CLOUD_ID)
    p.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    p.add_argument("--workspace-ari", default=DEFAULT_WORKSPACE_ARI)
    p.add_argument("--extension-key", default=DEFAULT_EXTENSION_KEY)
    p.add_argument("--extension-type", default=DEFAULT_EXTENSION_TYPE)
    p.add_argument("--collapse-title", default="Diagram source",
                    help="title of the collapsed expand section wrapping the raw mermaid source")
    p.add_argument("--wrap-existing", action="store_true",
                    help="also wrap already-decorated bare codeBlock+extension pairs "
                         "(e.g. native /mermaid editor inserts) in the collapse — off by "
                         "default so existing diagrams are never touched without asking")
    args = p.parse_args()

    raw = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    data = json.loads(raw)
    doc = extract_doc(data)
    new_doc = copy.deepcopy(doc)
    new_doc["content"] = inject(doc["content"], args)
    new_doc.setdefault("version", 1)
    json.dump(new_doc, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
