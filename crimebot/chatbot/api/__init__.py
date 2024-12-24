from .router import router
from .docker_info import DockerInfoAPI
from .firewall_status import FirewallStatusAPI
from .nmap_scan import NMAPScanAPI
from .create_python_project import CreatePythonProjectAPI
from ..models import DockerInfo

# crimebot/chatbot/api/__init__.py


# Create a system service table
system_services_commands = {
    "get_docker_info": DockerInfoAPI.get_docker_info,
    "get_firewall_status": FirewallStatusAPI.get_firewall_status,
    "scan_hosts": NMAPScanAPI.scan_hosts,
    "create_python_project": CreatePythonProjectAPI.create_python_project
    "detonate_commands": DockerInfoAPI.
}
