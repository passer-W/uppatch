import os
import subprocess
import requests
from config import Config

class DependencyScanner:
    """Module responsible for scanning Maven dependencies and checking for CVEs."""

    def __init__(self, project_path):
        self.project_path = project_path

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
        """Run mvn dependency:list and parse the output."""
        print("Scanning dependencies...")
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
                            'scope': parts[4] if len(parts) > 4 else 'compile'
                        })
            os.remove(deps_file)
        return deps

    def check_cve(self, group_id, artifact_id, version):
        """Query OSV.dev for vulnerabilities."""
        payload = {
            "package": {
                "name": f"{group_id}:{artifact_id}",
                "ecosystem": "Maven"
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
            vulns = self.check_cve(dep['groupId'], dep['artifactId'], dep['version'])
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
