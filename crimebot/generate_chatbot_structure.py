import os

root_dir = "chatbot"

directories = ["api", "models", "services", "utils", "config"]

files = {
    "main.py": "",
    "Dockerfile": "",
    "docker-compose.yml": "",
    "requirements.txt": "",
}

for dir in directories:
    full_dir_path = os.path.join(root_dir, dir)
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path)

    if (
        dir == "api"
        or dir == "models"
        or dir == "services"
        or dir == "utils"
        or dir == "config"
    ):
        init_file_path = os.path.join(full_dir_path, "__init__.py")
        if not os.path.exists(init_file_path):
            with open(init_file_path, "w") as f:
                pass  # Create empty __init__.py files

    if dir in ["api", "models", "services", "utils", "config"]:
        file_list = {
            "api": [
                "router.py",
                "docker_info.py",
                "firewall_status.py",
                "nmap_scan.py",
                "create_python_project.py",
            ],
            "models": ["docker_info.py", "nmap_result.py", "project_config.py"],
            "services": [
                "docker_service.py",
                "firewall_service.py",
                "nmap_service.py",
                "project_service.py",
            ],
            "utils": ["loggers.py", "prometheus_exporter.py"],
            "config": ["config.py", "logging_config.ini"],
        }[dir]

        for file in file_list:
            full_file_path = os.path.join(full_dir_path, file)
            if not os.path.exists(full_file_path):
                with open(full_file_path, "w") as f:
                    pass  # Create empty files

for file, content in files.items():
    full_file_path = os.path.join(root_dir, file)
    if not os.path.exists(full_file_path):
        with open(full_file_path, "w") as f:
            f.write(
                content
            )  # Create empty files with specified content for main.py, Dockerfile, etc.
