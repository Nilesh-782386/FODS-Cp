import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import numpy as np
import sys
import os
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch
from matplotlib.gridspec import GridSpec

class AlgorithmVisualizer:
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.is_playing = False
        self.speed = 1.5
        self.config = {}
        self.learning_mode = False
        
        self.colors = {
            'bg': '#0F172A', 'panel_bg': '#1E293B', 'dark_bg': '#0A0E1A',
            'text': '#F7FAFC', 'accent': '#667EEA', 'comparing': '#F56565',
            'swapping': '#ED8936', 'sorted': '#48BB78', 'pivot': '#ECC94B',
            'selected': '#9F7AEA', 'active': '#4299E1', 'node': '#4C51BF',
            'stack_base': '#2D3748', 'link_arrow': '#4299E1', 'tree_node': '#805AD5',
            'highlight_1': '#F56565',  # Red - comparing/current
            'highlight_2': '#48BB78',  # Green - sorted/swapped
            'highlight_3': '#ECC94B',  # Yellow - pivot/selected
            'highlight_4': '#9F7AEA',  # Purple - merged/completed
        }
        
        self.load_data()
        self.setup_figure()
        
        self.is_playing = True
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, interval=int(1000/self.speed), 
            repeat=True, blit=False, cache_frame_data=False
        )
        plt.show()
    
    def load_data(self):
        try:
            with open('algorithm_steps.json', 'r') as f:
                data = json.load(f)
                self.steps = data['steps']
            with open('algorithm_config.json', 'r') as f:
                self.config = json.load(f)
            print(f"✅ Loaded {len(self.steps)} steps")
            print(f"📊 Structure: {self.config.get('structure_type', 'unknown')}")
            print(f"⚙️  Operation: {self.config.get('operation', 'unknown')}")
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {e}")
            sys.exit(1)
    
    def setup_figure(self):
        self.fig = plt.figure(figsize=(20, 11))
        self.fig.patch.set_facecolor(self.colors['bg'])
        
        gs = GridSpec(12, 12, figure=self.fig, hspace=0.5, wspace=0.4,
                     left=0.04, right=0.98, top=0.94, bottom=0.08)
        
        self.ax_main = self.fig.add_subplot(gs[0:7, 0:8])
        self.ax_main.set_facecolor(self.colors['panel_bg'])
        
        self.ax_info = self.fig.add_subplot(gs[0:2, 8:12])
        self.ax_info.set_facecolor(self.colors['panel_bg'])
        
        self.ax_stats = self.fig.add_subplot(gs[2:4, 8:12])
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        self.ax_progress = self.fig.add_subplot(gs[4:6, 8:12])
        self.ax_progress.set_facecolor(self.colors['panel_bg'])
        
        self.ax_learn = self.fig.add_subplot(gs[7:9, 0:12])
        self.ax_learn.set_facecolor(self.colors['bg'])
        
        self.ax_code = self.fig.add_subplot(gs[9:11, 0:8])
        self.ax_code.set_facecolor(self.colors['dark_bg'])
        
        self.ax_controls = self.fig.add_subplot(gs[11, :])
        self.ax_controls.set_facecolor(self.colors['bg'])
        self.ax_controls.axis('off')
        
        self.setup_ui()
        self.update_visualization()
    
    def setup_ui(self):
        positions = [0.05, 0.13, 0.21, 0.29, 0.37]
        props = {'width': 0.07, 'height': 0.035, 'y': 0.02}
        
        ax_play = plt.axes([positions[0], props['y'], props['width'], props['height']])
        self.btn_play = Button(ax_play, '▶ Play', color='#48BB78')
        self.btn_play.on_clicked(self.toggle_play)
        
        ax_reset = plt.axes([positions[1], props['y'], props['width'], props['height']])
        self.btn_reset = Button(ax_reset, '↻ Reset', color='#F56565')
        self.btn_reset.on_clicked(self.reset_animation)
        
        ax_back = plt.axes([positions[2], props['y'], props['width'], props['height']])
        self.btn_back = Button(ax_back, '◀ Back', color='#ED8936')
        self.btn_back.on_clicked(self.step_back)
        
        ax_forward = plt.axes([positions[3], props['y'], props['width'], props['height']])
        self.btn_forward = Button(ax_forward, 'Next ▶', color='#4299E1')
        self.btn_forward.on_clicked(self.step_forward)
        
        ax_learn = plt.axes([positions[4], props['y'], props['width']*1.2, props['height']])
        self.btn_learn = Button(ax_learn, '💡 Learn', color='#9F7AEA')
        self.btn_learn.on_clicked(self.toggle_learning_mode)
        
        ax_speed = plt.axes([0.60, props['y'] + 0.01, 0.3, 0.02])
        self.slider_speed = Slider(ax_speed, 'Speed', 0.5, 5.0, valinit=1.5, color='#667EEA')
        self.slider_speed.on_changed(self.update_speed)
        
        operation = self.config.get('operation', '').replace('_', ' ').title()
        structure = self.config.get('structure_type', '').replace('_', ' ').title()
        self.fig.suptitle(f'🎯 {structure} - {operation}', fontsize=20, 
                         color=self.colors['text'], fontweight='bold', y=0.98)
    
    def is_sorting_algorithm(self):
        op = self.config.get('operation', '').lower()
        return any(s in op for s in ['bubble', 'selection', 'insertion', 'quick', 'merge', 'sort'])
    
    def get_highlight_color(self, h):
        """Map C highlight values to colors - EXACT match with C code"""
        if h == 0:
            return self.colors['accent']  # Default/unhighlighted
        elif h == 1:
            return self.colors['highlight_1']  # Red - comparing/current
        elif h == 2:
            return self.colors['highlight_2']  # Green - swapped/sorted
        elif h == 3:
            return self.colors['highlight_3']  # Yellow - pivot/selected
        elif h == 4:
            return self.colors['highlight_4']  # Purple - merged
        else:
            return self.colors['accent']
    
    def visualize_sorting_bars(self, step):
        """BAR FORMAT - Exact visualization of C sorting algorithms"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        pointers = step.get('pointers', [-1] * 10)
        action = step.get('action', '')
        
        if not data:
            self.ax_main.text(0.5, 0.5, 'No Data', ha='center', va='center',
                            transform=self.ax_main.transAxes, fontsize=20, color='white')
            return
        
        n = len(data)
        max_val, min_val = max(data), min(data)
        value_range = max_val - min_val if max_val != min_val else 1
        
        bar_width = 0.8
        for i, (value, h) in enumerate(zip(data, highlighted)):
            normalized = (value - min_val) / value_range
            bar_height = 0.5 + normalized * 5.0
            
            color = self.get_highlight_color(h)
            edge_color = '#FFFFFF' if h != 0 else '#4A5568'
            edge_width = 3 if h != 0 else 1.5
            
            rect = Rectangle((i, 0), bar_width, bar_height, facecolor=color, alpha=0.9,
                           edgecolor=edge_color, linewidth=edge_width, zorder=3)
            self.ax_main.add_patch(rect)
            
            self.ax_main.text(i + bar_width/2, bar_height + 0.2, str(value),
                            ha='center', va='bottom', fontsize=11, fontweight='bold',
                            color='white', zorder=4)
            self.ax_main.text(i + bar_width/2, -0.3, f'[{i}]', ha='center', va='top',
                            fontsize=9, color='#A0AEC0')
        
        # Show pointers (L=left, R=right, P=pivot/mid) - matching C implementation
        pointer_labels = [
            (0, 'L', self.colors['active']),      # Left pointer
            (1, 'R', self.colors['pivot']),       # Right pointer
            (2, 'P', self.colors['comparing'])    # Pivot/Mid pointer
        ]
        
        for idx, symbol, col in pointer_labels:
            if pointers[idx] != -1 and pointers[idx] < n:
                x = pointers[idx] + bar_width/2
                self.ax_main.annotate(symbol, xy=(x, 0), xytext=(x, 6.5),
                                    arrowprops=dict(arrowstyle='->', color=col, lw=2.5),
                                    fontsize=12, color=col, fontweight='bold', ha='center',
                                    bbox=dict(boxstyle='circle,pad=0.3', facecolor=col, alpha=0.4))
        
        # Add action-specific annotations
        if 'PIVOT' in action:
            self.ax_main.text(0.98, 0.95, '🎯 Pivot Selected', transform=self.ax_main.transAxes,
                             ha='right', va='top', fontsize=11, color=self.colors['pivot'],
                             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=self.colors['panel_bg'], edgecolor=self.colors['pivot'], linewidth=2))
        elif 'DIVIDE' in action:
            self.ax_main.text(0.98, 0.95, '✂️ Dividing', transform=self.ax_main.transAxes,
                             ha='right', va='top', fontsize=11, color=self.colors['active'],
                             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=self.colors['panel_bg'], edgecolor=self.colors['active'], linewidth=2))
        elif 'MERGE' in action and 'COMPLETE' in action:
            self.ax_main.text(0.98, 0.95, '✅ Merged', transform=self.ax_main.transAxes,
                             ha='right', va='top', fontsize=11, color=self.colors['sorted'],
                             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=self.colors['panel_bg'], edgecolor=self.colors['sorted'], linewidth=2))
        
        self.ax_main.set_xlim(-0.5, n)
        self.ax_main.set_ylim(-0.5, 7.0)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.grid(axis='y', alpha=0.15, linestyle='--', linewidth=0.5)
        self.ax_main.set_title(step.get('description', ''), fontsize=13, 
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def visualize_stack_vertical(self, step):
        """VERTICAL STACK - LIFO visualization"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        pointers = step.get('pointers', [-1] * 10)
        
        if not data:
            self.ax_main.text(0.5, 0.5, '📚 Stack Empty\nLIFO (Last In, First Out)',
                            ha='center', va='center', transform=self.ax_main.transAxes,
                            fontsize=18, fontweight='bold', color=self.colors['text'])
            return
        
        box_h, box_w, base_y, cx = 0.6, 2.5, 1.0, 0.5
        
        # Draw base
        base = FancyBboxPatch((cx - box_w/2 - 0.2, base_y - 0.25), box_w + 0.4, 0.15,
                             boxstyle="round,pad=0.05", facecolor=self.colors['stack_base'],
                             edgecolor='#718096', linewidth=3, zorder=1)
        self.ax_main.add_patch(base)
        self.ax_main.text(cx, base_y - 0.4, '⬛ BASE ⬛', ha='center', va='top',
                         fontsize=12, color='#E2E8F0', fontweight='bold')
        
        # Draw stack elements
        for i, (val, h) in enumerate(zip(data, highlighted)):
            y = base_y + i * (box_h + 0.1)
            col = self.get_highlight_color(h)
            edge_col = '#FFFFFF' if h != 0 else '#667EEA'
            edge_w = 4 if h != 0 else 2
            
            box = FancyBboxPatch((cx - box_w/2, y), box_w, box_h, boxstyle="round,pad=0.05",
                                facecolor=col, alpha=0.9, edgecolor=edge_col,
                                linewidth=edge_w, zorder=3)
            self.ax_main.add_patch(box)
            
            self.ax_main.text(cx, y + box_h/2, str(val), ha='center', va='center',
                            fontsize=18, fontweight='bold', color='white', zorder=4)
            self.ax_main.text(cx - box_w/2 - 0.4, y + box_h/2, f'{i}', ha='right',
                            va='center', fontsize=11, color='#CBD5E0', fontweight='bold')
        
        # TOP pointer - matching C's pointer[0] for top
        top_idx = pointers[0] if pointers[0] != -1 else len(data) - 1
        if top_idx >= 0 and top_idx < len(data):
            top_y = base_y + top_idx * (box_h + 0.1) + box_h/2
            arrow = FancyArrowPatch((cx + box_w/2 + 0.5, top_y),
                                   (cx + box_w/2 + 0.1, top_y),
                                   arrowstyle='->', mutation_scale=30, color=self.colors['comparing'],
                                   linewidth=4, zorder=5)
            self.ax_main.add_patch(arrow)
            
            self.ax_main.text(cx + box_w/2 + 1.2, top_y, '🔝 TOP', ha='left',
                             va='center', fontsize=14, color=self.colors['comparing'],
                             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=self.colors['comparing'], alpha=0.3,
                             edgecolor=self.colors['comparing'], linewidth=2))
        
        self.ax_main.text(0.95, 0.95, f'📊 Size: {len(data)}', transform=self.ax_main.transAxes,
                         ha='right', va='top', fontsize=13, color=self.colors['active'],
                         fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                         facecolor=self.colors['panel_bg'], edgecolor=self.colors['active'], linewidth=2))
        
        top_y = base_y + len(data) * (box_h + 0.1)
        self.ax_main.set_xlim(-1, 4)
        self.ax_main.set_ylim(0, top_y + 1)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(step.get('description', ''), fontsize=14,
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def visualize_queue_horizontal(self, step):
        """HORIZONTAL QUEUE - FIFO visualization"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        pointers = step.get('pointers', [-1] * 10)
        
        if not data:
            self.ax_main.text(0.5, 0.5, '🎫 Queue Empty\nFIFO (First In, First Out)',
                            ha='center', va='center', transform=self.ax_main.transAxes,
                            fontsize=18, fontweight='bold', color=self.colors['text'])
            return
        
        box_w, box_h, start_x, cy, sp = 0.9, 1.2, 1.0, 0.5, 0.15
        
        for i, (val, h) in enumerate(zip(data, highlighted)):
            x = start_x + i * (box_w + sp)
            col = self.get_highlight_color(h)
            edge_col = '#FFFFFF' if h != 0 else '#667EEA'
            edge_w = 4 if h != 0 else 2
            
            box = FancyBboxPatch((x, cy - box_h/2), box_w, box_h, boxstyle="round,pad=0.05",
                                facecolor=col, alpha=0.9, edgecolor=edge_col,
                                linewidth=edge_w, zorder=3)
            self.ax_main.add_patch(box)
            
            self.ax_main.text(x + box_w/2, cy, str(val), ha='center', va='center',
                            fontsize=18, fontweight='bold', color='white', zorder=4)
            self.ax_main.text(x + box_w/2, cy - box_h/2 - 0.25, f'[{i}]', ha='center',
                            va='top', fontsize=10, color='#CBD5E0', fontweight='bold')
            
            if i < len(data) - 1:
                arrow = FancyArrowPatch((x + box_w, cy), (x + box_w + sp, cy),
                                       arrowstyle='->', mutation_scale=25,
                                       color=self.colors['link_arrow'], linewidth=3, zorder=2)
                self.ax_main.add_patch(arrow)
        
        # FRONT pointer - matching C's pointers[0]
        front_idx = pointers[0] if pointers[0] != -1 else 0
        if front_idx >= 0 and front_idx < len(data):
            front_x = start_x + front_idx * (box_w + sp) + box_w/2
            self.ax_main.annotate('🔴 FRONT\n(Dequeue)', xy=(front_x, cy - box_h/2),
                                xytext=(front_x, cy - box_h/2 - 0.8),
                                arrowprops=dict(arrowstyle='->', color='#F56565', lw=4),
                                fontsize=12, color='#F56565', fontweight='bold', ha='center',
                                bbox=dict(boxstyle='round,pad=0.5', facecolor='#F56565',
                                alpha=0.3, edgecolor='#F56565', linewidth=2))
        
        # REAR pointer - matching C's pointers[1]
        rear_idx = pointers[1] if pointers[1] != -1 else len(data) - 1
        if rear_idx >= 0 and rear_idx < len(data):
            rear_x = start_x + rear_idx * (box_w + sp) + box_w/2
            self.ax_main.annotate('🟢 REAR\n(Enqueue)', xy=(rear_x, cy + box_h/2),
                                xytext=(rear_x, cy + box_h/2 + 0.8),
                                arrowprops=dict(arrowstyle='->', color='#48BB78', lw=4),
                                fontsize=12, color='#48BB78', fontweight='bold', ha='center',
                                bbox=dict(boxstyle='round,pad=0.5', facecolor='#48BB78',
                                alpha=0.3, edgecolor='#48BB78', linewidth=2))
        
        self.ax_main.text(0.95, 0.95, f'📊 Size: {len(data)}', transform=self.ax_main.transAxes,
                         ha='right', va='top', fontsize=13, color=self.colors['active'],
                         fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
                         facecolor=self.colors['panel_bg'], edgecolor=self.colors['active'], linewidth=2))
        
        total_w = start_x + len(data) * (box_w + sp) + 1
        self.ax_main.set_xlim(0, total_w)
        self.ax_main.set_ylim(-2, 3)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(step.get('description', ''), fontsize=14,
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def visualize_linked_list_proper(self, step):
        """PROPER LINKED LIST with nodes and arrows"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, '🔗 List Empty', ha='center', va='center',
                            transform=self.ax_main.transAxes, fontsize=22,
                            fontweight='bold', color=self.colors['text'])
            return
        
        node_r, arrow_len, y_c, start_x = 0.35, 0.8, 0.5, 1.0
        
        for i, (val, h) in enumerate(zip(data, highlighted)):
            x_c = start_x + i * (node_r * 2 + arrow_len)
            col = self.get_highlight_color(h)
            edge_col = '#FFFFFF' if h != 0 else '#667EEA'
            edge_w = 4 if h != 0 else 2
            
            circle = Circle((x_c, y_c), node_r, facecolor=col, alpha=0.9,
                          edgecolor=edge_col, linewidth=edge_w, zorder=3)
            self.ax_main.add_patch(circle)
            
            self.ax_main.text(x_c, y_c, str(val), ha='center', va='center',
                            fontsize=16, fontweight='bold', color='white', zorder=4)
            self.ax_main.text(x_c, y_c - node_r - 0.25, f'Node {i}', ha='center',
                            va='top', fontsize=10, color='#CBD5E0', fontweight='bold')
            
            if i < len(data) - 1:
                arrow_s = x_c + node_r
                arrow_e = start_x + (i + 1) * (node_r * 2 + arrow_len) - node_r
                arrow = FancyArrowPatch((arrow_s, y_c), (arrow_e, y_c), arrowstyle='->',
                                       mutation_scale=25, color=self.colors['link_arrow'],
                                       linewidth=3.5, zorder=2)
                self.ax_main.add_patch(arrow)
                self.ax_main.text((arrow_s + arrow_e)/2, y_c + 0.15, 'next', ha='center',
                                va='bottom', fontsize=9, color=self.colors['link_arrow'],
                                style='italic')
        
        # HEAD pointer
        head_x = start_x
        self.ax_main.annotate('🎯 HEAD', xy=(head_x, y_c), xytext=(head_x - 0.8, y_c + 0.8),
                            arrowprops=dict(arrowstyle='->', color='#F56565', lw=4),
                            fontsize=13, color='#F56565', fontweight='bold', ha='center',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F56565',
                            alpha=0.3, edgecolor='#F56565', linewidth=2))
        
        # NULL at end
        last_x = start_x + (len(data) - 1) * (node_r * 2 + arrow_len) + node_r
        null_box = FancyBboxPatch((last_x + 0.2, y_c - 0.15), 0.5, 0.3,
                                 boxstyle="round,pad=0.05", facecolor='#1A202C',
                                 edgecolor='#F56565', linewidth=2, zorder=3)
        self.ax_main.add_patch(null_box)
        self.ax_main.text(last_x + 0.45, y_c, 'NULL', ha='center', va='center',
                         fontsize=10, color='#F56565', fontweight='bold')
        
        arrow = FancyArrowPatch((last_x, y_c), (last_x + 0.2, y_c), arrowstyle='->',
                               mutation_scale=20, color=self.colors['link_arrow'],
                               linewidth=3, zorder=2)
        self.ax_main.add_patch(arrow)
        
        total_w = start_x + len(data) * (node_r * 2 + arrow_len) + 1.5
        self.ax_main.set_xlim(-0.5, total_w)
        self.ax_main.set_ylim(-0.5, 2)
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(step.get('description', ''), fontsize=14,
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def visualize_binary_search_tree(self, step):
        """BST TREE - matching C's tree_to_array traversal"""
        self.ax_main.clear()
        data = step['data']
        highlighted = step.get('highlighted', [0] * len(data))
        
        if not data:
            self.ax_main.text(0.5, 0.5, '🌳 BST Empty', ha='center', va='center',
                            transform=self.ax_main.transAxes, fontsize=22,
                            fontweight='bold', color=self.colors['text'])
            return
        
        # Calculate positions based on C's traversal order
        positions = self.calculate_tree_positions_cstyle(data)
        
        # Draw edges first
        for i in range(1, len(data)):
            if i < len(positions):
                parent_idx = (i - 1) // 2
                if parent_idx < len(positions):
                    self.ax_main.plot([positions[parent_idx][0], positions[i][0]],
                                     [positions[parent_idx][1], positions[i][1]],
                                     color=self.colors['link_arrow'], linewidth=3,
                                     alpha=0.7, zorder=1)
        
        # Draw nodes
        for i, (val, h) in enumerate(zip(data, highlighted)):
            if i < len(positions):
                x, y = positions[i]
                col = self.get_highlight_color(h)
                edge_col = '#FFFFFF' if h != 0 else '#9F7AEA'
                edge_w = 4 if h != 0 else 2
                
                circle = Circle((x, y), 0.15, facecolor=col, alpha=0.9,
                              edgecolor=edge_col, linewidth=edge_w, zorder=3)
                self.ax_main.add_patch(circle)
                self.ax_main.text(x, y, str(val), ha='center', va='center',
                                fontsize=11, fontweight='bold', color='white', zorder=4)
        
        if positions:
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            x_margin = (max(x_coords) - min(x_coords)) * 0.2 + 0.5
            y_margin = (max(y_coords) - min(y_coords)) * 0.2 + 0.5
            self.ax_main.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
            self.ax_main.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        
        self.ax_main.set_xticks([])
        self.ax_main.set_yticks([])
        self.ax_main.set_title(step.get('description', ''), fontsize=14,
                              color=self.colors['text'], pad=15, fontweight='bold')
    
    def calculate_tree_positions_cstyle(self, data):
        """Calculate tree positions matching C's tree_to_array implementation"""
        if not data:
            return []
        
        positions = []
        for i in range(len(data)):
            level = 0
            temp = i + 1
            while temp > 1:
                temp //= 2
                level += 1
            
            level_start = 2 ** level - 1
            pos_in_level = i - level_start
            total_in_level = 2 ** level
            
            # Horizontal positioning
            x = (pos_in_level + 0.5) * (8.0 / total_in_level) - 4.0
            # Vertical positioning
            y = -level * 0.6
            
            positions.append((x, y))
        
        return positions
    
    def update_info_panel(self, step):
        self.ax_info.clear()
        self.ax_info.set_facecolor(self.colors['panel_bg'])
        
        complexity = step.get('complexity', 'N/A')
        progress = int((self.current_step + 1) / len(self.steps) * 100)
        
        self.ax_info.text(0.5, 0.95, '📊 Algorithm Info', ha='center', va='top',
                         fontsize=11, fontweight='bold', color=self.colors['text'],
                         transform=self.ax_info.transAxes)
        
        self.ax_info.text(0.5, 0.70, f'Step {self.current_step + 1} / {len(self.steps)}',
                         ha='center', va='center', fontsize=10, color='#4299E1',
                         fontweight='bold', transform=self.ax_info.transAxes,
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='#2D3748', alpha=0.8))
        
        self.ax_info.text(0.5, 0.50, f'{progress}% Complete', ha='center', va='center',
                         fontsize=9, color='#48BB78', transform=self.ax_info.transAxes)
        
        self.ax_info.text(0.5, 0.30, 'Time Complexity', ha='center', va='center',
                         fontsize=9, color='#A0AEC0', transform=self.ax_info.transAxes)
        
        self.ax_info.text(0.5, 0.15, complexity, ha='center', va='center',
                         fontsize=12, color='#48BB78', fontweight='bold',
                         transform=self.ax_info.transAxes,
                         bbox=dict(boxstyle='round,pad=0.4', facecolor='#2D3748', alpha=0.9))
        
        self.ax_info.set_xticks([])
        self.ax_info.set_yticks([])
        for spine in self.ax_info.spines.values():
            spine.set_edgecolor('#4A5568')
            spine.set_linewidth(1)
    
    def update_stats_panel(self):
        self.ax_stats.clear()
        self.ax_stats.set_facecolor(self.colors['panel_bg'])
        
        # Count operations based on C's action names
        comparisons = sum(1 for i in range(self.current_step + 1) 
                         if 'COMPARE' in self.steps[i].get('action', ''))
        swaps = sum(1 for i in range(self.current_step + 1) 
                   if 'SWAP' in self.steps[i].get('action', ''))
        
        self.ax_stats.text(0.5, 0.95, '📈 Live Statistics', ha='center', va='top',
                          fontsize=11, fontweight='bold', color=self.colors['text'],
                          transform=self.ax_stats.transAxes)
        
        stats = [('Comparisons', comparisons, '#4299E1'),
                ('Swaps', swaps, '#48BB78'),
                ('Steps', self.current_step + 1, '#ECC94B')]
        
        y_pos = 0.65
        for label, value, color in stats:
            self.ax_stats.text(0.15, y_pos, f'{label}:', ha='left', va='center',
                              fontsize=9, color='#CBD5E0', transform=self.ax_stats.transAxes)
            self.ax_stats.text(0.85, y_pos, str(value), ha='right', va='center',
                              fontsize=11, fontweight='bold', color=color,
                              transform=self.ax_stats.transAxes)
            y_pos -= 0.25
        
        self.ax_stats.set_xticks([])
        self.ax_stats.set_yticks([])
        for spine in self.ax_stats.spines.values():
            spine.set_edgecolor('#4A5568')
            spine.set_linewidth(1)
    
    def update_progress_bar(self):
        self.ax_progress.clear()
        self.ax_progress.set_facecolor(self.colors['panel_bg'])
        
        progress = (self.current_step + 1) / len(self.steps)
        
        self.ax_progress.barh(0, 1, height=0.5, color='#2D3748', alpha=0.5,
                             transform=self.ax_progress.transAxes)
        self.ax_progress.barh(0, progress, height=0.5, color='#48BB78', alpha=0.9,
                             transform=self.ax_progress.transAxes)
        
        self.ax_progress.text(0.5, 0, f'{int(progress*100)}%', ha='center', va='center',
                             fontsize=10, color='#F7FAFC', fontweight='bold',
                             transform=self.ax_progress.transAxes)
        
        self.ax_progress.set_xlim(0, 1)
        self.ax_progress.set_ylim(-0.5, 0.5)
        self.ax_progress.set_xticks([])
        self.ax_progress.set_yticks([])
        for spine in self.ax_progress.spines.values():
            spine.set_edgecolor('#4A5568')
            spine.set_linewidth(1)
    
    def update_learning_panel(self, step):
        self.ax_learn.clear()
        self.ax_learn.set_facecolor(self.colors['bg'])
        
        if not self.learning_mode:
            self.ax_learn.axis('off')
            return
        
        action = step.get('action', '')
        
        self.ax_learn.text(0.02, 0.85, '💡 Learning Mode - What\'s Happening?',
                          ha='left', va='top', fontsize=12, fontweight='bold',
                          color='#ECC94B', transform=self.ax_learn.transAxes)
        
        explanation = self.get_explanation(action)
        
        self.ax_learn.text(0.05, 0.55, explanation, ha='left', va='top',
                          fontsize=10, color='#E2E8F0', wrap=True,
                          transform=self.ax_learn.transAxes,
                          bbox=dict(boxstyle='round,pad=0.8', facecolor='#1A202C', alpha=0.9))
        
        self.ax_learn.set_xticks([])
        self.ax_learn.set_yticks([])
        for spine in self.ax_learn.spines.values():
            spine.set_edgecolor('#4299E1')
            spine.set_linewidth(2)
    
    def update_code_panel(self, step):
        self.ax_code.clear()
        self.ax_code.set_facecolor(self.colors['dark_bg'])
        
        action = step.get('action', '')
        code = self.get_pseudocode(action)
        
        self.ax_code.text(0.02, 0.92, '< Code />', ha='left', va='top',
                         fontsize=11, fontweight='bold', color='#4299E1',
                         transform=self.ax_code.transAxes)
        
        lines = code.split('\n')
        y_pos = 0.75
        for line in lines[:8]:
            self.ax_code.text(0.05, y_pos, line, ha='left', va='top',
                            fontsize=8, color='#48BB78', family='monospace',
                            transform=self.ax_code.transAxes)
            y_pos -= 0.12
        
        self.ax_code.set_xticks([])
        self.ax_code.set_yticks([])
        for spine in self.ax_code.spines.values():
            spine.set_edgecolor('#2D3748')
            spine.set_linewidth(1)
    
    def get_explanation(self, action):
        """Explanations matching C's exact action names"""
        explanations = {
            'BUBBLE_COMPARE': 'Comparing adjacent elements in Bubble Sort.',
            'BUBBLE_SWAP': 'Swapping adjacent elements because they are in wrong order.',
            'BUBBLE_COMPLETE': 'Bubble Sort completed! Array is now sorted.',
            
            'SELECTION_START': 'Starting new pass of Selection Sort.',
            'SELECTION_COMPARE': 'Comparing to find minimum element in unsorted portion.',
            'SELECTION_SWAP': 'Swapping minimum element with current position.',
            'SELECTION_COMPLETE': 'Selection Sort completed! Array is now sorted.',
            
            'INSERTION_START': 'Taking element to insert in correct position.',
            'INSERTION_SHIFT': 'Shifting elements right to make space.',
            'INSERTION_PLACE': 'Element placed in its correct sorted position.',
            'INSERTION_COMPLETE': 'Insertion Sort completed! Array is now sorted.',
            
            'QUICK_START': 'Starting Quick Sort - divide and conquer algorithm.',
            'QUICK_SUBARRAY': 'Processing a subarray - will partition around pivot.',
            'QUICK_PIVOT_SELECT': 'Selected rightmost element as pivot.',
            'QUICK_COMPARE': 'Comparing element with pivot for partitioning.',
            'QUICK_SWAP': 'Swapping elements during partitioning.',
            'QUICK_PIVOT_PLACE': 'Placing pivot in its final sorted position.',
            'QUICK_PIVOT_FINAL': 'Pivot is now in correct position, dividing array.',
            'QUICK_RECURSIVE': 'Recursively sorting left and right subarrays.',
            'QUICK_COMPLETE': 'Quick Sort completed! Array is now sorted.',
            
            'MERGE_START': 'Starting Merge Sort - divide and conquer algorithm.',
            'MERGE_DIVIDE': 'Dividing array into smaller subarrays.',
            'MERGE_READY': 'Both halves sorted, ready to merge them.',
            'MERGE_COMPARE': 'Comparing elements from both sorted subarrays.',
            'MERGE_TAKE': 'Taking smaller element and placing in merged array.',
            'MERGE_COPY': 'Copying remaining elements from subarray.',
            'MERGE_COMPLETE_SUB': 'Subarray successfully merged and sorted.',
            'MERGE_COMPLETE': 'Merge Sort completed! Array is now sorted.',
            
            'LINEAR_SEARCH': 'Checking each element sequentially from left to right.',
            'LINEAR_SEARCH_FOUND': 'Target element found!',
            'LINEAR_SEARCH_NOT_FOUND': 'Target not in array after checking all elements.',
            
            'BINARY_SEARCH': 'Checking middle element (array must be sorted).',
            'BINARY_SEARCH_FOUND': 'Target found using binary search!',
            'BINARY_SEARCH_NOT_FOUND': 'Target not found - search space exhausted.',
            
            'PUSH': 'Adding element to top of stack (LIFO).',
            'POP_BEFORE': 'About to remove element from top of stack.',
            'POP_AFTER': 'Element removed from stack top.',
            
            'ENQUEUE': 'Adding element to rear of queue (FIFO).',
            'DEQUEUE_BEFORE': 'About to remove element from front of queue.',
            'DEQUEUE_AFTER': 'Element removed from queue front.',
            
            'INSERT_BEGINNING': 'Inserted new node at the beginning of linked list.',
            'INSERT_END': 'Inserted new node at the end of linked list.',
            'INSERT_SEQUENTIAL': 'Adding element sequentially to linked list.',
            'SEARCH_LIST': 'Traversing linked list to find target element.',
            'SEARCH_LIST_FOUND': 'Target element found in linked list!',
            'SEARCH_LIST_NOT_FOUND': 'Target not found after traversing entire list.',
            
            'INSERT_BST': 'Inserting node in Binary Search Tree maintaining BST property.',
            'SEARCH_BST': 'Searching in BST by comparing with current node.',
            'SEARCH_BST_FOUND': 'Target found in Binary Search Tree!',
            'SEARCH_BST_NOT_FOUND': 'Target not found in BST.',
            'DELETE_BST_SEARCH': 'Searching for node to delete in BST.',
            'DELETE_BST_FOUND': 'Node found, proceeding with deletion.',
            'DELETE_BST_COMPLETE': 'Node deleted and BST structure maintained.',
            'INORDER_TRAVERSAL': 'Visiting BST nodes in sorted order (left-root-right).'
        }
        
        # Check for exact match first
        if action in explanations:
            return explanations[action]
        
        # Check for partial matches
        for key, exp in explanations.items():
            if key in action:
                return exp
        
        return 'Processing data structure operation step by step.'
    
    def get_pseudocode(self, action):
        """Pseudocode matching C implementations"""
        codes = {
            'BUBBLE': '''// Bubble Sort
for (i = 0; i < n-1; i++)
  for (j = 0; j < n-i-1; j++)
    if (arr[j] > arr[j+1])
      swap(&arr[j], &arr[j+1])''',
      
            'SELECTION': '''// Selection Sort
for (i = 0; i < n-1; i++)
  min_idx = i
  for (j = i+1; j < n; j++)
    if (arr[j] < arr[min_idx])
      min_idx = j
  swap(&arr[i], &arr[min_idx])''',
  
            'INSERTION': '''// Insertion Sort
for (i = 1; i < n; i++)
  key = arr[i]
  j = i - 1
  while (j >= 0 && arr[j] > key)
    arr[j+1] = arr[j]
    j--
  arr[j+1] = key''',
  
            'QUICK': '''// Quick Sort
quickSort(arr, low, high):
  if (low < high)
    pi = partition(arr, low, high)
    quickSort(arr, low, pi-1)
    quickSort(arr, pi+1, high)
    
partition: pivot = arr[high]
  i = low - 1
  for j = low to high-1
    if arr[j] < pivot
      swap(arr[++i], arr[j])
  swap(arr[i+1], arr[high])''',
  
            'MERGE': '''// Merge Sort
mergeSort(arr, left, right):
  if (left < right)
    mid = (left + right) / 2
    mergeSort(arr, left, mid)
    mergeSort(arr, mid+1, right)
    merge(arr, left, mid, right)
    
merge: combines two sorted halves
  into single sorted array''',
  
            'LINEAR': '''// Linear Search
for (i = 0; i < n; i++)
  if (arr[i] == target)
    return i  // found
return -1  // not found''',
  
            'BINARY': '''// Binary Search (sorted array)
left = 0, right = n-1
while (left <= right)
  mid = left + (right-left)/2
  if (arr[mid] == target)
    return mid
  else if (arr[mid] < target)
    left = mid + 1
  else
    right = mid - 1''',
  
            'PUSH': '''// Stack Push
push(stack, element):
  if (!isFull())
    stack.arr[++stack.top] = element''',
  
            'POP': '''// Stack Pop
pop(stack):
  if (!isEmpty())
    return stack.arr[stack.top--]''',
  
            'ENQUEUE': '''// Queue Enqueue
enqueue(queue, element):
  if (!isFull())
    if (front == -1) front = 0
    queue.arr[++rear] = element''',
  
            'DEQUEUE': '''// Queue Dequeue
dequeue(queue):
  if (!isEmpty())
    element = queue.arr[front++]
    if (front > rear)
      front = rear = -1
    return element''',
  
            'INSERT': '''// Linked List Insert
newNode = createNode(data)
if (head == NULL)
  head = newNode
else
  temp = head
  while (temp->next != NULL)
    temp = temp->next
  temp->next = newNode''',
  
            'SEARCH': '''// Search in List/Tree
current = head/root
while (current != NULL)
  if (current->data == target)
    return current
  current = current->next/left/right''',
  
            'BST': '''// Binary Search Tree
insert(root, data):
  if (root == NULL)
    return createNode(data)
  if (data < root->data)
    root->left = insert(root->left, data)
  else
    root->right = insert(root->right, data)
  return root'''
        }
        
        # Check for matches
        for key, code in codes.items():
            if key in action:
                return code
        
        return '// Processing data structure\nprocess(structure);'
    
    def update_visualization(self):
        if not self.steps:
            return
        
        step = self.steps[self.current_step]
        
        # Choose visualization based on structure type
        structure = self.config.get('structure_type', 'array')
        
        if self.is_sorting_algorithm() or 'SEARCH' in step.get('action', ''):
            self.visualize_sorting_bars(step)
        elif structure == 'stack' or self.config.get('is_stack', False):
            self.visualize_stack_vertical(step)
        elif structure == 'queue' or self.config.get('is_queue', False):
            self.visualize_queue_horizontal(step)
        elif structure == 'linked_list' or self.config.get('is_linked_list', False):
            self.visualize_linked_list_proper(step)
        elif structure == 'binary_search_tree' or self.config.get('is_binary_search_tree', False):
            self.visualize_binary_search_tree(step)
        else:
            self.visualize_sorting_bars(step)
        
        # Update all panels
        self.update_info_panel(step)
        self.update_stats_panel()
        self.update_progress_bar()
        self.update_learning_panel(step)
        self.update_code_panel(step)
        
        plt.draw()
    
    def animate(self, frame):
        if self.is_playing and self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_visualization()
        elif self.current_step >= len(self.steps) - 1:
            self.is_playing = False
            self.btn_play.label.set_text('↻ Restart')
        return []
    
    def toggle_play(self, event):
        if self.current_step >= len(self.steps) - 1:
            self.current_step = 0
            self.is_playing = True
            self.btn_play.label.set_text('⏸ Pause')
        else:
            self.is_playing = not self.is_playing
            self.btn_play.label.set_text('⏸ Pause' if self.is_playing else '▶ Play')
    
    def reset_animation(self, event):
        self.current_step = 0
        self.is_playing = False
        self.btn_play.label.set_text('▶ Play')
        self.update_visualization()
    
    def step_back(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.is_playing = False
            self.btn_play.label.set_text('▶ Play')
            self.update_visualization()
    
    def step_forward(self, event):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.is_playing = False
            self.btn_play.label.set_text('▶ Play')
            self.update_visualization()
    
    def toggle_learning_mode(self, event):
        self.learning_mode = not self.learning_mode
        print(f"💡 Learning Mode: {'ON' if self.learning_mode else 'OFF'}")
        self.update_visualization()
    
    def update_speed(self, val):
        self.speed = val
        if hasattr(self, 'ani'):
            self.ani.event_source.interval = int(1000 / self.speed)

def main():
    print("=" * 70)
    print("🎨 ALGORITHM VISUALIZER v9.0 - SYNCED WITH C")
    print("=" * 70)
    print("✅ EXACT MATCH with C Implementation:")
    print("   • All action names synchronized")
    print("   • Highlight values (0-4) properly mapped")
    print("   • Pointers displayed correctly")
    print("   • Quick Sort partition steps shown")
    print("   • Merge Sort divide/conquer visualized")
    print("   • BST structure matches C traversal")
    print("=" * 70)
    print("📊 Visualizations:")
    print("   • Sorting â†' Bar Format")
    print("   • Stack â†' Vertical (LIFO)")
    print("   • Queue â†' Horizontal (FIFO)")
    print("   • Linked List â†' Nodes with Arrows")
    print("   • BST â†' Tree Structure")
    print("=" * 70)
    
    if not os.path.exists('algorithm_steps.json'):
        print("❌ Error: algorithm_steps.json not found!")
        print("   Run the C program first to generate data files.")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists('algorithm_config.json'):
        print("❌ Error: algorithm_config.json not found!")
        print("   Run the C program first to generate data files.")
        input("Press Enter to exit...")
        return
    
    try:
        visualizer = AlgorithmVisualizer()
    except KeyboardInterrupt:
        print("\n⏹ Visualization stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()