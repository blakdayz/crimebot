"""
This is the Commander module for the CrimeBOT API.
This module is responsible for executing arbitrary commands at the demand of the model
"""

from .docker import (
    DOCKER_COMPOSE,
    check_docker_daemon,
    start_containers,
    get_running_containers,
)
from .api import router as docker_router
