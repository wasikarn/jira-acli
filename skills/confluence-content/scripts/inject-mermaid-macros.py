#!/usr/bin/env python3
"""inject-mermaid-macros — add the "Mermaid diagram" Forge render macro after
every mermaid code block on a Confluence page.

Why this exists: a ```mermaid fenced code block in Markdown (or a `code`
macro with language=mermaid in storage format) only gets you syntax-
highlighted TEXT — Confluence Cloud has no native Mermaid renderer. This repo's
sites have the "Mermaid diagram" marketplace app installed (a Forge custom-UI
macro, extension-type `com.atlassian.ecosystem`), which DOES render the
diagram, but it is a *separate* macro instance that must sit immediately
after each code block — one macro renders one code block, not the whole page.

Discovered 2026-07-14 against TP-807's spec page (100-stars.atlassian.net,
space BEP) by inserting the macro once by hand via the Confluence editor's
`/mermaid` slash command, then reading the page back with
`getConfluencePage(contentFormat="html")` to see the exact HTML+ syntax the
Atlassian MCP tools expect on write — a `<div data-type="extension" ...>`
node, documented in `createConfluencePage`/`updateConfluencePage`'s own
`body` param description. Verified round-trip on 7 instances on one page.

What varies between instances (confirmed by diffing 7 real macro instances):
  - `data-local-id` / `localId` — any fresh UUID4, unique per instance.
  - `guestParams.index` — 0-based, sequential in PAGE ORDER across every
    "Mermaid diagram" macro instance on the page (not just the ones this
    script adds — if the page already has some, continue the count).
Everything else (extension-key, cloud-id, account-id, workspace ARI,
`extensionData.content.version` which is a fixed macro-schema constant and
NOT the real page version) is a per-site/per-author constant — safe to reuse
across pages on the SAME site, wrong on a different Atlassian site or a
different Forge app install. Re-derive by inserting the macro once by hand
and re-running this discovery if the org/site changes.

Usage:
  # 1. Fetch the current page as HTML (round-trip-safe format):
  #      getConfluencePage(cloudId, pageId, contentFormat="html")  -> body
  # 2. Save that body to a file, run this script, feed the result back to
  #      updateConfluencePage(cloudId, pageId, body=<output>, contentFormat="html")
  python3 inject-mermaid-macros.py page.html --page-id 217743376 > page-with-macros.html
  python3 inject-mermaid-macros.py - --page-id 217743376 < page.html > out.html

Idempotent: a code block already followed by a Mermaid-diagram extension div
(from a prior run, or from a manual /mermaid insert) is left untouched and
does not count twice — safe to re-run after adding more diagrams to a page
that already has some rendered.
"""
import argparse
import re
import sys
import uuid

# ── site-specific constants (100-stars.atlassian.net / TaThep) ─────────────
# Re-derive these if this script is ever pointed at a different Atlassian
# site: insert the macro once by hand via the editor, then diff the page's
# contentFormat="html" body against this script's output.
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

CODE_BLOCK_RE = re.compile(
    r'<pre[^>]*><code class="language-mermaid">.*?</code></pre>',
    re.DOTALL,
)
EXISTING_MACRO_RE = re.compile(r'data-extension-key="[^"]*static/mermaid-diagram"')


def build_macro_div(local_id, index, args):
    params = (
        '{{&quot;layout&quot;:&quot;extension&quot;,'
        '&quot;guestParams&quot;:{{&quot;index&quot;:{index}}},'
        '&quot;forgeEnvironment&quot;:&quot;PRODUCTION&quot;,'
        '&quot;embeddedMacroContext&quot;:{{'
        '&quot;accountId&quot;:&quot;{account_id}&quot;,'
        '&quot;cloudId&quot;:&quot;{cloud_id}&quot;,'
        '&quot;contextIds&quot;:[&quot;{workspace_ari}&quot;],'
        '&quot;extensionData&quot;:{{&quot;type&quot;:&quot;macro&quot;,'
        '&quot;content&quot;:{{&quot;id&quot;:&quot;{page_id}&quot;,'
        '&quot;type&quot;:&quot;page&quot;,&quot;version&quot;:{content_version}}},'
        '&quot;space&quot;:{{&quot;id&quot;:&quot;{space_id}&quot;,'
        '&quot;key&quot;:&quot;{space_key}&quot;}}}}}},'
        '&quot;localId&quot;:&quot;{local_id}&quot;,'
        '&quot;extensionId&quot;:&quot;ari:cloud:ecosystem::extension/{extension_key}&quot;,'
        '&quot;extensionTitle&quot;:&quot;Mermaid diagram&quot;}}'
    ).format(
        index=index,
        account_id=args.account_id,
        cloud_id=args.cloud_id,
        workspace_ari=args.workspace_ari,
        page_id=args.page_id,
        content_version=CONTENT_VERSION,
        space_id=args.space_id,
        space_key=args.space_key,
        local_id=local_id,
        extension_key=args.extension_key,
    )
    return (
        f'<div data-local-id="{local_id}" data-type="extension" '
        f'data-extension-key="{args.extension_key}" '
        f'data-extension-type="{args.extension_type}" data-layout="default" '
        f'data-parameters="{params}">Mermaid diagram</div>'
    )


def inject(html, args):
    existing = len(EXISTING_MACRO_RE.findall(html))
    added = 0

    def replace(match):
        nonlocal added
        block = match.group(0)
        tail = html[match.end():match.end() + 400]
        if EXISTING_MACRO_RE.search(tail[:200]):
            return block  # already has a macro right after it — leave alone
        local_id = str(uuid.uuid4())
        index = existing + added
        added += 1
        return block + build_macro_div(local_id, index, args)

    result = CODE_BLOCK_RE.sub(replace, html)
    print(f"mermaid code blocks found: total existing macros: {existing}, "
          f"macros added this run: {added}", file=sys.stderr)
    return result


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="HTML body file (contentFormat=html), or '-' for stdin")
    p.add_argument("--page-id", required=True, help="target Confluence page id")
    p.add_argument("--space-key", default=DEFAULT_SPACE_KEY)
    p.add_argument("--space-id", default=DEFAULT_SPACE_ID)
    p.add_argument("--cloud-id", default=DEFAULT_CLOUD_ID)
    p.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID)
    p.add_argument("--workspace-ari", default=DEFAULT_WORKSPACE_ARI)
    p.add_argument("--extension-key", default=DEFAULT_EXTENSION_KEY)
    p.add_argument("--extension-type", default=DEFAULT_EXTENSION_TYPE)
    args = p.parse_args()

    html = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    sys.stdout.write(inject(html, args))


if __name__ == "__main__":
    main()
