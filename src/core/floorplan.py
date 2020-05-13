from lxml import etree
from lxml.cssselect import CSSSelector


class Floorplan:

    def __init__(self, output_pipe, floorplan_svg_path, video_file_processing, room_color='#69c7e5'):
        """
        Construct a floorplan.

        Parameters
        ----------
        - output_pipe - The pipe to write data to.
        - floorplan_svg_path -- The path to the SVG to show.
        - video_file_processing -- The video file we're processing.
        - room_color -- Color to color the rooms with. (Default: #69c7e5)
        """
        self._output_pipe = output_pipe
        self._room_color = room_color
        self.__init_html_tree(floorplan_svg_path)
        self.update_current_video(video_file_processing)


    def __init_html_tree(self, floorplan_svg_path):
        """
        Construct the HTML tree for the given SVG.

        Parameters
        ----------
        - floorplan_svg_path -- The path to the SVG to show.
        """
        self.html = etree.Element("html")
        head = etree.SubElement(self.html, "head")
        title = etree.SubElement(head, "title")
        title.text = 'MSK floorplan'
        style = etree.SubElement(head, "style")
        style.text = "#content { display: flex; flex-direction: column; justify-content: space-around; align-items: center; } #content img { width: 50%; }"
        body = etree.SubElement(self.html, "body")

        content = etree.SubElement(body, 'div')
        content.set('id', 'content')

        svg = etree.parse(floorplan_svg_path, parser=etree.HTMLParser())
        content.append(svg.getroot())

        img = etree.SubElement(content, "img")
        img.set('alt', 'Video frame processed will come here...')


        self._img_preview = img
        self.html_tree = etree.ElementTree(self.html)


    def __content_updated(self):
        """
        Send the updated HTML tree to the given output pipe.
        """
        if not self.html_tree:
            raise Exception('No root element created!')

        self._output_pipe.send(etree.tostring(self.html))


    def __update_room(self, room, chance, is_current=False):
        """
        Update the chance of the given room if the room exists.

        Parameters
        ----------
        - room - The room to update.
        - chance - The chance of the room.
        - is_current - Is this room the current one? (Default: False)

        Returns
        -------
        Nothing.
        """
        rooms_found = CSSSelector(f'polygon#{room}')(self.html)

        if len(rooms_found):
            room_in_svg = rooms_found[0]
            room_in_svg.set('style', f'fill:{self._room_color};opacity:{round(chance, 4)}')

            if is_current:
                current_room = CSSSelector('text#currentRoom')(self.html)[0]
                current_room.text = room

                probability = CSSSelector('text#probability')(self.html)[0]
                probability.text = f'{round(chance * 100, 2)} %'


    def __update_image(self, image):
        self._img_preview.set('src', f'data:image/jpeg;base64,{image}')


    def update_current_video(self, video):
        """
        Update the video that's currently being processed.

        Parameters
        ----------
        - video - The room to set.
        """
        current_video = CSSSelector('text#currentVideo')(self.html)[0]
        current_video.text = video
        self.__content_updated()


    def update_rooms(self, all_room_chances, current_room, image):
        """
        Update the chances for all rooms.

        Parameters
        ----------
        - all_room_chances -- The chances for all rooms.
        - current_room -- The current room we're in.
        """
        for room, chance in all_room_chances.items():
            self.__update_room(room, chance, room == current_room)

        self.__update_image(image)
        self.__content_updated()
