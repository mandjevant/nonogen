import PIL
import re


class no_generator:
    def __init__(self, img_path, size, colour):
        self.img_path = img_path
        self.size = size
        self.colour = colour

        self._img = PIL.Image.Open(self.img_path)
        self._filename = re.findall(r"[^\/]+(?=\.)", self.img_path)[0]
        self._solution = None
        self._nonogram = None

    def main(self):
        try:
            self._resize()
            self._save_nonogram()
        except Exception as e:
            print(f"Something went wrong. \nThe error: {e}")

        return True

    def _resize(self):
        return True

    def _save_nonogram(self):
        self._nonogram.save(f"nonograms/{self._filename}_nonogram.png")

    def _save_solution(self):
        self._solution.save(f"solutions/{self._filename}_solution.png")


