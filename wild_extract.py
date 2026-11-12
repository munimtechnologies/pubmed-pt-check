#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# wild_extract.py - frame and snippet extraction for PREREG-WILD-1
# (published PubMed search strategies that quote MeSH names renamed or deleted 2016-2019).
# MV2, Munim, Inc., mv2@munimtech.com. Made with AI agents working in MV2's name.
#
# What it does (standard library only):
#   1. Runs five fixed Europe PMC searches (open-access full text, first published
#      2017-01-01 .. 2026-11-12) for "<old name>[<MeSH tag>]" and takes the union.
#   2. Downloads each article's full-text XML from Europe PMC.
#   3. Finds every "<old name>[mesh|mh|majr...]" in the text and classifies how it is quoted:
#        name_quoted   "Biological Markers"[mh]   -> finds nothing in PubMed today
#        whole_quoted  "Biological Markers[mh]"   -> PubMed still maps it to the new heading
#        unquoted      Biological Markers[mh]     -> PubMed still maps it to the new heading
#        single_quote / other                       -> read by hand
#   4. Writes frame.csv, snippets.jsonl, text/<PMCID>.txt, sample.json and summary.json.
# It does not run any PubMed search; the losses are measured by hand from the snippets.

import argparse
import csv
import json
import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NAMES = {
    "Questionnaires": "Surveys and Questionnaires",
    "Biological Markers": "Biomarkers",
    "Great Britain": "United Kingdom",
    "Cognitive Therapy": "Cognitive Behavioral Therapy",
    "Intensive Care": "Critical Care",
}
TAGS = ["Mesh", "mh", "MeSH Terms", "majr", "MeSH Major Topic"]
DATE_FROM = "2017-01-01"
DATE_TO = "2026-11-12"
SEED = 20261112
SAMPLE_MAX = 25
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
UA = "MV2-Munim-wild-census/0.1 (mailto:mv2@munimtech.com)"

QCLASS = "[\"'“”„″]"
QUOTE_CHARS = "\"'“”„″"
BLOCK_TAGS = {"p", "td", "th", "preformat", "code", "title"}


def build_query(name):
    parts = " OR ".join('"%s[%s]"' % (name, t) for t in TAGS)
    q = "(%s)" % parts
    if name == "Questionnaires":
        q += ' NOT "Surveys and Questionnaires"'
    q += " AND OPEN_ACCESS:y AND FIRST_PDATE:[%s TO %s]" % (DATE_FROM, DATE_TO)
    return q


def make_pattern(name):
    words = r"\s+".join(re.escape(w) for w in name.split())
    return re.compile(
        r"(?P<q1>%s?)\s*(?<![A-Za-z])(?P<name>%s)\s*(?P<q2>%s?)\s*\[\s*(?P<tag>(?:mesh|mh|majr)[^\]]{0,30})\]"
        % (QCLASS, words, QCLASS),
        re.I,
    )


PATTERNS = {n: make_pattern(n) for n in NAMES}


def classify(text, m):
    q1, q2 = m.group("q1"), m.group("q2")
    after = text[m.end():m.end() + 1]
    if "'" in (q1, q2):
        return "single_quote"
    if q1 and q2:
        return "name_quoted"
    if q1 and not q2 and after and after in QUOTE_CHARS:
        return "whole_quoted"
    if not q1 and not q2:
        return "unquoted"
    return "other"


def find_matches(text):
    out = []
    for name, pat in PATTERNS.items():
        for m in pat.finditer(text):
            prev = text[max(0, m.start() - 60):m.start()]
            out.append({
                "name": name,
                "new_name": NAMES[name],
                "cls": classify(text, m),
                "tag": m.group("tag").strip(),
                "matched": m.group(0).strip(),
                "prev": prev,
                "after_surveys_and": bool(re.search(r"surveys\s+and\s*$", prev, re.I)),
                "start": m.start(),
            })
    return out


def _local(tag):
    return tag.split("}")[-1] if isinstance(tag, str) else ""


def norm(s):
    return " ".join(s.split())


