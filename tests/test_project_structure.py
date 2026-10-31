import unittest
from pathlib import Path

class TestProjectStructure(unittest.TestCase):
    def test_readme_exists(self):
        """Verify that README.md exists in the repository root."""
        self.assertTrue(Path('README.md').exists(), "README.md is missing from root directory")

    def test_scripts_exist(self):
        """Verify that required automation scripts exist."""
        required_scripts = ['backup_runner.sh']
        for script in required_scripts:
            self.assertTrue(Path(f'scripts/{script}').exists(),
                          f'Missing script: scripts/{script}')

    def test_procedures_exist(self):
        """Verify that diagnostic procedures exist."""
        required_procedures = [
            '01_crosh_hypervisor_health_check.py',
            '02_lxd_container_health_check.py',
            '03_restart_unresponsive_container.py',
            '04_container_safety_snapshot.py',
            '05_list_container_snapshots.py'
        ]
        for proc in required_procedures:
            self.assertTrue(Path(f'automation/procedures/{proc}').exists(),
                          f'Missing procedure: automation/procedures/{proc}')

if __name__ == '__main__':
    unittest.main()
