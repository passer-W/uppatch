import os
import time
from config import Config
from scanner import DependencyScanner
from pom_updater import PomUpdater
from pip_updater import PipUpdater
from npm_updater import NpmUpdater
from builder import BuildManager
from fixer import AIFixer

class AutoPatcher:
    """Main Orchestrator for the automated patching process."""

    def __init__(self, project_path):
        self.project_path = project_path
        self.scanner = DependencyScanner(project_path)
        self.project_type = self.scanner.project_type
        
        if self.project_type == "maven":
            self.updater = PomUpdater(project_path)
        elif self.project_type == "pip":
            self.updater = PipUpdater(project_path)
        elif self.project_type == "npm":
            self.updater = NpmUpdater(project_path)
        else:
            print(f"Unsupported project type at {project_path}")
            self.updater = None

        self.builder = BuildManager(project_path, self.project_type)
        self.fixer = AIFixer()

    def run(self):
        print(f"=== Starting AutoPatcher for {self.project_path} ({self.project_type}) ===")
        
        if not self.updater:
            print("No valid updater found. Exiting.")
            return

        # 1. Scan for Vulnerabilities
        report = self.scanner.scan()
        if not report:
            print("No actionable vulnerabilities found.")
            return

        # 2. Iterate through vulnerable dependencies
        for item in report:
            dep = item['dependency']
            safe_ver = item['safe_version']
            
            print(f"\n>>> Processing {dep['artifactId']}: {dep['version']} -> {safe_ver}")
            
            # 3. Update POM
            if not self.updater.update_dependency(dep['groupId'], dep['artifactId'], safe_ver):
                print("Skipping due to POM update failure.")
                continue

            # 4. Build and Fix Loop
            self.build_and_fix(dep['artifactId'])

    def build_and_fix(self, artifact_id):
        """Loop to compile and fix errors."""
        success = False
        
        for attempt in range(Config.MAX_RETRIES):
            print(f"  [Attempt {attempt+1}/{Config.MAX_RETRIES}] Compiling...")
            code, out, err = self.builder.run_build()
            
            if code == 0:
                print(f"  SUCCESS: Upgraded {artifact_id} without errors.")
                success = True
                break
            
            print("  Build Failed. Analyzing errors...")
            errors = self.builder.parse_errors(out, err)
            
            if not errors:
                print("  No parseable Java errors found (might be configuration issue).")
                break
            
            # Try to fix the first error found
            first_error = errors[0]
            print(f"  Fixing error in {os.path.basename(first_error['file'])}...")
            
            if not self.fixer.fix_error(first_error, self.project_type):
                print("  Fix failed. Aborting this upgrade.")
                break
                
            time.sleep(1) # Brief pause

        if not success:
            print(f"  FAILED: Could not stabilize upgrade for {artifact_id} after {Config.MAX_RETRIES} attempts.")
            # Future improvement: Rollback POM changes here

if __name__ == "__main__":
    project_path = input("Enter Maven project path (default: current dir): ").strip()
    if not project_path:
        project_path = os.getcwd()
    
    patcher = AutoPatcher(project_path)
    patcher.run()
