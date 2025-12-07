"""
3D Room Visualization Module
Provides interactive 3D room visualization and building interface.
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Wall:
    """Represents a wall in the room."""
    name: str
    material: str
    # Wall positions: start (x1, y1, z1), end (x2, y2, z2)
    x_coords: Tuple[float, float]  # (x1, x2)
    y_coords: Tuple[float, float]  # (y1, y2)
    z_coords: Tuple[float, float]  # (z1, z2)

class Room3DVisualizer:
    """Creates 3D visualizations of room layouts."""
    
    def __init__(self, length: float, width: float, height: float):
        """
        Initialize room visualizer.
        
        Args:
            length (float): Room length (x-axis)
            width (float): Room width (y-axis)
            height (float): Room height (z-axis)
        """
        self.length = length
        self.width = width
        self.height = height
        self.walls = {}
        self.speakers = []
        self.listeners = []
        self._init_default_walls()
    
    def _init_default_walls(self):
        """Initialize default wall structure."""
        self.walls = {
            'floor': Wall('Floor', 'hardwood', (0, self.length), (0, self.width), (0, 0)),
            'ceiling': Wall('Ceiling', 'drywall', (0, self.length), (0, self.width), (self.height, self.height)),
            'wall_front': Wall('Front Wall', 'drywall', (0, self.length), (0, 0), (0, self.height)),
            'wall_back': Wall('Back Wall', 'drywall', (0, self.length), (self.width, self.width), (0, self.height)),
            'wall_left': Wall('Left Wall', 'drywall', (0, 0), (0, self.width), (0, self.height)),
            'wall_right': Wall('Right Wall', 'drywall', (self.length, self.length), (0, self.width), (0, self.height)),
        }
    
    def update_wall_material(self, wall_name: str, material: str):
        """Update material for a specific wall."""
        if wall_name in self.walls:
            self.walls[wall_name].material = material
    
    def add_speaker(self, x: float, y: float, z: float, name: str = "Speaker"):
        """Add a speaker to the room."""
        self.speakers.append({'x': x, 'y': y, 'z': z, 'name': name})
    
    def add_listener(self, x: float, y: float, z: float, name: str = "Listener"):
        """Add a listener position to the room."""
        self.listeners.append({'x': x, 'y': y, 'z': z, 'name': name})
    
    def clear_speakers(self):
        """Clear all speakers."""
        self.speakers = []
    
    def clear_listeners(self):
        """Clear all listeners."""
        self.listeners = []
    
    def get_material_color(self, material: str) -> str:
        """Get color for a material."""
        color_map = {
            'drywall': 'lightgray',
            'hardwood': '#8B4513',
            'carpet': '#FF6347',
            'concrete': '#808080',
            'glass': 'rgba(173, 216, 230, 0.5)',
            'curtain': '#8B008B',
        }
        return color_map.get(material.lower(), 'lightgray')
    
    def create_3d_visualization(self) -> go.Figure:
        """
        Create interactive 3D visualization of the room.
        
        Returns:
            go.Figure: Plotly 3D figure
        """
        fig = go.Figure()
        
        # Define room corners for walls
        l, w, h = self.length, self.width, self.height
        
        # Floor
        floor = self.walls['floor']
        fig.add_trace(go.Surface(
            x=[[0, l], [0, l]],
            y=[[0, 0], [w, w]],
            z=[[0, 0], [0, 0]],
            colorscale=self._get_colorscale(floor.material),
            showscale=False,
            name=f'Floor ({floor.material})',
            opacity=0.8
        ))
        
        # Ceiling
        ceiling = self.walls['ceiling']
        # draw ceiling with slightly higher opacity and after walls so it's visible from most views
        # we'll add ceiling later (after walls) to improve visibility
        
        # Front wall (y=0)
        wall_front = self.walls['wall_front']
        fig.add_trace(go.Surface(
            x=[[0, l], [0, l]],
            y=[[0, 0], [0, 0]],
            z=[[0, 0], [h, h]],
            colorscale=self._get_colorscale(wall_front.material),
            showscale=False,
            name=f'Front Wall ({wall_front.material})',
            opacity=0.85
        ))
        
        # Back wall (y=w)
        wall_back = self.walls['wall_back']
        fig.add_trace(go.Surface(
            x=[[0, l], [0, l]],
            y=[[w, w], [w, w]],
            z=[[0, 0], [h, h]],
            colorscale=self._get_colorscale(wall_back.material),
            showscale=False,
            name=f'Back Wall ({wall_back.material})',
            opacity=0.85
        ))
        
        # Left wall (x=0)
        wall_left = self.walls['wall_left']
        fig.add_trace(go.Surface(
            x=[[0, 0], [0, 0]],
            y=[[0, 0], [w, w]],
            z=[[0, 0], [h, h]],
            colorscale=self._get_colorscale(wall_left.material),
            showscale=False,
            name=f'Left Wall ({wall_left.material})',
            opacity=0.85
        ))
        
        # Right wall (x=l)
        wall_right = self.walls['wall_right']
        fig.add_trace(go.Surface(
            x=[[l, l], [l, l]],
            y=[[0, 0], [w, w]],
            z=[[0, 0], [h, h]],
            colorscale=self._get_colorscale(wall_right.material),
            showscale=False,
            name=f'Right Wall ({wall_right.material})',
            opacity=0.85
        ))
        
        # Add speakers
        for speaker in self.speakers:
            fig.add_trace(go.Scatter3d(
                x=[speaker['x']],
                y=[speaker['y']],
                z=[speaker['z']],
                mode='markers+text',
                marker=dict(size=10, color='red', symbol='diamond'),
                text=[speaker['name']],
                textposition='top center',
                name='Speaker',
                hoverinfo='text',
                hovertext=f"{speaker['name']}<br>({speaker['x']:.1f}, {speaker['y']:.1f}, {speaker['z']:.1f})"
            ))
        
        # Add listeners
        for listener in self.listeners:
            fig.add_trace(go.Scatter3d(
                x=[listener['x']],
                y=[listener['y']],
                z=[listener['z']],
                mode='markers+text',
                marker=dict(size=10, color='blue', symbol='circle'),
                text=[listener['name']],
                textposition='top center',
                name='Listener',
                hoverinfo='text',
                hovertext=f"{listener['name']}<br>({listener['x']:.1f}, {listener['y']:.1f}, {listener['z']:.1f})"
            ))
        
        # Draw top-down plan lines on the floor so user sees the 2D plan within 3D view
        # room boundary
        fig.add_trace(go.Scatter3d(
            x=[0, self.length, self.length, 0, 0],
            y=[0, 0, self.width, self.width, 0],
            z=[0.02, 0.02, 0.02, 0.02, 0.02],
            mode='lines',
            line=dict(color='black', width=3),
            name='Room Plan (top-down)',
            hoverinfo='skip'
        ))

        # custom walls drawn as simple floor-level lines (no 3D surfaces to avoid collapse)
        if hasattr(self, 'custom_walls') and self.custom_walls:
            for w in self.custom_walls:
                x1, y1, x2, y2 = w['x1'], w['y1'], w['x2'], w['y2']
                fig.add_trace(go.Scatter3d(
                    x=[x1, x2], y=[y1, y2], z=[0.02, 0.02], mode='lines',
                    line=dict(color=self.get_material_color(w['material']), width=5),
                    name=w['name'],
                    hoverinfo='text',
                    hovertext=f"{w['name']} ({w['material']})"
                ))

        # Update layout
        fig.update_layout(
            title=f'3D Room Visualization ({self.length}m × {self.width}m × {self.height}m)',
            scene=dict(
                xaxis=dict(title='Length (m)', range=[0, l]),
                yaxis=dict(title='Width (m)', range=[0, w]),
                zaxis=dict(title='Height (m)', range=[0, h]),
                aspectmode='data'
            ),
            width=1000,
            height=700,
            hovermode='closest',
            showlegend=True
        )
        # add ceiling as last surface so it renders on top and is visible from camera angles
        fig.add_trace(go.Surface(
            x=[[0, l], [0, l]],
            y=[[0, 0], [w, w]],
            z=[[h, h], [h, h]],
            colorscale=self._get_colorscale(ceiling.material),
            showscale=False,
            name=f'Ceiling ({ceiling.material})',
            opacity=0.95
        ))

        return fig
    
    def _get_colorscale(self, material: str) -> str:
        """Get colorscale for material."""
        colorscale_map = {
            'drywall': 'Greys',
            'hardwood': 'Viridis',
            'carpet': 'Reds',
            'concrete': 'Greys',
            'glass': 'Blues',
            'curtain': 'Purples',
        }
        return colorscale_map.get(material.lower(), 'Greys')
    
    def get_room_summary(self) -> Dict:
        """Get room summary information."""
        return {
            'dimensions': f"{self.length}m × {self.width}m × {self.height}m",
            'volume': self.length * self.width * self.height,
            'walls': {name: wall.material for name, wall in self.walls.items()},
            'speakers': len(self.speakers),
            'listeners': len(self.listeners)
        }
    
    def export_room_config(self) -> Dict:
        """Export room configuration including custom walls."""
        config = {
            'dimensions': {
                'length': self.length,
                'width': self.width,
                'height': self.height
            },
            'materials': {name: wall.material for name, wall in self.walls.items()},
            'speakers': self.speakers,
            'listeners': self.listeners,
            'custom_walls': getattr(self, 'custom_walls', [])
        }
        return config
    
    def import_room_config(self, config: Dict):
        """Import room configuration including custom walls."""
        if 'materials' in config:
            for wall_name, material in config['materials'].items():
                self.update_wall_material(wall_name, material)
        
        if 'speakers' in config:
            self.clear_speakers()
            for speaker in config['speakers']:
                self.add_speaker(speaker['x'], speaker['y'], speaker['z'], speaker.get('name', 'Speaker'))
        
        if 'listeners' in config:
            self.clear_listeners()
            for listener in config['listeners']:
                self.add_listener(listener['x'], listener['y'], listener['z'], listener.get('name', 'Listener'))
        
        if 'custom_walls' in config:
            self.custom_walls = []
            for w in config['custom_walls']:
                self.add_custom_wall(w['x1'], w['y1'], w['x2'], w['y2'], height=w.get('height'), material=w.get('material', 'drywall'), name=w.get('name'))

    # ------------------ Custom wall support (top-down planar walls) ------------------
    def add_custom_wall(self, x1: float, y1: float, x2: float, y2: float, height: float = None, material: str = 'drywall', name: str = None):
        """Add an arbitrary wall segment defined on the floor (top-down coordinates).

        Args:
            x1, y1: start point on floor plane (meters)
            x2, y2: end point on floor plane (meters)
            height: wall height (m). If None, uses room height.
            material: material name for coloring
            name: optional wall name
        """
        if height is None:
            height = self.height
        wall = {
            'name': name or f'custom_wall_{len(self.walls)}',
            'material': material,
            'x1': float(x1), 'y1': float(y1),
            'x2': float(x2), 'y2': float(y2),
            'height': float(height)
        }
        # store in walls dict with unique key
        key = wall['name']
        idx = 1
        while key in self.walls:
            key = f"{wall['name']}_{idx}"
            idx += 1
        self.walls[key] = Wall(wall['name'], material, (min(x1, x2), max(x1, x2)), (min(y1, y2), max(y1, y2)), (0, float(height)))
        # also keep raw custom list for 2D planning
        if not hasattr(self, 'custom_walls'):
            self.custom_walls = []
        self.custom_walls.append(wall)

    def remove_custom_wall(self, name: str):
        """Remove a custom wall by name."""
        if hasattr(self, 'custom_walls'):
            self.custom_walls = [w for w in self.custom_walls if w['name'] != name]
        if name in self.walls:
            del self.walls[name]

    def get_2d_plan_figure(self) -> go.Figure:
        """Return a top-down 2D Plotly figure showing walls, speakers, and listeners."""
        fig = go.Figure()
        # floor rectangle
        fig.add_trace(go.Scatter(
            x=[0, self.length, self.length, 0, 0],
            y=[0, 0, self.width, self.width, 0],
            mode='lines', fill='toself', name='room', line=dict(color='black')
        ))
        # custom walls
        if hasattr(self, 'custom_walls'):
            for w in self.custom_walls:
                fig.add_trace(go.Scatter(
                    x=[w['x1'], w['x2']],
                    y=[w['y1'], w['y2']],
                    mode='lines', name=w['name'], line=dict(color=self.get_material_color(w['material']), width=6)
                ))
        # speakers
        for s in self.speakers:
            fig.add_trace(go.Scatter(x=[s['x']], y=[s['y']], mode='markers', marker=dict(size=12, color='red'), name=s.get('name', 'Speaker')))
        # listeners
        for l in self.listeners:
            fig.add_trace(go.Scatter(x=[l['x']], y=[l['y']], mode='markers', marker=dict(size=10, color='blue'), name=l.get('name', 'Listener')))
        fig.update_layout(xaxis=dict(range=[-0.5, self.length + 0.5]), yaxis=dict(range=[-0.5, self.width + 0.5]),
                          width=700, height=700, title='Top-down Room Plan')
        fig.update_yaxes(autorange='reversed')
        return fig

    def simulate_wave_2d(self, duration: float = 5.0, fps: int = 20, speed: float = 0.5) -> go.Figure:
        """Simulate expanding wavefronts in 2D top-down view with amplitude attenuation.

        Args:
            duration: seconds of simulated time
            fps: frames per second
            speed: propagation speed (m per frame, scaled for visualization)
        """
        # Start with base figure
        fig = self.get_2d_plan_figure()
        
        frames = []
        num_frames = int(duration * fps)
        times = np.linspace(0, duration, num_frames)
        theta = np.linspace(0, 2*np.pi, 128)

        # Build sources list
        sources = []
        for s in self.speakers:
            sources.append({'x': s['x'], 'y': s['y'], 'amp': 1.0, 'order': 0})

        # Single-order image sources from each wall
        if hasattr(self, 'custom_walls') and self.custom_walls:
            for w in self.custom_walls:
                x1, y1, x2, y2 = w['x1'], w['y1'], w['x2'], w['y2']
                dx, dy = x2 - x1, y2 - y1
                if dx*dx + dy*dy < 1e-6:
                    continue
                for s in self.speakers:
                    px, py = s['x'], s['y']
                    ux, uy = dx, dy
                    ux2 = ux*ux + uy*uy
                    t = ((px - x1) * ux + (py - y1) * uy) / ux2
                    projx, projy = x1 + t * ux, y1 + t * uy
                    rx, ry = 2*projx - px, 2*projy - py
                    sources.append({'x': rx, 'y': ry, 'amp': 0.6, 'order': 1})

        # Generate frames
        for frame_idx, ti in enumerate(times):
            frame_traces = []
            r = speed * frame_idx
            
            for src in sources:
                if r > 0.01:
                    xs = src['x'] + r * np.cos(theta)
                    ys = src['y'] + r * np.sin(theta)
                    alpha = max(0.1, src['amp'] * (1.0 - frame_idx / max(1, num_frames - 1)))
                    color = f'rgba(0,100,255,{alpha:.2f})'
                    frame_traces.append(go.Scatter(
                        x=xs, y=ys, mode='lines',
                        line=dict(width=2, color=color),
                        showlegend=False, hoverinfo='skip'
                    ))
            
            frame = go.Frame(data=frame_traces, name=str(ti))
            frames.append(frame)

        # Add initial frame traces to figure
        if frames and frames[0].data:
            for tr in frames[0].data:
                fig.add_trace(tr)
        
        # Attach frames
        fig.frames = frames
        
        # Add animation controls
        fig.update_layout(
            updatemenus=[dict(
                type='buttons', showactive=False, x=0.0, y=0.0,
                buttons=[
                    dict(label='▶ Play', method='animate', args=[None, {'frame': {'duration': int(1000/fps), 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 0}}]),
                    dict(label='⏸ Pause', method='animate', args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate', 'transition': {'duration': 0}}])
                ]
            )],
            sliders=[dict(
                active=0, currentvalue=dict(prefix='t = ', suffix='s', visible=True, xanchor='center'),
                steps=[dict(args=[[f.name], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}], label=f'{float(f.name):.2f}s') for f in frames],
                x=0.1, y=0.0, len=0.9, xanchor='left', yanchor='top'
            )] if frames else []
        )
        
        return fig

    def simulate_wave_3d(self, duration: float = 5.0, fps: int = 20, max_reflections: int = 3) -> go.Figure:
        """Simulate expanding wavefronts in 3D with simple expanding rings.

        Args:
            duration: seconds of simulated time
            fps: frames per second
            max_reflections: ignored for now (simplification)
        """
        # Start with base 3D room
        fig = self.create_3d_visualization()

        frames = []
        num_frames = int(duration * fps)
        theta = np.linspace(0, 2 * np.pi, 64)  # fewer points = cleaner animation
        speed = 0.5  # m per frame

        # Only animate primary speaker sources (no complex reflections)
        sources = []
        for s in self.speakers:
            sources.append({'x': s['x'], 'y': s['y'], 'z': s.get('z', 1.5), 'amp': 1.0})

        # Generate frames with expanding rings
        for frame_idx in range(num_frames):
            frame_traces = []
            r = speed * frame_idx

            if r > 0.05:  # only show rings when radius is meaningful
                for src in sources:
                    xs = src['x'] + r * np.cos(theta)
                    ys = src['y'] + r * np.sin(theta)
                    zs = np.full_like(xs, src['z'])
                    
                    # Fade out as time progresses
                    alpha = max(0.3, 1.0 - (frame_idx / num_frames))
                    color = f'rgba(0,150,255,{alpha:.2f})'
                    
                    frame_traces.append(go.Scatter3d(
                        x=xs, y=ys, z=zs, mode='lines',
                        line=dict(color=color, width=3),
                        showlegend=False, hoverinfo='skip'
                    ))

            frame = go.Frame(data=frame_traces, name=str(frame_idx))
            frames.append(frame)

        # Add initial frame (empty or first ring)
        if frames and len(frames) > 1:
            for tr in frames[1].data:  # use frame 1 instead of 0 so animation starts visible
                fig.add_trace(tr)

        fig.frames = frames

        # Add animation controls
        fig.update_layout(
            updatemenus=[dict(
                type='buttons', showactive=False, x=0.0, y=0.0,
                buttons=[
                    dict(label='▶ Play', method='animate', args=[None, {'frame': {'duration': int(1000/fps), 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 0}}]),
                    dict(label='⏸ Pause', method='animate', args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate', 'transition': {'duration': 0}}])
                ]
            )]
        )

        return fig

class RoomPresets:
    """Pre-defined room configurations."""
    
    @staticmethod
    def get_living_room() -> Dict:
        """Standard living room (5m × 4m × 3m)."""
        return {
            'name': 'Living Room',
            'dimensions': {'length': 5, 'width': 4, 'height': 3},
            'materials': {
                'floor': 'hardwood',
                'ceiling': 'drywall',
                'wall_front': 'drywall',
                'wall_back': 'drywall',
                'wall_left': 'drywall',
                'wall_right': 'drywall'
            },
            'speakers': [{'x': 1, 'y': 0.5, 'z': 1, 'name': 'Speaker'}],
            'listeners': [{'x': 2.5, 'y': 2, 'z': 1.2, 'name': 'Listener'}]
        }
    
    @staticmethod
    def get_bedroom() -> Dict:
        """Standard bedroom (4m × 3.5m × 2.8m)."""
        return {
            'name': 'Bedroom',
            'dimensions': {'length': 4, 'width': 3.5, 'height': 2.8},
            'materials': {
                'floor': 'carpet',
                'ceiling': 'drywall',
                'wall_front': 'drywall',
                'wall_back': 'drywall',
                'wall_left': 'drywall',
                'wall_right': 'drywall'
            },
            'speakers': [{'x': 1, 'y': 0.5, 'z': 1, 'name': 'Speaker'}],
            'listeners': [{'x': 2, 'y': 1.8, 'z': 1, 'name': 'Listener'}]
        }
    
    @staticmethod
    def get_office() -> Dict:
        """Standard office (4m × 3m × 2.8m)."""
        return {
            'name': 'Office',
            'dimensions': {'length': 4, 'width': 3, 'height': 2.8},
            'materials': {
                'floor': 'concrete',
                'ceiling': 'drywall',
                'wall_front': 'drywall',
                'wall_back': 'drywall',
                'wall_left': 'drywall',
                'wall_right': 'drywall'
            },
            'speakers': [{'x': 0.5, 'y': 0.5, 'z': 1, 'name': 'Speaker'}],
            'listeners': [{'x': 2, 'y': 1.5, 'z': 1, 'name': 'Listener'}]
        }
    
    @staticmethod
    def get_studio() -> Dict:
        """Professional studio (6m × 5m × 3.5m)."""
        return {
            'name': 'Studio',
            'dimensions': {'length': 6, 'width': 5, 'height': 3.5},
            'materials': {
                'floor': 'concrete',
                'ceiling': 'drywall',
                'wall_front': 'curtain',
                'wall_back': 'curtain',
                'wall_left': 'curtain',
                'wall_right': 'curtain'
            },
            'speakers': [{'x': 1, 'y': 2.5, 'z': 1.5, 'name': 'Speaker'}],
            'listeners': [{'x': 3, 'y': 2.5, 'z': 1.5, 'name': 'Listener'}]
        }
    
    @staticmethod
    def get_all_presets() -> Dict[str, Dict]:
        """Get all available presets."""
        return {
            'living_room': RoomPresets.get_living_room(),
            'bedroom': RoomPresets.get_bedroom(),
            'office': RoomPresets.get_office(),
            'studio': RoomPresets.get_studio()
        }
