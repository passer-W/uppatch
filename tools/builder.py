import subprocess
import re
from config import Config

class BuildManager:
    """Module responsible for running builds and analyzing logs."""

    def __init__(self, project_path):
        self.project_path = project_path

    def run_build(self):
        """Run mvn clean compile and return result."""
        print("Running Maven build...")
        try:
            cmd = f"{Config.MAVEN_CMD} clean compile"
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            print(f"Build execution failed: {e}")
            return -1, "", str(e)

    def parse_errors(self, stdout, stderr):
        """Parse build output for compilation errors."""
        full_log = stdout + "\n" + stderr
        errors = []
        # Pattern: [ERROR] /path/to/File.java:[line,col] error message
        # We need to capture the file path, line number, and error message
        pattern = re.compile(r"\[ERROR\]\s+(.*?):\[(\d+),(\d+)\]\s+(.*)")
        
        for line in full_log.splitlines():
            match = pattern.search(line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                error_msg = match.group(4)
                errors.append({
                    'file': file_path,
                    'line': line_num,
                    'msg': error_msg
                })
        return errors

if __name__ == "__main__":
    # Test stub
    path = input("Enter project path: ")
    builder = BuildManager(path)
    code, out, err = builder.run_build()
    if code != 0:
        print("Build failed. Errors:")
        errors = builder.parse_errors(out, err)
        for e in errors:
            print(e)
    else:
        print("Build successful.")
