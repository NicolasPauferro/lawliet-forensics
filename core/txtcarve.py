import os
import re

'''
In the future this will be implemented but now it's taking so much time and i don't wanna solve it right now

'''

# Professional approach: track ranges already carved to avoid redundant analysis
PROCESSED_RANGES = []

def is_processed(pos):
    # Check if the current position is within an already extracted text range
    for start, end in PROCESSED_RANGES:
        if start <= pos < end:
            return True
    return False

# Pattern for NON-printable characters (anything not ASCII 32-126 or common whitespace)
NON_PRINTABLE_PAT = re.compile(rb'[^ -~\t\n\r]')

def carve_txt(i, outpath, header_pos, g):
    # If this position was already part of a carved text file, skip it immediately
    if is_processed(header_pos):
        return 0
        
    original_pos = g.tell()
    g.seek(header_pos)
    
    # Read a sizeable chunk for analysis (256 bytes for header, 128KB for extraction)
    chunk_size = 128 * 1024
    data = g.read(chunk_size)
    
    if len(data) < 256:
        g.seek(original_pos)
        return 0
        
    # Professional Heuristic: 100% printability in the first 256 bytes
    # This ensures we aren't just picking up a short string inside a binary file.
    head = data[:256]
    non_printables_in_head = NON_PRINTABLE_PAT.findall(head)
    
    if len(non_printables_in_head) == 0:
        # Detect the end of the text block (where the first non-printable char appears)
        match = NON_PRINTABLE_PAT.search(data)
        if match:
            txt_len = match.start()
        else:
            # If the whole chunk is printable, keep searching in next chunks
            txt_len = len(data)
            while len(data) == chunk_size:
                next_chunk = g.read(chunk_size)
                if not next_chunk:
                    break
                m = NON_PRINTABLE_PAT.search(next_chunk)
                if m:
                    txt_len += m.start()
                    break
                else:
                    txt_len += len(next_chunk)
                    data = next_chunk
        
        # Professional Threshold: Minimum 512 bytes to consider it a "file" worth saving
        if txt_len >= 512:
            g.seek(header_pos)
            txt_content = g.read(txt_len)
            
            name = f"restored_{i}.txt"
            target_file = os.path.join(outpath, "txt", name)
            with open(target_file, 'wb') as rf:
                rf.write(txt_content)
            
            print(f"Success: txt extracted with success! Size: {txt_len} bytes")
            
            # Record the processed range so the main loop can skip it
            PROCESSED_RANGES.append((header_pos, header_pos + txt_len))
            g.seek(original_pos)
            return txt_len # Return length to skip the entire block in the main loop

    g.seek(original_pos)
    return 0