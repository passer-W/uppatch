import os
import json

class NpmUpdater:
    """Module responsible for updating package.json files."""

    def __init__(self, project_path):
        self.project_path = project_path
        self.package_json_path = os.path.join(project_path, "package.json")

    def update_dependency(self, group_id, artifact_id, new_version):
        """Update a specific dependency version in package.json."""
        if not os.path.exists(self.package_json_path):
            print(f"Error: package.json not found at {self.package_json_path}")
            return False

        try:
            with open(self.package_json_path, 'r') as f:
                data = json.load(f)

            updated = False
            
            # Check dependencies
            if 'dependencies' in data and artifact_id in data['dependencies']:
                print(f"  Found in dependencies: {artifact_id}: {data['dependencies'][artifact_id]} -> {new_version}")
                data['dependencies'][artifact_id] = new_version
                updated = True

            # Check devDependencies
            if 'devDependencies' in data and artifact_id in data['devDependencies']:
                print(f"  Found in devDependencies: {artifact_id}: {data['devDependencies'][artifact_id]} -> {new_version}")
                data['devDependencies'][artifact_id] = new_version
                updated = True

            if updated:
                with open(self.package_json_path, 'w') as f:
                    json.dump(data, f, indent=2)
                print("  package.json updated successfully.")
                return True
            else:
                print(f"  Dependency {artifact_id} not found in package.json.")
                return False

        except Exception as e:
            print(f"Error updating package.json: {e}")
            return False
