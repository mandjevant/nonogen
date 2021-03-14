from PIL import Image, ImageDraw
import statistics
import re


class no_generator:
    def __init__(self, img_path, size, colour):
        self._img_path = img_path
        self._size = size.split("x")
        self._colour = colour

        self._img = Image.open(self._img_path)
        self._filename = re.findall(r"[\w-]+\.", self._img_path)[0][:-1]
        self._solution = None
        self._nonogram = None
        self._pixels = None
        self._m = 32

    @staticmethod
    def r_g_b_to_hx(rgb: set) -> str:
        return "#%02x%02x%02x" % rgb

    def run(self):
        try:
            self._resize()
            if not self._colour:
                self._convert()

            self._pixel_matrix()

            img = self._new_image()
            self._solution = img

            self._fill_solution_grid()
            self._solution = self._visualize_grid(self._solution)

            # self._nonogram = self._img

            self._save_solution()
            return True
        except Exception as e:
            print(f"Something went wrong. \nThe error: {e}")
            return False

    def _pixel_matrix(self):
        pixels = list(self._img.getdata())
        self._pixels = [pixels[i * int(self._size[1]):(i + 1) * int(self._size[1])] for i in range(int(self._size[0]))]

    def _resize(self):
        self._img = self._img.resize((int(self._size[0]), int(self._size[1])))

    def _convert(self):
        self._img = self._img.convert("1")

    def _new_image(self) -> Image:
        img = Image.new(mode="RGB", size=((int(self._size[0]) + 2) * self._m,
                                          (int(self._size[1]) + 2) * self._m), color=(255, 255, 255))

        return img

    def _visualize_grid(self, img: Image) -> Image:
        draw = ImageDraw.Draw(img, mode="RGB")

        counter = 0
        for x in range(self._m, img.width - self._m + 1, self._m):
            if counter % 5 == 0:
                draw.line(((x, self._m), (x, img.width - self._m)), width=2, fill=(0, 0, 0))
            elif counter == int(self._size[0]):
                draw.line(((x, self._m), (x, img.width - self._m)), width=2, fill=(0, 0, 0))
            else:
                draw.line(((x, self._m), (x, img.width - self._m)), fill=(0, 0, 0))

            counter += 1

        counter = 0
        for y in range(self._m, img.height - self._m + 1, self._m):
            if counter % 5 == 0:
                draw.line(((self._m, y), (img.height - self._m, y)), width=2, fill=(0, 0, 0))
            elif counter == int(self._size[1]):
                draw.line(((self._m, y), (img.height - self._m, y)), width=2, fill=(0, 0, 0))
            else:
                draw.line(((self._m, y), (img.height - self._m, y)), fill=(0, 0, 0))

            counter += 1

        del counter
        del draw

        return img

    def _fill_solution_grid(self):
        draw = ImageDraw.Draw(self._solution, mode="RGB")
        for row_index in range(len(self._pixels)):
            for column_index in range(len(self._pixels[row_index])):
                if self._pixels[row_index][column_index] != 255 and self._pixels[row_index][column_index] != (255, 255, 255):
                    if self._colour:
                        draw.rectangle([(self._m + column_index * self._m, self._m + row_index * self._m),
                                        (self._m + column_index * self._m + self._m,
                                         self._m + row_index * self._m + self._m)],
                                       fill=self._pixels[row_index][column_index])
                    else:
                        draw.rectangle([(self._m + column_index * self._m, self._m + row_index * self._m),
                                        (self._m + column_index * self._m + self._m,
                                         self._m + row_index * self._m + self._m)],
                                       fill=(0, 0, 0))
        del draw

    def _save_nonogram(self):
        if self._colour:
            self._nonogram.save(f"nonograms/{self._filename}_colour_nonogram.png")
        else:
            self._nonogram.save(f"nonograms/{self._filename}_nonogram.png")

    def _save_solution(self):
        if self._colour:
            self._solution.save(f"solutions/{self._filename}_colour_solution.png")
        else:
            self._solution.save(f"solutions/{self._filename}_solution.png")
