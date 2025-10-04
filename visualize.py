import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import numpy as np
import sys
import os
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
import matplotlib.gridspec as gridspec
from matplotlib.patches import Polygon
import matplotlib.patheffects as path_effects

class AlgorithmVisualizer:
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.is_playing = False
        self.speed = 1.0
        self.config = {}
        self.theme = 'dark'
        self.show_code = True
        self.comparisons = 0
        self.swaps = 0
        self.animation_frames = 5  # Reduced frames for faster animation
        self.current_frame = 0
        self.previous_data = None
        self.previous_highlighted = None
        self.last_update_time = 0  # For throttling updates
        
        # Load data
        self.load_data()
        
        # Setup theme
        self.setup_theme()
        
        # Get screen size and create full-screen layout
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            # Use 95% of screen for full-screen experience
            fig_width = screen_width * 0.95 / 100
            fig_height = screen_height * 0.95 / 100
        except:
            fig_width, fig_height = 24, 16
        
        # Create full-screen figure with professional layout
        self.fig = plt.figure(figsize=(fig_width, fig_height), facecolor='#0a0a0a')
        self.fig.patch.set_facecolor('#0a0a0a')
        
        # Create a simple, clean grid layout
        gs = gridspec.GridSpec(10, 12, figure=self.fig, 
                              hspace=0.2, wspace=0.2,
                              left=0.03, right=0.97, 
                              top=0.92, bottom=0.08)
        
        # Main visualization area (takes most of the screen)
        self.ax_main = self.fig.add_subplot(gs[1:8, 0:12])
        self.ax_main.set_facecolor('#1a1a1a')
        
        # Control panel (bottom, compact)
        self.ax_controls = self.fig.add_subplot(gs[8:10, 0:12])
        self.ax_controls.set_facecolor('#0a0a0a')
        self.ax_controls.axis('off')
        
        # Info overlay (top right, small and unobtrusive)
        self.ax_info = self.fig.add_subplot(gs[0:1, 8:12])
        self.ax_info.set_facecolor('#2a2a2a')
        
        # Initialize view mode
        self.show_details = False
        
        # Set window position
        mngr = self.fig.canvas.manager
        try:
            if hasattr(mngr, 'window'):
                if hasattr(mngr.window, 'wm_geometry'):
                    mngr.window.wm_geometry("+20+20")
                elif hasattr(mngr.window, 'move'):
                    mngr.window.move(20, 20)
        except:
            pass
        
        # Setup UI and animation
        self.setup_ui()
        self.calculate_statistics()
        self.update_visualization()
        
        # Auto-start animation with optimized speed control
        self.is_playing = True
        initial_interval = max(16, int(1000 / (self.speed * 2)))  # Much faster default, minimum 16ms (60fps)
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=initial_interval, 
            repeat=True, blit=True  # Enable blitting for better performance
        )
        
        plt.show()
    
    def setup_theme(self):
        """Setup professional color themes"""
        themes = {
            'dark': {
                'bg': '#0a0a0a',
                'plot_bg': '#1a1a1a',
                'panel_bg': '#2a2a2a',
                'code_bg': '#1a1a1a',
                'text': '#ffffff',
                'accent': '#00ff88',
                'highlight': '#ffd700',
                'normal': '#4a9eff',
                'compare': '#ff4757',
                'found': '#2ed573',
                'pivot': '#ffa502',
                'special': '#a55eea',
                'success': '#26de81',
                'warning': '#f39c12',
                'error': '#e74c3c',
                'info': '#3498db',
                'border': '#404040',
                'shadow': '#000000'
            }
        }
        self.colors = themes.get(self.theme, themes['dark'])
        plt.style.use('dark_background')
        
        # Set global matplotlib parameters for professional look
        plt.rcParams.update({
            'font.size': 10,
            'font.family': 'sans-serif',
            'axes.linewidth': 1.5,
            'axes.edgecolor': self.colors['border'],
            'xtick.color': self.colors['text'],
            'ytick.color': self.colors['text'],
            'text.color': self.colors['text'],
            'axes.labelcolor': self.colors['text'],
            'axes.facecolor': self.colors['plot_bg'],
            'figure.facecolor': self.colors['bg'],
            'savefig.facecolor': self.colors['bg'],
            'grid.color': self.colors['border'],
            'grid.alpha': 0.3
        })
    
    def load_data(self):
        try:
            with open('algorithm_steps.json', 'r') as f:
                data = json.load(f)
                self.steps = data['steps']
            
            with open('algorithm_config.json', 'r') as f:
                self.config = json.load(f)
                
            print(f"✓ Loaded {len(self.steps)} visualization steps")
            print(f"✓ Structure: {self.config.get('structure_type', 'unknown')}")
            print(f"✓ Operation: {self.config.get('operation', 'unknown')}")
            
        except FileNotFoundError as e:
            print(f"✗ Error: Could not find required files - {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON format - {e}")
            sys.exit(1)
    
    def calculate_statistics(self):
        """Pre-calculate statistics from all steps"""
        self.comparisons = 0
        self.swaps = 0
        
        for step in self.steps:
            action = step.get('action', '')
            if 'COMPARE' in action:
                self.comparisons += 1
            if 'SWAP' in action:
                self.swaps += 1
    
    def setup_ui(self):
        """Setup clean, simple UI with minimal controls"""
        
        # Simple control buttons with better spacing
        button_width = 0.1
        button_height = 0.05
        button_y = 0.02
        spacing = 0.12
        
        # Play/Pause button
        self.ax_play = plt.axes([0.02, button_y, button_width, button_height])
        self.btn_play = Button(self.ax_play, '▶ PLAY', color=self.colors['success'], 
                              hovercolor=self.colors['accent'])
        self.btn_play.label.set_color('white')
        self.btn_play.label.set_fontsize(11)
        self.btn_play.label.set_fontweight('bold')
        self.btn_play.on_clicked(self.toggle_play)
        
        # Reset button
        self.ax_reset = plt.axes([0.02 + spacing, button_y, button_width, button_height])
        self.btn_reset = Button(self.ax_reset, '🔄 RESET', color=self.colors['error'], hovercolor='#c0392b')
        self.btn_reset.label.set_color('white')
        self.btn_reset.label.set_fontsize(11)
        self.btn_reset.label.set_fontweight('bold')
        self.btn_reset.on_clicked(self.reset_animation)
        
        # Step Back button
        self.ax_step_back = plt.axes([0.02 + spacing*2, button_y, button_width, button_height])
        self.btn_step_back = Button(self.ax_step_back, '⏮ BACK', color=self.colors['warning'], hovercolor='#e67e22')
        self.btn_step_back.label.set_color('white')
        self.btn_step_back.label.set_fontsize(11)
        self.btn_step_back.label.set_fontweight('bold')
        self.btn_step_back.on_clicked(self.step_back)
        
        # Step Forward button
        self.ax_step_forward = plt.axes([0.02 + spacing*3, button_y, button_width, button_height])
        self.btn_step_forward = Button(self.ax_step_forward, 'NEXT ⏭', color=self.colors['info'], hovercolor='#2980b9')
        self.btn_step_forward.label.set_color('white')
        self.btn_step_forward.label.set_fontsize(11)
        self.btn_step_forward.label.set_fontweight('bold')
        self.btn_step_forward.on_clicked(self.step_forward)
        
        # Toggle Details button (simple view switcher)
        self.ax_details = plt.axes([0.02 + spacing*4, button_y, button_width, button_height])
        self.btn_details = Button(self.ax_details, '📊 DETAILS', color=self.colors['special'], hovercolor='#8e44ad')
        self.btn_details.label.set_color('white')
        self.btn_details.label.set_fontsize(11)
        self.btn_details.label.set_fontweight('bold')
        self.btn_details.on_clicked(self.toggle_details)
        
        # Enhanced speed slider with real-time control (faster range)
        self.ax_speed = plt.axes([0.65, button_y + 0.01, 0.25, 0.03])
        self.slider_speed = Slider(self.ax_speed, '⚡ SPEED', 0.5, 10.0, valinit=2.0, 
                                  facecolor=self.colors['accent'], valfmt='%.1fx',
                                  edgecolor=self.colors['border'], linewidth=2,
                                  track_color=self.colors['panel_bg'])
        
        # Enhanced slider styling
        self.slider_speed.label.set_color(self.colors['text'])
        self.slider_speed.label.set_fontsize(11)
        self.slider_speed.label.set_fontweight('bold')
        self.slider_speed.valtext.set_color(self.colors['highlight'])
        self.slider_speed.valtext.set_fontsize(11)
        self.slider_speed.valtext.set_fontweight('bold')
        
        # Add speed preset buttons
        self.add_speed_presets()
        
        # Enhanced callback with real-time updates
        self.slider_speed.on_changed(self.update_speed)
        
        # Add keyboard shortcuts for speed control
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Clean title
        structure_name = self.config.get("structure_type", "").replace("_", " ").title()
        operation_name = self.config.get("operation", "").replace("_", " ").title()
        
        # Main title (simplified)
        title_text = f'{structure_name} - {operation_name}'
        self.fig.suptitle(title_text, fontsize=20, color=self.colors['highlight'], 
                         y=0.96, fontweight='bold')
        
        # Version subtitle (smaller)
        subtitle_text = 'Enhanced Algorithm Visualizer v5.1'
        self.fig.text(0.5, 0.91, subtitle_text, fontsize=12, color=self.colors['text'], 
                     ha='center', alpha=0.7)
    
    def add_speed_presets(self):
        """Add speed preset buttons for quick speed adjustment"""
        # Speed preset buttons
        preset_width = 0.035
        preset_height = 0.025
        preset_y = 0.045
        preset_spacing = 0.04
        start_x = 0.91
        
        # Speed presets: 1x, 2x, 5x, 10x (much faster defaults)
        presets = [
            (1.0, '▶️', '#6bcf7f'),  # Normal
            (2.0, '⚡', '#ffd93d'),  # Fast
            (5.0, '🚀', '#ff6b6b'),  # Very Fast
            (10.0, '💨', '#ff1744')  # Ultra Fast
        ]
        
        self.speed_preset_buttons = []
        for i, (speed, icon, color) in enumerate(presets):
            ax_preset = plt.axes([start_x + i * preset_spacing, preset_y, preset_width, preset_height])
            btn_preset = Button(ax_preset, f'{icon}', color=color, hovercolor='white')
            btn_preset.label.set_color('white')
            btn_preset.label.set_fontsize(10)
            btn_preset.label.set_fontweight('bold')
            btn_preset.on_clicked(lambda event, s=speed: self.set_speed_preset(s))
            self.speed_preset_buttons.append(btn_preset)
    
    def update_simple_info(self, step):
        """Simple info overlay - only essential information"""
        self.ax_info.clear()
        self.ax_info.set_facecolor('#2a2a2a')
        
        complexity = step.get('complexity', 'N/A')
        
        # Simple progress indicator
        progress_pct = int((self.current_step + 1) / len(self.steps) * 100)
        
        # Compact info display with speed indicator
        speed_icon = self.get_speed_icon(self.speed)
        info_text = f"Step {self.current_step + 1}/{len(self.steps)} ({progress_pct}%) | {complexity} | {speed_icon}{self.speed:.1f}x"
        self.ax_info.text(0.5, 0.5, info_text, ha='center', va='center',
                         fontsize=9, color=self.colors['text'], fontweight='bold',
                         transform=self.ax_info.transAxes)
        
        # Remove axes
        self.ax_info.set_xticks([])
        self.ax_info.set_yticks([])
        for spine in self.ax_info.spines.values():
            spine.set_visible(False)
    
    
    def get_pseudocode(self, action):
        """Get pseudocode for specific action"""
        codes = {
            'LINEAR_SEARCH': 'for i in range(n):\n    if arr[i] == target:\n        return i',
            'BINARY_SEARCH': 'while left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == target:\n        return mid',
            'BUBBLE': 'for i in range(n):\n    for j in range(n-i-1):\n        if arr[j] > arr[j+1]:\n            swap(arr[j], arr[j+1])',
            'SELECTION': 'for i in range(n):\n    min_idx = i\n    for j in range(i+1, n):\n        if arr[j] < arr[min_idx]:\n            min_idx = j\n    swap(arr[i], arr[min_idx])',
            'INSERTION': 'for i in range(1, n):\n    key = arr[i]\n    j = i-1\n    while j >= 0 and arr[j] > key:\n        arr[j+1] = arr[j]\n        j -= 1',
            'QUICK': 'pivot = arr[high]\nwhile i <= j:\n    if arr[i] < pivot:\n        swap(arr[i], arr[j])',
            'PUSH': 'stack[++top] = value',
            'POP': 'value = stack[top--]',
            'ENQUEUE': 'queue[rear++] = value',
            'DEQUEUE': 'value = queue[front++]',
            'INSERT_BST': 'if value < node.data:\n    node.left = insert(node.left, value)\nelse:\n    node.right = insert(node.right, value)',
            'SEARCH_BST': 'if value == node.data:\n    return node\nelif value < node.data:\n    search(node.left, value)\nelse:\n    search(node.right, value)',
        }
        
        for key, code in codes.items():
            if key in action.upper():
                return code
        
        return 'Processing...'
    
    def get_space_complexity(self, action):
        """Get space complexity based on action type"""
        space_complexities = {
            'LINEAR_SEARCH': 'O(1)',
            'BINARY_SEARCH': 'O(1)',
            'BUBBLE': 'O(1)',
            'SELECTION': 'O(1)',
            'INSERTION': 'O(1)',
            'QUICK': 'O(log n)',
            'PUSH': 'O(1)',
            'POP': 'O(1)',
            'ENQUEUE': 'O(1)',
            'DEQUEUE': 'O(1)',
            'INSERT_BST': 'O(h)',
            'SEARCH_BST': 'O(h)',
            'DELETE_BST': 'O(h)',
            'INSERT_BEGINNING': 'O(1)',
            'INSERT_END': 'O(1)',
            'SEARCH_LIST': 'O(1)',
        }
        
        for key, value in space_complexities.items():
            if key in action.upper():
                return value
        return 'O(1)'
    
    def wrap_text(self, text, max_length):
        """Wrap text to fit in panels"""
        if len(text) <= max_length:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def get_colors(self, highlighted):
        """Enhanced color scheme"""
        colors = []
        for h in highlighted:
            if h == 0:
                colors.append(self.colors['normal'])
            elif h == 1:
                colors.append(self.colors['compare'])
            elif h == 2:
                colors.append(self.colors['found'])
            elif h == 3:
                colors.append(self.colors['pivot'])
            else:
                colors.append(self.colors['special'])
        return colors
    
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        # Convert hex colors to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        interpolated = tuple(
            rgb1[i] + (rgb2[i] - rgb1[i]) * factor
            for i in range(3)
        )
        
        return rgb_to_hex(interpolated)
    
    def smooth_transition(self, current_data, current_highlighted, previous_data, previous_highlighted, frame):
        """Create smooth transition between states (optimized for speed)"""
        # Skip transitions for ultra-fast speeds
        if self.speed >= 8.0:
            return current_data, current_highlighted
        
        if previous_data is None or previous_highlighted is None:
            return current_data, current_highlighted
        
        # Normalize frame to 0-1 range
        progress = frame / self.animation_frames
        
        # Skip interpolation for very fast speeds
        if self.speed >= 5.0 and progress > 0.5:
            return current_data, current_highlighted
        
        # Interpolate data values (simplified for speed)
        if len(current_data) == len(previous_data):
            interpolated_data = []
            for i in range(len(current_data)):
                value = previous_data[i] + (current_data[i] - previous_data[i]) * progress
                interpolated_data.append(value)
        else:
            interpolated_data = current_data
        
        # Interpolate highlight colors (simplified)
        interpolated_highlighted = []
        if len(current_highlighted) == len(previous_highlighted):
            for i in range(len(current_highlighted)):
                # Simple interpolation for highlights (0 or 1)
                if previous_highlighted[i] != current_highlighted[i]:
                    # Transitioning between states
                    interpolated_highlighted.append(1 if progress > 0.5 else previous_highlighted[i])
                else:
                    interpolated_highlighted.append(current_highlighted[i])
        else:
            interpolated_highlighted = current_highlighted
        
        return interpolated_data, interpolated_highlighted
    
    def visualize_array(self, step):
        """Professional array visualization with enhanced effects"""
        self.ax_main.clear()
        self.ax_main.set_facecolor(self.colors['plot_bg'])
        
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, '📊 No data to display', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=24, color=self.colors['text'],
                        fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', 
                        facecolor=self.colors['panel_bg'], alpha=0.8))
            return
        
        # Apply smooth transition if animating
        if self.current_frame < self.animation_frames and self.previous_data is not None:
            data, highlighted = self.smooth_transition(
                data, highlighted, self.previous_data, self.previous_highlighted, self.current_frame
            )
        
        colors = self.get_colors(highlighted)
        
        # Create professional bar chart with enhanced styling
        x_positions = np.arange(len(data))
        bars = self.ax_main.bar(x_positions, data, color=colors, alpha=0.9, 
                               edgecolor='white', linewidth=2.5, 
                               capsize=5, capstyle='round')
        
        # Add professional value labels with enhanced styling
        max_value = max(data) if data else 1
        for i, (bar, value) in enumerate(zip(bars, data)):
            height = bar.get_height()
            if highlighted[i] > 0:
                # Highlighted elements with glow effect
                self.ax_main.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.05,
                            f'{value}', ha='center', va='bottom', fontsize=14, 
                            fontweight='bold', color='white',
                            bbox=dict(boxstyle='round,pad=0.4', facecolor=colors[i], 
                                    alpha=0.9, edgecolor=self.colors['highlight'], linewidth=3),
                            path_effects=[path_effects.withStroke(linewidth=3, foreground='black')])
            else:
                # Normal elements
                self.ax_main.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.02,
                            f'{value}', ha='center', va='bottom', fontsize=12, 
                            color='white', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='black', 
                                    alpha=0.7, edgecolor=colors[i], linewidth=1))
        
        # Enhanced index labels
        self.ax_main.set_xticks(x_positions)
        self.ax_main.set_xticklabels([f'[{i}]' for i in range(len(data))], 
                                     color=self.colors['text'], fontsize=12, fontweight='bold')
        
        # Professional pointer visualization for binary search
        pointers = step.get('pointers', [-1] * 10)
        pointer_colors = ['cyan', 'yellow', 'magenta', 'orange', 'pink']
        pointer_labels = ['Left', 'Right', 'Mid', 'Pivot', 'Current']
        
        for i, (ptr, color, label) in enumerate(zip(pointers[:5], pointer_colors, pointer_labels)):
            if ptr != -1 and ptr < len(data):
                self.ax_main.axvline(x=ptr, color=color, linestyle='--', 
                                   alpha=0.9, linewidth=3, label=label)
                # Add pointer label
                self.ax_main.text(ptr, max_value * 0.9, label, ha='center', va='bottom',
                                fontsize=10, color=color, fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.2', facecolor='black', 
                                        alpha=0.8, edgecolor=color, linewidth=1))
        
        if any(p != -1 for p in pointers[:3]):
            self.ax_main.legend(loc='upper right', fontsize=11, framealpha=0.9,
                              facecolor=self.colors['panel_bg'], edgecolor=self.colors['accent'])
        
        # Professional title and labels
        self.ax_main.set_title(step["description"], fontsize=16, color=self.colors['highlight'], 
                              pad=20, fontweight='bold',
                              bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['panel_bg'], 
                                      alpha=0.8, edgecolor=self.colors['accent'], linewidth=2))
        self.ax_main.set_ylabel('Values', color=self.colors['text'], fontsize=14, fontweight='bold')
        self.ax_main.set_xlabel('Array Index', color=self.colors['text'], fontsize=14, fontweight='bold')
        
        # Enhanced grid and styling
        self.ax_main.tick_params(colors=self.colors['text'], labelsize=12)
        self.ax_main.grid(True, alpha=0.3, linestyle='-', color=self.colors['border'], linewidth=1)
        
        # Set professional limits
        self.ax_main.set_ylim(0, max_value * 1.2)
        self.ax_main.set_xlim(-0.5, len(data) - 0.5)
        
        # Add subtle border
        for spine in self.ax_main.spines.values():
            spine.set_edgecolor(self.colors['accent'])
            spine.set_linewidth(2)
    
    def visualize_stack(self, step):
        """Enhanced stack visualization"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Stack Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Create vertical stack
        y_positions = range(len(data))
        bars = self.ax_main.barh(y_positions, [1] * len(data), color=colors, alpha=0.85, 
                           edgecolor='white', linewidth=2)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, data)):
            self.ax_main.text(0.5, i, f'{value}', ha='center', va='center', 
                        fontsize=14, fontweight='bold', color='white',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.3))
        
        # TOP pointer
        if data:
            self.ax_main.annotate('TOP', xy=(1.15, len(data) - 1), xytext=(1.6, len(data) - 1),
                           arrowprops=dict(arrowstyle='->', color='red', lw=3,
                                         connectionstyle='arc3,rad=0.3'),
                           fontsize=14, color='red', fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', 
                                   alpha=0.8, edgecolor='red', linewidth=2))
        
        self.ax_main.set_xlim(0, 2.5)
        self.ax_main.set_ylim(-0.5, len(data) + 0.5)
        self.ax_main.set_yticks(range(len(data)))
        self.ax_main.set_yticklabels([f'[{i}]' for i in range(len(data))], 
                                     color=self.colors['text'])
        self.ax_main.set_xticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_ylabel('Stack Positions', color=self.colors['text'])
    
    def visualize_queue(self, step):
        """Enhanced queue visualization"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Queue Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Create horizontal queue
        bars = self.ax_main.bar(range(len(data)), [1] * len(data), color=colors, 
                               alpha=0.85, edgecolor='white', linewidth=2)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, data)):
            self.ax_main.text(i, 0.5, f'{value}', ha='center', va='center',
                        fontsize=14, fontweight='bold', color='white',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.3))
        
        # FRONT and REAR pointers
        if data:
            self.ax_main.annotate('FRONT', xy=(0, 1.25), xytext=(0, 1.6),
                           arrowprops=dict(arrowstyle='->', color='red', lw=3),
                           fontsize=13, color='red', fontweight='bold', ha='center',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', 
                                   alpha=0.8, edgecolor='red', linewidth=2))
            
            self.ax_main.annotate('REAR', xy=(len(data) - 1, 1.25), xytext=(len(data) - 1, 1.6),
                           arrowprops=dict(arrowstyle='->', color='green', lw=3),
                           fontsize=13, color='green', fontweight='bold', ha='center',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', 
                                   alpha=0.8, edgecolor='green', linewidth=2))
        
        self.ax_main.set_xlim(-0.5, len(data) + 0.5)
        self.ax_main.set_ylim(0, 2.2)
        self.ax_main.set_xticks(range(len(data)))
        self.ax_main.set_xticklabels([f'[{i}]' for i in range(len(data))], 
                                     color=self.colors['text'])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_xlabel('Queue Positions', color=self.colors['text'])
    
    def visualize_linked_list(self, step):
        """Enhanced linked list visualization"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'List Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Enhanced node visualization
        node_width = 0.7
        node_height = 0.35
        y_center = 0.5
        
        for i, (value, color) in enumerate(zip(data, colors)):
            x_center = i * 1.3
            
            # Draw fancy node box
            fancy_box = FancyBboxPatch((x_center - node_width/2, y_center - node_height/2),
                                      node_width, node_height, 
                                      boxstyle="round,pad=0.05", 
                                      facecolor=color, edgecolor='white', 
                                      linewidth=2.5, alpha=0.9)
            self.ax_main.add_patch(fancy_box)
            
            # Add value text with shadow effect
            self.ax_main.text(x_center + 0.02, y_center - 0.02, f'{value}', 
                            ha='center', va='center',
                            fontsize=13, fontweight='bold', color='gray', alpha=0.5)
            self.ax_main.text(x_center, y_center, f'{value}', ha='center', va='center',
                            fontsize=13, fontweight='bold', color='white')
            
            # Draw fancy arrow to next node
            if i < len(data) - 1:
                arrow_start_x = x_center + node_width/2
                arrow_end_x = (i + 1) * 1.3 - node_width/2
                
                arrow = FancyArrowPatch((arrow_start_x, y_center), 
                                       (arrow_end_x, y_center),
                                       arrowstyle='->,head_width=0.4,head_length=0.4',
                                       color='cyan', lw=2.5, alpha=0.8,
                                       connectionstyle='arc3,rad=0.1')
                self.ax_main.add_patch(arrow)
        
        # Enhanced NULL pointer
        if data:
            last_x = (len(data) - 1) * 1.3 + node_width/2 + 0.2
            self.ax_main.text(last_x, y_center, 'NULL', ha='left', va='center',
                        fontsize=11, color='red', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', 
                                alpha=0.7, edgecolor='red', linewidth=2))
        
        # Enhanced HEAD pointer
        if data:
            self.ax_main.annotate('HEAD', xy=(-node_width/2 - 0.1, y_center), 
                           xytext=(-1.0, y_center + 0.4),
                           arrowprops=dict(arrowstyle='->', color='red', lw=3,
                                         connectionstyle='arc3,rad=0.3'),
                           fontsize=13, color='red', fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', 
                                   alpha=0.9, edgecolor='red', linewidth=2))
        
        self.ax_main.set_xlim(-1.5, len(data) * 1.3 + 0.8)
        self.ax_main.set_ylim(0.1, 0.9)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
    
    def visualize_binary_search_tree(self, step):
        """Enhanced BST visualization with proper tree structure"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'BST Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Build actual BST structure
        bst_root = self.build_bst_from_array(data)
        if not bst_root:
            return
        
        # Calculate proper tree positions
        positions = {}
        self.calculate_tree_layout(bst_root, positions)
        
        # Draw tree connections (parent-child relationships)
        self.draw_bst_connections(bst_root, positions)
        
        # Draw nodes
        for i, (value, color) in enumerate(zip(data, colors)):
            if value in positions:
                x, y = positions[value]
                
                # Draw fancy node circle with glow effect
                if highlighted[i] > 0:
                    # Outer glow
                    outer_circle = Circle((x, y), 0.5, facecolor=color, 
                                         edgecolor='yellow', linewidth=3, alpha=0.4)
                    self.ax_main.add_patch(outer_circle)
                
                # Main circle
                circle = Circle((x, y), 0.4, facecolor=color, edgecolor='white', 
                              linewidth=2.5, alpha=0.9)
                self.ax_main.add_patch(circle)
                
                # Add value with shadow
                self.ax_main.text(x + 0.02, y - 0.02, f'{value}', ha='center', va='center',
                            fontsize=11, fontweight='bold', color='gray', alpha=0.5)
                self.ax_main.text(x, y, f'{value}', ha='center', va='center',
                            fontsize=11, fontweight='bold', color='white')
        
        # Set limits with better margins
        if positions:
            x_coords = [pos[0] for pos in positions.values()]
            y_coords = [pos[1] for pos in positions.values()]
            if x_coords and y_coords:
                x_margin = max(1.5, (max(x_coords) - min(x_coords)) * 0.15)
                y_margin = max(1.0, (max(y_coords) - min(y_coords)) * 0.15)
                
                self.ax_main.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
                self.ax_main.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
    
    def draw_bst_connections(self, root, positions):
        """Draw parent-child connections in BST"""
        if root is None:
            return
        
        root_x, root_y = positions[root['value']]
        
        # Draw connection to left child
        if root['left'] is not None and root['left']['value'] in positions:
            left_x, left_y = positions[root['left']['value']]
            arrow = FancyArrowPatch((root_x, root_y - 0.35), (left_x, left_y + 0.35),
                                  arrowstyle='-', color='cyan', lw=2, alpha=0.7,
                                  connectionstyle='arc3,rad=0.1')
            self.ax_main.add_patch(arrow)
            self.draw_bst_connections(root['left'], positions)
        
        # Draw connection to right child
        if root['right'] is not None and root['right']['value'] in positions:
            right_x, right_y = positions[root['right']['value']]
            arrow = FancyArrowPatch((root_x, root_y - 0.35), (right_x, right_y + 0.35),
                                  arrowstyle='-', color='cyan', lw=2, alpha=0.7,
                                  connectionstyle='arc3,rad=-0.1')
            self.ax_main.add_patch(arrow)
            self.draw_bst_connections(root['right'], positions)
    
    def calculate_bst_positions_enhanced(self, data):
        """Proper BST layout algorithm using Reingold-Tilford approach"""
        if not data:
            return []
        
        # Create a proper BST structure from the data
        bst_nodes = self.build_bst_from_array(data)
        if not bst_nodes:
            return []
        
        # Calculate positions using proper tree layout
        positions = {}
        self.calculate_tree_layout(bst_nodes, positions)
        
        # Convert to list format expected by visualization
        result_positions = []
        for i, value in enumerate(data):
            if value in positions:
                result_positions.append(positions[value])
            else:
                # Fallback for values not in BST
                result_positions.append((i * 2, 0))
        
        return result_positions
    
    def build_bst_from_array(self, data):
        """Build actual BST structure from array data"""
        if not data:
            return None
        
        root = None
        for value in data:
            root = self.insert_into_bst(root, value)
        return root
    
    def insert_into_bst(self, root, value):
        """Insert value into BST and return new root"""
        if root is None:
            return {'value': value, 'left': None, 'right': None}
        
        if value < root['value']:
            root['left'] = self.insert_into_bst(root['left'], value)
        elif value > root['value']:
            root['right'] = self.insert_into_bst(root['right'], value)
        
        return root
    
    def calculate_tree_layout(self, root, positions, x_offset=0, y_offset=0, level=0):
        """Calculate proper tree layout using modified Reingold-Tilford algorithm"""
        if root is None:
            return x_offset
        
        # Recursively layout left and right subtrees
        left_x = self.calculate_tree_layout(root['left'], positions, x_offset, y_offset + 1, level + 1)
        current_x = left_x + 2  # Add spacing
        right_x = self.calculate_tree_layout(root['right'], positions, current_x + 2, y_offset + 1, level + 1)
        
        # Position current node
        positions[root['value']] = (current_x, -level)  # Negative for top-down display
        
        return right_x
    
    def update_visualization(self):
        """Update all visualization components"""
        if not self.steps:
            return
        
        step = self.steps[self.current_step]
        
        # Update info panel (simple by default)
        self.update_simple_info(step)
        
        # Show details only if enabled
        if self.show_details:
            # Create detailed panels on demand
            self.show_detailed_view(step)
        
        # Choose visualization based on structure type
        if self.config.get('is_stack', False):
            self.visualize_stack(step)
        elif self.config.get('is_queue', False):
            self.visualize_queue(step)
        elif self.config.get('is_linked_list', False):
            self.visualize_linked_list(step)
        elif self.config.get('is_binary_search_tree', False):
            self.visualize_binary_search_tree(step)
        else:  # Default to array visualization
            self.visualize_array(step)
        
        plt.draw()
    
    def animate(self, frame):
        """Optimized animation function with faster transitions"""
        import time
        
        # Throttle updates for better performance
        current_time = time.time()
        if current_time - self.last_update_time < 0.016:  # ~60fps max
            return []
        self.last_update_time = current_time
        
        # Reduced transition frames for faster animation
        if self.current_frame < self.animation_frames and self.previous_data is not None:
            self.current_frame += 1
            self.update_visualization()
            return []
        
        # Move to next step
        if self.is_playing and self.current_step < len(self.steps) - 1:
            # Store current data for smooth transition (only if needed)
            if self.current_step < len(self.steps) and self.speed < 5.0:  # Skip transitions for very fast speeds
                current_step_data = self.steps[self.current_step]
                self.previous_data = current_step_data['data'].copy()
                self.previous_highlighted = current_step_data.get('highlighted', [0] * len(current_step_data['data'])).copy()
            else:
                self.previous_data = None  # Skip transitions for ultra-fast speeds
            
            self.current_step += 1
            self.current_frame = 0  # Reset frame counter for new step
            self.update_visualization()
        elif self.current_step >= len(self.steps) - 1:
            self.is_playing = False
            self.btn_play.label.set_text('Restart')
        return []
    
    def toggle_play(self, event):
        if self.current_step >= len(self.steps) - 1:
            # Restart from beginning
            self.current_step = 0
            self.is_playing = True
            self.btn_play.label.set_text('Pause')
        else:
            self.is_playing = not self.is_playing
            self.btn_play.label.set_text('Pause' if self.is_playing else 'Play')
        print(f"Animation {'playing' if self.is_playing else 'paused'}")
    
    def reset_animation(self, event):
        self.current_step = 0
        self.current_frame = 0
        self.is_playing = False
        self.previous_data = None
        self.previous_highlighted = None
        self.btn_play.label.set_text('Play')
        self.update_visualization()
        print("Animation reset to beginning")
    
    def step_back(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.current_frame = 0
            self.is_playing = False
            self.previous_data = None
            self.previous_highlighted = None
            self.btn_play.label.set_text('Play')
            self.update_visualization()
        print(f"Step back to {self.current_step + 1}")
    
    def step_forward(self, event):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.current_frame = 0
            self.is_playing = False
            self.previous_data = None
            self.previous_highlighted = None
            self.btn_play.label.set_text('Play')
            self.update_visualization()
        print(f"Step forward to {self.current_step + 1}")
    
    def update_speed(self, val):
        """Update animation speed with real-time adjustment"""
        self.speed = val
        
        # Update animation interval in real-time (much faster)
        if hasattr(self, 'ani') and self.ani is not None:
            # Calculate new interval (lower interval = faster animation)
            new_interval = max(8, int(1000 / (self.speed * 2)))  # Much faster: minimum 8ms (120fps)
            self.ani.event_source.interval = new_interval
            
            # Update the slider display text color based on speed
            if self.speed >= 8.0:
                self.slider_speed.valtext.set_color('#ff1744')  # Ultra fast
            elif self.speed >= 5.0:
                self.slider_speed.valtext.set_color('#ff6b6b')  # Very fast
            elif self.speed >= 2.0:
                self.slider_speed.valtext.set_color('#ffd93d')  # Fast
            else:
                self.slider_speed.valtext.set_color('#6bcf7f')  # Normal
            
            # Force redraw of the slider
            self.fig.canvas.draw_idle()
        
        print(f"⚡ Speed updated to {self.speed:.1f}x (interval: {1000/self.speed:.0f}ms)")
    
    def set_speed_preset(self, speed):
        """Set speed using preset buttons"""
        self.slider_speed.set_val(speed)
        self.update_speed(speed)
        print(f"🎯 Speed preset applied: {speed:.1f}x")
    
    def get_speed_icon(self, speed):
        """Get appropriate icon based on speed"""
        if speed >= 8.0:
            return '💨'  # Ultra fast
        elif speed >= 5.0:
            return '🚀'  # Very fast
        elif speed >= 2.0:
            return '⚡'  # Fast
        else:
            return '▶️'  # Normal
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts for speed control"""
        if event.key == '1':
            self.set_speed_preset(1.0)  # Normal
        elif event.key == '2':
            self.set_speed_preset(2.0)  # Fast
        elif event.key == '3':
            self.set_speed_preset(5.0)  # Very Fast
        elif event.key == '4':
            self.set_speed_preset(10.0)  # Ultra Fast
        elif event.key == '+':
            # Increase speed by 1x
            new_speed = min(10.0, self.speed + 1.0)
            self.slider_speed.set_val(new_speed)
            self.update_speed(new_speed)
        elif event.key == '-':
            # Decrease speed by 1x
            new_speed = max(0.5, self.speed - 1.0)
            self.slider_speed.set_val(new_speed)
            self.update_speed(new_speed)
        elif event.key == ' ':
            # Spacebar to toggle play/pause
            self.toggle_play(event)
    
    def toggle_details(self, event):
        """Toggle between simple and detailed view"""
        self.show_details = not self.show_details
        
        if self.show_details:
            self.btn_details.label.set_text('📊 SIMPLE')
            self.btn_details.color = '#f44336'
        else:
            self.btn_details.label.set_text('📊 DETAILS')
            self.btn_details.color = '#9C27B0'
        
        # Update the visualization to show/hide details
        self.update_visualization()
        print(f"Details view {'enabled' if self.show_details else 'disabled'}")
    
    def show_detailed_view(self, step):
        """Show detailed information overlay on main visualization"""
        # Count operations
        current_comparisons = sum(1 for i in range(self.current_step + 1) 
                                if 'COMPARE' in self.steps[i].get('action', ''))
        current_swaps = sum(1 for i in range(self.current_step + 1) 
                          if 'SWAP' in self.steps[i].get('action', ''))
        
        # Show detailed info as overlay on main visualization
        self.ax_main.text(0.02, 0.98, '📊 DETAILED VIEW', 
                         transform=self.ax_main.transAxes, fontsize=12, 
                         color=self.colors['highlight'], fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['accent'], 
                                 alpha=0.2, edgecolor=self.colors['accent'], linewidth=2))
        
        # Performance metrics
        metrics_text = f"🔍 Comparisons: {current_comparisons} | 🔄 Swaps: {current_swaps}"
        self.ax_main.text(0.02, 0.92, metrics_text, 
                         transform=self.ax_main.transAxes, fontsize=10, 
                         color=self.colors['text'], fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.2', facecolor=self.colors['panel_bg'], 
                                 alpha=0.8))
        
        # Current action
        action = step.get('action', 'Unknown').replace('_', ' ').title()
        self.ax_main.text(0.02, 0.86, f"🎯 Action: {action}", 
                         transform=self.ax_main.transAxes, fontsize=10, 
                         color=self.colors['text'], fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.2', facecolor=self.colors['panel_bg'], 
                                 alpha=0.8))
        
        # Pseudocode
        code = self.get_pseudocode(step.get('action', ''))
        self.ax_main.text(0.02, 0.78, f"💻 Code:\n{code}", 
                         transform=self.ax_main.transAxes, fontsize=9, 
                         color=self.colors['accent'], fontfamily='monospace',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a0a', 
                                 alpha=0.9, edgecolor=self.colors['accent'], linewidth=1))

def main():
    print("=" * 60)
    print("Starting Enhanced Algorithm Visualizer v5.1...")
    print("=" * 60)
    print("🚀 SPEED OPTIMIZATIONS:")
    print("• 2x faster default speed (2.0x)")
    print("• Ultra-fast mode up to 10x speed")
    print("• 120fps animation (8ms intervals)")
    print("• Speed presets: ▶️⚡🚀💨 (1x, 2x, 5x, 10x)")
    print("• Keyboard shortcuts (1-4, +/-)")
    print("• Optimized rendering with blitting")
    print("• Reduced transition frames")
    print("=" * 60)
    print("New Features in v5.1:")
    print("• Enhanced Input Validation")
    print("• Memory Leak Fixes") 
    print("• Better Error Messages")
    print("• Improved BST Layout Algorithm")
    print("• Smooth Animations & Transitions")
    print("• Algorithm Comparison Mode")
    print("=" * 60)
    
    if not os.path.exists('algorithm_steps.json'):
        print("Error: algorithm_steps.json not found!")
        print("Please run the C program first to generate visualization data.")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists('algorithm_config.json'):
        print("Error: algorithm_config.json not found!")
        print("Please run the C program first to generate configuration.")
        input("Press Enter to exit...")
        return
    
    try:
        visualizer = AlgorithmVisualizer()
    except KeyboardInterrupt:
        print("\nVisualization interrupted by user")
    except Exception as e:
        print(f"Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
    