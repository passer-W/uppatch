import z3
from packaging.version import parse as parse_version
import sys

class SMTSolver:
    """
    An SMT-based solver to resolve compatibility between Java versions and Package versions.
    Uses Z3 to find a satisfying configuration.
    """

    def __init__(self):
        self.solver = z3.Solver()
        # Define Java version variable
        self.java_version = z3.Int('java_version')
        # Constrain Java versions to typical LTS and recent versions
        # 8, 11, 17, 21
        self.valid_java_versions = [8, 11, 17, 21]
        self.solver.add(z3.Or([self.java_version == v for v in self.valid_java_versions]))
        
        self.packages = {} # name -> z3_variable
        self.package_versions = {} # name -> list of actual version strings
        self.package_ver_map = {} # name -> {version_str: int_id}

    def _ver_to_int(self, version_str):
        """
        Maps a version string to an integer representation for Z3.
        Strategy: major * 1,000,000 + minor * 1,000 + patch
        """
        try:
            v = parse_version(version_str)
            major = v.major if v.major is not None else 0
            minor = v.minor if v.minor is not None else 0
            micro = v.micro if v.micro is not None else 0
            return major * 1000000 + minor * 1000 + micro
        except Exception:
            # Fallback for non-standard versions, hash them or assign incremental ID?
            # For SMT to work with inequalities (>=), we need monotonic mapping.
            # If parsing fails, we can't easily guarantee order.
            # For now, return -1 or raise
            print(f"Warning: Could not parse version {version_str}")
            return 0

    def register_package(self, package_name, available_versions):
        """
        Register a package and its available versions.
        The solver must pick one of the available versions.
        """
        if package_name in self.packages:
            return

        # Create Z3 variable
        pkg_var = z3.Int(f'pkg_{package_name}')
        self.packages[package_name] = pkg_var
        self.package_versions[package_name] = available_versions
        
        # Create mapping and constraints
        # We constrain the package variable to be one of the available versions' integer representations
        valid_ver_ints = []
        self.package_ver_map[package_name] = {}
        
        for ver in available_versions:
            ver_int = self._ver_to_int(ver)
            self.package_ver_map[package_name][ver] = ver_int
            valid_ver_ints.append(ver_int)
            
        if valid_ver_ints:
            self.solver.add(z3.Or([pkg_var == v for v in valid_ver_ints]))

    def add_constraint(self, package_name, min_ver=None, max_ver=None, min_java=None, max_java=None):
        """
        Add a compatibility constraint.
        E.g., "Package X versions [min_ver, max_ver) REQUIRES Java [min_java, max_java)"
        
        Logic: If Package X is selected within range, THEN Java must be within range.
        Implies( (min_ver <= Pkg < max_ver), (min_java <= Java < max_java) )
        """
        if package_name not in self.packages:
            raise ValueError(f"Package {package_name} not registered")

        pkg_var = self.packages[package_name]
        
        # Build Package Condition
        pkg_conds = []
        if min_ver:
            pkg_conds.append(pkg_var >= self._ver_to_int(min_ver))
        if max_ver:
            pkg_conds.append(pkg_var < self._ver_to_int(max_ver))
            
        if not pkg_conds:
            pkg_condition = True # Always applies if no version range specified
        else:
            pkg_condition = z3.And(pkg_conds)

        # Build Java Condition
        java_conds = []
        if min_java:
            java_conds.append(self.java_version >= min_java)
        if max_java:
            java_conds.append(self.java_version < max_java)
            
        if not java_conds:
            java_condition = True
        else:
            java_condition = z3.And(java_conds)

        # Add Implication: If Package is in this version range, it implies Java constraints
        self.solver.add(z3.Implies(pkg_condition, java_condition))

    def add_cve_constraint(self, package_name, vulnerable_ranges):
        """
        Add constraints to avoid vulnerable versions (CVEs).
        vulnerable_ranges: list of tuples (min_ver, max_ver) representing vulnerable ranges.
        The solver will ensure the selected version is NOT in any of these ranges.
        Use None for unbounded ranges.
        """
        if package_name not in self.packages:
            raise ValueError(f"Package {package_name} not registered")

        pkg_var = self.packages[package_name]
        
        cve_conditions = []
        for min_ver, max_ver in vulnerable_ranges:
            range_conds = []
            if min_ver:
                range_conds.append(pkg_var >= self._ver_to_int(min_ver))
            if max_ver:
                range_conds.append(pkg_var < self._ver_to_int(max_ver))
            
            if range_conds:
                # This range is defined as AND(conds)
                # We want Not(Range), so Not(And(conds))
                cve_conditions.append(z3.And(range_conds))
        
        if cve_conditions:
            # Avoid ALL vulnerable ranges
            # Not(Or(range1, range2, ...))
            self.solver.add(z3.Not(z3.Or(cve_conditions)))

    def solve(self):
        """
        Solve for a valid configuration.
        """
        print("Solving constraints...")
        result = self.solver.check()
        if result == z3.sat:
            model = self.solver.model()
            solution = {
                "java_version": model[self.java_version].as_long()
            }
            
            for name, var in self.packages.items():
                val_int = model[var].as_long()
                # Reverse map int back to string (first match)
                found_ver = None
                for ver_str, ver_int in self.package_ver_map[name].items():
                    if ver_int == val_int:
                        found_ver = ver_str
                        break
                solution[name] = found_ver
                
            return solution
        else:
            print("Unsatisfiable constraints!")
            return None

def main():
    # Example usage
    solver = SMTSolver()
    
    # 1. Register a package with available versions
    # Suppose we have 'lombok' versions available in a repo
    solver.register_package("lombok", ["1.16.0", "1.18.20", "1.18.30"])
    
    # 2. Add constraints (Knowledge base)
    # Lombok 1.18.30 requires Java 11+
    solver.add_constraint(
        "lombok", 
        min_ver="1.18.30", 
        min_java=11
    )
    
    # Lombok 1.16.0 works on Java 8, but not Java 17+ (hypothetical)
    solver.add_constraint(
        "lombok",
        max_ver="1.18.0", # versions < 1.18.0
        max_java=17
    )

    # 4. Add CVE Constraints
    # Suppose Lombok 1.18.20 has a CVE. Range [1.18.10, 1.18.25)
    solver.add_cve_constraint(
        "lombok",
        vulnerable_ranges=[("1.18.10", "1.18.25")]
    )

    # 3. Solve
    solution = solver.solve()
    if solution:
        print("Found valid configuration:")
        print(f"  Java Version: {solution['java_version']}")
        for pkg, ver in solution.items():
            if pkg != "java_version":
                print(f"  {pkg}: {ver}")
    else:
        print("No valid configuration found.")

if __name__ == "__main__":
    main()
