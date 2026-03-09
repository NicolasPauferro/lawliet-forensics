import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress


OVERLAP = 1024 #this is necessary because we need to search for the signature in the previous 1024 bytes
LIMIT_SECURITY = 400*1024*1024 #limiting the search to 400MB because i don't wanna to have a disaster


def carve_mp4(i, outpath, header, g):
    g.seek(header) #go to the header position
    size_mp4 = 0 #initialize some variables
    found_moov = False
    found_ftyp = False
    
    try:
        while size_mp4 < LIMIT_SECURITY: #limiting the size for security reasons (my pc not crashing pls)
            current_box_pos = header + size_mp4
            g.seek(current_box_pos)
            
            headers = g.read(8) #read the first 8 bytes of the file
            if len(headers) < 8: #if this headers length is less than 8 , is broken
                break
            
            box_size = int.from_bytes(headers[:4], byteorder='big') #the box size is stored in the first 4 bytes
            box_name = headers[4:] #the box name is stored in the next 4 bytes

            if box_size < 8: 
                break #if the box size is less than 8, is broken
            
            if box_name == b"ftyp": 
                found_ftyp = True #this thing is important for the majority of mp4 files
            if box_name == b"moov": 
                found_moov = True #this also
            
            if box_size == 1: 
                box_size = int.from_bytes(g.read(8), byteorder='big') # some mp4 files do this shit and store the size in the next 8 bytes
            
            if size_mp4 + box_size > LIMIT_SECURITY: # again, security reasons...
                break
                
            size_mp4 = size_mp4 + box_size #incrementing size_mp4 file size
            
            if found_ftyp and found_moov:
                g.seek(header + size_mp4)
                check = g.read(4)
                if not check or int.from_bytes(check, 'big') == 0: #checking if there something to read or just zeros, in any case, the file has ended so we break the loop
                    break

        if size_mp4 > 8 and found_ftyp: #if the file is valid...
            g.seek(header) #move the pointer to the initial position of the file
            name = f"restored_{i}.mp4" #name of the file
            target_path = os.path.join(outpath, "mp4", name) #patjh of the file
            
            with open(target_path, 'wb') as restored_file: #opening the file in write binary mode
                print(f"Success: mp4_{i} extracted with success!")
                remaining = size_mp4 #remaining size of the file (we are writing in chunks this time for not crashing the application)
                while remaining > 0:
                    chunk_to_read = min(1024 * 1024, remaining) #reading the file in chunks of 1MB or less if the file is smaller
                    chunk = g.read(chunk_to_read) #reading the file
                    if not chunk: break
                    restored_file.write(chunk) #writing the file
                    remaining -= len(chunk)
            
            
            return True
            
        return False
    except Exception as e:
        print(f"Error carving the mp4 file: {e}") #printing the error
        return False