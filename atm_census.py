#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# atm_census.py - which MeSH entry terms does PubMed's Automatic Term Mapping fail to map?
# Pre-registered as PREREG-ATM-1 in munimtechnologies/pubmed-pt-check.
# MV2, Munim, Inc., mv2@munimtech.com. Made with AI agents working in MV2's name.
"""atm_census: MeSH entry terms that PubMed does not map to their own heading.

PubMed's Automatic Term Mapping (ATM) is supposed to turn an untagged, unquoted entry term
into its MeSH heading: `heart attack` becomes `"myocardial infarction"[MeSH Terms] OR ...`.
On 2026-11-13 two entry terms that used to be headings of their own did not map at all:
`Pneumocystis jirovecii` (now a term of D045363 Pneumocystis carinii) is searched as the
genus AND the word jirovecii, and `Korarchaeota` (now a term of D019615 Crenarchaeota) is
searched as a plain word. This script measures how common that is:

  Set A: every name that is the preferred term of an obsolete (deleted) MeSH descriptor and
         is now a term of a current descriptor (from NLM's MeSH SPARQL, current graph);
  Set B: a seeded random sample of ordinary entry terms of current topical descriptors
         (from desc2026, the MeSH year PubMed searches with on 2026-11-13).

For each term it sends the term, unquoted and untagged, to E-utilities esearch and reads
`querytranslation`: 'own' if the term's own heading appears as "..."[MeSH Terms], otherwise
'other_mesh' (some other heading only) or 'none' (no heading at all). For every term that
fails it also counts the heading's records the untagged search does not retrieve:
`"<heading>"[mh] NOT (<term>)`.

    python atm_census.py --data-dir /data --out-dir /out [--n-sample 1500]

Python 3.8+, standard library only. Network: nlmpubs.nlm.nih.gov, id.nlm.nih.gov and
eutils.ncbi.nlm.nih.gov (about 2.5 requests per second, as NCBI asks without an API key).
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from fractions import Fraction

VERSION = "0.1.0"
MAILTO = "mv2@munimtech.com"
TOOL = "mv2-atm-census"
UA = "atm-census/%s (MV2, Munim, Inc.; mailto:%s)" % (VERSION, MAILTO)
DESC_URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2026.gz"
SPARQL_URL = "https://id.nlm.nih.gov/mesh/sparql"
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
SEED = 20261113
PAUSE = 0.4

# Pre-registered sanity rows, observed by hand on 2026-11-13 (term, descriptor UI, expected).
SANITY = [
    ("Heart Attack", "D009203", "own"),
    ("Healthy Habits", "D000070497", "own"),
    ("Korarchaeota", "D019615", "fail"),
    ("Pneumocystis jirovecii", "D045363", "fail"),
]

SET_A_QUERY = """PREFIX mv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?od ?y ?name ?d ?dl FROM <http://id.nlm.nih.gov/mesh> WHERE {
 ?od mv:lastActiveYear ?y ; a mv:TopicalDescriptor ; mv:preferredTerm ?pt .
 ?pt mv:prefLabel ?name .
 ?c mv:term|mv:preferredTerm ?pt .
 ?d mv:concept|mv:preferredConcept ?c ; rdfs:label ?dl .
 FILTER(?d != ?od)
 FILTER NOT EXISTS { ?d mv:lastActiveYear ?z }
} ORDER BY ?y ?name"""

MESH_PHRASE_RE = re.compile(r'"([^"]+)"\[MeSH Terms(?::noexp)?\]', re.I)


# ---------------------------------------------------------------- pure helpers
def norm(name):
    """Comparison key: lower case, punctuation as spaces, single spaces."""
    s = re.sub(r"[^0-9a-z]+", " ", str(name or "").lower())
    return " ".join(s.split())


def mesh_phrases(translation):
    """Every heading PubMed searched as "..."[MeSH Terms], normalised, in order."""
    return [norm(m.group(1)) for m in MESH_PHRASE_RE.finditer(translation or "")]


def classify_translation(translation, heading):
    """'own' if the heading appears as a [MeSH Terms] phrase, 'other_mesh' if only other
    headings do, 'none' if no heading is searched at all."""
    found = mesh_phrases(translation)
    if norm(heading) in found:
        return "own"
    return "other_mesh" if found else "none"


def usable(term):
    """Terms that can be sent untagged without changing PubMed's syntax."""
    return (bool(term) and not any(ch in term for ch in '[]"*')
            and term.count("(") == term.count(")")
            and not re.search(r"\b(?:AND|OR|NOT)\b", term))


