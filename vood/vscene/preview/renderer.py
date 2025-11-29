"""Preview rendering utilities for VScene (Jupyter notebooks and dev server)"""

from typing import List
from vood.config import get_config, ConfigKey
from .color_schemes import get_color_scheme


class PreviewRenderer:
    """Generates interactive HTML previews for VScene

    Used by both Jupyter notebooks and the development server to create
    interactive animation previews with playback controls.
    """

    def __init__(self, vscene):
        """Initialize with a VScene instance

        Args:
            vscene: The VScene instance to display
        """
        self.vscene = vscene

    def repr_svg(self) -> str:
        """Generate SVG string for Jupyter's _repr_svg_ display

        Returns:
            SVG string representation
        """
        drawing = self.vscene.to_drawing(frame_time=0.0)
        return drawing.as_svg(randomize_ids=True)

    def display_inline(self, frame_time: float = 0.0):
        """Display inline in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgInline object that displays in notebooks
        """
        drawing = self.vscene.to_drawing(frame_time=frame_time)
        return drawing.display_inline()

    def display_iframe(self, frame_time: float = 0.0):
        """Display within an iframe in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgFrame object that displays in notebooks
        """
        drawing = self.vscene.to_drawing(frame_time=frame_time)
        return drawing.display_iframe()

    def display_image(self, frame_time: float = 0.0):
        """Display within an img tag in the Jupyter web page.

        Args:
            frame_time: Time point to render (0.0 to 1.0)

        Returns:
            JupyterSvgImage object that displays in notebooks
        """
        drawing = self.vscene.to_drawing(frame_time=frame_time)
        return drawing.display_image()

    def preview_grid(self, num_frames: int = 10, scale: float = 1.0):
        """Preview animation by showing all frames in a grid layout.

        Useful for quickly checking animations in Jupyter without video export.
        Shows all frames at once for easy visual comparison.

        Args:
            num_frames: Number of frames to display (default: 10)
            scale: Scale factor for frame size, e.g. 0.5 for half size (default: 1.0)

        Returns:
            HTML object that displays in Jupyter notebooks
        """
        from IPython.display import HTML

        if num_frames < 2:
            raise ValueError("num_frames must be at least 2")
        if scale <= 0:
            raise ValueError("scale must be positive")

        # Generate frames at evenly spaced times
        times = [i / (num_frames - 1) for i in range(num_frames)]
        return self._render_grid(times, scale)

    def preview_animation(self, num_frames: int = 10, play_interval_ms: int = 100):
        """Preview animation with interactive controls (play/pause, slider, prev/next).

        Useful for checking animations in Jupyter without video export.
        Shows one frame at a time with playback controls.

        Args:
            num_frames: Number of frames to display (default: 10)
            play_interval_ms: Milliseconds between frames when playing (default: 100)

        Returns:
            HTML object that displays in Jupyter notebooks
        """
        from IPython.display import HTML

        if num_frames < 2:
            raise ValueError("num_frames must be at least 2")
        if play_interval_ms <= 0:
            raise ValueError("play_interval_ms must be positive")

        # Generate frames at evenly spaced times
        times = [i / (num_frames - 1) for i in range(num_frames)]
        return self._render_navigator(times, play_interval_ms)

    def _render_grid(self, times: List[float], scale: float = 1.0):
        """Display all frames in a grid layout

        Args:
            times: List of time points to render
            scale: Scale factor for frame size

        Returns:
            HTML object with grid layout
        """
        from IPython.display import HTML

        # Calculate scaled dimensions
        scaled_width = self.vscene.width * scale
        scaled_height = self.vscene.height * scale

        # Build HTML
        html_parts = ['<div style="display: flex; flex-wrap: wrap; gap: 10px;">']

        for i, t in enumerate(times):
            svg = self.vscene.to_svg(frame_time=t, log=False)

            # Apply scale by wrapping in a scaled container
            html_parts.append(f'''
                <div style="text-align: center;">
                    <div style="font-size: 11px; color: #666; margin-bottom: 3px;">
                        t={t:.2f}
                    </div>
                    <div style="border: 1px solid #ddd; display: inline-block; width: {scaled_width}px; height: {scaled_height}px; overflow: hidden;">
                        <div style="transform: scale({scale}); transform-origin: top left; width: {self.vscene.width}px; height: {self.vscene.height}px;">
                            {svg}
                        </div>
                    </div>
                </div>
            ''')

        html_parts.append('</div>')
        return HTML(''.join(html_parts))

    def _render_navigator(self, times: List[float], play_interval_ms: int):
        """Display one frame at a time with navigation controls (prev/next, slider, play)

        Args:
            times: List of time points to render
            play_interval_ms: Milliseconds between frames when playing

        Returns:
            HTML object with navigator interface
        """
        from IPython.display import HTML
        import uuid

        # Generate unique ID for this preview instance
        preview_id = str(uuid.uuid4())[:8]
        num_frames = len(times)

        # Get color scheme from config (with individual color overrides)
        colors = get_color_scheme()

        # Build HTML with navigation
        html_parts = [f'''
            <style>
                .preview-container-{preview_id} {{
                    text-align: center;
                    background: {colors.background};
                    padding: 24px;
                    border-radius: 8px;
                    border: 1px solid {colors.control_bg};
                }}
                .preview-header-{preview_id} {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                    margin-bottom: 16px;
                }}
                .preview-controls-{preview_id} {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    margin-top: 12px;
                    height: 40px;
                }}
                .preview-nav-btn-{preview_id} {{
                    width: 40px;
                    height: 40px;
                    border: none;
                    background: {colors.control_bg};
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    color: {colors.text};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    user-select: none;
                    transition: all 0.15s ease;
                    flex-shrink: 0;
                }}
                .preview-nav-btn-{preview_id}:hover {{
                    background: {colors.control_hover};
                }}
                .preview-nav-btn-{preview_id}:active {{
                    transform: scale(0.95);
                }}
                .preview-nav-btn-{preview_id}.disabled {{
                    opacity: 0.3;
                    cursor: not-allowed;
                }}
                .preview-nav-btn-{preview_id}.disabled:hover {{
                    background: {colors.control_bg};
                }}
                .preview-play-btn-{preview_id} {{
                    background: {colors.accent};
                    color: {colors.background};
                    margin: 0 4px;
                }}
                .preview-play-btn-{preview_id}:hover {{
                    background: {colors.accent_hover};
                }}
                .preview-play-btn-{preview_id}.playing {{
                    background: {colors.accent_hover};
                }}
                .preview-frame-info-{preview_id} {{
                    background: {colors.control_bg};
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 600;
                    color: {colors.text};
                    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                }}
                .preview-time-info-{preview_id} {{
                    background: {colors.control_bg};
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    color: {colors.text_muted};
                    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                }}
                .preview-interval-control-{preview_id} {{
                    background: {colors.control_bg};
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    color: {colors.text};
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    height: 40px;
                    flex-shrink: 0;
                }}
                .preview-loop-control-{preview_id} {{
                    background: {colors.control_bg};
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                    color: {colors.text};
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    user-select: none;
                    height: 40px;
                    flex-shrink: 0;
                }}
                .preview-loop-control-{preview_id} input[type="checkbox"] {{
                    margin-right: 6px;
                    cursor: pointer;
                }}
                .preview-interval-input-{preview_id} {{
                    width: 50px;
                    padding: 4px 6px;
                    border: 1px solid {colors.control_hover};
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    text-align: center;
                    color: {colors.text};
                    background: {colors.background};
                    outline: none;
                    transition: border-color 0.15s;
                }}
                .preview-interval-input-{preview_id}:focus {{
                    border-color: {colors.accent};
                }}
                .preview-slider-container-{preview_id} {{
                    width: 100%;
                    margin-top: 16px;
                    padding: 0 8px;
                }}
                .preview-slider-{preview_id} {{
                    width: 100%;
                    height: 6px;
                    -webkit-appearance: none;
                    appearance: none;
                    background: {colors.control_bg};
                    outline: none;
                    border-radius: 3px;
                    cursor: pointer;
                }}
                .preview-slider-{preview_id}::-webkit-slider-thumb {{
                    -webkit-appearance: none;
                    appearance: none;
                    width: 18px;
                    height: 18px;
                    background: {colors.accent};
                    cursor: grab;
                    border-radius: 50%;
                    transition: all 0.15s ease;
                }}
                .preview-slider-{preview_id}::-webkit-slider-thumb:hover {{
                    background: {colors.accent_hover};
                    transform: scale(1.2);
                }}
                .preview-slider-{preview_id}::-webkit-slider-thumb:active {{
                    cursor: grabbing;
                }}
                .preview-slider-{preview_id}::-moz-range-thumb {{
                    width: 18px;
                    height: 18px;
                    background: {colors.accent};
                    cursor: grab;
                    border-radius: 50%;
                    border: none;
                    transition: all 0.15s ease;
                }}
                .preview-slider-{preview_id}::-moz-range-thumb:hover {{
                    background: {colors.accent_hover};
                    transform: scale(1.2);
                }}
                .preview-slider-{preview_id}::-moz-range-thumb:active {{
                    cursor: grabbing;
                }}
                .preview-frame-{preview_id} {{
                    display: none;
                }}
                .preview-frame-{preview_id}.active {{
                    display: inline-block;
                }}
            </style>
            <div class="preview-container-{preview_id}">
                <div class="preview-header-{preview_id}">
                    <div class="preview-frame-info-{preview_id}">
                        FRAME <span id="current-frame-{preview_id}">1</span> / {num_frames}
                    </div>
                    <div class="preview-time-info-{preview_id}">
                        t=<span id="current-time-{preview_id}">0.00</span>
                    </div>
                </div>
                <div class="preview-frames-{preview_id}">
        ''']

        # Add all frames (hidden by default)
        for i, t in enumerate(times):
            active = 'active' if i == 0 else ''
            svg = self.vscene.to_svg(frame_time=t, log=False)
            html_parts.append(f'''
                <div class="preview-frame-{preview_id} {active}" id="frame-{preview_id}-{i}" data-time="{t:.2f}">
                    <div style="border: 1px solid #ddd; display: inline-block;">
                        {svg}
                    </div>
                </div>
            ''')

        # Add JavaScript for navigation
        html_parts.append(f'''
                </div>
                <div class="preview-slider-container-{preview_id}">
                    <input type="range" min="0" max="{num_frames - 1}" value="0"
                           class="preview-slider-{preview_id}" id="slider-{preview_id}"
                           oninput="sliderChange_{preview_id}(this.value)">
                </div>
                <div class="preview-controls-{preview_id}">
                    <div class="preview-nav-btn-{preview_id}" onclick="prevFrame_{preview_id}()" id="prev-btn-{preview_id}">
                        ⏮
                    </div>
                    <div class="preview-nav-btn-{preview_id} preview-play-btn-{preview_id}"
                         onmousedown="cancelResume_{preview_id}()"
                         onclick="togglePlay_{preview_id}()"
                         id="play-btn-{preview_id}">
                        ▶
                    </div>
                    <div class="preview-nav-btn-{preview_id}" onclick="nextFrame_{preview_id}()" id="next-btn-{preview_id}">
                        ⏭
                    </div>
                    <div class="preview-interval-control-{preview_id}">
                        <label for="fps-{preview_id}">FPS:</label>
                        <input type="number"
                               id="fps-{preview_id}"
                               class="preview-interval-input-{preview_id}"
                               value="{int(1000 / play_interval_ms)}"
                               min="1"
                               max="60"
                               onfocus="pauseForEdit_{preview_id}()"
                               onblur="resumeAfterEdit_{preview_id}()"
                               oninput="updateFpsValue_{preview_id}(this.value)">
                    </div>
                    <div class="preview-loop-control-{preview_id}">
                        <label for="loop-{preview_id}">
                            <input type="checkbox"
                                   id="loop-{preview_id}"
                                   checked>
                            Loop
                        </label>
                    </div>
                </div>
            </div>
            <script>
                (function() {{
                    let currentFrame_{preview_id} = 0;
                    const totalFrames_{preview_id} = {num_frames};
                    let isPlaying_{preview_id} = false;
                    let playInterval_{preview_id} = null;
                    let currentInterval_{preview_id} = {play_interval_ms};
                    let wasPlayingBeforeEdit_{preview_id} = false;
                    let inputHasFocus_{preview_id} = false;
                    let resumeTimeout_{preview_id} = null;

                    window.nextFrame_{preview_id} = function() {{
                        if (currentFrame_{preview_id} < totalFrames_{preview_id} - 1) {{
                            showFrame_{preview_id}(currentFrame_{preview_id} + 1);
                        }} else {{
                            // At last frame - check if loop is enabled
                            const loopCheckbox = document.getElementById('loop-{preview_id}');
                            if (loopCheckbox && loopCheckbox.checked) {{
                                showFrame_{preview_id}(0); // Loop back to start
                            }} else {{
                                stopPlay_{preview_id}(); // Stop playing
                            }}
                        }}
                    }};

                    window.prevFrame_{preview_id} = function() {{
                        if (currentFrame_{preview_id} > 0) {{
                            showFrame_{preview_id}(currentFrame_{preview_id} - 1);
                        }}
                    }};

                    window.sliderChange_{preview_id} = function(value) {{
                        showFrame_{preview_id}(parseInt(value));
                    }};

                    window.cancelResume_{preview_id} = function() {{
                        if (resumeTimeout_{preview_id}) {{
                            clearTimeout(resumeTimeout_{preview_id});
                            resumeTimeout_{preview_id} = null;
                        }}
                        wasPlayingBeforeEdit_{preview_id} = false;
                    }};

                    window.togglePlay_{preview_id} = function() {{
                        if (isPlaying_{preview_id}) {{
                            stopPlay_{preview_id}();
                        }} else {{
                            startPlay_{preview_id}();
                        }}
                    }};

                    window.pauseForEdit_{preview_id} = function() {{
                        inputHasFocus_{preview_id} = true;
                        if (isPlaying_{preview_id}) {{
                            wasPlayingBeforeEdit_{preview_id} = true;
                            stopPlay_{preview_id}();
                        }}
                    }};

                    window.updateFpsValue_{preview_id} = function(value) {{
                        const newFps = parseInt(value);
                        if (newFps > 0 && newFps <= 60) {{
                            currentInterval_{preview_id} = Math.floor(1000 / newFps);
                        }}
                    }};

                    window.resumeAfterEdit_{preview_id} = function() {{
                        inputHasFocus_{preview_id} = false;
                        const shouldResume = wasPlayingBeforeEdit_{preview_id};
                        wasPlayingBeforeEdit_{preview_id} = false;

                        resumeTimeout_{preview_id} = setTimeout(() => {{
                            resumeTimeout_{preview_id} = null;
                            if (shouldResume) {{
                                startPlay_{preview_id}();
                            }}
                        }}, 50);
                    }};

                    function startPlay_{preview_id}() {{
                        isPlaying_{preview_id} = true;
                        const playBtn = document.getElementById('play-btn-{preview_id}');
                        playBtn.textContent = '⏸';
                        playBtn.classList.add('playing');

                        playInterval_{preview_id} = setInterval(() => {{
                            if (currentFrame_{preview_id} < totalFrames_{preview_id} - 1) {{
                                showFrame_{preview_id}(currentFrame_{preview_id} + 1);
                            }} else {{
                                // At last frame - check if loop is enabled
                                const loopCheckbox = document.getElementById('loop-{preview_id}');
                                if (loopCheckbox && loopCheckbox.checked) {{
                                    showFrame_{preview_id}(0); // Loop back to start
                                }} else {{
                                    stopPlay_{preview_id}(); // Stop playing
                                }}
                            }}
                        }}, currentInterval_{preview_id});
                    }}

                    function stopPlay_{preview_id}() {{
                        isPlaying_{preview_id} = false;
                        const playBtn = document.getElementById('play-btn-{preview_id}');
                        playBtn.textContent = '▶';
                        playBtn.classList.remove('playing');

                        if (playInterval_{preview_id}) {{
                            clearInterval(playInterval_{preview_id});
                            playInterval_{preview_id} = null;
                        }}
                    }}

                    function showFrame_{preview_id}(index) {{
                        // Hide all frames
                        document.querySelectorAll('.preview-frame-{preview_id}').forEach(f => {{
                            f.classList.remove('active');
                        }});

                        // Show selected frame
                        const frame = document.getElementById('frame-{preview_id}-' + index);
                        if (!frame) {{
                            console.error('Frame not found:', index);
                            return;
                        }}

                        frame.classList.add('active');

                        // Update frame counter and time
                        document.getElementById('current-frame-{preview_id}').textContent = index + 1;
                        document.getElementById('current-time-{preview_id}').textContent = frame.dataset.time;

                        // Update current frame index
                        currentFrame_{preview_id} = index;

                        // Update slider position
                        document.getElementById('slider-{preview_id}').value = index;

                        // Update button states
                        const prevBtn = document.getElementById('prev-btn-{preview_id}');
                        const nextBtn = document.getElementById('next-btn-{preview_id}');

                        if (index === 0) {{
                            prevBtn.classList.add('disabled');
                        }} else {{
                            prevBtn.classList.remove('disabled');
                        }}

                        if (index === totalFrames_{preview_id} - 1) {{
                            nextBtn.classList.add('disabled');
                        }} else {{
                            nextBtn.classList.remove('disabled');
                        }}
                    }}

                    // Initialize button states
                    showFrame_{preview_id}(0);
                }})();
            </script>
        ''')

        return HTML(''.join(html_parts))
