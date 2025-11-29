import tkinter as tk
from tkinter import ttk, messagebox

def gray(n):
    return n ^ (n >> 1)

def gray_seq(bits):
    return [gray(i) for i in range(1 << bits)]

def bin_str(x, bits):
    return format(x, f"0{bits}b")

def build_layout(num_vars):
    if num_vars == 2:
        row_bits, col_bits = 1, 1
    elif num_vars == 3:
        row_bits, col_bits = 1, 2
    else:
        row_bits, col_bits = 2, 2

    rows = gray_seq(row_bits)
    cols = gray_seq(col_bits)

    mapping = {}
    for ri, rv in enumerate(rows):
        for ci, cv in enumerate(cols):
            if num_vars == 2:
                a = rv & 1
                b = cv & 1
                m = (a << 1) | b
            elif num_vars == 3:
                a = rv & 1
                b = (cv >> 1) & 1
                c = cv & 1
                m = (a << 2) | (b << 1) | c
            else:
                a = (rv >> 1) & 1
                b = rv & 1
                c = (cv >> 1) & 1
                d = cv & 1
                m = (a << 3) | (b << 2) | (c << 1) | d
            mapping[(ri, ci)] = m

    return rows, cols, mapping, row_bits, col_bits

class KMap:
    def __init__(self, nvars):
        self.nvars = nvars
        self.rows, self.cols, self.rc2m, self.rbits, self.cbits = build_layout(nvars)
        self.R = len(self.rows)
        self.C = len(self.cols)
        self.grid = [[0 for _ in range(self.C)] for _ in range(self.R)]

    def toggle(self, r, c):
        v = self.grid[r][c]
        if v == 0:
            self.grid[r][c] = 1
        elif v == 1:
            self.grid[r][c] = -1
        else:
            self.grid[r][c] = 0

    def set_all(self, val):
        for r in range(self.R):
            for c in range(self.C):
                self.grid[r][c] = val

    def cells_of_size(self, h, w):
        cells = []
        for r in range(self.R):
            for c in range(self.C):
                block = [((r + dr) % self.R, (c + dc) % self.C) for dr in range(h) for dc in range(w)]
                cells.append(block)
        return cells

    def is_group_valid(self, block):
        at_least_one_one = False
        for r, c in block:
            if self.grid[r][c] == 0:
                return False
            if self.grid[r][c] == 1:
                at_least_one_one = True
        return at_least_one_one

    def all_groups(self):
        if self.nvars == 2:
            sizes = [(2,2), (1,2), (2,1), (1,1)]
        elif self.nvars == 3:
            sizes = [(2,4), (1,4), (2,2), (1,2), (1,1)]
        else:
            sizes = [(4,4), (2,4), (4,2), (2,2), (1,4), (4,1), (1,2), (2,1), (1,1)]

        groups = []
        for h, w in sizes:
            if h > self.R or w > self.C:
                continue
            for blk in self.cells_of_size(h, w):
                if self.is_group_valid(blk):
                    groups.append(tuple(sorted(blk)))

        uniq = []
        seen = set()
        for g in groups:
            if g not in seen:
                uniq.append(g)
                seen.add(g)

        uniq.sort(key=lambda g: -len(g))
        return uniq

    def cover_ones_greedy(self):
        ones = {(r, c) for r in range(self.R) for c in range(self.C) if self.grid[r][c] == 1}
        if not ones:
            return []
        groups = self.all_groups()
        chosen = []
        covered = set()
        while ones - covered:
            best = None
            best_gain = 0
            for g in groups:
                gain = len([cell for cell in g if cell in (ones - covered)])
                if gain > best_gain:
                    best_gain = gain
                    best = g
            if best is None:
                remaining = list(ones - covered)
                for cell in remaining:
                    chosen.append((cell,))
                    covered.add(cell)
                break
            chosen.append(best)
            for cell in best:
                if cell in ones:
                    covered.add(cell)
        return chosen

    def group_to_literal(self, group):
        mins = [self.rc2m[cell] for cell in group]
        bits = self.nvars
        bitcols = list(zip(*[list(map(int, bin_str(m, bits))) for m in mins]))
        term = []
        varnames = ["A", "B", "C", "D"][:bits]
        for i, col in enumerate(bitcols):
            if all(b == 0 for b in col):
                term.append(varnames[i] + "'")
            elif all(b == 1 for b in col):
                term.append(varnames[i])
        if not term:
            return "1"
        return ''.join(term)

    def expression_SOP(self, groups):
        if not groups:
            if all(self.grid[r][c] == 0 for r in range(self.R) for c in range(self.C)):
                return "0"
            return "0"
        terms = [self.group_to_literal(g) for g in groups]
        uniq = []
        for t in terms:
            if t not in uniq:
                uniq.append(t)
        return ' + '.join(uniq)

class KMapGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("K-Map Simplifier (2/3/4 Variables)")
        self.geometry("980x620")
        self.resizable(False, False)

        self.nvars = tk.IntVar(value=4)
        self.kmap = KMap(self.nvars.get())

        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except:
            pass

        self._build_controls()
        self._build_canvas()
        self._redraw()

    def _build_controls(self):
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)

        ttk.Label(top, text="Variables:").pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="2", variable=self.nvars, value=2, command=self._change_vars).pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="3", variable=self.nvars, value=3, command=self._change_vars).pack(side=tk.LEFT)
        ttk.Radiobutton(top, text="4", variable=self.nvars, value=4, command=self._change_vars).pack(side=tk.LEFT)

        ttk.Button(top, text="All 0", command=lambda: self._set_all(0)).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="All 1", command=lambda: self._set_all(1)).pack(side=tk.LEFT)
        ttk.Button(top, text="All X", command=lambda: self._set_all(-1)).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Clear", command=lambda: self._set_all(0)).pack(side=tk.LEFT)

        ttk.Button(top, text="Minimize (SOP)", command=self._minimize).pack(side=tk.LEFT, padx=12)
        ttk.Button(top, text="Explain Steps", command=self._explain).pack(side=tk.LEFT)

        self.expr_var = tk.StringVar(value="F = 0")
        expr_frame = ttk.Frame(self)
        expr_frame.pack(side=tk.TOP, fill=tk.X, padx=10)
        ttk.Label(expr_frame, textvariable=self.expr_var, font=("Consolas", 12)).pack(side=tk.LEFT, pady=4)

    def _build_canvas(self):
        mid = ttk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self.canvas = tk.Canvas(mid, width=760, height=480, bg="#ffffff", highlightthickness=1, highlightbackground="#bbb")
        self.canvas.pack(side=tk.LEFT)

        right = ttk.Frame(mid)
        right.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Label(right, text="Legend:").pack(anchor='w')
        ttk.Label(right, text="Left-click: 0 → 1 → X → 0").pack(anchor='w')
        ttk.Label(right, text="SOP groups: 8/4/2/1 with wrap").pack(anchor='w')
        ttk.Separator(right, orient='horizontal').pack(fill=tk.X, pady=6)

        self.steps = tk.Text(right, width=32, height=24, font=("Consolas", 10))
        self.steps.pack()
        self.steps.insert('end', "Steps will appear here…\n")
        self.steps.configure(state='disabled')

        self.canvas.bind("<Button-1>", self._on_click)

    def _change_vars(self):
        self.kmap = KMap(self.nvars.get())
        self._redraw()
        self.expr_var.set("F = 0")
        self._set_steps(["Changed to {} variables".format(self.nvars.get())])

    def _set_all(self, val):
        self.kmap.set_all(val)
        self._redraw()
        self.expr_var.set("F = {}".format({0:"0",1:"1",-1:"X"}[val]))

    def _minimize(self):
        groups = self.kmap.cover_ones_greedy()
        expr = self.kmap.expression_SOP(groups)
        self.expr_var.set("F = " + expr)
        self._redraw(groups)
        lines = []
        lines.append("Found {} group(s)".format(len(groups)))
        for i, g in enumerate(groups, 1):
            mins = [self.kmap.rc2m[cell] for cell in g]
            term = self.kmap.group_to_literal(g)
            lines.append(f"G{i}: covers minterms {sorted(mins)} → {term}")
        self._set_steps(lines)

    def _explain(self):
        self._minimize()

    def _set_steps(self, lines):
        self.steps.configure(state='normal')
        self.steps.delete('1.0', 'end')
        for ln in lines:
            self.steps.insert('end', ln + "\n")
        self.steps.configure(state='disabled')

    def _redraw(self, groups=None):
        self.canvas.delete('all')
        W, H = 680, 400
        x0, y0 = 40, 40
        R, C = self.kmap.R, self.kmap.C
        cw = W // C
        ch = H // R

        for c in range(C):
            label = bin_str(self.kmap.cols[c], self.kmap.cbits)
            self.canvas.create_text(x0 + c*cw + cw/2, y0 - 16, text=label, font=("Consolas", 11))

        for r in range(R):
            label = bin_str(self.kmap.rows[r], self.kmap.rbits)
            self.canvas.create_text(x0 - 20, y0 + r*ch + ch/2, text=label, font=("Consolas", 11))

        for r in range(R):
            for c in range(C):
                x1 = x0 + c*cw
                y1 = y0 + r*ch
                x2 = x1 + cw
                y2 = y1 + ch
                v = self.kmap.grid[r][c]
                fill = "#ffffff"
                if v == 1:
                    fill = "#e6ffe6"
                elif v == -1:
                    fill = "#fff1cc"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#333")
                self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text={0:'0',1:'1',-1:'X'}[v], font=("Consolas", 14))
                m = self.kmap.rc2m[(r,c)]
                self.canvas.create_text(x1+12, y1+12, text=str(m), font=("Consolas", 9), fill="#666")

        if groups:
            for g in groups:
                self._draw_group(g, x0, y0, cw, ch)

        if self.kmap.nvars == 2:
            self.canvas.create_text(x0 + W/2, y0 - 36, text="B", font=("Consolas", 11))
            self.canvas.create_text(x0 - 32, y0 + H/2, text="A", font=("Consolas", 11), angle=90)
        elif self.kmap.nvars == 3:
            self.canvas.create_text(x0 + W/2, y0 - 36, text="BC", font=("Consolas", 11))
            self.canvas.create_text(x0 - 32, y0 + H/2, text="A", font=("Consolas", 11), angle=90)
        else:
            self.canvas.create_text(x0 + W/2, y0 - 36, text="CD", font=("Consolas", 11))
            self.canvas.create_text(x0 - 32, y0 + H/2, text="AB", font=("Consolas", 11), angle=90)

    def _draw_group(self, group, x0, y0, cw, ch):
        R, C = self.kmap.R, self.kmap.C
        cells = list(group)
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]

        def span(indices, mod):
            if not indices:
                return 0, 0
            best = (mod+1, 0)
            uniq = sorted(set(indices))
            for start in uniq:
                cover = set(((i - start) % mod) for i in indices)
                length = max(cover) - min(cover) + 1 if cover else 1
                best = min(best, (length, start), key=lambda x: x[0])
            return best

        hr, r0 = span(rs, R)
        hc, c0 = span(cs, C)

        r_range = [(r0 + i) % R for i in range(hr)]
        c_range = [(c0 + j) % C for j in range(hc)]

        def chunks(arr, mod):
            out = []
            cur = [arr[0]]
            for a, b in zip(arr, arr[1:]):
                if (b - a) % mod == 1:
                    cur.append(b)
                else:
                    out.append(cur)
                    cur = [b]
            out.append(cur)
            return out

        r_chunks = chunks(r_range, R)
        c_chunks = chunks(c_range, C)

        for rr in r_chunks:
            for cc in c_chunks:
                rx1 = x0 + min(cc)*cw + 4
                ry1 = y0 + min(rr)*ch + 4
                rx2 = x0 + (max(cc)+1)*cw - 4
                ry2 = y0 + (max(rr)+1)*ch - 4
                self.canvas.create_rectangle(rx1, ry1, rx2, ry2, outline="#ff4d4d", width=2)

    def _on_click(self, event):
        x, y = event.x, event.y
        x0, y0 = 40, 40
        W, H = 680, 400
        cw = W // self.kmap.C
        ch = H // self.kmap.R
        if not (x0 <= x <= x0 + self.kmap.C*cw and y0 <= y <= y0 + self.kmap.R*ch):
            return
        c = (x - x0) // cw
        r = (y - y0) // ch
        self.kmap.toggle(r, c)
        self._redraw()

if __name__ == "__main__":
    app = KMapGUI()
    app.mainloop()
