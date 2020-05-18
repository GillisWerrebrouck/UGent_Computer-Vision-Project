from time import time
from lxml import etree
from lxml.cssselect import CSSSelector

cdef class Floorplan:

    cdef str _room_color, _current_room_color
    cdef float _last_update
    cdef object _html, _img_preview, _html_tree

    def __init__(self, floorplan_svg_path, video_file_processing, room_color='#2980b9',
    current_room_color='#c0392b'):
        """
        Construct a floorplan.

        Parameters
        ----------
        - output_pipe - The pipe to write data to.
        - floorplan_svg_path -- The path to the SVG to show.
        - video_file_processing -- The video file we're processing.
        - room_color -- Color to color the rooms with. (Default: #69c7e5)
        """
        self._last_update = 0
        self._room_color = room_color
        self._current_room_color = current_room_color
        self.__init_html_tree(floorplan_svg_path)
        self.update_current_video(video_file_processing)


    cpdef __init_html_tree(self, str floorplan_svg_path):
        """
        Construct the HTML tree for the given SVG.

        Parameters
        ----------
        - floorplan_svg_path -- The path to the SVG to show.
        """
        self._html = etree.Element("html")
        cdef object head = etree.SubElement(self._html, "head")
        cdef object title = etree.SubElement(head, "title")
        title.text = 'MSK floorplan'
        cdef object style = etree.SubElement(head, "style")
        css_file = open('floorplan.css', 'r')
        style.text = css_file.read()

        cdef object body = etree.SubElement(self._html, "body")

        cdef object content = etree.SubElement(body, 'div')
        content.set('id', 'content')

        cdef object svg = etree.parse(floorplan_svg_path, parser=etree.HTMLParser())
        content.append(svg.getroot())

        cdef object img = etree.SubElement(content, "img")
        img.set('alt', 'Video frame processed will come here...')


        self._img_preview = img
        self._html_tree = etree.ElementTree(self._html)


    cdef __update_room(self, str room, float chance, int is_current=False):
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
        cdef list rooms_found = CSSSelector(f'polygon#{room}')(self._html)

        cdef object current_room, probability
        cdef str color = self._current_room_color if is_current else self._room_color
        cdef float opacity = 1 if is_current else round(chance, 4)
        if len(rooms_found):
            room_in_svg = rooms_found[0]
            room_in_svg.set('style', f'fill:{color};opacity:{opacity}')

            if is_current:
                current_room = CSSSelector('text#currentRoom')(self._html)[0]
                current_room.text = room

                probability = CSSSelector('text#probability')(self._html)[0]
                probability.text = f'{round(chance * 100, 2)} %'


    cdef update_image(self, object image):
        self._img_preview.set('src', f'data:image/jpeg;base64,{image}')


    cpdef update_current_video(self, str video):
        """
        Update the video that's currently being processed.

        Parameters
        ----------
        - video - The room to set.
        """
        current_video = CSSSelector('text#currentVideo')(self._html)[0]
        current_video.text = video


    cpdef update_rooms(self, dict all_room_chances, str current_room, object image, str video_file):
        """
        Update the chances for all rooms.

        Parameters
        ----------
        - all_room_chances -- The chances for all rooms.
        - current_room -- The current room we're in.
        """
        for room, chance in all_room_chances.items():
            self.__update_room(room, chance, room == current_room)

        self.update_image(image)
        self.update_current_video(video_file)
        return self.tostring()


    cpdef tostring(self):
        if not self._html or len(self._html) == 0:
            return 'Loading...'

        return etree.tostring(self._html)
