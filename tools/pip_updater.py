import os

class PipUpdater:
    """Module responsible for updating requirements.txt files."""

    def __init__(self, project_path):
        self.project_path = project_path
        self.req_path = os.path.join(project_path, "requirements.txt")

    def update_dependency(self, group_id, artifact_id, new_version):
        """Update a specific dependency version in requirements.txt."""
        if not os.path.exists(self.req_path):
            print(f"Error: requirements.txt not found at {self.req_path}")
            return False

        updated = False
        new_lines = []
        
        try:
            with open(self.req_path, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith('#') or not stripped:
                        new_lines.append(line)
                        continue
                        
                    # Check if line matches package==old_version
                    # Assuming format: package==version
                    if '==' in stripped:
                        parts = stripped.split('==')
                        pkg_name = parts[0].strip()
                        if pkg_name == artifact_id:
                            print(f"  Found in requirements.txt: {stripped} -> {pkg_name}=={new_version}")
                            new_lines.append(f"{pkg_name}=={new_version}\n")
                            updated = True
                            continue
                    
                    new_lines.append(line)

            if updated:
                with open(self.req_path, 'w') as f:
                    f.writelines(new_lines)
                print("  requirements.txt updated successfully.")
                return True
            else:
                print(f"  Dependency {artifact_id} not found in requirements.txt.")
                return False

        except Exception as e:
            print(f"Error updating requirements.txt: {e}")
            return False
