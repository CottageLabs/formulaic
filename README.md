# Formulaic

A form and data-structure definition and processing library developed by [Cottage Labs](https://cottagelabs.com/).

## Overview

Formulaic provides a framework for defining data structures (fields and structures), processing input data through coercion and validation pipelines, and serialising results.

## Installation

```bash
pip install .
```

For development with test dependencies:

```bash
pip install -e .[test]
```

## Usage

```python
from formulaic.core import Field, Structure
from formulaic.engine import get_data, set_data
from formulaic.fields import BasicUnicode, BasicBoolean, DateField
```

## Running Tests

```bash
pytest
```

## License

Apache 2.0

