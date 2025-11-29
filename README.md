## K-Map Simplifier GUI (Python + Tkinter)

This project is a graphical Karnaugh Map simplifier that supports 2, 3, and 4 variables. It allows the user to toggle cell values, visualize valid groups, and automatically generate the simplified Sum-of-Products (SOP) expression. The tool is built using pure Python and Tkinter without external dependencies.

# Features

- Supports 2-variable, 3-variable, and 4-variable K-Maps
- Click-based cell editing (0 → 1 → X)
- Automatic SOP simplification
- Wrap-around grouping (8, 4, 2, and 1-cell groups)
- Highlights groups visually
- Displays minterms and step-by-step grouping

# Requirements

- Python 3.x
- Tkinter (included by default)
- No additional libraries are required.

# Installation

- Clone the repository:
  git clone <repository-url>

- Run the program:
  python kmap_gui.py

# Usage

- Click on any cell to toggle values
- Use the buttons to fill the map or clear it
- Press “Minimize (SOP)” to compute the simplified expression
- Press “Explain Steps” to see the grouping logic and minterms covered

# How it works

The tool uses Gray code ordering to map cell positions to minterms. A greedy grouping algorithm is applied to cover 1-cells using maximal group sizes. Each group is converted into its Boolean literal and combined to produce the final simplified SOP expression.

# Project Structure

kmap_gui.py  

# Limitations

- Only SOP is generated
- Uses greedy grouping (practically correct, but may not cover rare edge cases)
