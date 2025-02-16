import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk
import math
import logging

class EagleSymbol:
    def __init__(self, canvas):
        self.canvas = canvas
        self.scale = 20  # Scale factor to convert Eagle units to pixels
        self.rotation = 0  # Current rotation in degrees
        self.symbol_color = "#8B0000"  # Dark red for both symbols and pins
        self.offset_x = 0  # Add offset support
        self.offset_y = 0
        self.zoom = 1.0  # Add zoom factor
        
    def draw_wire(self, x1, y1, x2, y2, layer="94"):
        x1, y1 = self.rotate_point(x1, y1)
        x2, y2 = self.rotate_point(x2, y2)
        
        canvas_x1 = x1 * self.scale * self.zoom + self.offset_x
        canvas_y1 = -y1 * self.scale * self.zoom + self.offset_y
        canvas_x2 = x2 * self.scale * self.zoom + self.offset_x
        canvas_y2 = -y2 * self.scale * self.zoom + self.offset_y
        
        return self.canvas.create_line(
            canvas_x1, canvas_y1, 
            canvas_x2, canvas_y2,
            fill=self.get_layer_color(layer), 
            width=2 * self.zoom  # Scale line width with zoom
        )
    
    def draw_circle(self, x, y, radius, layer="94"):
        x, y = self.rotate_point(x, y)
        canvas_x = x * self.scale * self.zoom + self.offset_x
        canvas_y = -y * self.scale * self.zoom + self.offset_y  # Invert y coordinate
        r = radius * self.scale * self.zoom  # Apply zoom to radius too
        
        return self.canvas.create_oval(
            canvas_x - r, canvas_y - r,
            canvas_x + r, canvas_y + r,
            outline=self.get_layer_color(layer),
            width=2 * self.zoom  # Scale line width with zoom
        )
    
    def draw_arc(self, x, y, radius, start_angle, end_angle, layer="94"):
        x, y = self.rotate_point(x, y)
        canvas_x = x * self.scale
        canvas_y = -y * self.scale
        r = radius * self.scale
        
        # Convert angles to degrees and adjust for coordinate system
        start = (start_angle + self.rotation) % 360
        extent = (end_angle - start_angle) % 360
        
        return self.canvas.create_arc(
            canvas_x - r, canvas_y - r,
            canvas_x + r, canvas_y + r,
            start=start, extent=extent,
            outline=self.get_layer_color(layer),
            style="arc", width=2
        )
    
    def draw_text(self, x, y, text, size=1.0, layer="94", align="center", tags=()):
        x, y = self.rotate_point(x, y)
        
        # Apply zoom and offset to coordinates
        canvas_x = x * self.scale * self.zoom + self.offset_x
        canvas_y = -y * self.scale * self.zoom + self.offset_y
        
        # Handle special text alignment for component labels
        if text.startswith('>'):
            # Move component values and names slightly above the component
            canvas_y -= self.scale * 0.8 * self.zoom  # Scale offset with zoom
            if text == '>VALUE':
                canvas_y -= self.scale * 0.8 * self.zoom  # Scale offset with zoom
        
        # Scale font size with zoom
        font_size = int(size * 12 * self.zoom)  # Scale font size with zoom
        
        # Map text anchors
        anchor_map = {
            "center": "center",
            "start": "w",
            "end": "e",
            "left": "w",
            "right": "e"
        }
        anchor = anchor_map.get(align, "center")
        
        return self.canvas.create_text(
            canvas_x, canvas_y,
            text=text,
            fill=self.get_layer_color(layer),
            font=("Arial", font_size),
            anchor=anchor,
            tags=tags  # Add tags parameter
        )
    
    def draw_pin(self, x, y, length, direction, name, layer="91"):
        x, y = self.rotate_point(x, y)
        dx, dy = self.get_direction_vector(direction)
        
        # Adjust pin direction for pin 2
        if name == "2":
            dx = -dx  # Reverse direction for pin 2
        
        # Draw pin line
        pin = self.draw_wire(
            x, y,
            x + dx * length, y + dy * length,
            layer
        )
        
        # Calculate pin number position
        number_offset = 0.3  # Offset in grid units
        
        # Position pin numbers consistently
        if name == "2":
            text_x = x + dx * length * 0.2  # Position number closer to the component
        else:
            text_x = x + dx * length * 0.2
        text_y = y - number_offset  # Always place numbers above the pin
        
        # Add pin number
        text = self.draw_text(
            text_x,
            text_y,
            str(name),
            size=0.7,  # Slightly smaller pin numbers
            layer=layer,
            align="center"  # Center align all pin numbers
        )
        
        return [pin, text]
    
    def rotate_point(self, x, y):
        if self.rotation == 0:
            return x, y
        angle = math.radians(self.rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
    
    def get_direction_vector(self, direction):
        # Convert direction to float and handle special cases
        try:
            if isinstance(direction, str):
                # Map text directions to angles
                direction_map = {
                    'R': 0,    # Right
                    'L': 180,  # Left
                    'U': 90,   # Up
                    'D': 270,  # Down
                    'io': 0,   # Default to right for IO pins
                    'in': 180, # Input pins come from left
                    'out': 0,  # Output pins go to right
                    '1': 0,    # Pin 1 goes right
                    '2': 0,    # Pin 2 also goes right (changed from 180)
                }
                angle = direction_map.get(direction, 0)
            else:
                angle = float(direction)
            
            # Apply rotation and convert to radians
            angle_rad = math.radians((angle + self.rotation) % 360)
            return (math.cos(angle_rad), math.sin(angle_rad))
        except (ValueError, TypeError):
            # If conversion fails, default to rightward direction
            return (1, 0)
    
    def get_layer_color(self, layer):
        colors = {
            "91": self.symbol_color,  # Pins - now using same dark red
            "94": self.symbol_color,  # Symbols
            "95": "#808080",  # Names
            "96": "#404040",  # Values
            "97": "#FF0000",  # Info
            "98": "#0000FF",  # Guide
        }
        return colors.get(layer, self.symbol_color)

    def draw_origin_markers(self, x, y, is_text=False):
        """Draw origin marker cross"""
        # Increase cross size (was 3)
        size = 5 * self.zoom  # Bigger cross size
        color = "#808080" if is_text else self.symbol_color
        
        # Convert coordinates
        canvas_x = x * self.scale * self.zoom + self.offset_x
        canvas_y = -y * self.scale * self.zoom + self.offset_y
        
        # Draw the cross
        markers = []
        # Horizontal line
        markers.append(self.canvas.create_line(
            canvas_x - size, canvas_y,
            canvas_x + size, canvas_y,
            fill=color, width=1.5 * self.zoom  # Slightly thicker lines
        ))
        # Vertical line
        markers.append(self.canvas.create_line(
            canvas_x, canvas_y - size,
            canvas_x, canvas_y + size,
            fill=color, width=1.5 * self.zoom  # Slightly thicker lines
        ))
        
        return markers

class CircuitApp:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        self.root = tk.Tk()
        self.root.title("Circuit Calculator")
        
        # Initialize zoom before creating canvas and drawing grid
        self.zoom = 1.0
        
        self.create_menu_bar()
        self.main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_sidebar()
        self.create_canvas()
        
        self.current_tool = "select"
        self.selected_components = []
        self.temp_component = []  # Changed to list to store multiple canvas items
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.load_eagle_library("eagle_libraries/ngspice-simulation.lbr")
        
        self.sidebar_visible = True
        self.current_component = None
        
        self.exit_via_menu = False
        self.root.protocol("WM_DELETE_WINDOW", self.close_application_window)
        self.root.bind('<Alt-F4>', self.close_application_hotkey)
        
        # Add keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.menu_new())
        self.root.bind('<Control-o>', lambda e: self.menu_open())
        self.root.bind('<Control-s>', lambda e: self.menu_save())
        self.root.bind('<Control-z>', lambda e: self.menu_undo())
        self.root.bind('<Control-y>', lambda e: self.menu_redo())
        self.root.bind('<Control-x>', lambda e: self.menu_cut())
        self.root.bind('<Control-c>', lambda e: self.menu_copy())
        self.root.bind('<Control-v>', lambda e: self.menu_paste())
        self.root.bind('<Control-plus>', lambda e: self.menu_zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.menu_zoom_out())
        self.root.bind('<Control-0>', lambda e: self.menu_zoom_reset())
        self.root.bind('<Control-g>', self.toggle_grid)
        self.root.bind('<Control-Shift-G>', self.toggle_snap)
        
        # Add keyboard bindings for delete
        self.root.bind('<Delete>', self.delete_selected)
        self.root.bind('<BackSpace>', self.delete_selected)
        
        # Force initial grid draw after window is fully initialized
        self.root.update_idletasks()  # Ensure geometry is updated
        self.draw_grid()
        
        self.placed_components = []  # Track placed components
        self.component_counters = {}  # Track component numbers
        
        # Add zoom bindings
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
        
        self.moving_component = None  # Track which component is being moved
        
        # Add selection variables
        self.selection_start_x = None
        self.selection_start_y = None
        self.selection_rectangle = None
        self.selected_components = []
        self.is_selecting = False
        
        # Bind mouse events for selection
        self.canvas.bind('<ButtonPress-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)
        
    def create_menu_bar(self):
        # Create notebook for tabs
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill=tk.X)
        
        # Create tab frames
        file_tab = ttk.Frame(self.tab_control)
        edit_tab = ttk.Frame(self.tab_control)
        view_tab = ttk.Frame(self.tab_control)
        grid_tab = ttk.Frame(self.tab_control)  # New grid tab
        
        # Add tabs to notebook
        self.tab_control.add(file_tab, text='File')
        self.tab_control.add(edit_tab, text='Edit')
        self.tab_control.add(view_tab, text='View')
        self.tab_control.add(grid_tab, text='Grid')  # Add grid tab
        
        # Style for toolbar buttons
        style = ttk.Style()
        style.configure(
            'Toolbar.TButton',
            padding=2,
            relief='flat',
            background='#f0f0f0'
        )
        
        # File tab buttons
        file_buttons = [
            ("New", "📄", self.menu_new, "Ctrl+N"),
            ("Open", "📂", self.menu_open, "Ctrl+O"),
            ("Save", "💾", self.menu_save, "Ctrl+S"),
        ]
        
        file_toolbar = ttk.Frame(file_tab)
        file_toolbar.pack(fill=tk.X, padx=2, pady=2)
        self.create_button_group(file_toolbar, "File", file_buttons)
        
        # Edit tab buttons
        edit_buttons = [
            ("Undo", "↩️", self.menu_undo, "Ctrl+Z"),
            ("Redo", "↪️", self.menu_redo, "Ctrl+Y"),
            None,  # Separator
            ("Cut", "✂️", self.menu_cut, "Ctrl+X"),
            ("Copy", "📋", self.menu_copy, "Ctrl+C"),
            ("Paste", "📌", self.menu_paste, "Ctrl+V"),
        ]
        
        edit_toolbar = ttk.Frame(edit_tab)
        edit_toolbar.pack(fill=tk.X, padx=2, pady=2)
        self.create_button_group(edit_toolbar, "Edit", edit_buttons)
        
        # View tab buttons
        view_buttons = [
            ("Zoom In", "🔍+", self.menu_zoom_in, "Ctrl++"),
            ("Zoom Out", "🔍-", self.menu_zoom_out, "Ctrl+-"),
            ("Reset View", "🔍1", self.menu_zoom_reset, "Ctrl+0"),
        ]
        
        view_toolbar = ttk.Frame(view_tab)
        view_toolbar.pack(fill=tk.X, padx=2, pady=2)
        self.create_button_group(view_toolbar, "View", view_buttons)
        
        # Grid tab - horizontal layout
        grid_toolbar = ttk.Frame(grid_tab)
        grid_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Show Grid checkbox
        self.grid_visible_var = tk.BooleanVar(value=True)
        show_grid_cb = ttk.Checkbutton(
            grid_toolbar,
            text="Show Grid",
            variable=self.grid_visible_var,
            command=self.toggle_grid
        )
        show_grid_cb.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(grid_toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=2)
        
        # Grid Style radio buttons in a labeled frame
        style_frame = ttk.LabelFrame(grid_toolbar, text="Style")
        style_frame.pack(side=tk.LEFT, padx=5)
        
        self.grid_style_var = tk.StringVar(value="lines")
        ttk.Radiobutton(
            style_frame,
            text="Lines",
            variable=self.grid_style_var,
            value="lines",
            command=self.update_grid_style
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            style_frame,
            text="Dots",
            variable=self.grid_style_var,
            value="dots",
            command=self.update_grid_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(grid_toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=2)
        
        # Grid Size input
        ttk.Label(grid_toolbar, text="Size:").pack(side=tk.LEFT, padx=(5, 0))
        self.grid_size_var = tk.StringVar(value="20")
        size_entry = ttk.Entry(
            grid_toolbar,
            textvariable=self.grid_size_var,
            width=5
        )
        size_entry.pack(side=tk.LEFT, padx=5)
        
        # Bind validation and update
        size_entry.bind('<Return>', self.update_grid_size)
        size_entry.bind('<FocusOut>', self.update_grid_size)
        
        # Snap to Grid checkbox
        self.snap_grid_var = tk.BooleanVar(value=True)
        snap_grid_cb = ttk.Checkbutton(
            grid_toolbar,
            text="Snap to Grid",
            variable=self.snap_grid_var,
            command=self.toggle_snap
        )
        snap_grid_cb.pack(side=tk.LEFT, padx=5)

    def create_button_group(self, parent, group_name, buttons):
        """Create a group of toolbar buttons"""
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=2)
        
        for button in buttons:
            if button is None:  # Add separator
                ttk.Separator(frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=2, fill=tk.Y)
                continue
                
            name, icon, command, accelerator = button
            btn = ttk.Button(
                frame,
                text=icon,
                style='Toolbar.TButton',
                command=command
            )
            btn.pack(side=tk.LEFT, padx=1)
            self.create_tooltip(btn, f"{name} ({accelerator})")

    def menu_new(self, event=None):
        self.logger.info("New file")
        # TODO: Implement new file functionality

    def menu_open(self, event=None):
        self.logger.info("Open file")
        # TODO: Implement open file functionality

    def menu_save(self, event=None):
        self.logger.info("Save file")
        # TODO: Implement save functionality

    def menu_exit(self):
        self.logger.info("Menu: Exit selected")
        self.exit_via_menu = True
        self.close_application()

    def menu_undo(self, event=None):
        self.logger.info("Undo")
        # TODO: Implement undo functionality

    def menu_redo(self, event=None):
        self.logger.info("Redo")
        # TODO: Implement redo functionality

    def menu_cut(self, event=None):
        self.logger.info("Cut")
        # TODO: Implement cut functionality

    def menu_copy(self, event=None):
        self.logger.info("Copy")
        # TODO: Implement copy functionality

    def menu_paste(self, event=None):
        self.logger.info("Paste")
        # TODO: Implement paste functionality

    def menu_zoom_in(self, event=None):
        self.zoom *= 1.2
        self.draw_grid()
        self.logger.info(f"Zoom in: {self.zoom:.2f}")

    def menu_zoom_out(self, event=None):
        self.zoom /= 1.2
        self.draw_grid()
        self.logger.info(f"Zoom out: {self.zoom:.2f}")

    def menu_zoom_reset(self, event=None):
        self.zoom = 1.0
        self.draw_grid()
        self.logger.info("Zoom reset")

    def close_application_window(self):
        """Handle window close button (X) click"""
        self.logger.info("Window close button (X) clicked")
        self.close_application()

    def close_application_hotkey(self, event=None):
        """Handle Alt-F4 hotkey"""
        self.logger.info("Alt-F4 pressed")
        self.close_application()

    def close_application(self):
        if not self.exit_via_menu:
            self.logger.info("Application closed by window X or Alt-F4")
        self.logger.info("Application closing")
        self.root.quit()
        
    def create_sidebar(self):
        # Create sidebar frame
        self.sidebar_frame = ttk.Frame(self.main_container, width=50)  # Reduced width
        self.main_container.add(self.sidebar_frame)
        
        # Create tools frame
        tools_frame = ttk.Frame(self.sidebar_frame)
        tools_frame.pack(fill=tk.X)
        
        # Initialize tool buttons dictionary
        self.tool_buttons = {}
        
        # Add tool buttons vertically
        tool_configs = [
            # Selection and manipulation tools
            ("select", "⬚"),    # Selection tool
            ("move", "↔"),      # Move tool
            ("rotate", "⟳"),    # Rotate tool
            ("mirror", "⇄"),    # Mirror tool
            ("duplicate", "⎘"),  # Duplicate tool
            ("delete", "✕"),    # Delete tool
            
            # Component tools
            (None, None),       # Separator
            ("add_part", "⊕"),  # Add component
            ("replace", "⟲"),   # Replace tool
            ("edit_part", "✎"), # Edit component
            
            # Connection tools
            (None, None),       # Separator
            ("net", "⌇"),       # Net tool
            ("junction", "●"),  # Junction tool
            
            # Text tools
            (None, None),       # Separator
            ("label", "L"),     # Label tool
            ("name", "N"),      # Name tool
            ("value", "V"),     # Value tool
            ("split", "Y")      # Split/fork tool
        ]
        
        # Create buttons vertically in tools frame
        for tool_id, icon in tool_configs:
            if tool_id is None:  # Add separator
                ttk.Separator(tools_frame, orient='horizontal').pack(fill='x', pady=5)
                continue
                
            btn = ttk.Button(
                tools_frame,
                text=icon,
                width=2,  # Make buttons square
                command=lambda t=tool_id: self.select_tool(t)
            )
            btn.pack(pady=1)
            self.tool_buttons[tool_id] = btn
            
            # Add tooltip with tool name
            tooltip_text = tool_id.replace('_', ' ').title()
            self.create_tooltip(btn, tooltip_text)
            
        # Create components frame
        self.components_frame = ttk.Frame(self.sidebar_frame)
        self.components_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        
        # Create scrollable frame for components
        components_canvas = tk.Canvas(self.components_frame)
        scrollbar = ttk.Scrollbar(self.components_frame, orient="vertical", command=components_canvas.yview)
        
        # Create frame for component buttons
        self.components_list = ttk.Frame(components_canvas)
        
        # Configure scrolling
        components_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        components_canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas for components list
        components_canvas.create_window((0,0), window=self.components_list, anchor="nw", width=components_canvas.winfo_width())
        
        # Update scroll region when components list size changes
        self.components_list.bind("<Configure>", lambda e: components_canvas.configure(scrollregion=components_canvas.bbox("all")))

    def select_tool(self, tool):
        self.current_tool = tool
        self.logger.info(f"Selected tool: {tool}")
        
        # Update button appearances
        for btn_id, btn in self.tool_buttons.items():
            if btn_id == tool:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])
        
        # Unbind all tool-specific events first
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        
        # Clear any existing selection rectangle
        if hasattr(self, 'selection_rectangle') and self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None
        
        if tool == "select":
            # Enable selection mode
            self.canvas.bind("<ButtonPress-1>", self.start_selection)
            self.canvas.bind("<B1-Motion>", self.update_selection)
            self.canvas.bind("<ButtonRelease-1>", self.end_selection)
            self.canvas.config(cursor="arrow")
        elif tool == "delete":
            self.canvas.bind("<Button-1>", self.handle_delete_click)
            self.canvas.config(cursor="X_cursor")
        elif tool == "add_part":
            self.canvas.bind("<Motion>", self.update_component_position)
            self.canvas.bind("<Button-1>", self.place_component)
            self.canvas.config(cursor="crosshair")

    def start_selection(self, event):
        # Only handle selection if in select tool mode
        if self.current_tool != "select":
            return
            
        # Convert screen coordinates to canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Get items at click position with smaller overlap area
        clicked_items = self.canvas.find_overlapping(
            canvas_x-1, canvas_y-1, 
            canvas_x+1, canvas_y+1
        )
        
        # Only start selection if clicking on empty space
        if not clicked_items:
            # Clear any existing selection rectangle
            if hasattr(self, 'selection_rectangle') and self.selection_rectangle:
                self.canvas.delete(self.selection_rectangle)
            
            self.is_selecting = True
            self.selection_start_x = canvas_x
            self.selection_start_y = canvas_y
            
            # Create new selection rectangle
            self.selection_rectangle = self.canvas.create_rectangle(
                canvas_x, canvas_y,
                canvas_x, canvas_y,
                outline='#0078D7',
                dash=(2, 2),
                fill='#0078D7',
                stipple='gray25',
                width=1,
                tags=('selection',)  # Add tag for easy identification
            )
            
            # Clear previous selection if not holding shift
            if not event.state & 0x1:  # Check if shift is not pressed
                self.selected_components = []
                self.highlight_selected_components()  # Clear highlights
            
            self.logger.debug(f"Started selection at ({canvas_x}, {canvas_y})")

    def update_selection(self, event):
        if self.is_selecting and self.selection_rectangle:
            # Get current mouse position in canvas coordinates
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            # Update selection rectangle
            self.canvas.coords(
                self.selection_rectangle,
                self.selection_start_x, self.selection_start_y,
                current_x, current_y
            )
            
            # Real-time highlight of components within selection
            x1, y1 = self.selection_start_x, self.selection_start_y
            x2, y2 = current_x, current_y
            
            # Normalize coordinates
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Update selection in real-time
            current_selection = []
            for component in self.placed_components:
                origin = component['origin']
                if (x1 <= origin[0] <= x2 and y1 <= origin[1] <= y2):
                    current_selection.append(component)
            
            # Update highlights
            self.selected_components = current_selection
            self.highlight_selected_components()
            
            self.logger.debug(f"Updated selection to ({current_x}, {current_y})")

    def end_selection(self, event):
        if self.is_selecting and self.selection_rectangle:
            coords = self.canvas.coords(self.selection_rectangle)
            x1, y1, x2, y2 = coords
            
            # Normalize coordinates
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Find components in selection area
            newly_selected = []
            for component in self.placed_components:
                origin = component['origin']
                if (x1 <= origin[0] <= x2 and y1 <= origin[1] <= y2):
                    if component not in self.selected_components:
                        newly_selected.append(component)
            
            # Add newly selected components
            self.selected_components.extend(newly_selected)
            
            # Highlight all selected components
            self.highlight_selected_components()
            
            # Clean up selection
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None
            self.selection_start_x = None
            self.selection_start_y = None
            self.is_selecting = False
            
            self.logger.info(f"Selection ended, {len(newly_selected)} new components selected")

    def highlight_selected_components(self):
        # Remove previous highlights
        for component in self.placed_components:
            for item in component['symbol']:
                self.canvas.itemconfig(item, width=2 * self.zoom)
        
        # Highlight selected components
        for component in self.selected_components:
            for item in component['symbol']:
                # Make selected items thicker
                self.canvas.itemconfig(item, width=3 * self.zoom)

    def delete_selected(self, event=None):
        if not self.selected_components:
            return
        
        # Store number of components being deleted for logging
        num_deleted = len(self.selected_components)
        
        # Delete each selected component
        for component in self.selected_components:
            # Delete all canvas items for this component
            for item in component['symbol']:
                self.canvas.delete(item)
            # Remove from placed components list
            self.placed_components.remove(component)
            
            # Decrement component counter if it was the last one
            component_type = component['type']
            component_number = int(component['name_text'][len(component_type):])
            if component_number == self.component_counters.get(component_type, 0):
                self.component_counters[component_type] = component_number - 1
        
        # Clear selection
        self.selected_components = []
        
        self.logger.info(f"Deleted {num_deleted} component{'s' if num_deleted > 1 else ''}")
            
    def run(self):
        try:
            self.root.geometry("1200x800")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
        finally:
            self.logger.info("Application terminated")

    def handle_delete_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        
        if not items:
            return
            
        for component in self.placed_components:
            # Check which part was clicked
            clicked_symbol = set(items) & set(component['symbol'])
            clicked_name = set(items) & set(component['name'])
            clicked_value = set(items) & set(component['value'])
            
            if clicked_symbol:
                # Delete entire component if clicking symbol origin
                clicked_item = list(clicked_symbol)[0]
                item_type = self.canvas.type(clicked_item)
                
                is_origin = (item_type == 'line' and 
                           any(self.canvas.type(other) == 'line' 
                               for other in clicked_symbol))
                
                if is_origin:
                    # Delete everything
                    for items in component.values():
                        for item in items:
                            self.canvas.delete(item)
                    self.placed_components.remove(component)
                    # Update counter
                    component_type = component['type']
                    component_number = int(component['name_text'][len(component_type):])
                    if component_number == self.component_counters.get(component_type, 0):
                        self.component_counters[component_type] = component_number - 1
                    self.logger.info(f"Deleted component {component['name_text']}")
                break
                
            elif clicked_name:
                # Hide name if clicking name text or origin
                for item in component['name']:
                    self.canvas.itemconfig(item, state='hidden')
                self.logger.info(f"Hidden name for component {component['name_text']}")
                break
                
            elif clicked_value:
                # Hide value if clicking value text or origin
                for item in component['value']:
                    self.canvas.itemconfig(item, state='hidden')
                self.logger.info(f"Hidden value for component {component['name_text']}")
                break

    def create_tooltip(self, widget, text):
        """Create a tooltip for a given widget."""
        def enter(event):
            # Create tooltip window
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)  # Remove window decorations
            
            # Position tooltip near mouse
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Create tooltip label
            label = ttk.Label(
                tooltip,
                text=text,
                justify=tk.LEFT,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Arial", "8", "normal")
            )
            label.pack()
            
            # Position tooltip window
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.attributes('-topmost', True)  # Keep tooltip on top
            
            # Store tooltip reference
            widget.tooltip = tooltip

        def leave(event):
            # Destroy tooltip when mouse leaves
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        # Bind mouse events
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def toggle_grid(self, event=None):
        """Toggle grid visibility"""
        self.grid_visible = not getattr(self, 'grid_visible', True)
        self.draw_grid()
        self.logger.info(f"Grid visibility: {self.grid_visible}")

    def toggle_snap(self, event=None):
        """Toggle grid snapping"""
        self.snap_to_grid = not getattr(self, 'snap_to_grid', True)
        self.logger.info(f"Snap to grid: {self.snap_to_grid}")

    def update_grid_style(self):
        # Implementation of update_grid_style method
        pass

    def update_grid_size(self):
        # Implementation of update_grid_size method
        pass

    def update_grid(self):
        # Implementation of update_grid method
        pass

    def update_component_position(self, event):
        # Implementation of update_component_position method
        pass

    def place_component(self, event):
        # Implementation of place_component method
        pass

    def on_mousewheel(self, event):
        # Implementation of on_mousewheel method
        pass

    def create_canvas(self):
        # Create canvas container frame
        self.canvas_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.canvas_frame)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='white',
            width=800,
            height=600
        )
        
        # Create scrollbars
        h_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        v_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        # Configure canvas scrolling
        self.canvas.configure(
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            scrollregion=(-2000, -2000, 2000, 2000)  # Initial scroll region
        )
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize canvas drag variables
        self.canvas_drag = False
        self.last_x = 0
        self.last_y = 0
        
        # Bind canvas pan events
        self.canvas.bind("<ButtonPress-2>", self.start_canvas_drag)  # Middle mouse button
        self.canvas.bind("<B2-Motion>", self.do_canvas_drag)
        self.canvas.bind("<ButtonRelease-2>", self.stop_canvas_drag)
        
        # Initialize grid
        self.grid_visible = True
        self.grid_size = 20
        self.grid_style = "lines"
        self.snap_to_grid = True
        
        # Draw initial grid
        self.draw_grid()

    def start_canvas_drag(self, event):
        self.canvas_drag = True
        self.last_x = event.x
        self.last_y = event.y

    def do_canvas_drag(self, event):
        if self.canvas_drag:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.canvas.scan_mark(self.last_x, self.last_y)
            self.last_x = event.x
            self.last_y = event.y

    def stop_canvas_drag(self, event):
        self.canvas_drag = False

    def draw_grid(self):
        # Clear existing grid
        self.canvas.delete("grid")
        
        if not self.grid_visible:
            return
            
        # Get canvas visible area
        bbox = self.canvas.bbox("all")
        if not bbox:
            bbox = (-2000, -2000, 2000, 2000)
            
        x1, y1, x2, y2 = bbox
        
        # Draw grid lines or dots
        grid_size = self.grid_size * self.zoom
        
        if self.grid_style == "lines":
            # Draw vertical lines
            for x in range(int(x1 - x1 % grid_size), int(x2), int(grid_size)):
                self.canvas.create_line(
                    x, y1, x, y2,
                    fill="#E0E0E0",
                    tags="grid"
                )
            
            # Draw horizontal lines
            for y in range(int(y1 - y1 % grid_size), int(y2), int(grid_size)):
                self.canvas.create_line(
                    x1, y, x2, y,
                    fill="#E0E0E0",
                    tags="grid"
                )
        else:  # dots
            for x in range(int(x1 - x1 % grid_size), int(x2), int(grid_size)):
                for y in range(int(y1 - y1 % grid_size), int(y2), int(grid_size)):
                    self.canvas.create_oval(
                        x-1, y-1, x+1, y+1,
                        fill="#E0E0E0",
                        outline="#E0E0E0",
                        tags="grid"
                    )

    def load_eagle_library(self, filename):
        """Load and parse an Eagle library file."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Find all symbol elements
            self.symbols = {}
            for symbol in root.findall(".//symbol"):
                symbol_name = symbol.get('name')
                if symbol_name:
                    self.symbols[symbol_name] = []
                    
                    # Store all drawing elements
                    for element in symbol:
                        if element.tag in ['wire', 'circle', 'text', 'pin', 'arc']:
                            self.symbols[symbol_name].append({
                                'type': element.tag,
                                'attributes': element.attrib
                            })
            
            # Find all device elements
            self.devices = {}
            for deviceset in root.findall(".//deviceset"):
                deviceset_name = deviceset.get('name')
                if deviceset_name:
                    for device in deviceset.findall('device'):
                        device_name = device.get('name', '')
                        full_name = f"{deviceset_name}{device_name}"
                        
                        # Get symbol reference
                        symbol_ref = device.find(".//symbol")
                        if symbol_ref is not None:
                            symbol_name = symbol_ref.get('name')
                            if symbol_name in self.symbols:
                                self.devices[full_name] = {
                                    'symbol': symbol_name,
                                    'description': deviceset.find('description').text if deviceset.find('description') is not None else '',
                                    'value': device.get('value', 'off') == 'on'
                                }
            
            self.logger.info(f"Loaded {len(self.symbols)} symbols and {len(self.devices)} devices from {filename}")
            
            # Update sidebar with loaded components
            self.update_component_list()
            
        except ET.ParseError as e:
            self.logger.error(f"Error parsing Eagle library file: {str(e)}")
        except FileNotFoundError:
            self.logger.error(f"Eagle library file not found: {filename}")
        except Exception as e:
            self.logger.error(f"Error loading Eagle library: {str(e)}")

    def update_component_list(self):
        """Update the sidebar component list with loaded devices."""
        # Clear existing items
        for widget in self.components_frame.winfo_children():
            widget.destroy()
            
        # Add components from loaded library
        for device_name, device_info in self.devices.items():
            btn = ttk.Button(
                self.components_frame,
                text=device_name,
                command=lambda d=device_name: self.select_component(d)
            )
            btn.pack(fill=tk.X, padx=2, pady=1)
            
            # Add tooltip with description
            if device_info.get('description'):
                self.create_tooltip(btn, device_info['description'])

    def select_component(self, device_name):
        """Handle component selection from sidebar."""
        self.current_component = device_name
        self.current_tool = "add_part"
        self.logger.info(f"Selected component: {device_name}")
        
        # Update tool buttons
        for btn_id, btn in self.tool_buttons.items():
            if btn_id == "add_part":
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

if __name__ == "__main__":
    app = CircuitApp()
    app.run()