
import stomp.utils
from stomp.utils import HEADER_LINE_RE

def parse_headers_patch(lines, offset=0):
    headers = {}
    for header_line in lines[offset:]:
        header_match = HEADER_LINE_RE.match(header_line)
        if header_match:
            key = header_match.group('key')
            value = header_match.group('value')
            if key not in headers:
                headers[key] = value
    return headers

stomp.utils.parse_headers = parse_headers_patch
