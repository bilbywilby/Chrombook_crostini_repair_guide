import unittest
from pathlib import Path

class TestProjectStructure(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue(Path("README.md").exists())

    def test_skill_md_exists(self):
        self.assertTrue(Path("SKILL.md").exists())

if __name__ == "__main__":
    unittest.main()
