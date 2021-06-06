from PIL import Image, ImageDraw, ImageFont
import traceback
import typing
import re
import os


class no_generator:
    """
    Main nonogram generator class
    """
    def __init__(self, img_path: str, size: str, colour: bool):
        """
        Initiate variables for nonogram generator class
         prepare initial variables
        :param img_path: path to image | str
        :param size: height and width of nonogram | str
        :param colour: colour | bool
        """
        self._img_path = img_path
        self.base_path = os.path.normpath(
            os.path.normpath(self._img_path + os.sep + os.pardir) + os.sep + os.pardir)

        self._size = size.split("x")
        self._colour = colour

        self._img = Image.open(self._img_path)
        self._filename = re.findall(r"[\w-]+\.", self._img_path)[0][:-1]
        self._solution = None
        self._nonogram = None
        self._pixels = None
        self._clean_rows = list()
        self._clean_columns = list()
        self._indic_rows = list()
        self._indic_columns = list()
        self._m = 32

    @staticmethod
    def r_g_b_to_hx(rgb: set) -> str:
        """
        Convert rgb to hex
        :param rgb: (r, g, b) | set
        :return: hex representation of rgb | str
        """
        return "#%02x%02x%02x" % rgb

    @staticmethod
    def transpose(arr: list) -> list:
        """
        Transpose a two-dimensional array
        :param arr: two-dimensional array | list
        :return: transposed array | list
        """
        return [[arr[j][i] for j in range(len(arr))] for i in range(len(arr[0]))]

    @staticmethod
    def _gen_indic_values(cleaned_list: list) -> list:
        """
        Generate indicative values based on pixel matrix
        :param cleaned_list: list of indicative rgb values | list
        :return: indicative values | list
        """
        indic_list = list()

        for i in cleaned_list:
            indic_i = list()
            prev_val = None

            for val_index in range(len(i)):
                if i[val_index] in [(255, 255, 255), 255]:
                    prev_val = None
                else:
                    if i[val_index] == prev_val:
                        indic_i[-1] = [indic_i[-1][0] + 1, indic_i[-1][1]]
                    else:
                        indic_i.append([1, i[val_index]])

                    prev_val = i[val_index]

            indic_list.append(indic_i)

        return indic_list

    def run(self) -> bool:
        """
        Main loop for nonogram generator
        :return: True on success, False and stacktrace on failure | bool
        """
        try:
            # Parse image and acquire pixel matrix
            self._resize()

            self._pixel_matrix()
            self._clean_pixels()

            self._indic_rows = no_generator._gen_indic_values(self._clean_rows)
            self._indic_columns = no_generator._gen_indic_values(self._clean_columns)

            # Generate and save solution
            self._solution = self._new_image()

            self._fill_solution_grid()
            self._solution = self._visualize_grid(self._solution)
            self._save_solution()

            # Generate and save nonogram
            extra_height = max([len(column) for column in self._indic_columns])
            extra_width = max([len(row) for row in self._indic_rows])
            self._nonogram = self._new_image(width=(int(self._size[0]) + 2 + extra_width) * self._m,
                                             height=(int(self._size[1]) + 2 + extra_height) * self._m)

            self._nonogram = self._visualize_grid(self._nonogram, extra_width * self._m, extra_height * self._m)
            self._nonogram = self._indic_boxes(self._nonogram, extra_width * self._m, extra_height * self._m)

            self._save_nonogram()

            return True
        except Exception as e:
            print(f"Something went wrong. \nThe error: {e}")

            traceback.print_exc()

            return False

    def _clean_pixels(self) -> None:
        """
        Remove white pixels (not part of image) from pixel matrix
        """
        if self._colour:
            for row in self._pixels:
                clean_row = [pix for pix in row if pix != (255, 255, 255)]
                self._clean_rows.append(clean_row)

            for column in no_generator.transpose(self._pixels):
                clean_column = [pix for pix in column if pix != (255, 255, 255)]
                self._clean_columns.append(clean_column)
        else:
            self._clean_rows = self._pixels
            self._clean_columns = no_generator.transpose(self._pixels)

    def _pixel_matrix(self) -> None:
        """
        Generate pixel matrix from PILLOW image
        """
        pixels = list(self._img.getdata())
        self._pixels = [pixels[i * int(self._size[0]):(i + 1) * int(self._size[0])] for i in range(int(self._size[1]))]

        if not self._colour:
            for row in self._pixels:
                for i in range(len(row)):
                    if row[i] not in [(255, 255, 255), 255]:
                        row[i] = (0, 0, 0)

    def _resize(self) -> None:
        """
        Resize image to desired nonogram size
        """
        self._img = self._img.resize((int(self._size[0]), int(self._size[1])))

    def _convert(self) -> None:
        """
        Convert image to greyscale
        """
        self._img = self._img.convert("1")

    def _new_image(self, width: typing.Optional[int] = None, height: typing.Optional[int] = None) -> Image:
        """
        Create new image using PILLOW
        :param width: width of image | Optional[int]
        :param height: height of image | Optional[int]
        :return: new image | Image
        """
        if width is None:
            width = (int(self._size[0]) + 2) * self._m

        if height is None:
            height = (int(self._size[1]) + 2) * self._m

        img = Image.new(mode="RGB", size=(width, height), color=(255, 255, 255))

        return img

    def _indic_boxes(self, img: Image, w_off: int, h_off: int) -> Image:
        """
        Main function for drawing indicative boxes on the nonogram
        :param img: nonogram image | Image
        :param w_off: width offset | int
        :param h_off: height offset | int
        :return: nonogram image | Image
        """
        self._indic_columns = [[[0, (240, 240, 240)]] if col == [] else col for col in self._indic_columns]
        self._indic_rows = [[[0, (240, 240, 240)]] if row == [] else row for row in self._indic_rows]

        img = self._draw_indic_columns(img, w_off, h_off)
        img = self._draw_indic_rows(img, w_off, h_off)

        return img

    def _draw_indic_columns(self, img: Image, w_off: int, h_off: int) -> Image:
        """
        Draw indicative boxes for columns on the nonogram
        :param img: nonogram image | Image
        :param w_off: width offset | int
        :param h_off: height offset | int
        :return: nonogram image | Image
        """
        draw = ImageDraw.Draw(img, mode="RGB")

        column_counter = 0
        for column in self._indic_columns:
            if len(column) > 0:
                box_counter = 0
                for indic_c_box in column[::-1]:
                    min_x = self._m + w_off + column_counter * self._m
                    min_y = self._m + h_off - box_counter * self._m
                    rect_fill = indic_c_box[1] if self._colour else (240, 240, 240)

                    draw.rectangle(xy=[(min_x, min_y), (min_x + self._m, min_y - self._m)],
                                   fill=rect_fill,
                                   outline=(0, 0, 0))

                    draw.line(((min_x, min_y), (min_x, min_y - self._m)), fill=(0, 0, 0))
                    draw.line(((min_x, min_y), (min_x + self._m, min_y)), fill=(0, 0, 0))
                    draw.line(((min_x, min_y + self._m), (min_x + self._m, min_y + self._m)), fill=(0, 0, 0))
                    draw.line(((min_x + self._m, min_y), (min_x + self._m, min_y - self._m)), fill=(0, 0, 0))

                    box_counter += 1

                for y in range(len(column[::-1])):
                    min_x = 1 + self._m + w_off + column_counter * self._m
                    min_y = self._m + h_off - y * self._m
                    rect_fill = column[::-1][y][1] if self._colour else (240, 240, 240)

                    if column_counter % 5 == 0:
                        draw.line(((min_x, min_y), (min_x, min_y - self._m)), width=2, fill=(0, 0, 0))

                    if column_counter == len(self._indic_columns) - 1:
                        draw.line(((min_x + self._m, min_y), (min_x + self._m, min_y - self._m)), width=2,
                                  fill=(0, 0, 0))

                    if y == len(column[::1]) - 1:
                        draw.line(((min_x - 1, min_y - self._m), (min_x - 1 + self._m, min_y - self._m)), width=2,
                                  fill=(0, 0, 0))

                    draw.text(xy=(min_x + round(self._m/3, 0) if column[::-1][y][0] < 10
                                  else min_x + round(self._m/6, 0),
                                  min_y - 2*self._m/3),
                              text=str(column[::-1][y][0]),
                              font=ImageFont.truetype("arial.ttf", int(round(self._m / 2, 0))),
                              fill=(0, 0, 0) if sum(rect_fill) > 350 else (255, 255, 255),
                              align="center")

                if column_counter != 0:
                    beg_y = self._m + h_off - len(self._indic_columns[column_counter - 1]) * self._m
                    end_y = self._m + h_off - len(self._indic_columns[column_counter]) * self._m
                    if len(self._indic_columns[column_counter]) > len(self._indic_columns[column_counter - 1]):
                        cal_x = 1 + self._m + w_off + column_counter * self._m
                        draw.line(((cal_x, beg_y), (cal_x, end_y)), width=2, fill=(0, 0, 0))
                    elif len(self._indic_columns[column_counter]) < len(self._indic_columns[column_counter - 1]):
                        cal_x = self._m + w_off + column_counter * self._m
                        draw.line(((cal_x, beg_y), (cal_x, end_y)), width=2, fill=(0, 0, 0))

            column_counter += 1

        del column_counter
        del draw

        return img

    def _draw_indic_rows(self, img: Image, w_off: int, h_off: int) -> Image:
        """
        Draw indicative boxes for rows on the nonogram
        :param img: nonogram image | Image
        :param w_off: width offset | int
        :param h_off: height offset | int
        :return: nonogram image | Image
        """
        draw = ImageDraw.Draw(img, mode="RGB")

        row_counter = 0
        for row in self._indic_rows:
            if len(row) > 0:
                box_counter = 0
                for indic_r_box in row[::-1]:
                    min_x = self._m + w_off - box_counter * self._m
                    min_y = self._m + h_off + row_counter * self._m
                    rect_fill = indic_r_box[1] if self._colour else (240, 240, 240)

                    draw.rectangle(xy=[(min_x, min_y), (min_x - self._m, min_y + self._m)],
                                   fill=rect_fill,
                                   outline=(0, 0, 0))

                    draw.line(((min_x, min_y), (min_x, min_y + self._m)), fill=(0, 0, 0))
                    draw.line(((min_x, min_y), (min_x - self._m, min_y)), fill=(0, 0, 0))
                    draw.line(((min_x, min_y + self._m), (min_x - self._m, min_y + self._m)), fill=(0, 0, 0))
                    draw.line(((min_x - self._m, min_y), (min_x - self._m, min_y + self._m)), fill=(0, 0, 0))

                    box_counter += 1

                for y in range(len(row[::-1])):
                    min_x = 1 + self._m + w_off - y * self._m
                    min_y = self._m + h_off + row_counter * self._m
                    rect_fill = row[::-1][y][1] if self._colour else (240, 240, 240)

                    if row_counter % 5 == 0:
                        draw.line(((min_x, min_y + 1), (min_x - self._m, min_y + 1)), width=2, fill=(0, 0, 0))

                    if row_counter == len(self._indic_rows) - 1:
                        draw.line(((min_x, min_y + self._m + 1), (min_x - self._m, min_y + self._m + 1)), width=2,
                                  fill=(0, 0, 0))

                    if y == len(row[::1]) - 1:
                        draw.line(((min_x - 1 - self._m, min_y), (min_x - 1 - self._m, min_y + self._m)), width=2,
                                  fill=(0, 0, 0))

                    draw.text(xy=(min_x - self._m + round(self._m/3, 0) if row[::-1][y][0] < 10
                                  else min_x - self._m + round(self._m/6, 0),
                                  min_y + self._m/4),
                              text=str(row[::-1][y][0]),
                              font=ImageFont.truetype("arial.ttf", int(round(self._m/2, 0))),
                              fill=(0, 0, 0) if sum(rect_fill) > 350 else (255, 255, 255),
                              align="center")

                if row_counter != 0:
                    beg_x = self._m + w_off - len(self._indic_rows[row_counter - 1]) * self._m
                    end_x = self._m + w_off - len(self._indic_rows[row_counter]) * self._m

                    if len(self._indic_rows[row_counter]) > len(self._indic_rows[row_counter - 1]):
                        cal_y = 1 + self._m + h_off + row_counter * self._m
                        draw.line(((beg_x, cal_y), (end_x, cal_y)), width=2, fill=(0, 0, 0))
                    elif len(self._indic_rows[row_counter]) < len(self._indic_rows[row_counter - 1]):
                        cal_y = self._m + h_off + row_counter * self._m
                        draw.line(((beg_x, cal_y), (end_x, cal_y)), width=2, fill=(0, 0, 0))

            row_counter += 1

        del row_counter
        del draw

        return img

    def _visualize_grid(self, img: Image, w_offset: typing.Optional[int] = 0,
                        h_offset: typing.Optional[int] = 0) -> Image:
        """
        Visualize grid on solution and nonogram images
        :param img: image to draw grid on | Image
        :param w_offset: width offset | Optional[int]
        :param h_offset: height offset | Optional[int]
        :return: image with grid | Image
        """
        draw = ImageDraw.Draw(img, mode="RGB")

        counter = 0
        for x in range(w_offset + self._m, img.width - self._m + 1, self._m):
            if counter % 5 == 0:
                draw.line(((x, self._m + h_offset), (x, img.height - self._m)), width=2, fill=(0, 0, 0))
            elif counter == int(self._size[0]):
                draw.line(((x, self._m + h_offset), (x, img.height - self._m)), width=2, fill=(0, 0, 0))
            else:
                draw.line(((x, self._m + h_offset), (x, img.height - self._m)), fill=(0, 0, 0))

            counter += 1

        counter = 0
        for y in range(h_offset + self._m, img.height - self._m + 1, self._m):
            if counter % 5 == 0:
                draw.line(((self._m + w_offset, y), (img.width - self._m, y)), width=2, fill=(0, 0, 0))
            elif counter == int(self._size[1]):
                draw.line(((self._m + w_offset, y), (img.width - self._m, y)), width=2, fill=(0, 0, 0))
            else:
                draw.line(((self._m + w_offset, y), (img.width - self._m, y)), fill=(0, 0, 0))

            counter += 1

        del counter
        del draw

        return img

    def _fill_solution_grid(self) -> None:
        """
        Fill grid on solution image
        """
        draw = ImageDraw.Draw(self._solution, mode="RGB")

        for row_index in range(len(self._pixels)):
            for column_index in range(len(self._pixels[row_index])):
                if self._pixels[row_index][column_index] != 255 and \
                        self._pixels[row_index][column_index] != (255, 255, 255):
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

    def _save_nonogram(self) -> None:
        """
        Save the nonogram image
        """
        if self._colour:
            self._nonogram.save(os.path.join(self.base_path, "nonograms", f"{self._filename}_colour_nonogram.png"))
        else:
            self._nonogram.save(os.path.join(self.base_path, "nonograms", f"{self._filename}_nonogram.png"))

    def _save_solution(self) -> None:
        """
        Save the solution image
        """
        if self._colour:
            self._solution.save(os.path.join(self.base_path, "solutions", f"{self._filename}_colour_solution.png"))
        else:
            self._solution.save(os.path.join(self.base_path, "solutions", f"{self._filename}_solution.png"))
