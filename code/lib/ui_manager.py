"""
Main UI Manager for AudioEmm Streamlit Application
Manages the interface and routing between equalizer and room simulator.
"""

import streamlit as st
import tempfile
import os
import json
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
from lib.audio import AudioAnalyzer
from lib.equalizer import DeviceEqualizer
from lib.room_simulator import RoomSimulator, RoomDimensions, Vector3D, Room3DVisualizer, RoomPresets
from lib.utils import ConfigManager

class UIManager:
    """Manages the Streamlit UI for AudioEmm."""
    
    def __init__(self):
        """Initialize the UI Manager."""
        self.config_manager = ConfigManager()
        self.analyzer = AudioAnalyzer()
        self.eq = DeviceEqualizer()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize Streamlit session state."""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Device Equalizer"
        if 'eq_calculated' not in st.session_state:
            st.session_state.eq_calculated = False
        if 'room_config' not in st.session_state:
            room_cfg = self.config_manager.get('room_settings', {})
            st.session_state.room_config = room_cfg
        if 'show_3d' not in st.session_state:
            st.session_state.show_3d = False  # On-demand 3D rendering
        if 'simulation_done' not in st.session_state:
            st.session_state.simulation_done = False
        if 'last_wave_fig_2d' not in st.session_state:
            st.session_state.last_wave_fig_2d = None
        if 'last_wave_fig_3d' not in st.session_state:
            st.session_state.last_wave_fig_3d = None
    
    def run(self):
        """Run the main Streamlit application."""
        st.set_page_config(
            page_title="AudioEmm",
            page_icon="🎵",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 3em;
            font-weight: bold;
            color: #1DB954;
            text-align: center;
        }
        .feature-card {
            padding: 20px;
            border-radius: 10px;
            background: #f0f0f0;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        with st.sidebar:
            st.title("🎵 AudioEmm")
            page = st.radio(
                "Navigate to:",
                ["Device Equalizer", "Room Simulator", "About"]
            )
            st.session_state.current_page = page
        
        # Main content routing
        if st.session_state.current_page == "Device Equalizer":
            self.render_equalizer_page()
        elif st.session_state.current_page == "Room Simulator":
            self.render_room_page()
        elif st.session_state.current_page == "About":
            self.render_about_page()
    
    def render_equalizer_page(self):
        """Render the device equalizer page."""
        st.markdown('<h1 class="main-header">🎧 Device Equalizer</h1>', unsafe_allow_html=True)
        
        st.write("""
        Select your current audio device (Source) and the device you want to emulate (Target).
        AudioEmm will analyze their frequency responses and create an equalizer to make your 
        source device sound like the target device.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📱 Source Device (What you have)")
            source_audio = st.file_uploader(
                "Upload reference audio from your device",
                type=['mp3', 'wav', 'flac'],
                key='source_audio'
            )
            source_name = st.text_input(
                "Source device name",
                value="My Device",
                key='source_name'
            )
        
        with col2:
            st.subheader("🎯 Target Device (What you want)")
            target_audio = st.file_uploader(
                "Upload reference audio from target device",
                type=['mp3', 'wav', 'flac'],
                key='target_audio'
            )
            target_name = st.text_input(
                "Target device name",
                value="Target Device",
                key='target_name'
            )
        
        # Analyze and calculate equalizer
        if st.button("🔍 Analyze & Calculate Equalizer", key='calc_eq'):
            if source_audio is None or target_audio is None:
                st.error("⚠️ Please upload audio files for both devices!")
            else:
                with st.spinner("Analyzing frequency responses..."):
                    try:
                        # Save uploaded files temporarily
                        with tempfile.TemporaryDirectory() as tmpdir:
                            source_path = os.path.join(tmpdir, 'source_audio.wav')
                            target_path = os.path.join(tmpdir, 'target_audio.wav')
                            
                            with open(source_path, 'wb') as f:
                                f.write(source_audio.getbuffer())
                            with open(target_path, 'wb') as f:
                                f.write(target_audio.getbuffer())
                            
                            # Load and analyze devices
                            self.eq.set_source_device(source_path, source_name)
                            self.eq.set_target_device(target_path, target_name)
                            
                            # Calculate EQ curve
                            self.eq.calculate_eq_curve()
                            st.session_state.eq_calculated = True
                            
                            st.success("✅ Equalizer calculated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
        
        # Display results if EQ has been calculated
        if st.session_state.eq_calculated:
            st.divider()
            st.subheader("📊 Analysis Results")
            
            try:
                comparison = self.eq.get_device_comparison()
            except ValueError:
                st.warning("Please upload both source and target audio files to see results.")
                return
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(comparison['source_frequencies'], comparison['source_db'], 
                   label=source_name, linewidth=2, color='blue')
            ax.plot(comparison['target_frequencies'], comparison['target_db'], 
                   label=target_name, linewidth=2, color='orange')
            
            ax.set_xlabel('Frequency (Hz)', fontsize=12)
            ax.set_ylabel('Magnitude (dB)', fontsize=12)
            ax.set_title('Frequency Response Comparison', fontsize=14, fontweight='bold')
            ax.set_xscale('log')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            
            # Show EQ curve
            st.subheader("🎚️ Required Equalization Curve")
            
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            ax2.plot(comparison['target_frequencies'], comparison['eq_curve'], 
                    linewidth=2, color='green')
            ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax2.fill_between(comparison['target_frequencies'], comparison['eq_curve'], 0, 
                            alpha=0.3, color='green')
            
            ax2.set_xlabel('Frequency (Hz)', fontsize=12)
            ax2.set_ylabel('Gain (dB)', fontsize=12)
            ax2.set_title('EQ Curve to Apply to Source Device', fontsize=14, fontweight='bold')
            ax2.set_xscale('log')
            ax2.grid(True, alpha=0.3)
            
            st.pyplot(fig2)
            
            # Interpretation
            with st.expander("📖 How to interpret the EQ curve"):
                st.write("""
                - **Positive values**: Boost these frequencies
                - **Negative values**: Cut these frequencies
                - **Peak values**: The most significant adjustments needed
                
                The EQ curve tells you exactly how much to boost or cut each frequency 
                to make your device sound like the target device.
                """)
    
    def render_room_page(self):
        """Render the room simulator page with 3D room builder."""
        st.markdown('<h1 class="main-header">🏠 Room Acoustic Simulator</h1>', unsafe_allow_html=True)
        
        st.write("""
        Build your room visually! Design the dimensions, choose materials, and place speakers/listeners.
        Choose from presets or create a custom room from scratch.
        """)
        
        # Initialize session state for room building
        if 'visualizer' not in st.session_state:
            preset = RoomPresets.get_living_room()
            st.session_state.visualizer = Room3DVisualizer(
                preset['dimensions']['length'],
                preset['dimensions']['width'],
                preset['dimensions']['height']
            )
            for name, mat in preset['materials'].items():
                st.session_state.visualizer.update_wall_material(name, mat)
        
        # Room selection tabs
        tab1, tab2, tab3 = st.tabs(["🎨 Room Builder", "🏠 Presets", "📊 Simulation"])
        
        # ==================== ROOM BUILDER TAB ====================
        with tab1:
            st.subheader("Build Your Custom Room")
            
            # Room dimensions section
            col1, col2, col3 = st.columns(3)
            with col1:
                length = st.slider(
                    "Length (m)", 1.0, 20.0, float(st.session_state.visualizer.length), step=0.1, key='rb_length'
                )
            with col2:
                width = st.slider(
                    "Width (m)", 1.0, 20.0, float(st.session_state.visualizer.width), step=0.1, key='rb_width'
                )
            with col3:
                height = st.slider(
                    "Height (m)", 1.0, 10.0, float(st.session_state.visualizer.height), step=0.1, key='rb_height'
                )
            
            # Update visualizer dimensions
            if (length != st.session_state.visualizer.length or 
                width != st.session_state.visualizer.width or 
                height != st.session_state.visualizer.height):
                st.session_state.visualizer = Room3DVisualizer(length, width, height)
            
            st.divider()
            
            # Materials selection
            st.subheader("🪵 Select Wall Materials")
            
            col1, col2, col3 = st.columns(3)
            materials = ["hardwood", "carpet", "concrete", "drywall", "glass", "curtain"]
            
            with col1:
                st.write("**Horizontal Surfaces**")
                floor_mat = st.selectbox("Floor", materials, key='builder_floor')
                st.session_state.visualizer.update_wall_material('floor', floor_mat)
                
                ceiling_mat = st.selectbox("Ceiling", materials, key='builder_ceiling')
                st.session_state.visualizer.update_wall_material('ceiling', ceiling_mat)
            
            with col2:
                st.write("**Front & Back Walls**")
                wall_front_mat = st.selectbox("Front Wall", materials, key='builder_front')
                st.session_state.visualizer.update_wall_material('wall_front', wall_front_mat)
                
                wall_back_mat = st.selectbox("Back Wall", materials, key='builder_back')
                st.session_state.visualizer.update_wall_material('wall_back', wall_back_mat)
            
            with col3:
                st.write("**Side Walls**")
                wall_left_mat = st.selectbox("Left Wall", materials, key='builder_left')
                st.session_state.visualizer.update_wall_material('wall_left', wall_left_mat)
                
                wall_right_mat = st.selectbox("Right Wall", materials, key='builder_right')
                st.session_state.visualizer.update_wall_material('wall_right', wall_right_mat)
            
            st.divider()

            # Draw / Add custom walls (drag-and-drop style)
            st.subheader("✏️ Draw Walls")
            st.write("Add walls by entering start and end coordinates, then select material.")
            
            wall_col1, wall_col2 = st.columns(2)
            with wall_col1:
                st.write("**Start Point**")
                x1 = st.number_input("X (m)", min_value=0.0, max_value=100.0, value=0.5, step=0.1, key='wall_x1')
                y1 = st.number_input("Y (m)", min_value=0.0, max_value=100.0, value=0.5, step=0.1, key='wall_y1')
            
            with wall_col2:
                st.write("**End Point**")
                x2 = st.number_input("X (m)", min_value=0.0, max_value=100.0, value=2.0, step=0.1, key='wall_x2')
                y2 = st.number_input("Y (m)", min_value=0.0, max_value=100.0, value=1.5, step=0.1, key='wall_y2')
            
            wall_cfg_col1, wall_cfg_col2 = st.columns(2)
            with wall_cfg_col1:
                wh = st.number_input("Wall Height (m)", min_value=0.1, max_value=10.0, value=2.5, step=0.1, key='wall_h')
                wmat = st.selectbox("Material", ["drywall", "concrete", "glass", "curtain", "carpet"], key='wall_mat')
            
            with wall_cfg_col2:
                wname = st.text_input("Name (optional)", value=f"wall_{len(getattr(st.session_state.visualizer, 'custom_walls', []))+1}")
                if st.button("➕ Add Wall", use_container_width=True):
                    st.session_state.visualizer.add_custom_wall(x1, y1, x2, y2, height=wh, material=wmat, name=wname)
                    st.success(f"✓ Wall '{wname}' added!")
            
            # Show existing walls
            if hasattr(st.session_state.visualizer, 'custom_walls') and st.session_state.visualizer.custom_walls:
                st.write("**Walls in room:**")
                for w in st.session_state.visualizer.custom_walls:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.caption(f"📍 {w['name']} ({w['material']})")
                    with col2:
                        st.caption(f"({w['x1']:.1f},{w['y1']:.1f}) → ({w['x2']:.1f},{w['y2']:.1f})")
                    with col3:
                        if st.button("🗑", key=f"del_{w['name']}", help="Delete wall"):
                            st.session_state.visualizer.remove_custom_wall(w['name'])
                            st.rerun()

            st.divider()

            # 2D Room Plan preview
            st.subheader("📐 2D Room Plan (Preview)")
            plan_fig = st.session_state.visualizer.get_2d_plan_figure()
            st.plotly_chart(plan_fig, use_container_width=True, key='builder_plan_fig')

            st.divider()

            # Render button for 3D room (on-demand rendering)
            st.subheader("🎨 Render 3D Room")
            st.write("Click the render button below to generate the 3D visualization. Large rooms may take a few seconds.")
            if st.button("🔄 Render 3D Room", use_container_width=True, key='render_3d_btn'):
                st.session_state.show_3d = True
            
            # Only render 3D if button clicked
            if st.session_state.get('show_3d', False):
                with st.spinner("Rendering 3D room..."):
                    fig = st.session_state.visualizer.create_3d_visualization()
                    st.plotly_chart(fig, use_container_width=True, key='builder_room_fig')
            
            # Room summary
            summary = st.session_state.visualizer.get_room_summary()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📏 Dimensions", summary['dimensions'])
            col2.metric("📦 Volume", f"{summary['volume']:.1f} m³")
            col3.metric("🔊 Speakers", summary['speakers'])
            col4.metric("👂 Listeners", summary['listeners'])
            
            # Save/Load room configurations
            st.divider()
            st.subheader("💾 Save & Load Configurations")
            save_load_col1, save_load_col2 = st.columns(2)
            with save_load_col1:
                room_name = st.text_input("Room name to save", value="custom_room")
                if st.button("💾 Save this room"):
                    config = st.session_state.visualizer.export_room_config()
                    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            all_configs = json.load(f)
                    else:
                        all_configs = {'rooms': {}}
                    all_configs['rooms'][room_name] = config
                    with open(config_path, 'w') as f:
                        json.dump(all_configs, f, indent=2)
                    st.success(f"✅ Room '{room_name}' saved!")
            
            with save_load_col2:
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')
                saved_rooms = {}
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        all_configs = json.load(f)
                        saved_rooms = all_configs.get('rooms', {})
                
                if saved_rooms:
                    room_to_load = st.selectbox("Saved rooms", list(saved_rooms.keys()), key='load_room_select')
                    if st.button("📂 Load selected room"):
                        config = saved_rooms[room_to_load]
                        new_viz = Room3DVisualizer(
                            config['dimensions']['length'],
                            config['dimensions']['width'],
                            config['dimensions']['height']
                        )
                        new_viz.import_room_config(config)
                        st.session_state.visualizer = new_viz
                        st.success(f"✅ Loaded '{room_to_load}'!")
                        st.rerun()
                else:
                    st.info("No saved rooms yet. Save one to load it later.")
        
        # ==================== PRESETS TAB ====================
        with tab2:
            st.subheader("Quick Room Presets")
            st.write("Start with one of our pre-configured rooms:")
            
            col1, col2 = st.columns(2)
            
            presets = RoomPresets.get_all_presets()
            
            with col1:
                if st.button("🛋️ Living Room", use_container_width=True):
                    preset = presets['living_room']
                    st.session_state.visualizer = Room3DVisualizer(
                        preset['dimensions']['length'],
                        preset['dimensions']['width'],
                        preset['dimensions']['height']
                    )
                    st.session_state.visualizer.import_room_config(preset)
                    st.success("Living room loaded!")
                    st.rerun()
                
                if st.button("🛏️ Bedroom", use_container_width=True):
                    preset = presets['bedroom']
                    st.session_state.visualizer = Room3DVisualizer(
                        preset['dimensions']['length'],
                        preset['dimensions']['width'],
                        preset['dimensions']['height']
                    )
                    st.session_state.visualizer.import_room_config(preset)
                    st.success("Bedroom loaded!")
                    st.rerun()
            
            with col2:
                if st.button("🖥️ Office", use_container_width=True):
                    preset = presets['office']
                    st.session_state.visualizer = Room3DVisualizer(
                        preset['dimensions']['length'],
                        preset['dimensions']['width'],
                        preset['dimensions']['height']
                    )
                    st.session_state.visualizer.import_room_config(preset)
                    st.success("Office loaded!")
                    st.rerun()
                
                if st.button("🎙️ Studio", use_container_width=True):
                    preset = presets['studio']
                    st.session_state.visualizer = Room3DVisualizer(
                        preset['dimensions']['length'],
                        preset['dimensions']['width'],
                        preset['dimensions']['height']
                    )
                    st.session_state.visualizer.import_room_config(preset)
                    st.success("Studio loaded!")
                    st.rerun()
            
            st.divider()
            
            # Display current room
            st.subheader("Current Room Configuration")
            fig = st.session_state.visualizer.create_3d_visualization()
            st.plotly_chart(fig, use_container_width=True, key='presets_room_fig')
        
        # ==================== SIMULATION TAB ====================
        with tab3:
            st.subheader("Place Speakers and Listeners")
            
            length = float(st.session_state.visualizer.length)
            width = float(st.session_state.visualizer.width)
            height = float(st.session_state.visualizer.height)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🔊 Speaker Position**")
                speaker_x = st.slider("Speaker X (m)", 0.0, length, 1.0, step=0.01, key='sim_sp_x')
                speaker_y = st.slider("Speaker Y (m)", 0.0, width, 1.0, step=0.01, key='sim_sp_y')
                speaker_z = st.slider("Speaker Z (m)", 0.0, height, 1.0, step=0.01, key='sim_sp_z')
            
            with col2:
                st.write("**👂 Listener Position**")
                listener_x = st.slider("Listener X (m)", 0.0, length, float(length)/2.0, step=0.01, key='sim_ls_x')
                listener_y = st.slider("Listener Y (m)", 0.0, width, float(width)/2.0, step=0.01, key='sim_ls_y')
                listener_z = st.slider("Listener Z (m)", 0.0, height, 1.2, step=0.01, key='sim_ls_z')
            
            # Update positions in visualizer
            st.session_state.visualizer.clear_speakers()
            st.session_state.visualizer.clear_listeners()
            st.session_state.visualizer.add_speaker(speaker_x, speaker_y, speaker_z, "Speaker")
            st.session_state.visualizer.add_listener(listener_x, listener_y, listener_z, "Listener")
            
            # Show 3D visualization with speaker/listener
            st.subheader("Room with Speaker and Listener")
            fig = st.session_state.visualizer.create_3d_visualization()
            st.plotly_chart(fig, use_container_width=True, key='simulation_room_fig')
            
            st.divider()
            
            # Run simulation
            show_wave = st.checkbox("Show wave animation (2D)", value=True, key='show_wave_checkbox')
            if st.button("🎯 Simulate Room Acoustics", key='simulate_room', use_container_width=True):
                with st.spinner("Simulating room acoustics..."):
                    try:
                        dimensions = RoomDimensions(length=length, width=width, height=height)
                        simulator = RoomSimulator(dimensions)
                        
                        # Get materials from visualizer
                        materials_dict = {}
                        for wall_name, wall in st.session_state.visualizer.walls.items():
                            if wall_name == 'floor':
                                materials_dict['floor'] = wall.material
                            elif wall_name == 'ceiling':
                                materials_dict['ceiling'] = wall.material
                            elif wall_name.startswith('wall_'):
                                materials_dict['walls'] = wall.material
                        
                        simulator.set_materials(materials_dict)
                        simulator.set_speaker_position(Vector3D(x=speaker_x, y=speaker_y, z=speaker_z))
                        simulator.set_listener_position(Vector3D(x=listener_x, y=listener_y, z=listener_z))
                        
                        results = simulator.simulate_frequency_response()
                        
                        st.success("✅ Simulation complete!")
                        
                        # Display results
                        st.divider()
                        st.subheader("📊 Simulation Results")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            direct = results['direct_sound']
                            st.metric("Direct Sound Distance", f"{direct['distance']:.2f} m")
                            st.metric("Direct Sound Delay", f"{direct['delay']*1000:.2f} ms")
                        
                        with col2:
                            st.metric("Reverberation Time (RT60)", f"{results['reverberation_time']:.2f} s")
                            st.metric("Room Volume", f"{results['room_characteristics']['volume']:.1f} m³")
                        
                        with col3:
                            st.metric("Speed of Sound", "343 m/s")
                            rt60 = results['reverberation_time']
                            if rt60 < 0.3:
                                quality = "🟢 Very Dry"
                            elif rt60 < 0.6:
                                quality = "🟢 Good"
                            elif rt60 < 1.0:
                                quality = "🟡 Moderate"
                            else:
                                quality = "🔴 Too Reverberant"
                            st.metric("Room Quality", quality)
                        
                        # Early reflections
                        st.subheader("🔄 Early Reflections")
                        reflections_data = {
                            'Reflection #': [r['number'] for r in results['early_reflections']],
                            'Distance (m)': [f"{r['distance']:.2f}" for r in results['early_reflections']],
                            'Delay (ms)': [f"{r['delay']*1000:.2f}" for r in results['early_reflections']],
                            'Amplitude Factor': [f"{r['amplitude_factor']:.4f}" for r in results['early_reflections']]
                        }
                        st.dataframe(reflections_data, use_container_width=True)
                        
                        # Generate and store wave figures in session state
                        try:
                            st.session_state.simulation_done = True
                            if show_wave:
                                st.session_state.last_wave_fig_2d = st.session_state.visualizer.simulate_wave_2d(duration=5.0, fps=30, speed=3.43)
                                # don't pre-generate 3D; let it lazy-load when user selects 3D view
                                st.session_state.last_wave_fig_3d = None
                            else:
                                st.session_state.last_wave_fig_2d = None
                                st.session_state.last_wave_fig_3d = None
                        except Exception as e:
                            st.warning(f"Wave generation failed: {str(e)[:120]}")
                        
                        # Interpretation guide
                        with st.expander("💡 Understanding the Results"):
                            st.write(f"""
                            **RT60 = {results['reverberation_time']:.2f} seconds**
                            
                            - RT60 is the time for sound to decay by 60 dB
                            - **< 0.3s**: Very dry, dead acoustics (good for speech, less for music)
                            - **0.3-0.6s**: Good for most music and speech
                            - **0.6-1.0s**: Moderate, acceptable for music
                            - **> 1.0s**: Too reverberant, sounds echoey
                            
                            **Early Reflections**: Sound bouncing off walls, floor, ceiling
                            - Creates sense of space and room character
                            - Delay tells you when reflections arrive after direct sound
                            - Amplitude shows how loud reflections are relative to direct sound
                            """)
                        
                    except Exception as e:
                        st.error(f"❌ Simulation error: {str(e)}")

            # --- Wave visualization controls (outside simulate button) ---
            if st.session_state.get('simulation_done', False):
                st.divider()
                st.subheader("🌊 Wave Propagation Visualization")
                # Reflection controls
                limit_ref = st.checkbox("Limit reflected sources", value=True, key='limit_reflections')
                max_reflections = st.slider("Max reflections", 0, 12, 3, key='max_reflections') if limit_ref else None
                wave_type = st.radio("Wave animation type", ["2D Top-down", "3D Projection", "Both"], horizontal=True, key='wave_type')

                if st.session_state.get('last_wave_fig_2d') is None and st.session_state.get('last_wave_fig_3d') is None:
                    st.info("Wave results not generated or 'Show wave animation' was unchecked during simulation.")
                else:
                    if st.session_state.get('last_wave_fig_2d') is not None and wave_type in ["2D Top-down", "Both"]:
                        st.write("**2D Top-down View** - Direct and reflected wavefronts")
                        st.plotly_chart(st.session_state.last_wave_fig_2d, width='stretch', key='wave_sim_2d')

                    if wave_type in ["3D Projection", "Both"]:
                        # lazy-generate 3D figure if missing
                        if st.session_state.get('last_wave_fig_3d') is None and st.session_state.get('simulation_done', False):
                            with st.spinner("Generating 3D wave projection..."):
                                try:
                                    st.session_state.last_wave_fig_3d = st.session_state.visualizer.simulate_wave_3d(duration=5.0, fps=20, max_reflections=max_reflections if max_reflections is not None else 999)
                                except Exception as e:
                                    st.warning(f"Failed to generate 3D wave: {str(e)[:120]}")
                        if st.session_state.get('last_wave_fig_3d') is not None:
                            st.write("**3D View** - Expanding rings at multiple heights (with reflections)")
                            st.plotly_chart(st.session_state.last_wave_fig_3d, width='stretch', key='wave_sim_3d')
    
    def render_about_page(self):
        """Render the about page."""
        st.markdown('<h1 class="main-header">ℹ️ About AudioEmm</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        ## 🎵 What is AudioEmm?
        
        AudioEmm is an advanced audio emulation platform with two powerful features:
        
        ### 1. 🎧 Device Equalizer
        Ever wanted to know how a different headphone or speaker would sound before buying it?
        AudioEmm analyzes the frequency response of your current device and your target device,
        then creates a custom equalizer that makes your device sound like the target.
        
        **How it works:**
        - Upload reference audio from both devices
        - AudioEmm analyzes their frequency responses
        - Creates an EQ curve that transforms your device's sound profile to match the target
        - Apply the EQ and hear the difference!
        
        ### 2. 🏠 Room Acoustic Simulator
        The acoustic properties of a room significantly affect how sound is perceived.
        AudioEmm lets you design your room and understand how it impacts sound.
        
        **Features:**
        - Define room dimensions and materials
        - Place speaker and listener positions
        - Calculate direct sound, reflections, and reverberation
        - Understand how your room acoustics affect audio
        
        ---
        
        ## 🔬 Technical Details
        
        **Audio Analysis:**
        - Uses FFT (Fast Fourier Transform) for frequency analysis
        - Applies Hann windowing for smooth frequency response
        - Normalizes responses for accurate comparison
        
        **Room Acoustics:**
        - Sabine formula for reverberation time calculation
        - Inverse square law for sound propagation
        - Material absorption coefficients for accurate simulation
        
        ---
        
        ## 📝 Tips for Best Results
        
        **Device Equalizer:**
        1. Use high-quality reference audio files (lossless formats preferred)
        2. Use the same audio content for both source and target devices
        3. Ensure good recording conditions
        4. Test the resulting EQ with various music genres
        
        **Room Simulator:**
        1. Measure your actual room dimensions accurately
        2. Consider furniture and objects for material selection
        3. Experiment with different positions to find the sweet spot
        4. A typical listening distance is 1-3 meters from the speaker
        
        ---
        
        ## 📧 About
        AudioEmm - Making Audio Science Accessible
        """)

def run_app():
    """Entry point for the application."""
    ui = UIManager()
    ui.run()

if __name__ == "__main__":
    run_app()