def build_pool(recs):
    """Ordinary entry terms of current topical descriptors, sorted.

    Excluded: the record's preferred name; a term whose key equals the key of its own
    heading (punctuation variants) or of any descriptor's preferred name; a term key held by
    more than one descriptor (ambiguous); unusable strings."""
    pref_keys = {norm(r["name"]) for r in recs.values()}
    holders = {}
    for ui, r in recs.items():
        for t in r["terms"]:
            holders.setdefault(norm(t["string"]), set()).add(ui)
    pool = []
    for ui in sorted(recs):
        r = recs[ui]
        if r.get("cls") != "1":
            continue
        seen = set()
        for t in r["terms"]:
            k = norm(t["string"])
            if t["record_preferred"] or k in pref_keys or k in seen:
                continue
            if len(holders.get(k, ())) != 1 or not usable(t["string"]):
                continue
            seen.add(k)
            row = dict(t)
            row.update({"ui": ui, "heading": r["name"]})
            pool.append(row)
    pool.sort(key=lambda x: (x["ui"], x["string"]))
    return pool


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes in n trials, as (low, high)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def fisher_greater(a, b, c, d):
    """One-sided Fisher exact p that row 1's failure share (a of a+b) exceeds row 2's
    (c of c+d): P(X >= a) for the hypergeometric draw of a+b items."""
    n1, k_tot, n_tot = a + b, a + c, a + b + c + d
    den = math.comb(n_tot, n1)
    num = sum(math.comb(k_tot, x) * math.comb(n_tot - k_tot, n1 - x)
              for x in range(a, min(k_tot, n1) + 1))
    return float(Fraction(num, den))


def word_bucket(term):
    n = len(term.split())
    return "1" if n == 1 else ("2" if n == 2 else "3+")


def year_bucket(year):
    try:
        y = int(year)
    except (TypeError, ValueError):
        return "unknown"
    return "<2000" if y < 2000 else ("2000-2019" if y < 2020 else "2020+")


def subgroups(rows):
    """Failure counts by term features (exploratory, not graded)."""
    out = {}
    feats = {
        "concept_preferred": lambda r: "Y" if r.get("concept_preferred") else "N",
        "lexical_tag": lambda r: r.get("lexical_tag") or "",
        "words": lambda r: word_bucket(r["string"]),
        "created": lambda r: year_bucket(r.get("year")),
        "has_comma": lambda r: "Y" if "," in r["string"] else "N",
    }
    for name, f in feats.items():
        tab = {}
        for r in rows:
            if r.get("result") not in ("own", "other_mesh", "none"):
                continue
            g = tab.setdefault(f(r), [0, 0])
            g[1] += 1
            if r["result"] != "own":
                g[0] += 1
        out[name] = {k: {"fail": v[0], "n": v[1]} for k, v in sorted(tab.items())}
    return out


# ---------------------------------------------------------------- I/O
def parse_desc(source):
    """{ui: {name, cls, terms: [{string, concept_preferred, record_preferred, year,
    lexical_tag}]}} from a MeSH descriptor XML stream."""
    out = {}
    root = None
    for event, elem in ET.iterparse(source, events=("start", "end")):
        if root is None and event == "start":
            root = elem
            continue
        if event != "end" or elem.tag != "DescriptorRecord":
            continue
        ui = (elem.findtext("DescriptorUI") or "").strip()
        name = (elem.findtext("DescriptorName/String") or "").strip()
        terms = []
        for c in elem.findall("ConceptList/Concept"):
            cpref = c.get("PreferredConceptYN") == "Y"
            for t in c.findall("TermList/Term"):
                s = (t.findtext("String") or "").strip()
                if not s:
                    continue
                terms.append({"string": s, "concept_preferred": cpref,
                              "record_preferred": t.get("RecordPreferredTermYN") == "Y",
                              "year": (t.findtext("DateCreated/Year") or "").strip(),
                              "lexical_tag": t.get("LexicalTag") or ""})
        if ui:
            out[ui] = {"ui": ui, "name": name, "cls": elem.get("DescriptorClass") or "",
                       "terms": terms}
        elem.clear()
        root.clear()
    return out