def leaf_blocks(xml_text):
    """Return (blocks, full_text). Blocks are p/td/th/preformat/code/title elements
    that contain no other such element, whitespace-normalised."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        plain = norm(re.sub(r"<[^>]+>", " ", xml_text))
        return [plain], plain
    blocks = []
    for el in root.iter():
        if _local(el.tag) not in BLOCK_TAGS:
            continue
        if any(_local(d.tag) in BLOCK_TAGS for d in el.iter() if d is not el):
            continue
        t = norm("".join(el.itertext()))
        if t:
            blocks.append(t)
    return blocks, norm(" ".join(root.itertext()))


def process_doc(xml_text):
    blocks, full = leaf_blocks(xml_text)
    recs = []
    for bi, b in enumerate(blocks):
        for mt in find_matches(b):
            mt["block_index"] = bi
            mt["block"] = b[:6000]
            recs.append(mt)
    if not recs:
        for mt in find_matches(full):
            s = mt["start"]
            mt["block_index"] = -1
            mt["block"] = full[max(0, s - 2000):s + 2000]
            recs.append(mt)
    return blocks, recs


def pick_sample(pmcids, k=SAMPLE_MAX, seed=SEED):
    ids = sorted(set(pmcids))
    if len(ids) <= k:
        return ids
    return sorted(random.Random(seed).sample(ids, k))


def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = e
        except Exception as e:  # network hiccup: retry
            last = e
        time.sleep(3 * (i + 1))
    raise RuntimeError("GET failed %s: %s" % (url, last))


def epmc_search(query):
    results, cursor, hit = [], "*", None
    while True:
        params = {"query": query, "resultType": "lite", "pageSize": "1000",
                  "format": "json", "cursorMark": cursor}
        body = get(EPMC + "search?" + urllib.parse.urlencode(params))
        if body is None:
            raise RuntimeError("search 404: " + query)
        data = json.loads(body)
        hit = data.get("hitCount")
        rl = data.get("resultList", {}).get("result", [])
        results.extend(rl)
        nxt = data.get("nextCursorMark")
        if not rl or not nxt or nxt == cursor:
            break
        cursor = nxt
    return hit, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out_dir, "text"), exist_ok=True)

    summary = {"date_from": DATE_FROM, "date_to": DATE_TO, "queries": {}}
    frame = {}
    for name in NAMES:
        q = build_query(name)
        hit, res = epmc_search(q)
        summary["queries"][name] = {"query": q, "hitCount": hit, "returned": len(res)}
        for r in res:
            pmcid = r.get("pmcid")
            if not pmcid:
                continue
            row = frame.setdefault(pmcid, {
                "pmcid": pmcid, "pmid": r.get("pmid", ""), "doi": r.get("doi", ""),
                "year": r.get("pubYear", ""), "journal": r.get("journalTitle", ""),
                "title": r.get("title", ""), "names": []})
            row["names"].append(name)
        time.sleep(0.5)

    missing, snippets = [], []
    docs_cls = {}
    for pmcid in sorted(frame):
        xml_text = get(EPMC + pmcid + "/fullTextXML")
        time.sleep(0.4)
        if not xml_text:
            missing.append(pmcid)
            continue
        blocks, recs = process_doc(xml_text)
        with open(os.path.join(a.out_dir, "text", pmcid + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n\n".join(blocks))
        for r in recs:
            r["pmcid"] = pmcid
            snippets.append(r)
            if not r["after_surveys_and"]:
                docs_cls.setdefault(pmcid, set()).add(r["cls"])

    with open(os.path.join(a.out_dir, "frame.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pmcid", "pmid", "doi", "year", "journal", "title", "names"])
        for pmcid in sorted(frame):
            r = frame[pmcid]
            w.writerow([pmcid, r["pmid"], r["doi"], r["year"], r["journal"], r["title"],
                        ";".join(r["names"])])
    with open(os.path.join(a.out_dir, "snippets.jsonl"), "w", encoding="utf-8") as f:
        for r in snippets:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by = {}
    for r in snippets:
        if r["after_surveys_and"]:
            continue
        by.setdefault(r["name"], {}).setdefault(r["cls"], 0)
        by[r["name"]][r["cls"]] += 1
    quoted_docs = [p for p, c in docs_cls.items() if "name_quoted" in c]
    sample = pick_sample(quoted_docs)
    with open(os.path.join(a.out_dir, "sample.json"), "w", encoding="utf-8") as f:
        json.dump({"seed": SEED, "max": SAMPLE_MAX, "name_quoted_docs": sorted(quoted_docs),
                   "sample": sample}, f, indent=1)
    summary.update({
        "union": len(frame),
        "fulltext_missing": missing,
        "docs_with_match": len(docs_cls),
        "docs_without_match": sorted(p for p in frame if p not in docs_cls and p not in missing),
        "docs_name_quoted": len(quoted_docs),
        "docs_only_mapping_forms": len([p for p, c in docs_cls.items()
                                        if c and c <= {"unquoted", "whole_quoted"}]),
        "matches_by_name_class": by,
        "sample_size": len(sample),
    })
    with open(os.path.join(a.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
