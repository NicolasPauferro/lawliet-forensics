SIGNATURES = {
    'jpeg': {
        'headers': [b'\xff\xd8\xff'],
        'footers': [b'\xff\xd9'],
        'extension': 'jpg',
        'strategy': 'default carving'
    },
    'png': {
        'headers': [b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'],
        'footers': [b'\x49\x45\x4e\x44\xae\x42\x60\x82'],
        'extension': 'png',
        'strategy': 'default carving'
    },
    'pdf': {
        'headers': [b'\x25\x50\x44\x46'],
        'footers': [b'\x25\x25\x45\x4f\x46'],
        'extension': 'pdf',
        'strategy': 'default carving'
    },
    'gif': {
        'headers': [b'\x47\x49\x46\x38\x39\x61'], 
        'footers': [b'\x00\x3b'],
        'extension': 'gif',
        'strategy': 'default carving'
    },
    'zip': {
        'headers': [b'\x50\x4b\x03\x04'],
        'footers': [b'\x50\x4b\x05\x06'],
        'extension': 'zip',
        'strategy': 'carve_zip' # own strategy
    },
    'docx': {
        'headers': [b'\x50\x4b\x03\x04'],
        'footers': [b'\x50\x4b\x05\x06'],
        'extension': 'docx',
        'strategy': 'carve_zip' # own strategy
    },
    'xlsx': {
        'headers': [b'\x50\x4b\x03\x04'],
        'footers': [b'\x50\x4b\x05\x06'],
        'extension': 'xlsx',
        'strategy': 'carve_zip' # own strategy
    },
    'mp4': {
        'headers': [ b'ftyp'], 
        'footers': [b'\x00\x00\x00\x00\x6d\x6f\x6f\x76'], #but that's not for every mp4 so we will not use
        'extension': 'mp4',
        'strategy': 'carve_mp4'
    }
}