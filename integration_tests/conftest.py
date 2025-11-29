import pytest
import docker
import subprocess


@pytest.fixture(scope="session")
def docker_host():
    """Return the docker host"""
    print("getting docker host address")
    try:
        # Run `ip route` inside the container to find the default gateway
        result = subprocess.check_output(["ip", "route"], text=True)
        for line in result.splitlines():
            if line.startswith("default via"):
                return line.split()[2]  # Gateway IP
    except Exception as e:
        print(f"Error: {e}")
    return None


@pytest.fixture(scope="session")
def docker_client():
    """Return a Docker client"""
    print("getting docker client")
    return docker.from_env()


@pytest.fixture
def ardusub_container(
    docker_client,
    docker_host,
):
    """Create an ArduSub container"""

    bash_command = f"/ardupilot/Tools/autotest/sim_vehicle.py -v ArduSub -L RATBeach --out=udp:{docker_host}:14550 -f vectored_6dof --no-rebuild --add-param-file=/ardupilot/Tools/autotest/eiva_params/external-positioning.parm"

    print("starting ArduSub container")
    container = docker_client.containers.run(
        "ardupilot-dev:latest",
        command=bash_command,
        detach=True,
        privileged=True,
        pid_mode="host",
        network_mode="host",
        volumes={
            "/mnt/c/Users/mijd/source/repos/ardupilot": {'bind': '/ardupilot', 'mode': 'rw'},
        },
        extra_hosts={
            "host.docker.internal": docker_host,
        },
        tty=True,
    )

    print("ArduSub container started")

    yield container

    container.remove(force=True)
