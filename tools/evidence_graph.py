"""Offline evidence-scope checks, not causal inference or clinical prediction.

Uses the unchanged, pinned Virtual Human graph container (see vendor provenance).
Evidence assertions are manually curated metadata. Matching cannot verify their
truth, source quality, independence, or scientific completeness.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

try:
    from .vendor.virtual_human.core import EdgeRule, Graph, Schema
except ImportError:  # Direct execution from the repository root.
    from vendor.virtual_human.core import EdgeRule, Graph, Schema


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / "anti-yo-evidence-graph.json"
KINDS = {"reported_observation", "curated_annotation", "source_method", "published_intervention", "design_inference"}
AXES = {"recognition", "injury"}
UNKNOWN = "unknown"


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _mapping(value, label, allow_null=False):
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{label}: expected nonempty object")
    if any(not _text(k) or not (_text(v) or (allow_null and v is None)) for k, v in value.items()):
        raise ValueError(f"{label}: expected nonempty text values")


def _requirement(value, label):
    if not isinstance(value, dict) or set(value) - {"relation", "subject", "object", "context", "source_ids"}:
        raise ValueError(f"{label}: invalid requirement fields")
    for field in ("relation", "subject", "object"):
        if not _text(value.get(field)) or value[field] == UNKNOWN:
            raise ValueError(f"{label}: missing or unknown {field}")
    _mapping(value.get("context"), f"{label}.context")
    if UNKNOWN in value["context"].values():
        raise ValueError(f"{label}: an unknown context cannot satisfy a requirement")
    if "source_ids" in value and (not isinstance(value["source_ids"], list)
                                 or not value["source_ids"]
                                 or any(not _text(x) for x in value["source_ids"])):
        raise ValueError(f"{label}: invalid source_ids")


class EvidenceMap:
    """A conjunction must be supported by one observation, never marginal joins.

    Requests ask whether an encoded observation exists with these attributes.
    Omitted context is NOT generalized to other contexts; every match returns
    its full retained context. Callers must specify every distinction their
    intended inference requires. This tool cannot determine those distinctions
    automatically. No context transfer or relation conversion is implicit.
    Missing evidence remains unresolved, not false.
    """

    def __init__(self, data, sources):
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            raise ValueError("expected schema_version 1")
        self.data = data
        self.observations = data.get("observations")
        if not isinstance(self.observations, list) or not self.observations:
            raise ValueError("expected observations")
        self.graph = Graph("anti-Yo public evidence and unresolved requirements")
        source_map = {s["id"]: s for s in sources}
        seen_keys = set()
        for row in self.observations:
            self._validate_observation(row, source_map)
            key = row["observation_key"]
            if key in seen_keys:
                raise ValueError(f"duplicate observation_key {key}")
            seen_keys.add(key)
            self.graph.add_node(row["id"], "observation", **{k: v for k, v in row.items() if k != "id"})
            for source in row["source_ids"]:
                if source not in self.graph.nodes:
                    self.graph.add_node(source, "source", url=source_map[source]["url"])
                self.graph.add_edge(source, row["id"], "documents", locator=row["locator"])
        for hypothesis in data.get("hypotheses", []):
            if hypothesis.get("axis") not in AXES:
                raise ValueError("hypothesis must have a recognition or injury axis")
            self.graph.add_node(hypothesis["id"], "hypothesis", axis=hypothesis["axis"],
                                interpretation=hypothesis["interpretation"])
            if not hypothesis.get("requirements"):
                raise ValueError("hypothesis needs explicit requirements")
            for index, requirement in enumerate(hypothesis["requirements"]):
                _requirement(requirement, hypothesis["id"])
                nid = f"{hypothesis['id']}:requirement:{index + 1}"
                self.graph.add_node(nid, "requirement", **requirement)
                self.graph.add_edge(nid, hypothesis["id"], "requires")
                result = self.assess(requirement)
                for polarity, edge_type in (("supporting", "supports"), ("counterevidence", "contradicts")):
                    for evidence_id in result[polarity]:
                        self.graph.add_edge(evidence_id, nid, edge_type)
        errors = self.graph.validate(Schema(
            node_types={"source": {"url"}, "observation": {"context", "kind", "locator"},
                        "hypothesis": {"axis", "interpretation"},
                        "requirement": {"relation", "subject", "object", "context"}},
            edge_rules=[EdgeRule("documents", {"source"}, {"observation"}, {"locator"}),
                        EdgeRule("requires", {"requirement"}, {"hypothesis"}),
                        EdgeRule("supports", {"observation"}, {"requirement"}),
                        EdgeRule("contradicts", {"observation"}, {"requirement"})]))
        if errors:
            raise ValueError("; ".join(errors))

    @staticmethod
    def _validate_observation(row, source_map):
        if not isinstance(row, dict):
            raise ValueError("observation must be an object")
        for field in ("id", "observation_key", "relation", "subject", "object", "locator", "summary"):
            if not _text(row.get(field)):
                raise ValueError(f"observation: missing {field}")
        if row.get("kind") not in KINDS or row.get("polarity") not in {"supports", "contradicts"}:
            raise ValueError(f"{row['id']}: invalid evidence kind/polarity")
        refs = row.get("source_ids")
        if not isinstance(refs, list) or not refs or any(x not in source_map for x in refs):
            raise ValueError(f"{row['id']}: source reference is missing or unknown")
        _mapping(row.get("context"), f"{row['id']}.context", allow_null=True)

    def assess(self, requirement, observation_ids=None):
        """Return scope support and provenance, without estimating mechanism truth."""
        _requirement(requirement, "requirement")
        ids = {row["id"] for row in self.observations}
        if observation_ids is not None and (not isinstance(observation_ids, list)
                                             or not set(observation_ids) <= ids):
            raise ValueError("unknown observation selection")
        selected = ids if observation_ids is None else set(observation_ids)
        supporting, counterevidence, mismatches = [], [], {}
        for row in self.observations:
            if row["id"] not in selected:
                continue
            failures = [field for field in ("relation", "subject", "object")
                        if row[field] != requirement[field]]
            failures += [f"context.{key}" for key, value in requirement["context"].items()
                         if row["context"].get(key) != value]
            if not set(requirement.get("source_ids", [])) <= set(row["source_ids"]):
                failures.append("source_ids")
            if failures:
                mismatches[row["id"]] = sorted(failures)
            elif row["polarity"] == "supports":
                supporting.append(row["id"])
            else:
                counterevidence.append(row["id"])
        status = ("conflicting" if supporting and counterevidence else
                  "supported_within_scope" if supporting else
                  "counterevidence" if counterevidence else "unresolved")
        matched = set(supporting + counterevidence)
        provenance = [{key: row[key] for key in
                       ("id", "source_ids", "locator", "context", "kind", "polarity", "summary")}
                      for row in self.observations if row["id"] in matched]
        return {"status": status, "supporting": sorted(supporting),
                "counterevidence": sorted(counterevidence), "matched_evidence": provenance,
                "mismatches": mismatches}

    def report(self):
        fixtures = []
        for case in self.data.get("queries", []):
            result = self.assess(case["requires"], case["evidence_ids"])
            fixtures.append({"id": case["id"], "question": case["question"],
                             "expected": case["expected"], **result})
        hypotheses = []
        for hypothesis in self.data.get("hypotheses", []):
            results = [{"requires": req, **self.assess(req)} for req in hypothesis["requirements"]]
            hypotheses.append({"id": hypothesis["id"], "axis": hypothesis["axis"],
                               "interpretation": hypothesis["interpretation"], "requirements": results})
        return {"scope": "Manually curated public metadata; no research-data acquisition or mechanism inference.",
                "observations": len(self.observations),
                "query_status_counts": dict(sorted(Counter(x["status"] for x in fixtures).items())),
                "fixtures_match_expectations": all(x["status"] == x["expected"] for x in fixtures),
                "queries": fixtures, "hypotheses": hypotheses,
                "limits": ["Support means an encoded assertion matches the request, not that biology is proven.",
                           "Omitted context is not generalized; callers must specify the distinctions their question needs.",
                           "Recognition and injury are separate, potentially coexisting axes.",
                           "Unresolved requirements are not evidence of absence; counts are not probabilities.",
                           "Sources sharing participants, assays, or data are not independent replication."]}


def load(path=REGISTRY, sources_path=ROOT / "registries" / "sources.json"):
    return EvidenceMap(json.loads(Path(path).read_text()), json.loads(Path(sources_path).read_text())["sources"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the complete evidence-gap report")
    args = parser.parse_args()
    report = load().report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['observations']} curated public evidence assertions; {len(report['queries'])} request fixtures")
        print(json.dumps(report["query_status_counts"], sort_keys=True))
        for h in report["hypotheses"]:
            states = [r["status"] for r in h["requirements"]]
            print(f"{h['axis']} / {h['id']}: " + ", ".join(states))
        print("Fixture expectations matched:", report["fixtures_match_expectations"])
        print("No mechanism probabilities, causal conclusions, or patient predictions are produced.")
    return 0 if report["fixtures_match_expectations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
