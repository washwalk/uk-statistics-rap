import unittest
from pathlib import Path


class PublishNarrativeGuardrails(unittest.TestCase):
    def test_campaign_for_better_transport_phrase_is_not_reintroduced(self):
        project = Path(__file__).resolve().parents[1]
        banned_fragments = [
            "Campaign for Better Transport",
            "Campaign for Better Transport's Report",
            "Campaign for Better Transport’s Report",
            "Relationship to Campaign for Better Transport",
        ]

        for relative_path in ("src/publish.py", "docs/index.html"):
            text = (project / relative_path).read_text(encoding="utf-8")
            for fragment in banned_fragments:
                self.assertNotIn(fragment, text, f"{fragment!r} was reintroduced in {relative_path}")


if __name__ == "__main__":
    unittest.main()
