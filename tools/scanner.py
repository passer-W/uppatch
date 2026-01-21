import os
import subprocess
import requests
from config import Config

class DependencyScanner:
    """Module responsible for scanning Maven dependencies and checking for CVEs."""

    def __init__(self, project_path):
        self.project_path = project_path
        self.project_type = self._detect_project_type()

    def _detect_project_type(self):
        if os.path.exists(os.path.join(self.project_path, "pom.xml")):
            return "maven"
        elif os.path.exists(os.path.join(self.project_path, "requirements.txt")):
            return "pip"
        elif os.path.exists(os.path.join(self.project_path, "package.json")):
            return "npm"
        return "unknown"

    def run_command(self, command):
        """Helper to run shell commands."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            print(f"Command execution failed: {e}")
            return -1, "", str(e)

    def get_dependencies(self):
        """Scan dependencies based on project type."""
        if self.project_type == "maven":
            return self._get_maven_dependencies()
        elif self.project_type == "pip":
            return self._get_pip_dependencies()
        elif self.project_type == "npm":
            return self._get_npm_dependencies()
        else:
            print("Unknown project type.")
            return []

    def _get_maven_dependencies(self):
        """Run mvn dependency:list and parse the output."""
        print("Scanning Maven dependencies...")
        cmd = f"{Config.MAVEN_CMD} dependency:list -DoutputFile=deps.txt -DoutputAbsoluteArtifactFilename=true"
        code, _, err = self.run_command(cmd)
        
        if code != 0:
            print(f"Error executing Maven: {err}")
            return []

        deps = []
        deps_file = os.path.join(self.project_path, "deps.txt")
        if os.path.exists(deps_file):
            with open(deps_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Format: groupId:artifactId:type:version:scope
                    parts = line.split(':')
                    if len(parts) >= 4:
                        deps.append({
                            'groupId': parts[0],
                            'artifactId': parts[1],
                            'version': parts[3],
                            'scope': parts[4] if len(parts) > 4 else 'compile',
                            'ecosystem': 'Maven'
                        })
            os.remove(deps_file)
        return deps

    def _get_pip_dependencies(self):
        """Parse requirements.txt (simple parser)."""
        print("Scanning Pip dependencies...")
        deps = []
        req_file = os.path.join(self.project_path, "requirements.txt")
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Very basic parsing: package==version
                    if '==' in line:
                        parts = line.split('==')
                        deps.append({
                            'groupId': 'pypi', # Placeholder
                            'artifactId': parts[0].strip(),
                            'version': parts[1].strip(),
                            'ecosystem': 'PyPI'
                        })
        return deps

    def _get_npm_dependencies(self):
        """Use npm list --json."""
        print("Scanning Npm dependencies...")
        import json
        cmd = f"{Config.NPM_CMD} list --json --depth=0"
        code, out, err = self.run_command(cmd)
        
        deps = []
        try:
            data = json.loads(out)
            dependencies = data.get('dependencies', {})
            for name, info in dependencies.items():
                if 'version' in info:
                    deps.append({
                        'groupId': 'npm',
                        'artifactId': name,
                        'version': info['version'],
                        'ecosystem': 'npm'
                    })
        except Exception as e:
            print(f"Error parsing npm output: {e}")
        return deps

    def check_cve(self, group_id, artifact_id, version, ecosystem="Maven"):
        """Query OSV.dev for vulnerabilities."""
        package_name = f"{group_id}:{artifact_id}" if ecosystem == "Maven" else artifact_id
        
        payload = {
            "package": {
                "name": package_name,
                "ecosystem": ecosystem
            },
            "version": version
        }
        try:
            response = requests.post(Config.OSV_QUERY_URL, json=payload)
            if response.status_code == 200:
                return response.json().get("vulns", [])
        except Exception as e:
            print(f"Error checking CVE for {group_id}:{artifact_id}: {e}")
        return []

    def find_safe_version(self, vulns):
        """Determine a safe version from vulnerability data."""
        fixed_versions = set()
        for vuln in vulns:
            for affected in vuln.get('affected', []):
                for range_info in affected.get('ranges', []):
                    for event in range_info.get('events', []):
                        if 'fixed' in event:
                            fixed_versions.add(event['fixed'])
        
        if not fixed_versions:
            return None
            
        # Return the highest fixed version lexicographically (simplified)
        return sorted(list(fixed_versions))[-1]

    def scan(self):
        """Main method to scan project and return actionable vulnerability report."""
        deps = self.get_dependencies()
        report = []
        
        print(f"Found {len(deps)} dependencies. Checking for vulnerabilities...")
        
        for dep in deps:
            vulns = self.check_cve(dep['groupId'], dep['artifactId'], dep['version'], dep.get('ecosystem', 'Maven'))
            if vulns:
                safe_ver = self.find_safe_version(vulns)
                if safe_ver:
                    print(f"[VULNERABLE] {dep['artifactId']} {dep['version']} -> Fix: {safe_ver}")
                    report.append({
                        'dependency': dep,
                        'safe_version': safe_ver,
                        'vulns': vulns
                    })
                else:
                    print(f"[VULNERABLE] {dep['artifactId']} {dep['version']} (No clear fix found)")
        
        return report

if __name__ == "__main__":
    # Test stub
    path = input("Enter project path: ")
    scanner = DependencyScanner(path)
    scanner.scan()
