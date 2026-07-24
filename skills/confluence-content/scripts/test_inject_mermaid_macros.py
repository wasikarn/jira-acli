#!/usr/bin/env python3
"""Self-check for inject-mermaid-macros.py. No framework — run directly: python3 test_inject_mermaid_macros.py

Uses a synthetic minimal ADF fixture only — never real page content."""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("inject_mermaid_macros", Path(__file__).parent / "inject-mermaid-macros.py")
assert spec and spec.loader
inject_mermaid_macros = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inject_mermaid_macros)
inject = inject_mermaid_macros.inject
is_matching_extension = inject_mermaid_macros.is_matching_extension


def make_args(wrap_existing=False):
    return SimpleNamespace(
        extension_key="test-extension-key",
        extension_type="com.atlassian.ecosystem",
        cloud_id="cloud-1",
        account_id="account-1",
        workspace_ari="ari:cloud:confluence:cloud-1:workspace/w-1",
        page_id="999",
        space_id="1",
        space_key="TST",
        collapse_title="Diagram source",
        wrap_existing=wrap_existing,
    )


def mermaid_block(text="graph TD; A-->B;"):
    return {"type": "codeBlock", "attrs": {"language": "mermaid"}, "content": [{"type": "text", "text": text}]}


def other_block(lang="bash", text="echo hi"):
    return {"type": "codeBlock", "attrs": {"language": lang}, "content": [{"type": "text", "text": text}]}


def paragraph(text="p"):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def test_fresh_injection_wraps_and_adds_macro():
    content = [paragraph(), mermaid_block()]
    result = inject(content, make_args())
    assert result[0]["type"] == "paragraph"
    assert result[1]["type"] == "expand"
    assert result[1]["content"][0]["type"] == "codeBlock"
    assert result[2]["type"] == "extension"
    assert is_matching_extension(result[2], "test-extension-key")
    assert len(result) == 3


def test_idempotent_on_already_wrapped_and_decorated():
    first_pass = inject([paragraph(), mermaid_block()], make_args())
    second_pass = inject(first_pass, make_args())
    assert second_pass == first_pass  # nothing added or rewrapped on a rerun


def test_bare_pair_left_as_is_without_wrap_existing():
    block = mermaid_block()
    ext = inject_mermaid_macros.build_extension_node(0, make_args())
    content = [block, ext]
    result = inject(content, make_args(wrap_existing=False))
    assert result == content  # native /mermaid insert, untouched by default


def test_bare_pair_wrapped_with_wrap_existing_flag():
    block = mermaid_block()
    ext = inject_mermaid_macros.build_extension_node(0, make_args())
    content = [block, ext]
    result = inject(content, make_args(wrap_existing=True))
    assert result[0]["type"] == "expand"
    assert result[0]["content"][0] is block
    assert result[1] is ext  # unchanged extension, same object, appended by the loop's next iteration


def test_mixed_language_index_counts_all_code_blocks():
    # a non-mermaid block before the mermaid one must still bump the index —
    # guestParams.index tracks ALL codeBlocks on the page, not mermaid-only
    # (see the script's own docstring on this exact, previously-unverified edge case)
    content = [other_block(), mermaid_block()]
    result = inject(content, make_args())
    assert result[0]["type"] == "codeBlock"  # non-mermaid block passed through untouched
    extension = result[2]
    assert extension["attrs"]["parameters"]["guestParams"]["index"] == 1


def test_nested_code_block_is_not_touched():
    # deliberately top-level-only traversal (ponytail-annotated in the script) —
    # a mermaid block nested inside another container is invisible to this pass
    nested = {"type": "table", "content": [{"type": "tableRow", "content": [mermaid_block()]}]}
    content = [nested]
    result = inject(content, make_args())
    assert result == content


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
