import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider, RadioButtons, CheckButtons
import numpy as np
import sys
import os
import time
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

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
        
        # 🚀 SMART INPUT SYSTEM - New variables
        self.input_mode = 'manual'
        self.test_cases = {
            'sorted': 'Sorted Array',
            'reverse': 'Reverse Sorted', 
            'random': 'Random Array',
            'nearly_sorted': 'Nearly Sorted',
            'all_equal': 'All Equal Elements',
            'few_unique': 'Few Unique Elements'
        }
        
        # 🎯 ALGORITHM BATTLE MODE - New variables
        self.battle_mode = False
        self.battle_algorithms = []
        self.battle_steps = []
        self.current_battle_step = 0
        
        # 📊 LIVE ANALYTICS DASHBOARD - New variables
        self.performance_metrics = {
            'comparisons': 0,
            'swaps': 0,
            'accesses': 0,
            'start_time': time.time(),
            'efficiency_score': 0
        }
        
        # 🎮 INTERACTIVE LEARNING MODE - New variables
        self.learning_mode = False
        self.current_explanation = ""
        self.quiz_mode = False
        self.quiz_question = ""
        self.quiz_options = []
        self.quiz_answer = 0
        
        # Load data
        self.load_data()
        
        # Setup theme
        self.setup_theme()
        
        # Get screen size and set window size
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            
            fig_width = min(20, screen_width * 0.9 / 100)
            fig_height = min(12, screen_height * 0.9 / 100)
        except:
            fig_width, fig_height = 18, 11
        
        # Create figure with subplots
        self.fig = plt.figure(figsize=(fig_width, fig_height))
        self.fig.patch.set_facecolor(self.colors['bg'])
        
        # Main visualization area (left side, larger)
        self.ax_main = plt.subplot2grid((8, 8), (0, 0), colspan=5, rowspan=4)
        self.ax_main.set_facecolor(self.colors['plot_bg'])
        
        # Side info chart (right top)
        self.ax_side = plt.subplot2grid((8, 8), (0, 5), colspan=3, rowspan=2)
        self.ax_side.set_facecolor(self.colors['panel_bg'])
        
        # 📊 LIVE ANALYTICS DASHBOARD (right middle)
        self.ax_stats = plt.subplot2grid((8, 8), (2, 5), colspan=3, rowspan=2)
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        # 🎮 INTERACTIVE LEARNING MODE area
        self.ax_learn = plt.subplot2grid((8, 8), (4, 0), colspan=8, rowspan=2)
        self.ax_learn.set_facecolor(self.colors['learn_bg'])
        
        # Code display area (bottom)
        self.ax_code = plt.subplot2grid((8, 8), (6, 0), colspan=5, rowspan=1)
        self.ax_code.set_facecolor(self.colors['code_bg'])
        
        # Control area at very bottom
        self.ax_controls = plt.subplot2grid((8, 8), (7, 0), colspan=8)
        self.ax_controls.set_facecolor(self.colors['bg'])
        self.ax_controls.axis('off')
        
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
        
        # Auto-start animation
        self.is_playing = True
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=1000/self.speed, 
            repeat=True, blit=False
        )
        
        plt.show()
    
    def setup_theme(self):
        """Setup color themes with enhanced colors for new features"""
        themes = {
            'dark': {
                'bg': '#1a1a1a',
                'plot_bg': '#2a2a2a',
                'panel_bg': '#1e1e1e',
                'code_bg': '#0d0d0d',
                'learn_bg': '#1a2a3a',
                'text': 'white',
                'accent': '#4CAF50',
                'highlight': '#FFD700',
                'normal': '#3f51b5',
                'compare': '#f44336',
                'found': '#4caf50',
                'pivot': '#ff9800',
                'special': '#9c27b0',
                'battle_1': '#FF6B6B',
                'battle_2': '#4ECDC4',
                'battle_3': '#45B7D1',
                'quiz_correct': '#4CAF50',
                'quiz_wrong': '#f44336'
            }
        }
        self.colors = themes.get(self.theme, themes['dark'])
        plt.style.use('dark_background')
    
    def load_data(self):
        """Enhanced data loading with battle mode support"""
        try:
            with open('algorithm_steps.json', 'r') as f:
                data = json.load(f)
                self.steps = data['steps']
            
            with open('algorithm_config.json', 'r') as f:
                self.config = json.load(f)
                
            print(f"✓ Loaded {len(self.steps)} visualization steps")
            print(f"✓ Structure: {self.config.get('structure_type', 'unknown')}")
            print(f"✓ Operation: {self.config.get('operation', 'unknown')}")
            
            # 🚀 SMART INPUT SYSTEM - Analyze input pattern
            self.analyze_input_pattern()
            
        except FileNotFoundError as e:
            print(f"✗ Error: Could not find required files - {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON format - {e}")
            sys.exit(1)
    
    def analyze_input_pattern(self):
        """🚀 SMART INPUT SYSTEM - Analyze input data pattern"""
        if not self.steps:
            return
            
        first_step_data = self.steps[0]['data']
        if not first_step_data:
            return
            
        # Analyze data characteristics
        sorted_asc = all(first_step_data[i] <= first_step_data[i+1] for i in range(len(first_step_data)-1))
        sorted_desc = all(first_step_data[i] >= first_step_data[i+1] for i in range(len(first_step_data)-1))
        all_equal = len(set(first_step_data)) == 1
        few_unique = len(set(first_step_data)) <= len(first_step_data) // 2
        
        # Determine input pattern
        if all_equal:
            self.input_mode = 'all_equal'
        elif sorted_asc:
            self.input_mode = 'sorted'
        elif sorted_desc:
            self.input_mode = 'reverse'
        elif few_unique:
            self.input_mode = 'few_unique'
        else:
            # Check if nearly sorted
            inversions = 0
            for i in range(len(first_step_data)):
                for j in range(i+1, len(first_step_data)):
                    if first_step_data[i] > first_step_data[j]:
                        inversions += 1
            if inversions <= len(first_step_data):
                self.input_mode = 'nearly_sorted'
            else:
                self.input_mode = 'random'
        
        print(f"✓ Input Pattern Detected: {self.test_cases.get(self.input_mode, 'Unknown')}")
    
    def calculate_statistics(self):
        """Enhanced statistics with performance metrics"""
        self.comparisons = 0
        self.swaps = 0
        self.performance_metrics['comparisons'] = 0
        self.performance_metrics['swaps'] = 0
        self.performance_metrics['accesses'] = 0
        
        for step in self.steps:
            action = step.get('action', '')
            if 'COMPARE' in action or 'SEARCH' in action:
                self.comparisons += 1
                self.performance_metrics['comparisons'] += 1
            if 'SWAP' in action:
                self.swaps += 1
                self.performance_metrics['swaps'] += 1
            self.performance_metrics['accesses'] += 1
        
        # Calculate efficiency score
        total_steps = len(self.steps)
        if total_steps > 0:
            optimal_steps = len(self.steps[0]['data']) * np.log2(max(2, len(self.steps[0]['data'])))
            self.performance_metrics['efficiency_score'] = max(0, min(100, (1 - (total_steps / (optimal_steps * 10))) * 100))
    
    def setup_ui(self):
        """Enhanced UI with new feature controls"""
        plt.subplots_adjust(bottom=0.08, top=0.94, left=0.04, right=0.98, hspace=0.5, wspace=0.4)
        
        # Control buttons
        button_width = 0.06
        button_height = 0.03
        button_y = 0.02
        spacing = 0.07
        
        # Play/Pause
        self.ax_play = plt.axes([0.02, button_y, button_width, button_height])
        self.btn_play = Button(self.ax_play, 'Play', color=self.colors['accent'], 
                              hovercolor=self.colors['highlight'])
        self.btn_play.label.set_color(self.colors['text'])
        self.btn_play.on_clicked(self.toggle_play)
        
        # Reset
        self.ax_reset = plt.axes([0.02 + spacing, button_y, button_width, button_height])
        self.btn_reset = Button(self.ax_reset, 'Reset', color='#f44336', hovercolor='#d32f2f')
        self.btn_reset.label.set_color('white')
        self.btn_reset.on_clicked(self.reset_animation)
        
        # Step Back
        self.ax_step_back = plt.axes([0.02 + spacing*2, button_y, button_width, button_height])
        self.btn_step_back = Button(self.ax_step_back, 'Back', color='#FF9800', hovercolor='#F57C00')
        self.btn_step_back.label.set_color('white')
        self.btn_step_back.on_clicked(self.step_back)
        
        # Step Forward
        self.ax_step_forward = plt.axes([0.02 + spacing*3, button_y, button_width, button_height])
        self.btn_step_forward = Button(self.ax_step_forward, 'Next', color='#2196F3', hovercolor='#1976D2')
        self.btn_step_forward.label.set_color('white')
        self.btn_step_forward.on_clicked(self.step_forward)
        
        # 🎮 INTERACTIVE LEARNING MODE toggle
        self.ax_learn_btn = plt.axes([0.02 + spacing*4, button_y, button_width*1.5, button_height])
        self.btn_learn = Button(self.ax_learn_btn, 'Learn Mode', color='#9C27B0', hovercolor='#7B1FA2')
        self.btn_learn.label.set_color('white')
        self.btn_learn.on_clicked(self.toggle_learning_mode)
        
        # Speed slider
        self.ax_speed = plt.axes([0.4, button_y + 0.01, 0.2, 0.02])
        self.slider_speed = Slider(self.ax_speed, 'Speed', 0.5, 4.0, valinit=1.0, 
                                  facecolor=self.colors['accent'], valfmt='%.1fx')
        self.slider_speed.label.set_color(self.colors['text'])
        self.slider_speed.valtext.set_color(self.colors['text'])
        self.slider_speed.on_changed(self.update_speed)
        
        # Title
        structure_name = self.config.get("structure_type", "").replace("_", " ").title()
        operation_name = self.config.get("operation", "").replace("_", " ").title()
        
        # 🚀 SMART INPUT SYSTEM - Show input pattern in title
        input_pattern = self.test_cases.get(self.input_mode, 'Custom')
        title = f'{structure_name} - {operation_name} | Input: {input_pattern}'
        
        self.fig.suptitle(title, fontsize=16, color=self.colors['highlight'], y=0.97, fontweight='bold')
    
    def update_side_chart(self, step):
        """Enhanced side chart with input pattern info"""
        self.ax_side.clear()
        self.ax_side.set_facecolor(self.colors['panel_bg'])
        
        complexity = step.get('complexity', 'N/A')
        action = step.get('action', 'Unknown')
        
        time_complexity = complexity
        space_complexity = self.get_space_complexity(action)
        
        # Title
        self.ax_side.text(0.5, 0.95, 'Algorithm Info', ha='center', va='top', 
                         fontsize=13, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        
        # 🚀 SMART INPUT SYSTEM - Show input pattern
        input_pattern = self.test_cases.get(self.input_mode, 'Custom')
        self.ax_side.text(0.5, 0.88, f'Input: {input_pattern}', ha='center', va='top',
                         fontsize=9, color='cyan', transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.2', facecolor=self.colors['plot_bg'], 
                                 edgecolor=self.colors['accent'], linewidth=1))
        
        # Current step with progress
        progress_pct = int((self.current_step + 1) / len(self.steps) * 100)
        step_info = f"Step {self.current_step + 1} / {len(self.steps)} ({progress_pct}%)"
        self.ax_side.text(0.5, 0.80, step_info, ha='center', va='top',
                         fontsize=10, color='cyan', transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['plot_bg'], 
                                 edgecolor=self.colors['accent'], linewidth=2))
        
        # Time Complexity
        self.ax_side.text(0.05, 0.70, 'Time:', ha='left', va='top',
                         fontsize=10, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        self.ax_side.text(0.05, 0.63, time_complexity, ha='left', va='top',
                         fontsize=11, color=self.colors['text'], transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#4CAF50', alpha=0.8))
        
        # Space Complexity
        self.ax_side.text(0.05, 0.53, 'Space:', ha='left', va='top',
                         fontsize=10, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        self.ax_side.text(0.05, 0.46, space_complexity, ha='left', va='top',
                         fontsize=11, color=self.colors['text'], transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#2196F3', alpha=0.8))
        
        # Current Action
        self.ax_side.text(0.05, 0.36, 'Action:', ha='left', va='top',
                         fontsize=10, fontweight='bold', color=self.colors['highlight'], 
                         transform=self.ax_side.transAxes)
        action_wrapped = self.wrap_text(action.replace('_', ' ').title(), 12)
        self.ax_side.text(0.05, 0.29, action_wrapped, ha='left', va='top',
                         fontsize=9, color=self.colors['text'], transform=self.ax_side.transAxes,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FF9800', alpha=0.8))
        
        # Progress bar at bottom
        progress = (self.current_step + 1) / len(self.steps)
        bar_y = 0.08
        bar_height = 0.04
        
        # Background bar
        self.ax_side.barh(bar_y, 1, height=bar_height, color='#333333', alpha=0.5,
                         transform=self.ax_side.transAxes)
        # Progress bar
        self.ax_side.barh(bar_y, progress, height=bar_height, color=self.colors['accent'], 
                         alpha=0.9, transform=self.ax_side.transAxes)
        
        # Remove axes
        self.ax_side.set_xticks([])
        self.ax_side.set_yticks([])
        for spine in self.ax_side.spines.values():
            spine.set_visible(False)
    
    def update_statistics_dashboard(self, step):
        """📊 ENHANCED LIVE ANALYTICS DASHBOARD"""
        self.ax_stats.clear()
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        # Title
        self.ax_stats.text(0.5, 0.95, 'Live Analytics', ha='center', va='top',
                          fontsize=13, fontweight='bold', color=self.colors['highlight'],
                          transform=self.ax_stats.transAxes)
        
        # Count operations up to current step
        current_comparisons = 0
        current_swaps = 0
        current_accesses = 0
        
        for i in range(self.current_step + 1):
            action = self.steps[i].get('action', '')
            if 'COMPARE' in action or 'SEARCH' in action:
                current_comparisons += 1
            if 'SWAP' in action:
                current_swaps += 1
            current_accesses += 1
        
        # Update performance metrics
        self.performance_metrics['comparisons'] = current_comparisons
        self.performance_metrics['swaps'] = current_swaps
        self.performance_metrics['accesses'] = current_accesses
        
        # Calculate real-time efficiency
        elapsed_time = time.time() - self.performance_metrics['start_time']
        if elapsed_time > 0:
            steps_per_second = (self.current_step + 1) / elapsed_time
        
        # Display enhanced statistics
        y_pos = 0.75
        spacing = 0.15
        
        # Comparisons with visual indicator
        self.ax_stats.text(0.1, y_pos, f'Comparisons:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'], 
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_comparisons}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#FFD700',
                          transform=self.ax_stats.transAxes)
        
        # Swaps
        y_pos -= spacing
        self.ax_stats.text(0.1, y_pos, f'Swaps:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_swaps}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#4CAF50',
                          transform=self.ax_stats.transAxes)
        
        # Array Accesses
        y_pos -= spacing
        self.ax_stats.text(0.1, y_pos, f'Accesses:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{current_accesses}', ha='right', va='center',
                          fontsize=11, fontweight='bold', color='#2196F3',
                          transform=self.ax_stats.transAxes)
        
        # Efficiency Score
        y_pos -= spacing
        efficiency = self.performance_metrics['efficiency_score']
        efficiency_color = '#4CAF50' if efficiency > 70 else '#FF9800' if efficiency > 40 else '#f44336'
        
        self.ax_stats.text(0.1, y_pos, f'Efficiency:', ha='left', va='center',
                          fontsize=9, color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        self.ax_stats.text(0.85, y_pos, f'{efficiency:.1f}%', ha='right', va='center',
                          fontsize=11, fontweight='bold', color=efficiency_color,
                          transform=self.ax_stats.transAxes)
        
        # Efficiency meter
        y_pos -= spacing * 0.7
        self.ax_stats.barh(y_pos, efficiency/100, height=0.03, color=efficiency_color, alpha=0.8,
                          transform=self.ax_stats.transAxes)
        
        # Remove axes
        self.ax_stats.set_xticks([])
        self.ax_stats.set_yticks([])
        for spine in self.ax_stats.spines.values():
            spine.set_visible(False)
    
    def update_learning_dashboard(self, step):
        """🎮 INTERACTIVE LEARNING MODE Dashboard"""
        self.ax_learn.clear()
        self.ax_learn.set_facecolor(self.colors['learn_bg'])
        
        if not self.learning_mode:
            self.ax_learn.axis('off')
            return
        
        action = step.get('action', '')
        description = step.get('description', '')
        
        # Title
        self.ax_learn.text(0.02, 0.85, '🤔 Learning Mode - Why This Step?', 
                         ha='left', va='top', fontsize=12, fontweight='bold', 
                         color=self.colors['highlight'], transform=self.ax_learn.transAxes)
        
        # Get explanation for current step
        explanation = self.get_step_explanation(action, description, step)
        self.current_explanation = explanation
        
        # Display explanation with better formatting
        wrapped_explanation = self.wrap_text(explanation, 80)
        self.ax_learn.text(0.02, 0.65, wrapped_explanation, ha='left', va='top',
                         fontsize=10, color=self.colors['text'], transform=self.ax_learn.transAxes,
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#2a3a4a', alpha=0.8))
        
        # Algorithm Insight
        insight = self.get_algorithm_insight(action)
        if insight:
            self.ax_learn.text(0.02, 0.35, '💡 Algorithm Insight:', ha='left', va='top',
                             fontsize=10, fontweight='bold', color='#FFD700',
                             transform=self.ax_learn.transAxes)
            wrapped_insight = self.wrap_text(insight, 70)
            self.ax_learn.text(0.05, 0.25, wrapped_insight, ha='left', va='top',
                             fontsize=9, color='#90CAF9', transform=self.ax_learn.transAxes)
        
        # Performance Tip
        if self.current_step > len(self.steps) * 0.7:  # Show tips near the end
            tip = self.get_performance_tip()
            self.ax_learn.text(0.02, 0.15, '🚀 Performance Tip:', ha='left', va='top',
                             fontsize=10, fontweight='bold', color='#4CAF50',
                             transform=self.ax_learn.transAxes)
            wrapped_tip = self.wrap_text(tip, 70)
            self.ax_learn.text(0.05, 0.05, wrapped_tip, ha='left', va='top',
                             fontsize=9, color='#A5D6A7', transform=self.ax_learn.transAxes)
        
        # Remove axes
        self.ax_learn.set_xticks([])
        self.ax_learn.set_yticks([])
        for spine in self.ax_learn.spines.values():
            spine.set_edgecolor(self.colors['accent'])
            spine.set_linewidth(2)
    
    def get_step_explanation(self, action, description, step):
        """Get educational explanation for current step"""
        explanations = {
            'COMPARE': "The algorithm is comparing two elements to determine their order. This is fundamental to sorting and searching algorithms.",
            'SWAP': "The algorithm is swapping two elements to correct their positions. Swapping is expensive but necessary for rearrangement.",
            'SEARCH': "The algorithm is searching for a specific element. Different search strategies have different time complexities.",
            'PIVOT': "In Quick Sort, the pivot element helps divide the array into smaller subproblems for efficient sorting.",
            'MERGE': "Merge Sort combines two sorted subarrays into one sorted array. This is the 'conquer' step of divide-and-conquer.",
            'DIVIDE': "The algorithm is dividing the problem into smaller subproblems. This is key to efficient algorithms like Merge Sort and Quick Sort.",
            'INSERT': "Inserting an element at the correct position while maintaining order. Common in Insertion Sort and data structure operations.",
            'BUBBLE': "Bubble Sort repeatedly compares adjacent elements and swaps them if they're in the wrong order. Simple but inefficient for large datasets.",
            'SELECTION': "Selection Sort finds the minimum element and places it at the beginning. It maintains two subarrays: sorted and unsorted.",
            'BINARY_SEARCH': "Binary Search efficiently finds elements in sorted arrays by repeatedly dividing the search interval in half.",
            'LINEAR_SEARCH': "Linear Search checks each element sequentially. Simple but slow for large datasets - O(n) time complexity.",
            'PUSH': "Pushing an element onto the stack - adds to the top (LIFO principle).",
            'POP': "Popping an element from the stack - removes from the top (LIFO principle).",
            'ENQUEUE': "Enqueuing an element - adds to the rear of the queue (FIFO principle).",
            'DEQUEUE': "Dequeuing an element - removes from the front of the queue (FIFO principle).",
        }
        
        for key, explanation in explanations.items():
            if key in action:
                return explanation
        
        # Default explanation based on action type
        if 'SORT' in action:
            return "The algorithm is rearranging elements in a specific order (ascending or descending). Different sorting algorithms have different strategies and performance characteristics."
        elif 'SEARCH' in action:
            return "The algorithm is looking for a specific element or condition. Search efficiency depends on data structure and algorithm choice."
        
        return "The algorithm is performing an operation to process the data. Each step brings us closer to the final result!"
    
    def get_algorithm_insight(self, action):
        """Get algorithm-specific insights"""
        insights = {
            'QUICK': "Quick Sort's efficiency depends on pivot selection. Good pivots lead to O(n log n), bad pivots to O(n²).",
            'MERGE': "Merge Sort is stable and always O(n log n), but requires O(n) extra space for merging.",
            'BUBBLE': "Bubble Sort is good for educational purposes but inefficient for real-world use. Best case O(n) when array is sorted.",
            'INSERTION': "Insertion Sort is efficient for small datasets and nearly sorted data. It's adaptive and stable.",
            'SELECTION': "Selection Sort always takes O(n²) time - it doesn't adapt to input order. Good for minimizing swaps.",
            'BINARY_SEARCH': "Binary Search requires sorted data but is extremely efficient - O(log n) vs O(n) for linear search.",
            'LINEAR_SEARCH': "Linear Search works on any data but is slow for large datasets. Useful when data is unsorted.",
            'STACK': "Stack follows LIFO (Last-In-First-Out) principle. Perfect for undo operations, function calls, and depth-first search.",
            'QUEUE': "Queue follows FIFO (First-In-First-Out) principle. Ideal for task scheduling, breadth-first search, and buffering.",
        }
        
        for key, insight in insights.items():
            if key in action:
                return insight
        return ""
    
    def get_performance_tip(self):
        """Get performance optimization tips"""
        tips = [
            "For large datasets, consider O(n log n) algorithms like Quick Sort or Merge Sort.",
            "For nearly sorted data, Insertion Sort can be very efficient.",
            "Binary Search is 100x faster than Linear Search for 1 million elements!",
            "Choosing the right data structure is as important as choosing the right algorithm.",
            "Cache-friendly algorithms (sequential access) often outperform random access patterns.",
            "Stack operations (push/pop) are O(1) time complexity - very efficient!",
            "Queue operations (enqueue/dequeue) are O(1) when implemented properly.",
        ]
        return np.random.choice(tips)
    
    def update_code_display(self, step):
        """Enhanced code display with learning features"""
        self.ax_code.clear()
        self.ax_code.set_facecolor(self.colors['code_bg'])
        
        if not self.show_code:
            self.ax_code.axis('off')
            return
        
        action = step.get('action', '')
        
        # Get pseudocode based on action
        code = self.get_pseudocode(action)
        
        # Title
        self.ax_code.text(0.02, 0.85, 'Pseudocode:', ha='left', va='top',
                         fontsize=10, fontweight='bold', color=self.colors['highlight'],
                         transform=self.ax_code.transAxes)
        
        # Highlight current line in pseudocode based on action
        highlighted_line = self.get_highlighted_line(action)
        
        # Display code with potential highlighting
        lines = code.split('\n')
        y_pos = 0.6
        line_height = 0.12
        
        for i, line in enumerate(lines):
            color = '#00FF00' if i == highlighted_line else '#CCCCCC'
            weight = 'bold' if i == highlighted_line else 'normal'
            self.ax_code.text(0.05, y_pos - i * line_height, line, ha='left', va='top',
                            fontsize=8, color=color, family='monospace', fontweight=weight,
                            transform=self.ax_code.transAxes)
        
        # Remove axes
        self.ax_code.set_xticks([])
        self.ax_code.set_yticks([])
        for spine in self.ax_code.spines.values():
            spine.set_edgecolor(self.colors['accent'])
            spine.set_linewidth(1)
    
    def get_highlighted_line(self, action):
        """Determine which line of pseudocode to highlight"""
        highlight_rules = {
            'COMPARE': 2,  # Usually the comparison line
            'SWAP': 3,     # Usually the swap line
            'SEARCH': 1,   # Search condition line
            'PIVOT': 0,    # Pivot selection
            'MERGE': 4,    # Merge operation
            'DIVIDE': 1,   # Division step
            'PUSH': 2,     # Push operation
            'POP': 1,      # Pop operation
            'ENQUEUE': 2,  # Enqueue operation
            'DEQUEUE': 1,  # Dequeue operation
        }
        
        for key, line in highlight_rules.items():
            if key in action:
                return line
        return 0
    
    # ==================== PROPER DATA STRUCTURE VISUALIZATIONS ====================
    
    def visualize_array(self, step):
        """Proper array visualization - horizontal layout"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Array Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=16, color=self.colors['text'])
            return
        
        colors = self.get_colors(highlighted)
        
        # Create horizontal array visualization
        x_pos = np.arange(len(data))
        bar_height = 0.6
        
        # Create bars
        for i, (value, color) in enumerate(zip(data, colors)):
            # Draw array element
            rect = Rectangle((i, 0), 0.8, bar_height, 
                           facecolor=color, alpha=0.85, edgecolor='white', 
                           linewidth=2, zorder=3)
            self.ax_main.add_patch(rect)
            
            # Add value
            self.ax_main.text(i + 0.4, bar_height/2, f'{value}', 
                            ha='center', va='center', fontsize=12, 
                            fontweight='bold', color='white', zorder=4)
            
            # Add index
            self.ax_main.text(i + 0.4, -0.1, f'[{i}]', 
                            ha='center', va='top', fontsize=9, 
                            color=self.colors['text'])
        
        # Handle pointers for algorithms
        pointers = step.get('pointers', [-1] * 10)
        if pointers[0] != -1:  # Left pointer
            self.ax_main.axvline(x=pointers[0] + 0.4, color='cyan', linestyle='--', 
                               alpha=0.8, linewidth=2, label='Left')
        if pointers[1] != -1:  # Right pointer
            self.ax_main.axvline(x=pointers[1] + 0.4, color='yellow', linestyle='--', 
                               alpha=0.8, linewidth=2, label='Right')
        if pointers[2] != -1:  # Mid pointer
            self.ax_main.axvline(x=pointers[2] + 0.4, color='magenta', linestyle='--', 
                               alpha=0.8, linewidth=2, label='Mid')
        
        # Set up the plot
        self.ax_main.set_xlim(-0.5, len(data) + 0.5)
        self.ax_main.set_ylim(-0.3, 1.0)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_stack(self, step):
        """Proper stack visualization - vertical LIFO structure"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Stack Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Stack configuration
        stack_width = 0.8
        element_height = 0.6
        base_y = 0.5
        
        # Draw stack base
        base_rect = Rectangle((0.1, base_y - 0.1), stack_width, 0.1,
                            facecolor='#666666', edgecolor='white', linewidth=2)
        self.ax_main.add_patch(base_rect)
        self.ax_main.text(0.5, base_y - 0.2, 'BASE', ha='center', va='top',
                         fontsize=10, color='white', fontweight='bold')
        
        # Draw stack elements (bottom to top)
        for i, (value, color) in enumerate(zip(data, colors)):
            y_pos = base_y + i * element_height
            
            # Stack element
            rect = Rectangle((0.1, y_pos), stack_width, element_height,
                           facecolor=color, alpha=0.85, edgecolor='white', 
                           linewidth=2, zorder=3)
            self.ax_main.add_patch(rect)
            
            # Value
            self.ax_main.text(0.5, y_pos + element_height/2, f'{value}', 
                            ha='center', va='center', fontsize=12, 
                            fontweight='bold', color='white', zorder=4)
        
        # TOP pointer
        if data:
            top_y = base_y + len(data) * element_height
            self.ax_main.annotate('TOP', 
                               xy=(0.5, top_y + 0.1), 
                               xytext=(0.9, top_y + 0.5),
                               arrowprops=dict(arrowstyle='->', color='red', lw=3),
                               fontsize=14, color='red', fontweight='bold', ha='center',
                               bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', 
                                       alpha=0.9, edgecolor='red', linewidth=2))
        
        # Stack info
        self.ax_main.text(0.9, 0.9, f'Size: {len(data)}', 
                        ha='right', va='top', transform=self.ax_main.transAxes,
                        fontsize=10, color=self.colors['text'],
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel_bg']))
        
        # Set up the plot
        self.ax_main.set_xlim(0, 1.2)
        self.ax_main.set_ylim(0, base_y + len(data) * element_height + 1.0)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_queue(self, step):
        """Proper queue visualization - horizontal FIFO structure"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'Queue Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Queue configuration
        element_width = 0.8
        element_height = 0.6
        base_x = 0.5
        
        # Draw queue elements (left to right)
        for i, (value, color) in enumerate(zip(data, colors)):
            x_pos = base_x + i * element_width
            
            # Queue element
            rect = Rectangle((x_pos, 0.2), element_width, element_height,
                           facecolor=color, alpha=0.85, edgecolor='white', 
                           linewidth=2, zorder=3)
            self.ax_main.add_patch(rect)
            
            # Value
            self.ax_main.text(x_pos + element_width/2, 0.2 + element_height/2, f'{value}', 
                            ha='center', va='center', fontsize=12, 
                            fontweight='bold', color='white', zorder=4)
            
            # Position indicator
            self.ax_main.text(x_pos + element_width/2, 0.1, f'pos {i}', 
                            ha='center', va='top', fontsize=8, color=self.colors['text'])
        
        # FRONT and REAR pointers
        if data:
            # FRONT pointer (first element)
            front_x = base_x + element_width/2
            self.ax_main.annotate('FRONT', 
                               xy=(front_x, 0.85), 
                               xytext=(front_x, 1.1),
                               arrowprops=dict(arrowstyle='->', color='red', lw=3),
                               fontsize=12, color='red', fontweight='bold', ha='center',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', 
                                       alpha=0.9, edgecolor='red', linewidth=2))
            
            # REAR pointer (last element)
            rear_x = base_x + (len(data) - 1) * element_width + element_width/2
            self.ax_main.annotate('REAR', 
                               xy=(rear_x, 0.85), 
                               xytext=(rear_x, 1.1),
                               arrowprops=dict(arrowstyle='->', color='green', lw=3),
                               fontsize=12, color='green', fontweight='bold', ha='center',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', 
                                       alpha=0.9, edgecolor='green', linewidth=2))
        
        # Queue info
        self.ax_main.text(0.95, 0.95, f'Size: {len(data)}', 
                        ha='right', va='top', transform=self.ax_main.transAxes,
                        fontsize=10, color=self.colors['text'],
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['panel_bg']))
        
        # Set up the plot
        self.ax_main.set_xlim(0, base_x + len(data) * element_width + 0.5)
        self.ax_main.set_ylim(0, 1.3)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_linked_list(self, step):
        """Proper linked list visualization - nodes with pointers"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'List Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Node configuration
        node_width = 0.6
        node_height = 0.4
        pointer_length = 0.3
        y_center = 0.5
        
        # Draw linked list nodes
        for i, (value, color) in enumerate(zip(data, colors)):
            x_center = 0.5 + i * (node_width + pointer_length)
            
            # Node rectangle
            rect = Rectangle((x_center - node_width/2, y_center - node_height/2),
                           node_width, node_height,
                           facecolor=color, alpha=0.85, edgecolor='white', 
                           linewidth=2, zorder=3)
            self.ax_main.add_patch(rect)
            
            # Value
            self.ax_main.text(x_center, y_center, f'{value}', 
                            ha='center', va='center', fontsize=11, 
                            fontweight='bold', color='white', zorder=4)
            
            # Next pointer arrow (except for last node)
            if i < len(data) - 1:
                arrow_start = (x_center + node_width/2, y_center)
                arrow_end = (x_center + node_width/2 + pointer_length, y_center)
                
                arrow = FancyArrowPatch(arrow_start, arrow_end,
                                      arrowstyle='->', color='cyan', 
                                      linewidth=2, zorder=2)
                self.ax_main.add_patch(arrow)
        
        # HEAD pointer
        if data:
            head_x = 0.5 - node_width/2
            self.ax_main.annotate('HEAD', 
                               xy=(head_x, y_center + node_height/2 + 0.1), 
                               xytext=(head_x - 0.3, y_center + node_height/2 + 0.4),
                               arrowprops=dict(arrowstyle='->', color='red', lw=2),
                               fontsize=11, color='red', fontweight='bold', ha='center')
        
        # NULL pointer for last node
        if data:
            last_x = 0.5 + (len(data) - 1) * (node_width + pointer_length) + node_width/2
            self.ax_main.text(last_x + 0.2, y_center, 'NULL', 
                            ha='left', va='center', fontsize=10, 
                            color='red', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='black', 
                                    alpha=0.7, edgecolor='red', linewidth=1))
        
        # Set up the plot
        total_width = 0.5 + len(data) * (node_width + pointer_length) + 0.5
        self.ax_main.set_xlim(0, total_width)
        self.ax_main.set_ylim(0, 1)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def visualize_binary_search_tree(self, step):
        """Proper BST visualization - tree structure"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'BST Empty', ha='center', va='center', 
                        transform=self.ax_main.transAxes, fontsize=18, 
                        color=self.colors['text'], fontweight='bold')
            return
        
        colors = self.get_colors(highlighted)
        
        # Calculate tree positions
        positions = self.calculate_tree_positions(data)
        
        # Draw connections first
        for i in range(1, len(data)):
            if i < len(positions):
                parent_idx = (i - 1) // 2
                if parent_idx < len(positions):
                    # Draw line from parent to child
                    x_values = [positions[parent_idx][0], positions[i][0]]
                    y_values = [positions[parent_idx][1], positions[i][1]]
                    self.ax_main.plot(x_values, y_values, 'cyan', linewidth=2, alpha=0.6, zorder=1)
        
        # Draw nodes
        for i, (value, color) in enumerate(zip(data, colors)):
            if i < len(positions):
                x, y = positions[i]
                
                # Node circle
                circle = Circle((x, y), 0.15, facecolor=color, alpha=0.85, 
                              edgecolor='white', linewidth=2, zorder=3)
                self.ax_main.add_patch(circle)
                
                # Value
                self.ax_main.text(x, y, f'{value}', ha='center', va='center',
                                fontsize=10, fontweight='bold', color='white', zorder=4)
        
        # Set up the plot
        if positions:
            x_coords = [pos[0] for pos in positions]
            y_coords = [pos[1] for pos in positions]
            x_margin = (max(x_coords) - min(x_coords)) * 0.2 + 0.5
            y_margin = (max(y_coords) - min(y_coords)) * 0.2 + 0.5
            
            self.ax_main.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
            self.ax_main.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        else:
            self.ax_main.set_xlim(-1, 1)
            self.ax_main.set_ylim(-1, 1)
        
        self.ax_main.set_aspect('equal')
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        
        self.ax_main.set_title(f'{step["description"]}', fontsize=11, 
                              color=self.colors['text'], pad=10, fontweight='bold')
        self.ax_main.set_facecolor(self.colors['plot_bg'])
    
    def calculate_tree_positions(self, data):
        """Calculate positions for BST nodes"""
        if not data:
            return []
        
        positions = []
        n = len(data)
        
        for i in range(n):
            level = 0
            temp = i + 1
            while temp > 1:
                temp //= 2
                level += 1
            
            # Calculate horizontal position
            level_start = 2 ** level - 1
            pos_in_level = i - level_start
            level_width = 2 ** (level + 1)
            
            x = (pos_in_level + 1) * (1.0 / (2 ** level + 1)) - 0.5
            x = x * (2 ** level)  # Scale by level
            
            # Vertical position (root at top)
            y = -level * 0.3
            
            positions.append((x, y))
        
        return positions
    
    def get_colors(self, highlighted):
        """Enhanced color mapping with smooth transitions"""
        colors = []
        for h in highlighted:
            if h == 1:  # Comparing
                colors.append(self.colors['compare'])
            elif h == 2:  # Found/target
                colors.append(self.colors['found'])
            elif h == 3:  # Pivot
                colors.append(self.colors['pivot'])
            elif h == 4:  # Special
                colors.append(self.colors['special'])
            else:  # Normal
                colors.append(self.colors['normal'])
        return colors
    
    def get_space_complexity(self, action):
        """Get space complexity for current operation"""
        complexities = {
            'BUBBLE_SORT': 'O(1)',
            'SELECTION_SORT': 'O(1)',
            'INSERTION_SORT': 'O(1)',
            'MERGE_SORT': 'O(n)',
            'QUICK_SORT': 'O(log n)',
            'LINEAR_SEARCH': 'O(1)',
            'BINARY_SEARCH': 'O(1)',
            'PUSH': 'O(1)',
            'POP': 'O(1)',
            'ENQUEUE': 'O(1)',
            'DEQUEUE': 'O(1)',
        }
        
        for key, complexity in complexities.items():
            if key in action:
                return complexity
        return 'O(1)'
    
    def wrap_text(self, text, max_chars):
        """Wrap text to specified character limit"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def get_pseudocode(self, action):
        """Get pseudocode for current algorithm step"""
        pseudocodes = {
            # Sorting algorithms
            'BUBBLE': """function bubbleSort(arr):
    for i from 0 to n-1:
        for j from 0 to n-i-1:
            if arr[j] > arr[j+1]:
                swap arr[j] and arr[j+1]""",
            
            'QUICK': """function quickSort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        quickSort(arr, low, pivot-1)
        quickSort(arr, pivot+1, high)""",
            
            'MERGE': """function mergeSort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergeSort(arr[:mid])
    right = mergeSort(arr[mid:])
    return merge(left, right)""",
            
            'SELECTION': """function selectionSort(arr):
    for i from 0 to n-1:
        min_idx = i
        for j from i+1 to n:
            if arr[j] < arr[min_idx]:
                min_idx = j
        swap arr[i] and arr[min_idx]""",
            
            'INSERTION': """function insertionSort(arr):
    for i from 1 to n-1:
        key = arr[i]
        j = i-1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j = j-1
        arr[j+1] = key""",
            
            # Searching algorithms
            'BINARY_SEARCH': """function binarySearch(arr, target):
    low = 0, high = n-1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1""",
            
            'LINEAR_SEARCH': """function linearSearch(arr, target):
    for i from 0 to n-1:
        if arr[i] == target:
            return i
    return -1""",
            
            # Stack operations
            'PUSH': """function push(stack, element):
    if stack.isFull():
        return "Overflow"
    stack.top = stack.top + 1
    stack.arr[stack.top] = element""",
            
            'POP': """function pop(stack):
    if stack.isEmpty():
        return "Underflow"
    element = stack.arr[stack.top]
    stack.top = stack.top - 1
    return element""",
            
            # Queue operations
            'ENQUEUE': """function enqueue(queue, element):
    if queue.isFull():
        return "Overflow"
    queue.rear = queue.rear + 1
    queue.arr[queue.rear] = element""",
            
            'DEQUEUE': """function dequeue(queue):
    if queue.isEmpty():
        return "Underflow"
    element = queue.arr[queue.front]
    queue.front = queue.front + 1
    return element"""
        }
        
        for key, code in pseudocodes.items():
            if key in action:
                return code
        
        # Default pseudocode
        return """function algorithm(data):
    // Algorithm pseudocode
    for each element in data:
        perform operation
    return result"""
    
    # 🎮 INTERACTIVE LEARNING MODE methods
    def toggle_learning_mode(self, event=None):
        """Toggle interactive learning mode"""
        self.learning_mode = not self.learning_mode
        print(f"🎮 Learning Mode: {'ON' if self.learning_mode else 'OFF'}")
        self.update_visualization()
    
    # 🚀 SMART INPUT SYSTEM methods
    def generate_test_case(self, case_type, size=10):
        """Generate different test cases for algorithm testing"""
        if case_type == 'sorted':
            return list(range(1, size + 1))
        elif case_type == 'reverse':
            return list(range(size, 0, -1))
        elif case_type == 'random':
            return np.random.randint(1, 100, size).tolist()
        elif case_type == 'nearly_sorted':
            arr = list(range(1, size + 1))
            # Swap a few elements to make it nearly sorted
            for _ in range(size // 10):
                i, j = np.random.randint(0, size, 2)
                arr[i], arr[j] = arr[j], arr[i]
            return arr
        elif case_type == 'all_equal':
            return [5] * size
        elif case_type == 'few_unique':
            unique_values = [1, 2, 3, 5, 8]
            return [np.random.choice(unique_values) for _ in range(size)]
        else:
            return list(range(1, size + 1))
    
    # 🎯 ALGORITHM BATTLE MODE methods (stub for future implementation)
    def start_algorithm_battle(self, algorithms):
        """Start battle mode with multiple algorithms"""
        self.battle_mode = True
        self.battle_algorithms = algorithms
        print(f"🎯 Algorithm Battle Started: {', '.join(algorithms)}")
    
    def update_visualization(self):
        """Update all visualization components"""
        if not self.steps:
            return
        
        step = self.steps[self.current_step]
        
        # Update all panels
        self.update_side_chart(step)
        self.update_statistics_dashboard(step)
        self.update_learning_dashboard(step)
        self.update_code_display(step)
        
        # Choose visualization based on structure type
        structure_type = self.config.get('structure_type', 'array')
        
        if structure_type == 'stack' or self.config.get('is_stack', False):
            self.visualize_stack(step)
        elif structure_type == 'queue' or self.config.get('is_queue', False):
            self.visualize_queue(step)
        elif structure_type == 'linked_list' or self.config.get('is_linked_list', False):
            self.visualize_linked_list(step)
        elif structure_type == 'binary_search_tree' or self.config.get('is_binary_search_tree', False):
            self.visualize_binary_search_tree(step)
        else:  # Default to array visualization
            self.visualize_array(step)
        
        plt.draw()
    
    def animate(self, frame):
        if self.is_playing and self.current_step < len(self.steps) - 1:
            self.current_step += 1
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
        self.is_playing = False
        self.btn_play.label.set_text('Play')
        self.update_visualization()
        print("Animation reset to beginning")
    
    def step_back(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.is_playing = False
            self.btn_play.label.set_text('Play')
            self.update_visualization()
        print(f"Step back to {self.current_step + 1}")
    
    def step_forward(self, event):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.is_playing = False
            self.btn_play.label.set_text('Play')
            self.update_visualization()
        print(f"Step forward to {self.current_step + 1}")
    
    def update_speed(self, val):
        self.speed = val
        if hasattr(self, 'ani'):
            self.ani.event_source.interval = 1000 / self.speed
        print(f"Speed updated to {self.speed:.1f}x")

def main():
    print("=" * 60)
    print("Starting Enhanced Algorithm Visualizer v5.0...")
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