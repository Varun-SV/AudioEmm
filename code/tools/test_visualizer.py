import sys, os
# ensure project code path is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.room_simulator.visualizer import Room3DVisualizer

v = Room3DVisualizer(5.0, 4.0, 3.0)
v.add_custom_wall(1.0, 0.5, 1.0, 3.0, height=2.5, material='drywall', name='test_wall')
v.add_speaker(1.5, 1.5, 1.0)

fig = v.simulate_wave_3d(duration=1.0, fps=10)

print('FIG_TYPE:', type(fig))
print('NUM_FRAMES:', len(getattr(fig, 'frames', [])))
print('INITIAL_TRACES:', len(getattr(fig, 'data', [])))
if fig.frames:
    non_empty = sum(1 for f in fig.frames if getattr(f, 'data', None))
    print('NON_EMPTY_FRAMES:', non_empty)
    # list sample counts for first few frames
    for i, f in enumerate(fig.frames[:5]):
        print(f'frame {i} traces:', len(getattr(f, 'data', [])))
else:
    print('NO_FRAMES')
