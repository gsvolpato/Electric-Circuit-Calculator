import tkinter as tk
from tkinter import ttk
import schemdraw
from schemdraw import elements as elm
from io import BytesIO
from PIL import Image, ImageTk

class CircuitCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Calculator")
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create PanedWindow to allow resizing with a bar
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Schematic output at the top
        self.schematic_frame = ttk.Frame(self.paned)
        self.canvas = tk.Canvas(self.schematic_frame, width=400, height=200, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Terminal frame at the bottom
        self.terminal_frame = ttk.Frame(self.paned)
        self.terminal = tk.Text(self.terminal_frame, height=12, width=50, bg='black', fg='white')
        self.terminal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add frames to PanedWindow
        self.paned.add(self.schematic_frame)
        self.paned.add(self.terminal_frame)
        
        # Configure terminal font
        self.terminal.configure(font=('Consolas', 10))
        
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

        # Initialize last component position
        self.last_x = 200
        self.last_y = 100

    def handle_keypress(self, event):
        if self.terminal.index(tk.INSERT) < self.command_start:
            self.terminal.mark_set(tk.INSERT, tk.END)
            return "break"

    def draw_component(self, component_type):
        d = schemdraw.Drawing()
        
        if component_type == 'R':
            element = elm.Resistor().label('R')
        elif component_type == 'C':
            element = elm.Capacitor().label('C')
        elif component_type == 'L':
            element = elm.Inductor().label('L')
        else:
            return False
            
        d += element
        
        # Convert to image
        img_data = BytesIO()
        d.save(img_data, format='PNG')
        img_data.seek(0)
        img = Image.open(img_data)
        
        # Clear previous drawing
        self.canvas.delete("all")
        
        # Display new component
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(self.last_x, self.last_y, image=self.photo)
        return True

    def draw_circuit(self, circuit_type='series', components=None):
        if components is None:
            components = [('R', '10Ω'), ('V', '5V')]
            
        d = schemdraw.Drawing()
        
        if circuit_type == 'series':
            d += (V1 := elm.SourceV().label(components[1][1]))
            d += elm.Resistor().right().label(components[0][1])
            d += elm.Line().down()
            d += elm.Line().left()
            d += elm.Line().up()
            
        img_data = BytesIO()
        d.save(img_data, format='PNG')
        img_data.seek(0)
        img = Image.open(img_data)
        
        self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(200, 100, image=self.photo)

    def add_to_terminal(self, text):
        self.terminal.insert(tk.END, f"{text}\n>> ")
        self.command_start = self.terminal.index("end-1c")
        self.terminal.see(tk.END)

    def process_input(self, event=None):
        command_index = self.terminal.index(self.command_start)
        command = self.terminal.get(command_index, "end-1c").strip().upper()
        
        if command in ['R', 'C', 'L']:
            if self.draw_component(command):
                self.add_to_terminal(f"Drawing {command}")
            else:
                self.add_to_terminal(f"Error drawing component {command}")
        elif command.lower().startswith('draw series'):
            self.draw_circuit('series')
            self.add_to_terminal("Drawing series circuit...")
        elif command.lower() == 'clear':
            self.terminal.delete("1.0", tk.END)
            self.add_to_terminal("Circuit Calculator Terminal")
        elif command.lower() == 'help':
            help_text = """Available commands:
R - Draw a resistor
C - Draw a capacitor
L - Draw an inductor
draw series - Draw a series circuit
clear - Clear terminal
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
