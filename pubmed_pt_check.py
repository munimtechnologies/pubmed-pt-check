#!/usr/bin/env python3
# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Licensed under the Apache License, Version 2.0 (Apache-2.0). See LICENSE.
# Made with AI agents working in MV2's name.
"""pubmed-pt-check: find PubMed publication types and MeSH headings that PubMed no longer
recognizes under the name a search uses.

NLM renamed three PubMed publication types, in two MeSH years: "Retraction of Publication" is
now "Retraction Notice" (MeSH 2025, NLM Tech Bull 2024 Nov-Dec;(461):e4); "Congress" is now
"Conference Proceedings" and "Consensus Development Conference" is now "Consensus Statement"
(MeSH 2026, NLM Tech Bull 2026 Jan-Feb;(468):e6). PubMed's article-type filters followed in
March 2026 (NLM Tech Bull 2026 Mar-Apr;(469):e1). Checked against E-utilities on 2026-11-11, the
old names no longer match anything in a [pt] search: PubMed treats the term as an empty set and
only adds a "quoted phrase not found" warning.

- alone or joined with AND: the search (or AND clause) finds 0 records;
- joined with OR: the term is dropped and the rest of the OR group runs, so the result silently
  misses every record of the renamed type;
- after NOT: the term is dropped, so nothing is excluded.

Seventeen more types were discontinued: older citations keep them and they are still searchable,
but new citations no longer get them.

0.1.1: MeSH headings too. MeSH 2026 renamed the heading "Consensus Development Conferences as
Topic" to "Consensus Statements as Topic". PubMed maps an old heading name to the new one only
when the term is not in quotes; a quoted old name ("..."[mh], [mesh], [majr], with or without
:noexp) finds nothing, exactly like an old publication-type name (checked 2026-11-12). Published
guideline search filters quote their headings, so they lose these records silently.

This script reads search strings, saved strategies or source code, finds every term tagged [pt],
[ptyp], [Publication Type], [mh], [mesh], [majr] or [MeSH Terms], and reports renamed and
discontinued names with the effect that the surrounding Boolean operator has. --fix rewrites
renamed names; --live asks PubMed itself (E-utilities esearch) whether each publication type and
each quoted MeSH heading in the input is recognized today, which also catches renames this script
does not know about yet.

    python pubmed_pt_check.py '"Cochrane Database Syst Rev"[ta] NOT "Retraction of Publication"[pt]'
    python pubmed_pt_check.py --live search_strategy.txt
    python pubmed_pt_check.py --fix '("Retraction of Publication"[pt] OR "Retracted Publication"[pt])'

Exit codes: 0 = nothing renamed or unrecognized; 1 = at least one renamed or unrecognized
publication type or quoted MeSH heading; 2 = bad input or a failed --live lookup. Python 3.8+,
standard library only; --live makes read-only HTTPS GETs to eutils.ncbi.nlm.nih.gov (no API key).
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

VERSION = "0.1.1"
MAILTO = "mv2@munimtech.com"
TOOL = "pubmed-pt-check"
UA = "pubmed-pt-check/%s (MV2, Munim, Inc.; mailto:%s)" % (VERSION, MAILTO)
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
SOURCE = ("NLM Technical Bulletin 2024 Nov-Dec (461):e4, 2026 Jan-Feb (468):e6 and 2026 Mar-Apr "
          "(469):e1, https://www.nlm.nih.gov/pubs/techbull/ma26/ma26_pubmed_update_MeSH_changes.html")


def key(name):
    """Comparison key for a publication type name: lower case, no dots, single spaces."""
    return " ".join(str(name or "").replace(".", "").lower().split())


RENAMED = {
    key("Retraction of Publication"): "Retraction Notice",
    key("Congress"): "Conference Proceedings",
    key("Consensus Development Conference"): "Consensus Statement",
}
# MeSH year of each rename (NLM Technical Bulletins 461:e4 and 468:e6).
RENAMED_YEAR = {
    key("Retraction of Publication"): 2025,
    key("Congress"): 2026,
    key("Consensus Development Conference"): 2026,
}
DISCONTINUED = {key(n) for n in (
    "Autobiography", "Bibliography", "Clinical Conference",
    "Consensus Development Conference, NIH", "Dictionary", "Directory",
    "Government Publication", "Interactive Tutorial", "Legal Case", "Legislation",
    "Newspaper Article", "Overall", "Periodical Index", "Portrait",
    "Scientific Integrity Review", "Seminal Article", "Technical Report")}
# Renamed MeSH headings (descriptors). Only renames checked by hand against PubMed are listed;
# --live finds others. D003245: "use CONSENSUS DEVELOPMENT CONFERENCES AS TOPIC 2008-2025".
MESH_RENAMED = {
    key("Consensus Development Conferences as Topic"): "Consensus Statements as Topic",
}
MESH_RENAMED_YEAR = {
    key("Consensus Development Conferences as Topic"): 2026,
}
NOTES = {
    key("Retraction of Publication"): "NLM's own Retraction filter now runs "
                                      "'hasretractionof OR retraction notice[pt]'.",
}

TAG = re.compile(r"\[\s*(pt|ptyp|publication type)\s*\]", re.I)
MESH_TAG = re.compile(r"\[\s*(mh|mesh|majr|mesh terms|mesh major topic)(\s*:\s*noexp)?\s*\]", re.I)
OPS = re.compile(r"(?<![A-Za-z0-9_])(AND|OR|NOT)(?![A-Za-z0-9_])")
OP_END = re.compile(r"(?<![A-Za-z0-9_])(AND|OR|NOT)$")
OP_START = re.compile(r"(AND|OR|NOT)(?![A-Za-z0-9_])")
DELIMS = set("()\"'=`{}[]:;")


# ---------------------------------------------------------------- parsing (pure)
def _term_before(text, j):
    """(term, start, end) of the search term that ends just before index j (a field tag)."""
    while j > 0 and text[j - 1].isspace():
        j -= 1
    if j > 0 and text[j - 1] == '"':
        k = text.rfind('"', 0, j - 1)
        if k < 0:
            return "", j, j
        return text[k + 1:j - 1], k, j
    lo = j
    while lo > 0 and text[lo - 1] not in DELIMS:
        lo -= 1
    s = lo
    for m in OPS.finditer(text, lo, j):
        s = m.end()
    while s < j and text[s].isspace():
        s += 1
    return text[s:j], s, j


def operator_of(text, start, end):
    """(operator, side) joining the term text[start:end-of-tag] to its neighbours.

    side 'before': the operator comes before the term (skipping spaces and '('); side 'after':
    the term comes first and the operator follows (skipping spaces and ')'). (None, None) when the
    term stands alone. Implicit AND between bare words is not detected."""
    i = start
    while i > 0 and (text[i - 1].isspace() or text[i - 1] == "("):
        i -= 1
    m = OP_END.search(text, 0, i)
    if m:
        return m.group(1), "before"
    m = OP_START.match(text[end:].lstrip(" \t\r\n)"))
    if m:
        return m.group(1), "after"
    return None, None


def find_terms(text):
    """Every publication-type and MeSH term in text, in order: dicts with term, start, term_end,
    tag_end, tag, field ('pt' or 'mesh') and quoted (True if the term is in double quotes)."""
    out = []
    for field, rx in (("pt", TAG), ("mesh", MESH_TAG)):
        for m in rx.finditer(text):
            term, s, e = _term_before(text, m.start())
            if not term.strip():
                continue
            out.append({"term": term.strip(), "start": s, "term_end": e, "tag_end": m.end(),
                        "tag": text[m.start():m.end()], "field": field,
                        "quoted": text[s:s + 1] == '"'})
    out.sort(key=lambda d: d["start"])
    return out


def classify(term, field="pt", quoted=True):
    """(status, new_name). For MeSH headings, an unquoted old name is mapped to the new heading
    by PubMed, so it is 'renamed_mapped' (reported, not a problem)."""
    k = key(term)
    if field == "mesh":
        if k in MESH_RENAMED:
            return ("renamed" if quoted else "renamed_mapped"), MESH_RENAMED[k]
        return "ok", None
    if k in RENAMED:
        return "renamed", RENAMED[k]
    if k in DISCONTINUED:
        return "discontinued", None
    return "ok", None


def effect(status, op, side, new=None, field="pt"):
    """What PubMed does with a term of this status in this Boolean position."""
    if status == "discontinued":
        return ("Discontinued: still matches older citations, but NLM no longer assigns this "
                "type to new citations.")
    if status == "renamed_mapped":
        return ("PubMed maps this old heading name to \"%s\" because it is not in quotes; "
                "quoted, it would find nothing. Prefer the new name." % new)
    if status not in ("renamed", "not_recognized"):
        return ""
    if new:
        newtype = ("records indexed with \"%s\"" if field == "mesh" else "records typed \"%s\"") % new
    else:
        newtype = "the records you meant"
    if op == "OR":
        return ("PubMed drops this term without an error, so the OR group silently misses %s."
                % newtype)
    if op == "NOT" and side == "before":
        return ("PubMed drops this term, so this NOT excludes nothing; %s stay in the results."
                % newtype)
    if op in ("AND", "NOT"):
        return "This clause matches nothing, so the search (or this AND clause) finds 0 records."
    return "PubMed finds 0 records for this term."


def renamed_year(term, field):
    k = key(term)
    return (MESH_RENAMED_YEAR if field == "mesh" else RENAMED_YEAR).get(k)


def check_text(text):
    """Findings for every publication-type and MeSH term in one piece of text (no network)."""
    out = []
    for t in find_terms(text):
        status, new = classify(t["term"], t["field"], t["quoted"])
        op, side = operator_of(text, t["start"], t["tag_end"])
        out.append({"term": t["term"], "tag": t["tag"], "field": t["field"],
                    "quoted": t["quoted"], "status": status, "new_name": new,
                    "mesh_year": renamed_year(t["term"], t["field"]) if new else None,
                    "operator": op, "side": side,
                    "effect": effect(status, op, side, new, t["field"]),
                    "note": NOTES.get(key(t["term"]), "") if t["field"] == "pt" else "",
                    "start": t["start"], "term_end": t["term_end"]})
    return out


def fix_text(text):
    """text with every renamed publication type and MeSH heading replaced by its new name
    (quoted)."""
    for t in sorted(find_terms(text), key=lambda d: -d["start"]):
        status, new = classify(t["term"], t["field"], t["quoted"])
        if status in ("renamed", "renamed_mapped"):
            text = text[:t["start"]] + '"%s"' % new + text[t["term_end"]:]
    return text


def line_variants(line):
    """The line itself with escaped quotes undone, plus its URL-decoded form if it looks
    URL-encoded (PubMed links and E-utilities calls in scripts)."""
    out = [line.replace('\\"', '"')]
    low = line.lower()
    if "%5b" in low or "%22" in low:
        out.append(urllib.parse.unquote_plus(line).replace('\\"', '"'))
    return out


def scan_lines(text, source):
    """Findings for a multi-line text (a file), one pass per line and per line variant."""
    out, seen = [], set()
    for no, line in enumerate(text.splitlines(), 1):
        for variant in line_variants(line):
            for f in check_text(variant):
                sig = (no, f["field"], key(f["term"]), f["operator"], f["side"])
                if sig in seen:
                    continue
                seen.add(sig)
                f.update(source=source, line=no)
                out.append(f)
    return out


# ---------------------------------------------------------------- PubMed (--live)
def parse_esearch(obj):
    """{'count', 'recognized', 'not_found'} from an esearch JSON reply for one quoted term."""
    r = (obj or {}).get("esearchresult") or {}
    warn = r.get("warninglist") or {}
    err = r.get("errorlist") or {}
    nf = list(warn.get("quotedphrasesnotfound") or []) + list(err.get("phrasesnotfound") or [])
    try:
        count = int(r.get("count"))
    except (TypeError, ValueError):
        count = None
    return {"count": count, "recognized": (not nf) if count is not None else None,
            "not_found": nf}


def esearch_url(term, field="pt"):
    tag = "mh" if field == "mesh" else "pt"
    q = urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "retmax": "0",
                                "term": '"%s"[%s]' % (term.replace('"', ""), tag),
                                "tool": TOOL, "email": MAILTO})
    return ESEARCH + "?" + q


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def live_key(term, field="pt"):
    return ("mesh:" if field == "mesh" else "") + key(term)


def live_lookup(terms, fetch=None, pause=0.4):
    """{live_key: parse_esearch result or {'error': ...}} for each distinct term. Items are
    publication-type names or (name, field) pairs."""
    fetch = fetch or fetch_json
    out = {}
    n = 0
    for item in terms:
        term, field = (item, "pt") if isinstance(item, str) else item
        k = live_key(term, field)
        if k in out:
            continue
        if n and pause:
            time.sleep(pause)
        n += 1
        try:
            out[k] = parse_esearch(fetch(esearch_url(term, field)))
        except Exception as e:  # network or JSON failure: reported, never fatal
            out[k] = {"error": "%s: %s" % (type(e).__name__, e)}
    return out


def wants_live(f):
    """Publication types are always checked; MeSH headings only when quoted (PubMed maps an
    unquoted entry term to its heading, so a quoted-phrase test would mislead)."""
    return f.get("field", "pt") == "pt" or f.get("quoted")


def apply_live(findings, live):
    """Attach live results; an 'ok' term PubMed does not recognize becomes 'not_recognized'."""
    for f in findings:
        if not wants_live(f):
            continue
        res = live.get(live_key(f["term"], f.get("field", "pt"))) or {}
        f["live"] = res
        if res.get("recognized") is False and f["status"] == "ok":
            f["status"] = "not_recognized"
            f["effect"] = effect("not_recognized", f["operator"], f["side"], None,
                                 f.get("field", "pt"))
        elif res.get("recognized") is True and f["status"] == "renamed":
            f["effect"] = ("PubMed recognized this old name when checked (count %s); NLM has "
                           "still renamed it, so prefer the new name." % res.get("count"))
    return findings


def is_problem(f):
    if f["status"] == "not_recognized":
        return True
    if f["status"] == "renamed":
        return (f.get("live") or {}).get("recognized") is not True
    return False


# ---------------------------------------------------------------- CLI
def read_input(arg, stdin):
    """(source, text, is_file)."""
    if arg == "-":
        return "<stdin>", stdin.read(), False
    if os.path.isfile(arg):
        with open(arg, encoding="utf-8", errors="replace") as fh:
            return arg, fh.read(), True
    return "<query>", arg, False


def run(inputs, live=False, fetch=None, stdin=None, pause=0.4):
    """(findings, errors) for a list of query strings, file paths or '-'."""
    findings, errors = [], []
    for arg in inputs:
        try:
            source, text, is_file = read_input(arg, stdin or sys.stdin)
        except OSError as e:
            errors.append("%s: %s" % (arg, e))
            continue
        if is_file:
            findings.extend(scan_lines(text, source))
        else:
            for f in check_text(text):
                f.update(source=source, line=None)
                findings.append(f)
    asked = [f for f in findings if wants_live(f)]
    if live and asked:
        res = live_lookup([(f["term"], f.get("field", "pt")) for f in asked], fetch=fetch,
                          pause=pause)
        apply_live(findings, res)
        for k, r in res.items():
            if "error" in r:
                errors.append("live lookup failed for %r: %s" % (k, r["error"]))
    return findings, errors


def describe(f):
    where = f["source"] + (":%d" % f["line"] if f.get("line") else "")
    head = '%s: "%s"%s' % (where, f["term"], f["tag"])
    what = "MeSH heading" if f.get("field") == "mesh" else "publication type"
    year = (" (MeSH %s)" % f["mesh_year"]) if f.get("mesh_year") else ""
    if f["status"] == "renamed":
        head += ' -> renamed to "%s"%s.' % (f["new_name"], year)
    elif f["status"] == "renamed_mapped":
        head += ' -> renamed to "%s"%s; mapped because unquoted.' % (f["new_name"], year)
    elif f["status"] == "discontinued":
        head += " -> discontinued type."
    elif f["status"] == "not_recognized":
        head += " -> PubMed does not recognize this %s today." % what
    else:
        head += " -> current."
    if f.get("operator"):
        head += " Joined by %s." % f["operator"]
    lines = [head]
    if f.get("effect"):
        lines.append("    " + f["effect"])
    if f.get("note"):
        lines.append("    " + f["note"])
    live = f.get("live") or {}
    if "count" in live:
        lines.append("    PubMed today: %s records for \"%s\"[%s]%s." % (
            live["count"], f["term"], "mh" if f.get("field") == "mesh" else "pt",
            "" if live.get("recognized") else " (phrase not found)"))
    return "\n".join(lines)


def main(argv=None, fetch=None, out=None, stdin=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(prog="pubmed_pt_check.py", description=(
        "Find PubMed publication types ([pt]) and quoted MeSH headings ([mh]) that NLM renamed "
        "or discontinued."))
    ap.add_argument("inputs", nargs="+", help="query strings, file paths, or - for stdin")
    ap.add_argument("--live", action="store_true",
                    help="ask PubMed (E-utilities) whether each publication type and quoted "
                         "MeSH heading is recognized")
    ap.add_argument("--all", action="store_true", help="also list current terms")
    ap.add_argument("--fix", action="store_true",
                    help="print the input with renamed names replaced (one input only)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    a = ap.parse_args(argv)
    if a.fix:
        if len(a.inputs) != 1:
            out.write("--fix takes exactly one input\n")
            return 2
        try:
            _, text, _ = read_input(a.inputs[0], stdin or sys.stdin)
        except OSError as e:
            out.write("%s\n" % e)
            return 2
        out.write(fix_text(text))
        if not text.endswith("\n"):
            out.write("\n")
        return 0
    findings, errors = run(a.inputs, live=a.live, fetch=fetch, stdin=stdin)
    shown = [f for f in findings if a.all or f["status"] != "ok"]
    if a.json:
        out.write(json.dumps({"version": VERSION, "source": SOURCE, "findings": shown,
                              "errors": errors}, indent=1) + "\n")
    else:
        for f in shown:
            out.write(describe(f) + "\n")
        for e in errors:
            out.write("error: %s\n" % e)
        n = sum(1 for f in findings if is_problem(f))
        n_pt = sum(1 for f in findings if f.get("field", "pt") == "pt")
        out.write("checked %d publication-type term(s) and %d MeSH term(s): %d renamed or "
                  "unrecognized, %d discontinued.\n" % (
                      n_pt, len(findings) - n_pt, n,
                      sum(1 for f in findings if f["status"] == "discontinued")))
    if errors:
        return 2
    return 1 if any(is_problem(f) for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
