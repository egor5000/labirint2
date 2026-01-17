import tkinter as tk
import random
from collections import deque

CELL = 25
GRID = 21
DELAY = 100
DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
EXITS_COUNT = 2  


class maze:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабиринт")

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        self.new_maze_button = tk.Button(self.button_frame, text="Новый лабиринт", command=self.new_maze)
        self.new_maze_button.pack(side="left", padx=5)

        self.start_button = tk.Button(self.button_frame, text="Старт", command=self.search)
        self.start_button.pack(side="left", padx=5)

        self.canvas = tk.Canvas(root, width=GRID * CELL, height=GRID * CELL, bg="#f0f0f0")
        self.canvas.pack()

        self.status = tk.Label(root, text="Генерация лабиринта...", anchor="w", font=("Arial", 11))
        self.status.pack(fill="x")

        self.grid = self.generate(GRID)

        self.start = (GRID // 2, GRID // 2)
        if self.grid[self.start[0]][self.start[1]] == 1:
            self.start = self.find_nearest(self.start)

        self.exits = self.choose_exits(k=EXITS_COUNT)

        self.draw_maze()
        self.highlight_special_cells()
        self.search_started = False

    def new_maze(self):
        self.grid = self.generate(GRID)

        self.start = (GRID // 2, GRID // 2)
        if self.grid[self.start[0]][self.start[1]] == 1:
            self.start = self.find_nearest(self.start)

        self.exits = self.choose_exits(k=EXITS_COUNT)

        self.draw_maze()
        self.highlight_special_cells()
        self.status.config(text="Новый лабиринт создан")
        self.search_started = False

    def search(self):
        if not self.search_started:
            self.search_started = True
            self.visited = set()
            self.stack = [(self.start, [self.start])]
            self.status.config(text="Поиск пути...")
            self.root.after(DELAY, self.step)

    def generate(self, n):
        m = [[1] * n for _ in range(n)]
        start = (n // 2 | 1, n // 2 | 1)

        def carve(r, c):
            m[r][c] = 0
            dirs = DIRS[:]
            random.shuffle(dirs)
            for dr, dc in dirs:
                nr, nc = r + 2 * dr, c + 2 * dc
                if 1 <= nr < n - 1 and 1 <= nc < n - 1 and m[nr][nc] == 1:
                    m[r + dr][c + dc] = 0
                    carve(nr, nc)

        carve(*start)
        return m

    def find_nearest(self, start):
        q = deque([start])
        seen = {start}
        while q:
            r, c = q.popleft()
            if self.grid[r][c] == 0:
                return (r, c)
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID and 0 <= nc < GRID and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return start

    def choose_exits(self, k=2):
        candidates = []
        n = GRID

        for col in range(1, n - 1):
            if self.grid[1][col] == 0:
                candidates.append((0, col))
            if self.grid[n - 2][col] == 0:
                candidates.append((n - 1, col))

        for row in range(1, n - 1):
            if self.grid[row][1] == 0:
                candidates.append((row, 0))
            if self.grid[row][n - 2] == 0:
                candidates.append((row, n - 1))

        if not candidates:
            self.grid[n - 1][n // 2] = 0
            return {(n - 1, n // 2)}

        k = min(k, len(candidates))
        exits = set(random.sample(candidates, k))
        for r, c in exits:
            self.grid[r][c] = 0
        return exits

    def draw_maze(self):
        self.canvas.delete("all")
        for r in range(GRID):
            for c in range(GRID):
                color = "#333333" if self.grid[r][c] == 1 else "#ffffff"
                self.canvas.create_rectangle(
                    c * CELL, r * CELL,
                    c * CELL + CELL, r * CELL + CELL,
                    fill=color, outline="#bbbbbb"
                )

    def highlight_special_cells(self):
        sr, sc = self.start

        # старт
        self.canvas.create_rectangle(
            sc * CELL, sr * CELL,
            sc * CELL + CELL, sr * CELL + CELL,
            fill="#00cc66", outline="#00aa55", tags="start"
        )

        # выходы
        for er, ec in self.exits:
            self.canvas.create_rectangle(
                ec * CELL, er * CELL,
                ec * CELL + CELL, er * CELL + CELL,
                fill="#ff5050", outline="#cc0000", tags="exit"
            )

        self.draw_tarakan(self.start)

    def draw_tarakan(self, pos, color="#ff8c00"):
        r, c = pos
        cx, cy = c * CELL + CELL / 2, r * CELL + CELL / 2
        rad = CELL * 0.35
        self.canvas.delete("tarakan")
        self.canvas.create_oval(
            cx - rad, cy - rad, cx + rad, cy + rad,
            fill=color, outline="", tags="tarakan"
        )

    def step(self):
        if not self.stack:
            self.status.config(text="Путь не найден.")
            return

        (r, c), path = self.stack.pop()

        if (r, c) in self.visited:
            self.root.after(DELAY, self.step)
            return

        self.visited.add((r, c))

        if (r, c) != self.start and (r, c) not in self.exits:
            self.canvas.create_rectangle(
                c * CELL, r * CELL,
                c * CELL + CELL, r * CELL + CELL,
                fill="#cfe9ff", outline="#a0c8ff"
            )

        self.draw_tarakan((r, c))

        if (r, c) in self.exits:
            self.status.config(text=f"Выход найден! Длина пути: {len(path)}")
            return

        for dr, dc in reversed(DIRS):
            nr, nc = r + dr, c + dc
            if (0 <= nr < GRID and 0 <= nc < GRID and
                self.grid[nr][nc] == 0 and
                (nr, nc) not in self.visited):
                self.stack.append(((nr, nc), path + [(nr, nc)]))

        self.root.after(DELAY, self.step)


if __name__ == "__main__":
    root = tk.Tk()
    app = maze(root)
    root.mainloop()

