import tkinter as tk
from tkinter import ttk
import schemdraw
from schemdraw import elements as elm
from io import BytesIO
from PIL import Image, ImageTk
import sys
import os

class CircuitCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Calculator")
        
        # Configure window style for dark theme
        self.root.configure(bg='black')
        self.root.option_add('*foreground', 'white')
        self.root.option_add('*background', 'black')
        
        # Set window border and title bar to dark (Windows specific)
        try:
            self.root.tk.call('source', 'azure.tcl')
            self.root.tk.call('set_theme', 'dark')
        except:
            # If custom theme fails, try to make it as dark as possible
            self.root.attributes('-alpha', 0.95)  # Slight transparency
            if sys.platform.startswith('win'):
                self.root.attributes('-transparentcolor', 'white')
        
        self.style = ttk.Style()
        self.style.configure('Sharp.TFrame', background='black', borderwidth=0)
        self.style.configure('Sharp.TPanedwindow', background='black', borderwidth=0)
        self.style.configure('TFrame', background='black')
        self.style.configure('TPanedwindow', background='black')
        
        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main frame without padding
        self.main_frame = ttk.Frame(root, style='Sharp.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create PanedWindow without rounded corners
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL, style='Sharp.TPanedwindow')
        self.paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        
        # Schematic frame
        self.schematic_frame = ttk.Frame(self.paned, style='Sharp.TFrame')
        self.canvas = tk.Canvas(self.schematic_frame, width=400, height=200, 
                              bg='black', highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Terminal frame
        self.terminal_frame = ttk.Frame(self.paned, style='Sharp.TFrame')
        self.terminal = tk.Text(self.terminal_frame, height=12, width=50, 
                              bg='black', fg='white',
                              highlightthickness=0, bd=0,
                              insertbackground='white')  # Make cursor white
        self.terminal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add frames to PanedWindow
        self.paned.add(self.schematic_frame)
        self.paned.add(self.terminal_frame)
        
        # Configure terminal font
        self.terminal.configure(font=('Consolas', 10), wrap=tk.WORD)
        self.terminal.config(width=80)  # Increase terminal width
        
        # Initialize terminal with prompt
        self.terminal.insert(tk.END, "Circuit Calculator Terminal\nType 'help' for available commands\n>> ")
        self.command_start = self.terminal.index("end-1c")
        
        # Bind keys
        self.terminal.bind('<Return>', self.process_input)
        self.terminal.bind('<Key>', self.handle_keypress)
        
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.terminal_frame.grid_columnconfigure(0, weight=1)
        self.terminal_frame.grid_rowconfigure(0, weight=1)
        self.schematic_frame.grid_columnconfigure(0, weight=1)
        self.schematic_frame.grid_rowconfigure(0, weight=1)

        # Initialize component tracking
        self.components = []
        self.nodes = {}
        self.meshes = []
        
        # Configure drawing style
        schemdraw.theme('default')
        d = schemdraw.Drawing()
        d.config(unit=2.5, color='yellow')
        
        # Initialize spacing
        self.spacing = 100  # Horizontal spacing between components
        self.start_x = 100  # Starting x position
        self.current_x = self.start_x
        self.center_y = 100

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

    def handle_keypress(self, event):
        if self.terminal.index(tk.INSERT) < self.command_start:
            self.terminal.mark_set(tk.INSERT, tk.END)
            return "break"

    def draw_component(self, component_type, value=None):
        d = schemdraw.Drawing()
        
        # Add component to tracking list with value
        self.components.append((component_type, self.current_x, value))
        
        # Set up drawing style
        d.config(unit=2.5)  # Increase spacing
        
        # Draw all components with connecting lines and values
        prev_x = self.start_x
        for i, (comp_type, x_pos, val) in enumerate(self.components):
            label = f'{comp_type}{i+1}\n{val}' if val else f'{comp_type}{i+1}'
            
            if comp_type == 'R':
                d += elm.Resistor().at((x_pos, self.center_y)).label(label)
            elif comp_type == 'C':
                d += elm.Capacitor().at((x_pos, self.center_y)).label(label)
            elif comp_type == 'L':
                d += elm.Inductor().at((x_pos, self.center_y)).label(label)
            elif comp_type == 'CS':
                d += elm.SourceI().at((x_pos, self.center_y)).label(label)
            
            # Add node dots and numbers
            d += elm.Dot().at((x_pos - 25, self.center_y))
            d += (elm.Dot().at((x_pos + 25, self.center_y))
                 .label(f'{i+1}', 'top'))
            
            prev_x = x_pos
        
        # Update position for next component
        self.current_x += self.spacing
        
        # Convert to image and scale for display
        img_data = BytesIO()
        d.save(img_data)
        img_data.seek(0)
        img = Image.open(img_data)
        
        # Calculate scaling to fit all components
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = img.size
        
        scale = min(canvas_width/img_width, canvas_height/img_height) * 0.8
        new_size = (int(img_width * scale), int(img_height * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Clear and update canvas
        self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)
        return True

    def draw_circuit(self, circuit_type='series', components=None):
        if not self.components:
            self.add_to_terminal("No components to arrange. Add components first.")
            return
            
        d = schemdraw.Drawing()
        d.config(unit=2.5)  # Increase spacing
        
        if circuit_type == 'series':
            # Start with ground symbol
            start = (100, 100)
            d += elm.Ground().at(start)
            d += elm.Dot()
            
            # Draw components in series with node numbers
            current_pos = start
            for i, (comp_type, _, val) in enumerate(self.components):
                label = f'{comp_type}{i+1}\n{val}' if val else f'{comp_type}{i+1}'
                
                if comp_type == 'R':
                    d += elm.Resistor().right().label(label)
                elif comp_type == 'C':
                    d += elm.Capacitor().right().label(label)
                elif comp_type == 'L':
                    d += elm.Inductor().right().label(label)
                elif comp_type == 'CS':
                    d += elm.SourceI().right().label(label)
                
                # Add node number
                d += elm.Dot()
                d += (elm.Dot().at(d.here)
                     .label(f'{i+1}', 'top'))

        elif circuit_type == 'parallel':
            # Starting point
            start = (100, 100)
            d += elm.Dot().at(start)
            
            # Calculate spacing for parallel components
            num_components = len(self.components)
            if num_components > 0:
                spacing = 50
                total_height = (num_components - 1) * spacing
                start_y = start[1] + total_height/2
                
                # Draw vertical line at start
                d += elm.Line().up().length(total_height/2)
                d += elm.Line().down().length(total_height)
                
                # Draw each component in parallel
                for i, (comp_type, _, val) in enumerate(self.components):
                    y_pos = start_y - i * spacing
                    label = f'{comp_type}{i+1}\n{val}' if val else f'{comp_type}{i+1}'
                    
                    if comp_type == 'R':
                        d += (elm.Resistor().right().at((start[0], y_pos)).label(label))
                    elif comp_type == 'C':
                        d += (elm.Capacitor().right().at((start[0], y_pos)).label(label))
                    elif comp_type == 'L':
                        d += (elm.Inductor().right().at((start[0], y_pos)).label(label))
                    elif comp_type == 'CS':
                        d += (elm.SourceI().right().at((start[0], y_pos)).label(label))
                    
                    # Connect end points
                    d += elm.Line().right().at((start[0] + 100, y_pos))
                
                # Draw vertical line at end
                d += elm.Line().up().at((start[0] + 100, start[1] - total_height/2))
                d += elm.Dot()

        # Convert to image and display with scaling
        img_data = BytesIO()
        d.save(img_data)
        img_data.seek(0)
        img = Image.open(img_data)
        
        # Calculate scaling to fit
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = img.size
        
        scale = min(canvas_width/img_width, canvas_height/img_height) * 0.8
        new_size = (int(img_width * scale), int(img_height * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)

    def add_to_terminal(self, text):
        self.terminal.insert(tk.END, f"{text}\n>> ")
        self.command_start = self.terminal.index("end-1c")
        self.terminal.see(tk.END)

    def draw_example_circuit(self):
        d = schemdraw.Drawing()
        
        # Configure drawing style
        d.config(unit=2.5)
        d.style(color='yellow')
        
        # Define positions
        start = (100, 100)
        
        # Draw circuit
        d += (cs1 := elm.SourceI().label('CS1\n5A').at(start).up())
        d += (r2 := elm.Resistor2().right().label('R2\n4Ω'))
        d += (cs2 := elm.SourceI().down().label('CS2\n10A'))
        d += elm.Line().left()
        d += (r1 := elm.Resistor2().up().label('R1\n2Ω'))
        d += (r3 := elm.Resistor2().at((r2.start[0] + 50, r2.start[1])).down().label('R3\n6Ω'))
        
        # Add node numbers and dots
        d += elm.Dot().at(cs1.start).label('1', 'left')
        d += elm.Dot().at(r2.end).label('2', 'top')
        
        # Add ground symbol
        d += elm.Ground().at(cs2.end)
        
        # Add node voltage labels
        d += (elm.Dot().at((r1.start[0] - 10, r1.start[1]))
             .label('V1', 'left'))
        d += (elm.Dot().at((r2.end[0], r2.end[1] + 10))
             .label('V2', 'top'))
        
        # Add mesh analysis
        analysis = """Node 1:
5A = IR1 + IR2

V1 - V2 = IR1 · 2Ω
V1 - V2 = IR2 · 4Ω

IR1 = (V1 - V2)/2
IR2 = (V1 - V2)/4

5 = (V1 - V2)/2 + (V1 - V2)/4

5 = 3(V1 - V2)/4

V1 - V2 = 20/3"""
        
        # Add analysis text
        d.push()
        d += (elm.Text().at((r2.end[0] + 100, r2.end[1]))
             .color('yellow')
             .text(analysis))
        
        # Convert to image and display
        img_data = BytesIO()
        d.save(img_data)
        img_data.seek(0)
        img = Image.open(img_data)
        
        # Scale image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = img.size
        
        scale = min(canvas_width/img_width, canvas_height/img_height) * 0.8
        new_size = (int(img_width * scale), int(img_height * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)

    def process_input(self, event=None):
        command_index = self.terminal.index(self.command_start)
        command = self.terminal.get(command_index, "end-1c").strip().lower()
        
        if command == 'example':
            self.draw_example_circuit()
            self.add_to_terminal("Drawing example circuit with analysis")
        elif command == 'series':
            self.draw_circuit('series')
            self.add_to_terminal("Drawing series configuration")
        elif command == 'parallel':
            self.draw_circuit('parallel')
            self.add_to_terminal("Drawing parallel configuration")
        elif command.lower() == 'clear':
            self.terminal.delete("1.0", tk.END)
            self.canvas.delete("all")
            self.components = []
            self.current_x = self.start_x
            self.add_to_terminal("Circuit Calculator Terminal")
        elif command.lower() == 'help':
            help_text = """Available commands:
R - Add a resistor
C - Add a capacitor
L - Add an inductor
CS - Add a current source
SERIES - Arrange components in series
PARALLEL - Arrange components in parallel
clear - Clear terminal and components
help - Show this help message"""
            self.add_to_terminal(help_text)
        else:
            self.add_to_terminal(f"Unknown command: {command}\nType 'help' for available commands")
        
        return "break"

def main():
    root = tk.Tk()
    app = CircuitCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
