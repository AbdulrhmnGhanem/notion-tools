from setuptools import setup, find_packages

setup(
    name="notion-tools",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["tools"],
    install_requires=[
        "Click",
        "keyring",
        "notion-client",
        "typeguard",
        "todoist-api-python",
        "rich",
        "prompt-toolkit",
    ],
    entry_points={
        "console_scripts": [
            "weekly_readings = tools.weekly_readings:cli",
            "capture = tools.quick_capture:cli",
        ],
    },
)
