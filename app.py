"""
FlipBook - a FlipaClip-style frame-by-frame animator.

Frontend built with tkinter (ships with Python, nothing to install).
All the animation data lives in the hand-made linked lists of linked_lists.py.

Run:  python app.py
"""

import tkinter as tk

from animation import Animation, Stroke
from linked_lists import SinglyLinkedList

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 400
BACKGROUND = "#ffffff"

THUMB_WIDTH = 96
THUMB_HEIGHT = 60
THUMB_GAP = 12
THUMB_SCALE = THUMB_WIDTH / CANVAS_WIDTH
TIMELINE_HEIGHT = THUMB_HEIGHT + 34

ONION_PREVIOUS = "#f4b0b0"
ONION_NEXT = "#b0c8f4"
SELECTED_OUTLINE = "#e8553e"


class CanvasRenderer:
    """Draws frames on a tkinter canvas walking the linked lists node by node."""

    def __init__(self, canvas):
        self.canvas = canvas

    def draw_frame(self, frame, scale=1.0, offset_x=0, offset_y=0, tint=None):
        node = frame.strokes.head
        while node is not None:
            stroke = node.value
            color = stroke.color
            if tint is not None and color != BACKGROUND:
                color = tint
            self.draw_stroke(stroke, color, scale, offset_x, offset_y)
            node = node.next

    def draw_stroke(self, stroke, color, scale, offset_x, offset_y):
        width = stroke.width * scale
        if width < 1:
            width = 1
        node = stroke.points.head
        if node is None:
            return
        if node.next is None:
            self.draw_dot(offset_x + node.value.x * scale,
                          offset_y + node.value.y * scale, width, color)
            return
        while node.next is not None:
            start = node.value
            end = node.next.value
            self.draw_segment(offset_x + start.x * scale, offset_y + start.y * scale,
                              offset_x + end.x * scale, offset_y + end.y * scale,
                              width, color)
            node = node.next

    def draw_segment(self, x1, y1, x2, y2, width, color):
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width,
                                capstyle=tk.ROUND)

    def draw_dot(self, x, y, width, color):
        radius = width / 2
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=color, outline=color)


