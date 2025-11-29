from vood import VElement, VElementGroup
from vood.animations import crossfade
from vood.components import TextState, TextRenderer

# Create renderer
text_renderer = TextRenderer()

# Create two states
state1 = TextState(text="Hello", font_size=48, x=100, y=100)
state2 = TextState(text="World", font_size=48, x=100, y=100)

# Generate crossfade keyframes
all_keyframes = crossfade(state1, state2, at_time=0.5, duration=0.3)

# Split into two element keyframes (first 3 for state1, last 3 for state2)
elem1_keyframes = all_keyframes[:3]  # Fade out
elem2_keyframes = all_keyframes[3:]  # Fade in

# Create elements
elem1 = VElement(renderer=text_renderer, keyframes=elem1_keyframes)
elem2 = VElement(renderer=text_renderer, keyframes=elem2_keyframes)

# Group them
group = VElementGroup(elements=[elem1, elem2])

# Render at different times
frame_0 = group.render_at_frame_time(0.0)   # Shows "Hello"
frame_5 = group.render_at_frame_time(0.5)   # Mid-transition
frame_1 = group.render_at_frame_time(1.0)   # Shows "World"