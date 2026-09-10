"""Tests for tmux's open-path helper."""

import runpy
from pathlib import Path
import unittest


OPEN_PATH = runpy.run_path(Path(__file__).resolve().parents[1] / "open-path")
split_location = OPEN_PATH["split_location"]


class SplitLocationTests(unittest.TestCase):
    def test_github_style_line_fragment(self):
        path = (
            "modules/biz/libedit/src/main/java/com/vega/image/edit/panel/"
            "AiChatEditInputPanel.kt"
        )
        self.assertEqual(
            split_location(f"{path}#L921"),
            (path, 921, None, None),
        )

    def test_existing_line_formats(self):
        self.assertEqual(split_location("foo.kt:12:3"), ("foo.kt", 12, 3, None))
        self.assertEqual(split_location("foo.kt(12,3)"), ("foo.kt", 12, 3, None))


if __name__ == "__main__":
    unittest.main()
