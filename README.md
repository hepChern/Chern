[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/hepChern/Chern)
# Chern

Chern is a data analysis management toolkit designed for high energy physics research. It provides a structured environment for organizing projects, tasks, algorithms, and data, enabling reproducible and collaborative scientific workflows.

## Key Features and Benefits

Chern provides several advantages for scientific data analysis:

- **Structured Organization:** Clear separation of data, algorithms, and tasks
- **Dependency Tracking:** Automatic monitoring of relationships between objects
- **Version Control:** Impressions system for tracking object states over time
- **Reproducibility:** Complete capture of workflow and parameters
- **Adaptability:** Easy modification and re-execution of analysis components
- **Collaboration:** Project sharing and management capabilities

## Features

- **Project Management:** Create, organize, and switch between multiple analysis projects.
- **Task & Algorithm Handling:** Define tasks and algorithms with configuration files and documentation.
- **Data Organization:** Manage raw and processed data with clear directory structures.
- **Interactive Shell:** Launch an IPython shell for interactive exploration and command execution.
- **Extensible:** Easily add new commands, algorithms, and data types.

## Installation

Clone the repository and install dependencies:

```sh
git clone https://github.com/hepChern/Chern.git
cd Chern
pip install .
```

## Getting Started

Initialize a new project:

```sh
chern init
```

Start the interactive shell:

```sh
chern
```

## Common Commands

| Command | Description |
|---------|-------------|
| `cd` | Navigate between objects |
| `ls` | List contents of current object |
| `mkdir` | Create new objects |
| `mv` | Rename or move objects |
| `rm` | Remove objects |
| `add input/output` | Configure task inputs/outputs |
| `set_algorithm` | Associate algorithm with task |
| `run` | Execute a task |
| `readme edit` | Edit the README for any object |

See the [User Guide](doc/source/UserGuide.md) for more details.

## Documentation

Full documentation is available at [chern.readthedocs.io](http://chern.readthedocs.io/en/latest/).

## License

Apache License, Version 2.0

## Author

Mingrui Zhao  
2013–2024  
Center of High Energy Physics, Tsinghua University  
Department of Nuclear Physics, China Institute of Atomic Energy  
Niels Bohr Institute, University of Copenhagen
