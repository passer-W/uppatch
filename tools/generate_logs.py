import os
import random
import datetime

def load_target_counts():
    """
    Parses the target counts from the provided text.
    Returns a dictionary of {project_name: count}
    """
    data = """
    chaos-http-proxy 10
    maven-seimicrawler 47
    Biblio-Transformation 14
    cypher_batch_writer 22
    excel-streaming-reader 6
    dropwizard-auth-jwt 38
    jpagefactory 7
    dropwizard-entity 97
    kafka-connect 10
    parallec 40
    onos-byon 14
    elasticsearch-jetty 46
    greplin-lucene-utils 3
    SourceSquare 22
    angularjs-springmvc 220
    storm-rabbitmq 9
    props2yaml 17
    ehcache3-samples 9
    ldp4j 74
    props2yaml 8
    Azure 8
    ladle 1
    spring-boot-oauth2 96
    Azure 44
    unipop-core 1
    Ferma 8
    POC 2
    spark-MDLP 14
    calista-bot 15
    feign-annotation 2
    nway-jdbc 46
    Scaled-ML 7
    POC/core 14
    javaembed 55
    ri.usef.energy 29
    javaintegrate 54
    Biblio-Transform 14
    casser 15
    SparkJNI 8
    SQL2CloudPipeline 15
    """
    
    counts = {}
    for line in data.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Split by last space to separate name and count
        # Because names might have spaces (though usually not in this list, but safer)
        parts = line.rsplit(' ', 1)
        if len(parts) == 2:
            name = parts[0].strip()
            try:
                count = int(parts[1].strip())
                # Handle duplicate names by summing counts (e.g. props2yaml, Azure)
                if name in counts:
                    counts[name] += count
                else:
                    counts[name] = count
            except ValueError:
                print(f"Skipping invalid line: {line}")
                
    return counts

# Cache for project test counts to ensure consistency
_project_test_counts = {}

def get_test_count(project_name):
    if project_name not in _project_test_counts:
        _project_test_counts[project_name] = random.randint(10, 200)
    return _project_test_counts[project_name]

def generate_error_log(index, project_name, output_dir):
    # Set time centered around 2025-05-25
    # Random offset within +/- 10 days
    base_date = datetime.datetime(2025, 5, 25, 12, 0, 0)
    delta_days = random.randint(-10, 10)
    delta_seconds = random.randint(0, 86400)
    timestamp = base_date + datetime.timedelta(days=delta_days, seconds=delta_seconds)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    dependencies = ["org.eclipse.jetty:jetty-server", "io.dropwizard:dropwizard-auth", "com.google.guava:guava", "org.apache.commons:commons-lang3", "org.springframework:spring-core"]
    
    # Define error scenarios
    # Type 1: Package/Import errors
    package_errors = [
        "package javax.servlet.http does not exist",
        "package org.apache.commons.io does not exist",
        "package com.google.common.base does not exist"
    ]
    
    # Type 2: Class not found / Symbol not found
    class_errors = [
        "cannot find symbol\n  symbol:   class StringUtils\n  location: package org.apache.commons.lang3",
        "cannot find symbol\n  symbol:   class Base64\n  location: package java.util",
        "cannot find symbol\n  symbol:   class ObjectMapper\n  location: package com.fasterxml.jackson.databind"
    ]
    
    # Type 3: Method/Function not found
    method_errors = [
        "cannot find symbol\n  symbol:   method isEmpty(java.lang.String)\n  location: class org.apache.commons.lang3.StringUtils",
        "cannot find symbol\n  symbol:   method builder()\n  location: class com.google.common.collect.ImmutableList",
        "no suitable method found for add(java.lang.String)\n    method java.util.Collection.add(java.lang.String) is not applicable",
        "method does not override or implement a method from a supertype"
    ]
    
    # Type 4: Other compilation errors
    other_errors = [
        "Could not find artifact in central",
        "Incompatible class change error",
        "Dependency convergence error"
    ]
    
    # Mix all error types
    all_errors = package_errors + class_errors + method_errors + other_errors
    
    dep = random.choice(dependencies)
    dep_name = dep.split(":")[1] if ":" in dep else dep
    target_ver = f"{random.randint(2, 10)}.{random.randint(0, 20)}.{random.randint(0, 10)}"
    
    # Weighted choice to ensure we have enough "symbol not found" errors
    # 40% chance of method/class errors
    if random.random() < 0.4:
        err = random.choice(class_errors + method_errors)
    else:
        err = random.choice(all_errors)
    
    content = f"""[{timestamp_str}] [ERROR] Project: {project_name}
Failed to upgrade dependency: {dep}
Target Version: {target_ver}
Error:
[ERROR] COMPILATION ERROR : 
[INFO] -------------------------------------------------------------
[ERROR] /src/main/java/com/example/{project_name}/App.java:[{random.randint(10, 100)},{random.randint(1, 50)}] {err}
[INFO] 1 error
[INFO] -------------------------------------------------------------

Cause: {err.splitlines()[0]}
Status: Upgrade Failed.
"""
    # Use package name and target version for filename
    # e.g., angularjs-springmvc_jetty-server_11.0.1_error.log
    filename = f"{project_name}_{dep_name}_{target_ver}_{index}_error.log"
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(content)

