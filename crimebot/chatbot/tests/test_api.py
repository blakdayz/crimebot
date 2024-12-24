import os

import pytest


@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Hello, World!" in response.text


@pytest.mark.asyncio
async def test_get_docker_info(docker_info):
    assert "containers" in docker_info
    assert "images" in docker_info
    assert "networks" in docker_info


@pytest.mark.asyncio
async def test_get_firewall_status(firewall_status):
    assert isinstance(firewall_status, str)


@pytest.mark.asyncio
async def test_scan_hosts(nmap_results):
    assert "status" in nmap_results
    assert "scan" in nmap_results["status"]


@pytest.mark.asyncio
async def test_create_project(project_path):
    assert os.path.isdir(project_path)
