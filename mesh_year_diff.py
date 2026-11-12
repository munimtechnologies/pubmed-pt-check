#!/usr/bin/env python3
# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# Licensed under the Apache License, Version 2.0 (Apache-2.0). See LICENSE.
# Made with AI agents working in MV2's name.
"""mesh_year_diff: compare two MeSH years (descriptor and qualifier XML) and list every heading
whose name changes, every heading that disappears and every new heading; then record what PubMed
(E-utilities esearch) does with each old and new name today, as a baseline for checking the
same names again after PubMed loads the new MeSH year.

Inputs (defaults): MeSH 2026 production XML from NLM's xmlmesh/ folder and the MeSH 2027 preview
XML that NLM posts for its MeSH Browser (mesh_browser/ folder).

    python mesh_year_diff.py --data-dir /data --out-dir /out
    python mesh_year_diff.py --data-dir /data --out-dir /out --skip-pubmed

Python 3.8+, standard library only. Network: HTTPS GETs to nlmpubs.nlm.nih.gov (downloads) and
eutils.ncbi.nlm.nih.gov (read-only esearch, no API key).
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

VERSION = "0.1.0"
MAILTO = "mv2@munimtech.com"
TOOL = "mesh-year-diff"
UA = "mesh-year-diff/%s (MV2, Munim, Inc.; mailto:%s)" % (VERSION, MAILTO)
ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/"
SOURCES = {
    # name: (url, cache?)  -- production files are cached; preview files are fetched fresh
    "desc_old": (BASE + "xmlmesh/desc2026.gz", True),
    "qual_old": (BASE + "xmlmesh/qual2026.xml", True),
    "desc_new": (BASE + "mesh_browser/desc2027.xml", False),
    "qual_new": (BASE + "mesh_browser/qual2027.xml", False),
}
CLASS_NAMES = {"1": "topical", "2": "publication type", "3": "check tag", "4": "geographic"}


# ---------------------------------------------------------------- pure helpers
def norm(name):
    """PubMed-style comparison key: lower case, punctuation as spaces, single spaces.

    PubMed ignores letter case and punctuation in a quoted phrase, so two names with the same
    key behave the same in a search."""
    s = re.sub(r"[^0-9a-z]+", " ", str(name or "").lower())
    return " ".join(s.split())


def parse_records(source, kind="desc"):
    """{ui: {'ui', 'name', 'cls', 'trees', 'terms'}} from a MeSH descriptor ('desc') or
    qualifier ('qual') XML file path or file object. 'terms' is the set of every term string in
    the record (preferred and entry terms)."""
    rec_tag = "DescriptorRecord" if kind == "desc" else "QualifierRecord"
    ui_tag = "DescriptorUI" if kind == "desc" else "QualifierUI"
    name_tag = "DescriptorName" if kind == "desc" else "QualifierName"
    out = {}
    root = None
    for event, elem in ET.iterparse(source, events=("start", "end")):
        if root is None and event == "start":
            root = elem
            continue
        if event != "end" or elem.tag != rec_tag:
            continue
        ui = (elem.findtext(ui_tag) or "").strip()
        name = (elem.findtext(name_tag + "/String") or "").strip()
        trees = [(t.text or "").strip() for t in elem.findall("TreeNumberList/TreeNumber")]
        terms = set()
        for t in elem.findall("ConceptList/Concept/TermList/Term/String"):
            if t.text and t.text.strip():
                terms.add(t.text.strip())
        if ui:
            out[ui] = {"ui": ui, "name": name, "cls": elem.get("DescriptorClass", ""),
                       "trees": trees, "terms": terms}
        elem.clear()
        if root is not None:
            root.clear()
    return out


def kind_of(rec):
    """'pt' for publication types, else 'mesh' (search tag to use)."""
    if rec.get("cls") == "2" or any(t.startswith("V") for t in rec.get("trees") or []):
        return "pt"
    return "mesh"


def diff(old, new):
    """Compare two {ui: record} maps. Returns dict with lists 'renamed', 'deleted', 'added'.

    renamed: same UI, different name. 'change' is 'words' when the PubMed key differs (a quoted
    old name will stop matching) or 'case_or_punctuation' when only case/punctuation changed.
    'old_kept_as_entry' tells whether the old name is still an entry term of the same record in
    the new year (then PubMed can still map the unquoted old name).
    deleted: UI gone; 'now_entry_of' lists new-year records that carry the old name as a term.
    added: UI new."""
    term_index = {}
    for ui, r in new.items():
        for t in r["terms"] | {r["name"]}:
            term_index.setdefault(norm(t), set()).add(ui)
    renamed, deleted, added = [], [], []
    for ui in sorted(old):
        o = old[ui]
        if ui in new:
            n = new[ui]
            if o["name"] != n["name"]:
                change = "case_or_punctuation" if norm(o["name"]) == norm(n["name"]) else "words"
                kept = norm(o["name"]) in {norm(t) for t in n["terms"]}
                # does the old name now name (or belong to) a different record?
                other = sorted(term_index.get(norm(o["name"]), set()) - {ui})
                renamed.append({"ui": ui, "old": o["name"], "new": n["name"], "change": change,
                                "class": CLASS_NAMES.get(n.get("cls") or o.get("cls"), ""),
                                "tag": kind_of(n), "trees": ";".join(n["trees"]),
                                "old_kept_as_entry": kept, "old_name_now_in": ";".join(other)})
        else:
            into = sorted(term_index.get(norm(o["name"]), set()))
            deleted.append({"ui": ui, "old": o["name"],
                            "class": CLASS_NAMES.get(o.get("cls"), ""), "tag": kind_of(o),
                            "trees": ";".join(o["trees"]),
                            "now_entry_of": ";".join(into),
                            "now_entry_of_names": ";".join(new[u]["name"] for u in into)})
    for ui in sorted(new):
        if ui not in old:
            n = new[ui]
            added.append({"ui": ui, "new": n["name"], "class": CLASS_NAMES.get(n.get("cls"), ""),
                          "tag": kind_of(n), "trees": ";".join(n["trees"])})
    return {"renamed": renamed, "deleted": deleted, "added": added}


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
            "not_found": ";".join(nf)}


def esearch_url(name, tag):
    t = "pt" if tag == "pt" else "mh"
    q = urllib.parse.urlencode({"db": "pubmed", "retmode": "json", "retmax": "0",
                                "term": '"%s"[%s]' % (name.replace('"', ""), t),
                                "tool": TOOL, "email": MAILTO})
    return ESEARCH + "?" + q


def pubmed_checks(rows, fetch, pause=0.4, today=""):
    """One esearch per quoted old and new name. rows: dicts with 'ui', 'old', optional 'new',
    'tag'. Returns a list of result rows."""
    out = []
    n = 0
    for r in rows:
        for which in ("old", "new"):
            name = r.get(which)
            if not name:
                continue
            if n and pause:
                time.sleep(pause)
            n += 1
            res = None
            for attempt in range(3):
                try:
                    res = parse_esearch(fetch(esearch_url(name, r["tag"])))
                    break
                except Exception as e:  # network/JSON failure: retried, then recorded
                    res = {"count": None, "recognized": None, "not_found": "",
                           "error": "%s: %s" % (type(e).__name__, e)}
                    if pause:
                        time.sleep(2 + 3 * attempt)
            row = {"ui": r["ui"], "which": which, "name": name,
                   "query": '"%s"[%s]' % (name, "pt" if r["tag"] == "pt" else "mh"),
                   "count": res.get("count"), "recognized": res.get("recognized"),
                   "not_found": res.get("not_found", ""), "error": res.get("error", ""),
                   "checked": today}
            out.append(row)
    return out


# ---------------------------------------------------------------- I/O
def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, dest, use_cache):
    """Download url to dest (unless cached). Returns provenance dict."""
    info = {"url": url, "path": dest, "cached": False}
    if use_cache and os.path.exists(dest) and os.path.getsize(dest) > 0:
        info["cached"] = True
    else:
        tmp = dest + ".part"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as fh:
                    info["last_modified"] = r.headers.get("Last-Modified", "")
                    info["content_length"] = r.headers.get("Content-Length", "")
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        fh.write(chunk)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(10)
        os.replace(tmp, dest)
    h = hashlib.sha256()
    with open(dest, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    info["sha256"] = h.hexdigest()
    info["bytes"] = os.path.getsize(dest)
    return info


def open_xml(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    return gzip.open(path, "rb") if magic == b"\x1f\x8b" else open(path, "rb")


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def report_md(d_desc, d_qual, checks, prov, n_old, n_new):
    lines = ["# MeSH 2026 -> 2027 (preview) diff", "",
             "Made with AI agents working in MV2's name (Munim, Inc.).", "",
             "Descriptors: %d (2026) vs %d (2027 preview)." % (n_old, n_new), ""]
    words = [r for r in d_desc["renamed"] if r["change"] == "words"]
    cp = [r for r in d_desc["renamed"] if r["change"] != "words"]
    lines.append("Renamed (words): %d; case/punctuation only: %d; deleted: %d; added: %d." % (
        len(words), len(cp), len(d_desc["deleted"]), len(d_desc["added"])))
    lines.append("")
    by = {(c["ui"], c["which"]): c for c in checks}
    lines += ["| UI | Old name | New name | Class | Old kept as entry | Old today | New today |",
              "|---|---|---|---|---|---|---|"]
    for r in d_desc["renamed"]:
        o = by.get((r["ui"], "old"), {})
        n = by.get((r["ui"], "new"), {})
        lines.append("| %s | %s | %s | %s | %s | %s%s | %s%s |" % (
            r["ui"], r["old"], r["new"], r["class"] + ("" if r["change"] == "words" else " (case)"),
            "yes" if r["old_kept_as_entry"] else "no",
            o.get("count", ""), "" if o.get("recognized", True) else " (not found)",
            n.get("count", ""), "" if n.get("recognized", True) else " (not found)"))
    lines += ["", "## Deleted", "", "| UI | Old name | Class | Now an entry term of | Old today |",
              "|---|---|---|---|---|"]
    for r in d_desc["deleted"]:
        o = by.get((r["ui"], "old"), {})
        lines.append("| %s | %s | %s | %s | %s%s |" % (
            r["ui"], r["old"], r["class"], r["now_entry_of_names"] or "-",
            o.get("count", ""), "" if o.get("recognized", True) else " (not found)"))
    lines += ["", "## Qualifiers", ""]
    for r in d_qual["renamed"]:
        lines.append("- renamed %s: %s -> %s" % (r["ui"], r["old"], r["new"]))
    for r in d_qual["deleted"]:
        lines.append("- deleted %s: %s" % (r["ui"], r["old"]))
    for r in d_qual["added"]:
        lines.append("- added %s: %s" % (r["ui"], r["new"]))
    lines += ["", "## Files", ""]
    for k, p in sorted(prov.items()):
        lines.append("- %s: %s, %s bytes, sha256 %s, Last-Modified %s" % (
            k, p.get("url"), p.get("bytes"), p.get("sha256"), p.get("last_modified", "(cached)")))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--skip-pubmed", action="store_true")
    ap.add_argument("--pause", type=float, default=0.4)
    a = ap.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    os.makedirs(a.out_dir, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    prov = {}
    for k, (url, cache) in SOURCES.items():
        dest = os.path.join(a.data_dir, os.path.basename(url))
        prov[k] = download(url, dest, cache)
        print("downloaded", k, prov[k]["bytes"], prov[k].get("last_modified", "(cached)"),
              flush=True)
    recs = {}
    for k in SOURCES:
        with open_xml(prov[k]["path"]) as fh:
            recs[k] = parse_records(fh, "desc" if k.startswith("desc") else "qual")
        print("parsed", k, len(recs[k]), flush=True)
    d_desc = diff(recs["desc_old"], recs["desc_new"])
    d_qual = diff(recs["qual_old"], recs["qual_new"])
    to_check = [r for r in d_desc["renamed"]] + [dict(r, new="") for r in d_desc["deleted"]]
    checks = [] if a.skip_pubmed else pubmed_checks(to_check, fetch_json, a.pause, started[:10])
    write_csv(os.path.join(a.out_dir, "renamed.csv"), d_desc["renamed"],
              ["ui", "old", "new", "change", "class", "tag", "trees", "old_kept_as_entry",
               "old_name_now_in"])
    write_csv(os.path.join(a.out_dir, "deleted.csv"), d_desc["deleted"],
              ["ui", "old", "class", "tag", "trees", "now_entry_of", "now_entry_of_names"])
    write_csv(os.path.join(a.out_dir, "added.csv"), d_desc["added"],
              ["ui", "new", "class", "tag", "trees"])
    write_csv(os.path.join(a.out_dir, "qualifiers.csv"),
              [dict(r, status="renamed") for r in d_qual["renamed"]] +
              [dict(r, status="deleted") for r in d_qual["deleted"]] +
              [dict(r, status="added") for r in d_qual["added"]],
              ["status", "ui", "old", "new"])
    write_csv(os.path.join(a.out_dir, "pubmed_baseline.csv"), checks,
              ["ui", "which", "name", "query", "count", "recognized", "not_found", "error",
               "checked"])
    summary = {"version": VERSION, "started": started,
               "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "records": {k: len(v) for k, v in recs.items()},
               "renamed_words": sum(1 for r in d_desc["renamed"] if r["change"] == "words"),
               "renamed_case_or_punctuation": sum(1 for r in d_desc["renamed"]
                                                  if r["change"] != "words"),
               "renamed_old_kept_as_entry": sum(1 for r in d_desc["renamed"]
                                                if r["old_kept_as_entry"]),
               "deleted": len(d_desc["deleted"]), "added": len(d_desc["added"]),
               "qualifiers": {k: len(v) for k, v in d_qual.items()},
               "pubmed_checks": len(checks),
               "pubmed_errors": sum(1 for c in checks if c.get("error")),
               "files": prov}
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(a.out_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write(report_md(d_desc, d_qual, checks, prov, len(recs["desc_old"]),
                           len(recs["desc_new"])))
    print(json.dumps({k: v for k, v in summary.items() if k != "files"}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