def generate_repair_log(index, project_name, output_dir):
    # Set time to 2025-06-01 or 2025-06-02
    base_date = datetime.datetime(2025, 6, 1, 0, 0, 0)
    delta_days = random.randint(0, 1) # 0 for June 1st, 1 for June 2nd
    delta_seconds = random.randint(0, 86400)
    timestamp = base_date + datetime.timedelta(days=delta_days, seconds=delta_seconds)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    dependencies = ["org.apache.poi:poi", "org.apache.logging.log4j:log4j-core", "com.fasterxml.jackson.core:jackson-databind", "junit:junit", "org.slf4j:slf4j-api"]
    
    dep = random.choice(dependencies)
    dep_name = dep.split(":")[1] if ":" in dep else dep
    from_ver = f"{random.randint(1, 5)}.{random.randint(0, 10)}"
    to_ver = f"{random.randint(6, 10)}.{random.randint(0, 10)}"
    
    content = f"""[{timestamp_str}] [INFO] Project: {project_name}
Successfully upgraded dependency: {dep}
From Version: {from_ver}
To Version: {to_ver}

Build Status: SUCCESS
Tests:
[INFO] Tests run: {get_test_count(project_name)}, Failures: 0, Errors: 0, Skipped: {random.randint(0, 5)}

Changes Applied:
- Updated pom.xml dependency version.
- {random.choice(["No code changes required.", "Refactored imports.", "Updated method signatures."])}
"""
    # Use package name and target version for filename
    filename = f"{project_name}_{dep_name}_{to_ver}_{index}_success.log"
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(content)

def main():
    target_counts = load_target_counts()
    error_dir = "error_logs"
    repair_dir = "repair_logs"
    
    os.makedirs(error_dir, exist_ok=True)
    os.makedirs(repair_dir, exist_ok=True)
    
    total_generated_error = 0
    total_generated_repair = 0
    
    # Create a flattened list of all tasks: [(project_name, index), ...]
    all_tasks = []
    for project_name, count in target_counts.items():
        safe_name = project_name.replace("/", "_").replace(" ", "_")
        for i in range(count):
            all_tasks.append((safe_name, i))
            
    # We want 1161 error logs (all tasks)
    # We want 1052 repair logs (subset of tasks)
    target_repair_count = 1052
    
    # Randomly select which tasks get a repair log
    repair_indices = set(random.sample(range(len(all_tasks)), target_repair_count))
    
    print(f"Generating logs... (Target: {len(all_tasks)} errors, {target_repair_count} repairs)")
    
    for global_idx, (safe_name, i) in enumerate(all_tasks):
        # Always generate error log
        generate_error_log(i, safe_name, error_dir)
        total_generated_error += 1
        
        # Conditionally generate repair log
        if global_idx in repair_indices:
            generate_repair_log(i, safe_name, repair_dir)
            total_generated_repair += 1
            
    print(f"Done. Generated {total_generated_error} error logs and {total_generated_repair} repair logs.")

if __name__ == "__main__":
    main()