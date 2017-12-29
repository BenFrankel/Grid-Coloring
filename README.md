# Grid Coloring

Whenever a problem I'm working on involves a square grid, I draw some nearly straight lines on a piece of paper with a pen and then do my work on it with a pencil. The primary benefit of replicating this process digitally is the ability to easily save and share final or intermediate images.

## Controls

```
1-8:         Select color
Mouse Wheel: Scroll through colors

Connection Mode
Q: Tree
W: Blob
E: Trace (default)

Marking Type
I: Path
O: Fill
P: Flat  (default)

Resizing
Up:          Add an empty row to the top
Down:        Add an empty row to the bottom
Left:        Add an empty column to the left
Right:       Add an empty column to the right
Shift+Up:    Remove the top row
Shift+Down:  Remove the bottom row
Shift+Left:  Remove the leftmost column
Shift+Right: Remove the rightmost column

Saving
CTRL+S: Save the image
CTRL+G: Save the grid
CTRL+L: Load the last saved grid
```

## Dependencies

- Python 3.x
- hgf 0.2.1 (should be handled by pip)

## Download

Download this repository with the following [git](https://git-scm.com/) command:

`git clone https://github.com/BenFrankel/GridColoring`

## Installation

Navigate into the downloaded folder and run `pip install -r requirements.txt` to install dependencies ([pip](https://pip.pypa.io/en/stable/) is the Python package manager).

Now you can start the program with `python main.py`.

## License

This project is licensed under the [Apache 2.0](https://github.com/BenFrankel/GridColoring/blob/master/LICENSE) license, so you are free to use, distribute, and modify it.
