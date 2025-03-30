import subprocess

def test_setup_tables():
    result = subprocess.run(
        ["python","src/setup.py","init-db"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Tables created" in result.stdout