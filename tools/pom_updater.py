import os
from lxml import etree

class PomUpdater:
    """Module responsible for parsing and updating pom.xml files."""

    def __init__(self, project_path):
        self.project_path = project_path
        self.pom_path = os.path.join(project_path, "pom.xml")

    def update_dependency(self, group_id, artifact_id, new_version):
        """Update a specific dependency version in pom.xml."""
        if not os.path.exists(self.pom_path):
            print(f"Error: pom.xml not found at {self.pom_path}")
            return False

        try:
            parser = etree.XMLParser(remove_blank_text=False)
            tree = etree.parse(self.pom_path, parser)
            root = tree.getroot()

            # Handle namespaces dynamically
            ns = root.nsmap.get(None)
            ns_prefix = f"{{{ns}}}" if ns else ""

            updated = False

            # Helper to check dependency fields
            def check_dep(dep_node):
                g = dep_node.find(f"{ns_prefix}groupId")
                a = dep_node.find(f"{ns_prefix}artifactId")
                v = dep_node.find(f"{ns_prefix}version")
                if g is not None and a is not None and v is not None:
                    if g.text == group_id and a.text == artifact_id:
                        return v
                return None

            # 1. Search in main dependencies
            for dep in root.findall(f".//{ns_prefix}dependencies/{ns_prefix}dependency"):
                v_node = check_dep(dep)
                if v_node is not None:
                    print(f"  Found in <dependencies>: {v_node.text} -> {new_version}")
                    v_node.text = new_version
                    updated = True

            # 2. Search in dependencyManagement
            for dep in root.findall(f".//{ns_prefix}dependencyManagement/{ns_prefix}dependencies/{ns_prefix}dependency"):
                v_node = check_dep(dep)
                if v_node is not None:
                    print(f"  Found in <dependencyManagement>: {v_node.text} -> {new_version}")
                    v_node.text = new_version
                    updated = True

            if updated:
                tree.write(self.pom_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
                print("  pom.xml updated successfully.")
                return True
            else:
                print(f"  Dependency {group_id}:{artifact_id} not found in pom.xml (might be inherited).")
                return False

        except Exception as e:
            print(f"Error updating POM: {e}")
            return False

if __name__ == "__main__":
    # Test stub
    path = input("Enter project path: ")
    updater = PomUpdater(path)
    g = input("Group ID: ")
    a = input("Artifact ID: ")
    v = input("New Version: ")
    updater.update_dependency(g, a, v)
