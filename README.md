# Circuit Calculator Terminal

An interactive Python application for learning and analyzing electric circuits through a command-line interface.

## Features

- Draw circuit schematics directly from terminal commands
- Visualize common circuit components (resistors, capacitors, inductors)
- Create series and parallel circuit configurations
- Step-by-step circuit analysis using:
  - Kirchhoff's Voltage Law (KVL)
  - Kirchhoff's Current Law (KCL)
  - Nodal Analysis
  - Mesh Analysis

## Usage

1. Launch the application to open the terminal interface
2. Type commands to draw and analyze circuits:
   - `R` - Add a resistor
   - `C` - Add a capacitor 
   - `L` - Add an inductor
   - `draw series` - Create a series circuit
   - `clear` - Clear the terminal
   - `help` - Show all available commands

## Analysis Method

The calculator follows standard circuit analysis techniques as presented in engineering textbooks:

1. Identify circuit elements and topology
2. Apply KVL/KCL equations
3. Solve system of equations
4. Present step-by-step solution with explanations

Built with Python using tkinter for the GUI and schemdraw for circuit visualization.
