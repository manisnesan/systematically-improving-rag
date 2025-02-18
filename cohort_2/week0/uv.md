# Virtual Environments

When working through the different notebooks in this course, we highly recommend using virtual environments to manage dependencies. This is because of the following reasons

1. **Isolation**: Virtual environments allow you to isolate depencencies easily. This is useful when you'd like to share your code with others.
2. **Easy Cleanup** : If you'd like to delete the environment, you can simply delete the directory. This is not the case when you've messed up your system Python installation.

By using virtual environments, we can ensure that the dependencies are the same across different machines and help prevent a host of other issues.

## Why `uv`

`uv` is a new package manager which is faster and more efficient than traditional tools like `pip`. It is also tightly integrated with virtual environments, making it easier to create and manage them.

We recommend checking out their [docs here](https://docs.astral.sh/uv/) for the latest information. In this portion, we'll show a few common commands that you'll need to get started.

With its powerful features, `uv` provides several key benefits:

- **Lightning Fast Performance**: `uv` is 10-100x faster than pip, making dependency installation and management significantly more efficient
- **All-in-One Solution**: Replaces multiple tools like pip, poetry, virtualenv and more with a single unified interface
- **Space Efficient**: Uses a global cache to deduplicate dependencies across projects, saving disk space while maintaining isolation

## Installation

For MacOS and Linux, you can install `uv` using the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows, you can use the following command:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Once you've done so, you'll be able to use the `uv` command in your terminal.

## Creating a virtual environment

To create a virtual environment, you can use the following command:

```bash
uv venv
```

This will in turn create a new virtual environment in the `.venv` directory. We can also specify a specific python version to use for the environment.

```bash
uv venv --python 3.10
```

If you'd like to also name your virtual environment something other than `.venv`, you can do so by specifying the name as follows:

```bash
uv venv my-env
```

This will create a virtual environment called `my-env` in the current directory.

## Activating a virtual environment

To activate a virtual environment, you can use the following command:

```bash
source .venv/bin/activate
```

If you're using a terminal like `fish`, the command is slightly different.

```bash
source .venv/bin/activate.fish
```

## Installing Dependencies

You can then install dependencies using the following command

```bash
uv sync
```

This will install all of the dependencies specified in the `pyproject.toml` file. If you have a `requirements.txt` file, you can also use it to install dependencies.

```bash
uv pip install -r requirements.txt
```

## Deactivating a virtual environment

To deactivate a virtual environment, you can use the following command:

```bash
deactivate
```

This will deactivate the virtual environment and return you to your regular shell. This is useful when you'd like to switch between different virtual environments.

## Best Practices

When working with virtual environments, we recommend the following best practices:

1. Always add your virtual environment to your gitignore file
2. Try to use a `pyproject.toml` file where possible to ensure that you have a consistent way of installing dependencies. This will result in `uv.lock` file that you should always commit to your repository.