def http_get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))


def download(url, dest):
    info = {"url": url, "cached": os.path.exists(dest) and os.path.getsize(dest) > 0}
    if not info["cached"]:
        data = http_get(url)
        with open(dest + ".part", "wb") as fh:
            fh.write(data)
        os.replace(dest + ".part", dest)
    h = hashlib.sha256()
    with open(dest, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    info.update({"sha256": h.hexdigest(), "bytes": os.path.getsize(dest), "path": dest})
    return info


def open_xml(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    return gzip.open(path, "rb") if magic == b"\x1f\x8b" else open(path, "rb")


def esearch(term):
    """(count, querytranslation, problems) for one PubMed query."""
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json",
                                "retmax": "0", "tool": TOOL, "email": MAILTO})
    time.sleep(PAUSE)
    try:
        js = json.loads(http_get(ESEARCH_URL + "?" + q).decode("utf-8"))
    except Exception as e:  # recorded, never silently dropped
        return None, "", "request_failed: %s" % type(e).__name__
    r = js.get("esearchresult", {})
    probs = []
    for key in ("errorlist", "warninglist"):
        for k, v in (r.get(key) or {}).items():
            if v:
                probs.append("%s.%s=%s" % (key, k, v))
    try:
        count = int(r.get("count"))
    except (TypeError, ValueError):
        count = None
    return count, r.get("querytranslation", ""), "; ".join(probs)


def check_term(row):
    """Fill result, count, translation (and missed/heading_total on failure)."""
    count, qt, probs = esearch(row["string"])
    row.update({"count": count, "translation": qt, "problems": probs})
    if count is None and probs.startswith("request_failed"):
        row["result"] = "error"
        return row
    row["result"] = classify_translation(qt, row["heading"])
    if row["result"] != "own":
        total, _, p1 = esearch('"%s"[mh]' % row["heading"])
        missed, _, p2 = esearch('"%s"[mh] NOT (%s)' % (row["heading"], row["string"]))
        row.update({"heading_total": total, "missed": missed,
                    "miss_problems": "; ".join(x for x in (p1, p2) if x)})
    return row


def load_set_a(recs):
    url = SPARQL_URL + "?" + urllib.parse.urlencode(
        {"query": SET_A_QUERY, "format": "JSON", "inference": "false"})
    js = json.loads(http_get(url).decode("utf-8"))
    rows, seen = [], set()
    for b in js["results"]["bindings"]:
        od = b["od"]["value"].rsplit("/", 1)[-1]
        d = b["d"]["value"].rsplit("/", 1)[-1]
        name = b["name"]["value"]
        key = (d, norm(name))
        if key in seen:
            continue
        seen.add(key)
        r = recs.get(d)
        in_xml = bool(r) and any(norm(t["string"]) == norm(name) for t in r["terms"])
        rows.append({"set": "A", "string": name, "ui": d,
                     "heading": r["name"] if r else b["dl"]["value"],
                     "obsolete_ui": od, "last_active": b["y"]["value"],
                     "in_desc2026": in_xml, "usable": usable(name)})
    return rows, len(js["results"]["bindings"])


