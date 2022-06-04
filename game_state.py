class GameState:
    def __init__(self, init_pos: set):
        self.dead_cells = init_pos.copy()
        self.active_cells = init_pos
        self.CURR_CELL_SIZE = 1
        self.is_running = True

    def shift_cells(self, dx, dy):
        return set([(i - dx, j - dy) for i, j in self.active_cells])

    def get_cell_corner(self, pos, dx, dy):
        return (
            pos[0] * self.CURR_CELL_SIZE - dx % self.CURR_CELL_SIZE,
            pos[1] * self.CURR_CELL_SIZE - dy % self.CURR_CELL_SIZE,
        )

    def get_cell_coord(self, pos, dx, dy):
        return (
            ((pos[0] + dx % self.CURR_CELL_SIZE) // self.CURR_CELL_SIZE),
            ((pos[1] + dy % self.CURR_CELL_SIZE) // self.CURR_CELL_SIZE),
        )

    def update_cells(self):
        self.dead_cells = self.active_cells.copy()

        if self.is_running:
            all_neighbors = {}
            for i in self.active_cells:
                all_neighbors.setdefault(i, 0)
                curr_neighbors = (
                    (i[0] - 1, i[1]),
                    (i[0] + 1, i[1]),
                    (i[0], i[1] - 1),
                    (i[0], i[1] + 1),
                    (i[0] - 1, i[1] - 1),
                    (i[0] - 1, i[1] + 1),
                    (i[0] + 1, i[1] + 1),
                    (i[0] + 1, i[1] - 1),
                )
                for j in curr_neighbors:
                    all_neighbors.setdefault(j, 0)
                    all_neighbors[j] += 1
            for i in self.active_cells.copy():
                if all_neighbors[i] > 3 or all_neighbors[i] < 2:
                    self.active_cells.remove(i)
            for k in all_neighbors:
                if all_neighbors[k] == 3:
                    self.active_cells.add(k)

    def update(self):
        self.view.update_screen()