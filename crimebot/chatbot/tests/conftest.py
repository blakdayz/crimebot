import asyncio
import os
import shutil
import subprocess
from typing import AsyncGenerator

import pytest
import docker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ..api.docker_info import DockerInfoAPI
from ..api.create_python_project import (
    CreatePythonProjectAPI,
    ProjectConfig,
    ProjectService,
)
from ..api.firewall_status import FirewallStatusAPI
from ..api.nmap_scan import NMAPScanAPI

from crimebot.chatbot.models import ProjectConfig
from crimebot.chatbot.services import ProjectService, NMAPService, get_docker_info
from ..main import app


@pytest.fixture(scope="session")
def event_loop():
    """Overrides the default event loop used by pytest-asyncio."""
    return asyncio.get_event_loop_policy().new_event_loop()


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    """Creates a test client for making API requests."""
    yield AsyncClient(app=app, base_url="http://test")


@pytest.fixture(scope="session")
def docker_client():
    """Returns the Docker client instance."""
    return docker.from_env()


@pytest.fixture(scope="session")
async def nmap_service():
    """Returns the NMAP service instance with a temporary NMap executable."""
    # Create a temporary NMap executable for testing
    temp_nmap_path = "/tmp/nmap_test"
    subprocess.run(["cp", "/usr/local/bin/nmap", temp_nmap_path], check=True)
    yield NMAPService(nmap_path=temp_nmap_path)
    os.remove(temp_nmap_path)


@pytest.fixture(scope="session")
async def project_service():
    """Returns the Project service instance with a temporary template cache directory."""
    # Create a temporary template cache directory for testing
    temp_cache_dir = "/tmp/template_cache_test"
    os.makedirs(temp_cache_dir, exist_ok=True)
    yield ProjectService(TEMPLATE_CACHE_DIR=temp_cache_dir)
    shutil.rmtree(temp_cache_dir)


@pytest.fixture(scope="session")
async def docker_info():
    """Returns the Docker info as a dictionary."""
    return await get_docker_info()


@pytest.fixture(scope="session")
async def firewall_status():
    """Returns the current firewall status."""
    return await FirewallStatusAPI.get_firewall_status()


@pytest.fixture(scope="session")
async def nmap_results():
    """Performs an NMAP scan on a test target and returns the results."""
    # Replace 'test_target' with an actual target for testing
    service = NMAPService()
    results = await service.scan_hosts("test_target")
    assert "scan_results" in results, "NMAP scan failed"
    return results["scan_results"]


@pytest.fixture(scope="session")
async def project_path():
    """Creates a test project using a template and returns the project path."""
    # Replace 'test_name' and 'test_template_url' with actual values for testing
    project_config = ProjectConfig(
        name="test_name",
        template="https://github.com/test-org/templates/test-template.git",
    )
    service = ProjectService
    results = await service.create_project(project_config)
    assert "project_path" in results, "Project creation failed"
    yield results["project_path"]
    # Clean up the created test project
    shutil.rmtree(results["project_path"])