FIELDS = ["set", "ui", "heading", "string", "result", "count", "heading_total", "missed",
          "obsolete_ui", "last_active", "in_desc2026", "concept_preferred", "year",
          "lexical_tag", "problems", "miss_problems", "translation"]


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def tally(rows):
    graded = [r for r in rows if r.get("result") in ("own", "other_mesh", "none")]
    fail = [r for r in graded if r["result"] != "own"]
    lo, hi = wilson(len(fail), len(graded))
    return {"n": len(graded), "fail": len(fail),
            "other_mesh": sum(1 for r in fail if r["result"] == "other_mesh"),
            "none": sum(1 for r in fail if r["result"] == "none"),
            "errors": sum(1 for r in rows if r.get("result") == "error"),
            "fail_rate": (len(fail) / len(graded)) if graded else None,
            "fail_rate_ci95": [lo, hi]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="MeSH entry terms PubMed ATM does not map")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--n-sample", type=int, default=1500)
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    shared = os.path.join(a.data_dir, "annot", "desc2026.gz")
    if os.path.exists(shared) and os.path.getsize(shared) > 0 \
            and not os.path.exists(shared + ".part"):
        info = download(DESC_URL, shared)
    else:
        ddir = os.path.join(a.data_dir, "atm")
        os.makedirs(ddir, exist_ok=True)
        info = download(DESC_URL, os.path.join(ddir, "desc2026.gz"))
    with open_xml(info["path"]) as fh:
        recs = parse_desc(fh)
    print("parsed desc2026", len(recs), flush=True)

    # sanity rows first
    san = []
    for term, ui, expect in SANITY:
        row = check_term({"set": "sanity", "string": term, "ui": ui,
                          "heading": recs[ui]["name"] if ui in recs else ""})
        got = "own" if row["result"] == "own" else "fail"
        row["expected"], row["pass"] = expect, (got == expect)
        san.append(row)
    san_ok = all(r["pass"] for r in san)
    print("sanity", [(r["string"], r["result"], r["pass"]) for r in san], flush=True)

    set_a_error = ""
    try:
        set_a, n_bind = load_set_a(recs)
    except Exception as e:  # reported in summary.json; set B still runs
        set_a, n_bind, set_a_error = [], 0, "%s: %s" % (type(e).__name__, e)
    for r in set_a:
        if r["usable"] and r["in_desc2026"]:
            check_term(r)
        else:
            r["result"] = "skipped"
    print("set A", len(set_a), tally(set_a), flush=True)

    a_keys = {(r["ui"], norm(r["string"])) for r in set_a}
    pool = [p for p in build_pool(recs) if (p["ui"], norm(p["string"])) not in a_keys]
    rng = random.Random(SEED)
    sample = rng.sample(pool, min(a.n_sample, len(pool)))
    set_b = []
    for i, p in enumerate(sample):
        row = dict(p)
        row["set"] = "B"
        set_b.append(check_term(row))
        if (i + 1) % 100 == 0:
            print("set B", i + 1, tally(set_b), flush=True)

    ta, tb = tally(set_a), tally(set_b)
    p_ab = fisher_greater(ta["fail"], ta["n"] - ta["fail"], tb["fail"], tb["n"] - tb["fail"]) \
        if ta["n"] and tb["n"] else None
    b_fail = [r for r in set_b if r.get("result") in ("other_mesh", "none")]
    big_miss = sum(1 for r in b_fail if isinstance(r.get("missed"), int) and r["missed"] >= 100)

    write_csv(os.path.join(a.out_dir, "set_a.csv"), set_a)
    write_csv(os.path.join(a.out_dir, "set_b.csv"), set_b)
    write_csv(os.path.join(a.out_dir, "failures.csv"),
              [r for r in set_a + set_b if r.get("result") in ("other_mesh", "none")])
    with open(os.path.join(a.out_dir, "sanity.json"), "w", encoding="utf-8") as fh:
        json.dump({"all_pass": san_ok, "rows": san}, fh, indent=1)
    summary = {
        "version": VERSION, "started": started,
        "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "descriptors": len(recs), "pool_size": len(pool), "seed": SEED,
        "sanity_all_pass": san_ok,
        "set_a_error": set_a_error, "set_a_bindings": n_bind, "set_a_rows": len(set_a),
        "set_a_skipped": sum(1 for r in set_a if r["result"] == "skipped"),
        "set_a": ta, "set_b": tb, "fisher_a_gt_b_p": p_ab,
        "set_b_fail_missed_ge_100": big_miss,
        "set_a_fail_by_last_active": {
            y: {"fail": sum(1 for r in set_a if r["last_active"] == y
                            and r.get("result") in ("other_mesh", "none")),
                "n": sum(1 for r in set_a if r["last_active"] == y
                         and r.get("result") in ("own", "other_mesh", "none"))}
            for y in sorted({r["last_active"] for r in set_a})},
        "set_b_subgroups": subgroups(set_b),
        "desc_file": info,
    }
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "desc_file"}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
