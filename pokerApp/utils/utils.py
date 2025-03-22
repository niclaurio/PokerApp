import os


def get_env_variable(env_name: str):
    variable = os.environ.get(env_name)
    if not variable:
        raise EnvironmentError(f"{env_name} not found")
