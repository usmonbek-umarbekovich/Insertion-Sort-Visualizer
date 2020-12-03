import random
import tkinter as tk
import math
import time


class DrawingCanvas():
    """ A canvas drawing manager """

    def __init__(self, canvas, wxmin, wymin, wxmax, wymax, dmargin, y_is_flipped):
        self.canvas = canvas
        self.wxmin = wxmin
        self.wymin = wymin
        self.wxmax = wxmax
        self.wymax = wymax
        self.dmargin = dmargin
        self.y_is_flipped = y_is_flipped

        self.set_scales()

    def set_scales(self):
        """ Calculate scale parameters for the canvas's current size. """
        self.canvas.update()
        self.dxmin = self.dmargin
        self.dymin = self.dmargin
        self.dxmax = self.canvas.winfo_width() - self.dmargin - 1
        self.dymax = self.canvas.winfo_height() - self.dmargin - 1

        # Flip the coordinates to invert the result
        if self.y_is_flipped:
            self.dymin, self.dymax = self.dymax, self.dymin

        self.xscale = (self.dxmax - self.dxmin) / (self.wxmax - self.wxmin)
        self.yscale = (self.dymax - self.dymin) / (self.wymax - self.wymin)

        # Calculate 1 pixel in world coordinates
        self.xpix = 1 / self.xscale
        self.ypix = 1 / self.yscale

    def w_to_d(self, wx, wy):
        """ Map a point from world to device coordinates """
        dx = (wx - self.wxmin) * self.xscale + self.dxmin
        dy = (wy - self.wymin) * self.yscale + self.dymin
        return dx, dy

    def clear(self):
        self.canvas.delete(tk.ALL)

    def rectangle(self, wx0, wy0, wx1, wy1, fill, outline):
        """ Draw a rectangle at the indicated position in world coordinates """
        dx0, dy0 = self.w_to_d(wx0, wy0)
        dx1, dy1 = self.w_to_d(wx1, wy1)
        return self.canvas.create_rectangle(dx0, dy0, dx1, dy1, fill=fill, outline=outline)

    def rect_coords(self, obj, x0, y0, x1, y1):
        dx0, dy0 = self.w_to_d(x0, y0)
        dx1, dy1 = self.w_to_d(x1, y1)
        self.canvas.coords(obj, dx0, dy0, dx1, dy1)

    def rect_config(self, obj, fill, outline):
        self.canvas.itemconfigure(obj, fill=fill, outline=outline)


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Insertion Sort')
        self.window.protocol('WM_DELETE_WINDOW', self.kill_callback)

        self.canvas = tk.Canvas(self.window, relief=tk.RIDGE, bd=5, highlightthickness=0,
                                bg='white')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        frame = tk.Frame(self.window)
        frame.pack(side=tk.TOP, expand=True)

        label = tk.Label(frame, text='Intervals:')
        label.grid(padx=5, pady=2, row=0, column=0)
        self.intervals_entry = tk.Entry(frame, width=5, justify=tk.RIGHT)
        self.intervals_entry.grid(padx=5, pady=2, row=0, column=1)
        self.intervals_entry.insert(0, '10')

        label = tk.Label(frame, text='Time:')
        label.grid(padx=5, pady=2, row=1, column=0)
        self.elapsed = tk.Label(frame, text='')
        self.elapsed.grid(padx=5, pady=2, row=1, column=1)

        generate = tk.Button(frame, text='Generate', width=10, command=self.generate)
        generate.grid(padx=5, pady=2, row=2, column=0)

        self.insertion_button = tk.Button(frame, text='Insertion', width=10, command=self.insertion)
        self.insertion_button.grid(padx=5, pady=2, row=2, column=2)


        self.speed = tk.IntVar()
        radiobutton = tk.Radiobutton(frame, text="Slow", variable=self.speed, value=0)
        radiobutton.grid(padx=5, pady=2, row=0, column=2)
        radiobutton = tk.Radiobutton(frame, text="Fast", variable=self.speed, value=1)
        radiobutton.grid(padx=5, pady=2, row=1, column=2)

        # make the DrawingCanvas
        self.wxmin = 1
        self.wymin = 1
        self.wxmax = 100
        self.wymax = 100
        self.drawing_canvas = DrawingCanvas(self.canvas, self.wxmin, self.wymin, self.wxmax, self.wymax, 0, True)

        self.intervals_entry.focus_force()
        self.window.mainloop()

    def kill_callback(self):
        self.window.destroy()

    def generate(self):
        self.drawing_canvas.clear()
        self.values = []
        self.insertion_button['state'] = tk.NORMAL
        self.elapsed['text'] = ''

        intervals = int(self.intervals_entry.get())
        dx = 99 / intervals

        x = 1
        for _ in range(intervals):
            y = random.randint(1, 100)
            cords = (x, 0, x + dx, y)
            rect = self.drawing_canvas.rectangle(*cords, 'lightblue', 'blue')
            self.values.append((rect, *cords))

            # move to the next slice
            x += dx
            
    def insertion(self):
        """ perform the integration """
        self.insertion_button['state'] = tk.DISABLED
        # get parameters
        intervals = int(self.intervals_entry.get())
        dx = 99 / intervals

        if self.values:
            start = time.time()
            for i in range(intervals):
                y = self.values[i]
                self.drawing_canvas.rect_config(y[0], 'red', 'red')
                self.values[i] = self.up_down(*self.values[i], 0, 0.06, 0, 0.06)
                for j in range(i, -1, -1):
                    if not(j) or y[4] >= self.values[j-1][4]:
                        self.drawing_canvas.rect_config(y[0], 'green', 'green')
                        self.values[j] = self.up_down(*self.values[j], 0, -0.06, 0, -0.06)
                        break
                    self.values[j-1], self.values[j] = self.move_same(self.values[j][0], self.values[j-1][0],
                                                                      (self.values[j][1:] + (-dx/50, 0, -dx/50, 0)),
                                                                      (self.values[j-1][1:] + (dx/50, 0, dx/50, 0)))
            end = time.time()
            res = end - start
            self.elapsed['text'] = f'{res:.3f} seconds'
        self.insertion_button['state'] = tk.NORMAL


    def up_down(self, obj, *cords):
        x0, y0, x1, y1 = cords[:4]
        x0m, y0m, x1m, y1m = cords[4:]
        for _ in range(50):
            if not self.speed.get():
                time.sleep(0.0000000000000000001)
            self.drawing_canvas.rect_coords(obj, x0, y0, x1, y1)
            x0 += x0m
            y0 += y0m
            x1 += x1m
            y1 += y1m
            self.canvas.update()
        return obj, x0, y0, x1, y1

    def move_same(self, obj1, obj2, cords1, cords2):
        x00, y00, x10, y10 = cords1[:4]
        x00m, y00m, x10m, y10m = cords1[4:]
        x01, y01, x11, y11 = cords2[:4]
        x01m, y01m, x11m, y11m = cords2[4:]
        for _ in range(50):
            if not self.speed.get():
                time.sleep(0.00000001)
            self.drawing_canvas.rect_coords(obj1, x00, y00, x10, y10)
            self.drawing_canvas.rect_coords(obj2, x01, y01, x11, y11)
            self.canvas.update()
            x00 += x00m
            y00 += y00m
            x10 += x10m
            y10 += y10m

            x01 += x01m
            y01 += y01m
            x11 += x11m
            y11 += y11m
            
        return (obj1, x00, y00, x10, y10), (obj2, x01, y01, x11, y11)
            


if __name__ == '__main__':
    app = App()
