import os
from pathlib import Path
from typing import List
import typer
from rich import print
from rich.progress import track

# Add nbformat as an optional import since it may not be installed yet
try:
    import nbformat
except ImportError:
    print(
        "[yellow]Warning: nbformat not installed. Please install with 'pip install nbformat'[/yellow]"
    )
    exit(1)


def get_week_and_name(notebook_path: Path) -> tuple[str, str]:
    """
    Extract week number and notebook name from path.

    Args:
        notebook_path: Path object for the notebook

    Returns:
        Tuple of (week_number, notebook_name)
    """
    parts = notebook_path.parts
    week = "unknown"
    for part in parts:
        if part.startswith("week"):
            week = part.replace("week", "")
            break

    name = notebook_path.stem
    return week, name


def convert_notebook_to_md(notebook_path: str, output_path: str) -> None:
    """
    Convert a Jupyter notebook to markdown format preserving code, outputs and markdown cells.

    Args:
        notebook_path: Path to the input notebook file
        output_path: Path where markdown file should be saved
    """
    # Create md directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Read the notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    md_content = []

    # Convert each cell
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            md_content.append(cell.source + "\n")

        elif cell.cell_type == "code":
            # Add code block
            md_content.append(f"```python\n{cell.source}\n```\n")
            # Add outputs if present
            if cell.outputs:
                md_content.append("<output>\n")
                for output in cell.outputs:
                    if "text" in output:
                        md_content.append("```\n" + output.text + "\n```\n")
                    elif "data" in output:
                        if "text/plain" in output.data:
                            md_content.append(
                                "```\n" + str(output.data["text/plain"]) + "\n```\n"
                            )
                md_content.append("</output>\n")

    # Write markdown file
    with open(output_path, "w") as f:
        f.write("\n".join(md_content))


def find_notebooks(root_dir: str) -> List[Path]:
    """
    Find all Jupyter notebooks in a directory and its subdirectories.

    Args:
        root_dir: Root directory to search for notebooks

    Returns:
        List of paths to notebook files
    """
    notebooks = []
    for path in Path(root_dir).rglob("*.ipynb"):
        if not ".ipynb_checkpoints" in str(path):
            notebooks.append(path)
    return notebooks


app = typer.Typer(help="Convert Jupyter notebooks to markdown files")


@app.command()
def convert(
    directory: str = typer.Argument(".", help="Root directory to search for notebooks"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show which files would be converted without actually converting",
    ),
) -> None:
    """
    Convert all Jupyter notebooks in a directory to markdown format.
    Preserves code cells, outputs, and markdown content. Saves all files in md/ folder.
    """
    root_dir = os.path.abspath(directory)
    notebooks = find_notebooks(root_dir)

    if not notebooks:
        print("[yellow]No notebooks found in the specified directory[/yellow]")
        raise typer.Exit()

    print(f"[green]Found {len(notebooks)} notebooks to convert[/green]")

    if dry_run:
        for nb_path in notebooks:
            week, name = get_week_and_name(nb_path)
            md_path = Path("md") / f"week{week}-{name}.md"
            print(f"Would convert {nb_path} to {md_path}")
        return

    # Convert each notebook with progress bar
    for nb_path in track(notebooks, description="Converting notebooks..."):
        week, name = get_week_and_name(nb_path)
        md_path = Path("md") / f"week{week}-{name}.md"
        print(f"Converting {nb_path} to {md_path}")
        convert_notebook_to_md(str(nb_path), str(md_path))

    print("[green]Conversion complete![/green]")


if __name__ == "__main__":
    app()
