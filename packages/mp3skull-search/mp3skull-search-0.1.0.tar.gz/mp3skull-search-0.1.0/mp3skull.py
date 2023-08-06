#/usr/bin/python3

from re import search, match
from datetime import timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment



class Mp3Skull(object):
    query_url = 'http://mp3skull.com/mp3/%(query)s.html'

    def __init__(self, query):
        self.query = query.strip().lower()


    def _strip_html_comment_nodes(self, soup):
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))

        for comment in comments:
            comment.extract()


    def _get_html(self):
        request = urlopen(self.query_url % { 'query': self.query })
        data = request.read()
        text = data.decode('utf-8')

        return text


    def _parse_info_node(self, node):
        text = ''.join(map(str, node.contents)).strip()

        file_size_search = search(r'(\d+(\.\d+)?) mb', text)
        file_size = float(file_size_search.group(1)) if file_size_search else None

        duration_search = search(r'\d+:\d+(:\d+)?', text)
        duration = None
        if duration_search:
            pieces = duration_search.group(0).split(':')
            seconds = int(pieces[-1])
            minutes = int(pieces[-2])
            hours = int(pieces[-3]) if len(pieces) > 2 else 0

            duration = timedelta(seconds=seconds, minutes=minutes, hours=hours)

        bitrate_search = search(r'(\d+) kbps', text)
        bitrate = int(bitrate_search.group(1)) if bitrate_search else None

        return (bitrate, duration, file_size)
 

    def _parse_result_line(self, line):
        bitrate, duration, file_size = self._parse_info_node(line.find('div', 'left'))
        file_name = line.find('b').text
        file_url = line.find('a', text='Download')['href']

        return Mp3SkullResult(file_name, file_url, duration, file_size, bitrate)


    def results(self):
        soup = BeautifulSoup(self._get_html())
        self._strip_html_comment_nodes(soup)
        result_lines = soup.find_all('div', id='song_html')

        for line in result_lines:
            yield self._parse_result_line(line)


    def __iter__(self):
        for result in self.results():
            yield result



class Mp3SkullResult(object):
    blacklisted_patterns = ['mp3']

    def __init__(self, file_name, file_url, duration=None, file_size=None, bitrate=None):
        self.file_name = file_name
        self.file_size = file_size
        self.bitrate = bitrate
        self.file_url = file_url
        self.duration = duration


    def _strip_blacklisted_patterns(self, s):
        for pattern in self.blacklisted_patterns:
            s = s.strip(pattern)
        return s


    def guess_artist(self):
        guess_match = match(r'(.*?)-.*', self.file_name)
        return self._strip_blacklisted_patterns(guess_match.group(1)).strip() if guess_match else None


    def guess_track(self):
        guess_match = match(r'.*-(.*)', self.file_name)
        return self._strip_blacklisted_patterns(guess_match.group(1)).strip() if guess_match else None


    def __str__(self):
        return '%(file_name)s | %(file_size)s | %(bitrate)s | %(duration)s' % self.__dict__



if __name__ == '__main__':
    for result in Mp3Skull('Daft Punk Harder Better'):
        print(result.guess_artist(), '-', result.guess_track())