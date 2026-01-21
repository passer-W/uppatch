import subprocess
import re
from config import Config

class BuildManager:
    """Module responsible for running builds and analyzing logs."""

    def __init__(self, project_path, project_type="maven"):
        self.project_path = project_path
        self.project_type = project_type

    def run_build(self):
        """Run build command based on project type."""
        if self.project_type == "maven":
            return self._run_maven_build()
        elif self.project_type == "pip":
            return self._run_pip_build()
        elif self.project_type == "npm":
            return self._run_npm_build()
        else:
            return -1, "", "Unknown project type"

    def _run_maven_build(self):
        """Run mvn clean compile."""
        print("Running Maven build...")
        cmd = f"{Config.MAVEN_CMD} clean compile"
        return self._execute_cmd(cmd)

    def _run_pip_build(self):
        """Run pip install to verify dependencies."""
        print("Verifying Pip dependencies...")
        # dry-run install or just install to venv?
        # For simplicity, try installing to a temp dir or just check if it resolves
        cmd = f"{Config.PIP_CMD} install -r requirements.txt --dry-run" # --dry-run requires recent pip, fallback to install?
        # Let's just run install. It might take time but it verifies.
        # Ideally we use a venv, but for this tool assume we just want to see if it Errors out.
        cmd = f"{Config.PIP_CMD} install -r requirements.txt" 
        return self._execute_cmd(cmd)

    def _run_npm_build(self):
        """Run npm install and build."""
        print("Running Npm build...")
        cmd = f"{Config.NPM_CMD} install"
        code, out, err = self._execute_cmd(cmd)
        if code != 0:
            return code, out, err
        
        # Try running build script if exists
        # Simplified: just return install result for now, or check package.json for build script
        # Assuming install is enough verification for dependency updates
        return code, out, err

    def _execute_cmd(self, cmd):
        try:
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
        """Parse build output for errors based on project type."""
        if self.project_type == "maven":
            return self._parse_maven_errors(stdout, stderr)
        elif self.project_type == "pip":
            return self._parse_pip_errors(stdout, stderr)
        elif self.project_type == "npm":
            return self._parse_npm_errors(stdout, stderr)
        return []

    def _parse_maven_errors(self, stdout, stderr):
        full_log = stdout + "\n" + stderr
        errors = []
        # Pattern: [ERROR] /path/to/File.java:[line,col] error message
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

    def _parse_pip_errors(self, stdout, stderr):
        # Basic pip error parsing
        full_log = stdout + "\n" + stderr
        errors = []
        for line in full_log.splitlines():
            if "ERROR:" in line or "error:" in line:
                 errors.append({'msg': line.strip(), 'file': 'requirements.txt', 'line': 0})
        return errors

    def _parse_npm_errors(self, stdout, stderr):
        # Basic npm error parsing
        full_log = stdout + "\n" + stderr
        errors = []
        for line in full_log.splitlines():
            if "ERR!" in line:
                 errors.append({'msg': line.strip(), 'file': 'package.json', 'line': 0})
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
