"""Run 40 narrow offline text cases with isolated persistent stores."""
import json
import tempfile
from pathlib import Path

from home_agent.service import HomeAgent

ROOT = Path(__file__).resolve().parent.parent
WORDS = {
    "ta": {"train": "ரயில்", "bill": "மின் கட்டணம்", "stock": "இருப்பு", "suggest": "என்ன சமைக்கலாம்", "cook": "சமை", "book": "முன்பதிவு", "hello": "வணக்கம்"},
    "ml": {"train": "ട്രെയിൻ", "bill": "വൈദ്യുതി ബിൽ", "stock": "സ്റ്റോക്ക്", "suggest": "ഭക്ഷണ നിർദേശങ്ങൾ", "cook": "പാചകം", "book": "ടിക്കറ്റ്", "hello": "നമസ്കാരം"},
    "kn": {"train": "ರೈಲು", "bill": "ವಿದ್ಯುತ್ ಬಿಲ್", "stock": "ದಾಸ್ತಾನು", "suggest": "ಊಟಕ್ಕೆ ಸಲಹೆ", "cook": "ಅಡುಗೆ", "book": "ಟಿಕೆಟ್", "hello": "ನಮಸ್ಕಾರ"},
    "hi": {"train": "ट्रेन", "bill": "बिजली बिल", "stock": "स्टॉक", "suggest": "खाने का सुझाव", "cook": "खाना", "book": "टिकट", "hello": "नमस्ते"},
}


def main():
    temporary_root = ROOT / "data" / "test-temp"
    temporary_root.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
        app = HomeAgent(Path(directory) / "evaluation.sqlite3")
        for language, words in WORDS.items():
            cases = [
                (words["train"] + " 12627 2026-11-01", "train_status", "succeeded"),
                (words["train"], "train_status", "needs_input"),
                (words["train"] + " 99999 2026-11-01", "train_status", "failed"),
                (words["bill"] + " DEMO-1042", "bill_preview", "awaiting_approval"),
                (words["bill"], "bill_preview", "needs_input"),
                (words["stock"], "inventory_list", "succeeded"),
                (words["suggest"], "dish_suggestions", "succeeded"),
                (words["cook"] + " tomato rice", "recipe_plan", "planned"),
                (words["book"], None, None),
                (words["hello"], None, None),
            ]
            for index, (content, expected_kind, expected_status) in enumerate(cases):
                response = app.message(content, language, f"eval-{language}-{index}", "one")
                task = response["task"] or {}
                passed = (task.get("kind"), task.get("status"), response["language"]) == (expected_kind, expected_status, language)
                results.append({"language": language, "input": content, "passed": passed,
                                "expected_kind": expected_kind, "actual_kind": task.get("kind"),
                                "expected_status": expected_status, "actual_status": task.get("status")})
    counts = {lang: {"passed": sum(r["passed"] for r in results if r["language"] == lang), "total": 10} for lang in WORDS}
    output = {"scope": "Offline phrase routing and template language only; no Muse, audio or human fluency evaluation", "counts": counts, "cases": results}
    (ROOT / "data" / "evaluation-results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Offline text-routing evaluation", "", output["scope"] + ".", "",
             "These synthetic cases cover known phrases. They do not establish general Indic-language understanding.", "",
             "| Language | Passed | Total |", "| --- | --- | --- |"]
    for language, count in counts.items():
        lines.append(f"| {language} | {count['passed']} | {count['total']} |")
    lines.extend(["", "Run: `python -m evals.run`", "", "Case-level results: `data/evaluation-results.json` (generated, ignored by Git)."])
    (ROOT / "docs" / "evaluation-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(counts))
    if not all(r["passed"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
