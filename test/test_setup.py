import subprocess
import os

def test_setup_tables():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() 

    result = subprocess.run(
        ["python", "src/setup.py", "init-db"],
        capture_output=True,
        text=True,
        env=env  
    )

    assert result.returncode == 0
    assert "Tables created" in result.stdout