class FlipbookApp:
    """Main window: toolbar, drawing canvas, frame controls, playback and timeline."""

    def __init__(self, root):
        self.root = root
        self.root.title("FlipBook - Doubly Linked List Animator")
        self.root.resizable(False, False)

        self.animation = Animation()
        self.palette = self._create_palette()
        self.brush_color = "#000000"
        self.brush_size = tk.IntVar(value=4)
        self.fps = tk.IntVar(value=8)
        self.loop = tk.BooleanVar(value=True)
        self.onion_skin = tk.BooleanVar(value=True)

        self.current_stroke = None
        self.last_x = 0
        self.last_y = 0
        self.playback_job = None
        self.play_direction = 1

        self._build_toolbar()
        self._build_canvas()
        self._build_frame_controls()
        self._build_playback_controls()
        self._build_timeline()
        self._bind_shortcuts()
        self.refresh()

    # --- setup -----------------------------------------------------------

    def _create_palette(self):
        palette = SinglyLinkedList()
        palette.append("#000000")
        palette.append("#e53935")
        palette.append("#fb8c00")
        palette.append("#fdd835")
        palette.append("#43a047")
        palette.append("#1e88e5")
        palette.append("#8e24aa")
        palette.append("#6d4c41")
        return palette

    def _button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command)
        button.pack(side=tk.LEFT, padx=2)
        return button

    def _build_toolbar(self):
        bar = tk.Frame(self.root, padx=8, pady=6)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="Color:").pack(side=tk.LEFT)
        node = self.palette.head
        while node is not None:
            self._add_swatch(bar, node.value)
            node = node.next
        self._button(bar, "Eraser", self.use_eraser)

        tk.Label(bar, text="  Current:").pack(side=tk.LEFT)
        self.color_preview = tk.Label(bar, width=3, bg=self.brush_color,
                                      relief=tk.SUNKEN, bd=2)
        self.color_preview.pack(side=tk.LEFT, padx=2)

        tk.Label(bar, text="  Brush:").pack(side=tk.LEFT)
        tk.Scale(bar, from_=1, to=20, orient=tk.HORIZONTAL, length=110,
                 variable=self.brush_size).pack(side=tk.LEFT)

        tk.Button(bar, text="Clear frame",
                  command=lambda: self._edit(self.animation.clear_frame)).pack(side=tk.RIGHT, padx=2)
        tk.Button(bar, text="Undo",
                  command=lambda: self._edit(self.animation.undo_stroke)).pack(side=tk.RIGHT, padx=2)

    def _add_swatch(self, parent, color):
        swatch = tk.Label(parent, bg=color, width=2, relief=tk.RAISED, bd=2, cursor="hand2")
        swatch.pack(side=tk.LEFT, padx=2)
        swatch.bind("<Button-1>", lambda event: self.select_color(color))

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg=BACKGROUND, cursor="crosshair",
                                highlightthickness=1, highlightbackground="#999999")
        self.canvas.pack(padx=8)
        self.canvas.bind("<ButtonPress-1>", self.start_stroke)
        self.canvas.bind("<B1-Motion>", self.continue_stroke)
        self.canvas.bind("<ButtonRelease-1>", self.end_stroke)
        self.renderer = CanvasRenderer(self.canvas)

    def _build_frame_controls(self):
        bar = tk.Frame(self.root, padx=8, pady=6)
        bar.pack(fill=tk.X)
        animation = self.animation
        self._button(bar, "|<", lambda: self._edit(animation.go_first))
        self._button(bar, "<", lambda: self._edit(animation.go_previous))
        self._button(bar, ">", lambda: self._edit(animation.go_next))
        self._button(bar, ">|", lambda: self._edit(animation.go_last))
        tk.Label(bar, text=" ").pack(side=tk.LEFT)
        self._button(bar, "+ New", lambda: self._edit(animation.add_frame))
        self._button(bar, "Duplicate", lambda: self._edit(animation.duplicate_frame))
        self._button(bar, "Delete", lambda: self._edit(animation.delete_frame))
        self._button(bar, "Move left", lambda: self._edit(animation.move_frame_backward))
        self._button(bar, "Move right", lambda: self._edit(animation.move_frame_forward))
        self.status = tk.Label(bar, font="TkDefaultFont 10 bold")
        self.status.pack(side=tk.RIGHT)

    def _build_playback_controls(self):
        bar = tk.Frame(self.root, padx=8)
        bar.pack(fill=tk.X)
        self._button(bar, "Play", lambda: self.play(1))
        self._button(bar, "Reverse", lambda: self.play(-1))
        self._button(bar, "Stop", self.stop_playback)
        tk.Label(bar, text="  FPS:").pack(side=tk.LEFT)
        tk.Scale(bar, from_=1, to=24, orient=tk.HORIZONTAL, length=110,
                 variable=self.fps).pack(side=tk.LEFT)
        tk.Checkbutton(bar, text="Loop", variable=self.loop).pack(side=tk.LEFT, padx=6)
        tk.Checkbutton(bar, text="Onion skin", variable=self.onion_skin,
                       command=self.refresh).pack(side=tk.LEFT)

    def _build_timeline(self):
        container = tk.Frame(self.root, padx=8, pady=6)
        container.pack(fill=tk.X)
        self.timeline = tk.Canvas(container, width=CANVAS_WIDTH, height=TIMELINE_HEIGHT,
                                  bg="#eeeeee", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.timeline.xview)
        self.timeline.configure(xscrollcommand=scrollbar.set)
        self.timeline.pack(fill=tk.X)
        scrollbar.pack(fill=tk.X)
        self.timeline.bind("<Button-1>", self.on_timeline_click)
        self.timeline_renderer = CanvasRenderer(self.timeline)

    def _bind_shortcuts(self):
        self.root.bind("<Left>", lambda event: self._edit(self.animation.go_previous))
        self.root.bind("<Right>", lambda event: self._edit(self.animation.go_next))
        self.root.bind("<space>", lambda event: self.toggle_play())
        self.root.bind("<Control-z>", lambda event: self._edit(self.animation.undo_stroke))

    # --- brush -----------------------------------------------------------

    def select_color(self, color):
        self.brush_color = color
        self.color_preview.configure(bg=color)

    def use_eraser(self):
        self.select_color(BACKGROUND)

    # --- drawing with the mouse ------------------------------------------

    def start_stroke(self, event):
        if self.is_playing():
            return
        self.current_stroke = Stroke(self.brush_color, self.brush_size.get())
        self.current_stroke.add_point(event.x, event.y)
        self.animation.current_frame().add_stroke(self.current_stroke)
        self.renderer.draw_dot(event.x, event.y, self.current_stroke.width, self.brush_color)
        self.last_x = event.x
        self.last_y = event.y

    def continue_stroke(self, event):
        if self.current_stroke is None:
            return
        self.current_stroke.add_point(event.x, event.y)
        self.renderer.draw_segment(self.last_x, self.last_y, event.x, event.y,
                                   self.current_stroke.width, self.current_stroke.color)
        self.last_x = event.x
        self.last_y = event.y

    def end_stroke(self, event):
        if self.current_stroke is None:
            return
        self.current_stroke = None
        self.refresh()

    # --- frame editing ---------------------------------------------------

    def _edit(self, action):
        """Stops playback, runs a frame action and redraws everything."""
        self._cancel_playback()
        action()
        self.refresh()

    def on_timeline_click(self, event):
        x = self.timeline.canvasx(event.x) - THUMB_GAP
        if x < 0:
            return
        slot = THUMB_WIDTH + THUMB_GAP
        index = int(x // slot)
        if x - index * slot > THUMB_WIDTH:
            return
        self._edit(lambda: self.animation.go_to(index))

    # --- playback --------------------------------------------------------

    def is_playing(self):
        return self.playback_job is not None

    def play(self, direction):
        self._cancel_playback()
        self.play_direction = direction
        if direction == 1 and self.animation.current.next is None:
            self.animation.go_first()
        if direction == -1 and self.animation.current.prev is None:
            self.animation.go_last()
        self.playback_job = self.root.after(self._frame_delay(), self._tick)
        self.refresh()

    def stop_playback(self):
        self._cancel_playback()
        self.refresh()

    def toggle_play(self):
        if self.is_playing():
            self.stop_playback()
        else:
            self.play(1)

    def _tick(self):
        if self.play_direction == 1:
            moved = self.animation.go_next(self.loop.get())
        else:
            moved = self.animation.go_previous(self.loop.get())
        if moved:
            self.playback_job = self.root.after(self._frame_delay(), self._tick)
        else:
            self.playback_job = None
        self.refresh()

    def _cancel_playback(self):
        if self.playback_job is not None:
            self.root.after_cancel(self.playback_job)
            self.playback_job = None

    def _frame_delay(self):
        return int(1000 / self.fps.get())

    # --- rendering -------------------------------------------------------

    def refresh(self):
        self.render_canvas()
        self.render_timeline()

    def render_canvas(self):
        self.canvas.delete("all")
        current = self.animation.current
        if self.onion_skin.get() and not self.is_playing():
            if current.next is not None:
                self.renderer.draw_frame(current.next.value, tint=ONION_NEXT)
            if current.prev is not None:
                self.renderer.draw_frame(current.prev.value, tint=ONION_PREVIOUS)
        self.renderer.draw_frame(current.value)

    def render_timeline(self):
        self.timeline.delete("all")
        slot = THUMB_WIDTH + THUMB_GAP
        top = 8
        current_index = 0
        node = self.animation.frames.head
        index = 0
        x = THUMB_GAP
        while node is not None:
            selected = node is self.animation.current
            if selected:
                current_index = index
            self.timeline.create_rectangle(
                x, top, x + THUMB_WIDTH, top + THUMB_HEIGHT, fill=BACKGROUND,
                outline=SELECTED_OUTLINE if selected else "#999999",
                width=3 if selected else 1)
            self.timeline_renderer.draw_frame(node.value, THUMB_SCALE, x, top)
            self.timeline.create_text(x + THUMB_WIDTH / 2, top + THUMB_HEIGHT + 12,
                                      text=str(index + 1))
            node = node.next
            index += 1
            x += slot

        total_width = x
        self.timeline.configure(scrollregion=f"0 0 {total_width} {TIMELINE_HEIGHT}")
        if total_width > CANVAS_WIDTH:
            left = THUMB_GAP + current_index * slot - (CANVAS_WIDTH - THUMB_WIDTH) / 2
            if left < 0:
                left = 0
            self.timeline.xview_moveto(left / total_width)

        state = "  (playing)" if self.is_playing() else ""
        self.status.configure(
            text=f"Frame {current_index + 1} / {self.animation.frame_count()}{state}")


def main():
    root = tk.Tk()
    FlipbookApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
