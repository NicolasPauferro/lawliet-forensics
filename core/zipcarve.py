import os
import sys
from signatures import SIGNATURES
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress


PROCESSED_OFFSETS = set()

def carve_zip(i, outpath, header_pos, g): #this was the hardest function to write, so everything is commented
    if header_pos in PROCESSED_OFFSETS: # Check if this header position has already been handled
        return False
    PROCESSED_OFFSETS.add(header_pos)
    original_pos = g.tell() #just saving the position that we had initially
    g.seek(header_pos) #move to the header position we have saved to header_pos variable
    max_search = 100 * 1024 * 1024 #limiting the search to 100MB because i don't wanna to have a disaster
    data_to_search = g.read(max_search)
    
    # Getting the footer signature from signatures.py
    zip_footer = SIGNATURES['zip']['footers'][0]
    eocd_pos = data_to_search.rfind(zip_footer) # Finding the End Of central directory (it is some ZIP shit)
    
    total_zip_size = -1
    if eocd_pos != -1:
        comment_len_offset = eocd_pos + 20 #the comment length is stored in the 20th byte of the End Of central directory
        if comment_len_offset + 2 <= len(data_to_search): #Checking if the comment is valid
            comment_len = int.from_bytes(data_to_search[comment_len_offset:comment_len_offset+2], 'little')
            total_zip_size = eocd_pos + 22 + comment_len
    
    # Robustness fallback: if EOCD is not found or invalid, try to find the last occurrence of PK12 (Central Directory)
    if total_zip_size == -1:
        cd_sig = b'\x50\x4b\x01\x02'
        last_cd = data_to_search.rfind(cd_sig)
        if last_cd != -1:
            # We found the last central directory record, we can assume the file ends shortly after
            # This is a heuristic but useful when EOCD is missing or corrupted
            total_zip_size = last_cd + 46 # Minimum size of CD record + some safety
            # Search for the end of the filename/extra/comment in this last record if possible, 
            # but for carving a rough estimate is often enough to get a openable file
    
    if total_zip_size != -1:
        g.seek(header_pos) #if all this shit is valid we move the pointer to header_pos and read the file
        zip_data = g.read(total_zip_size) #reading the file
        
        # Identifying the specific format based on XML signatures inside the ZIP structure
        if b"sheet" in zip_data or b"spreadsheetml" in zip_data:   
            print(f"Success: xlsx extracted with success!") 
            name = f"restored_{i}.xlsx"
            with open(os.path.join(outpath, "xlsx", name), 'wb') as rf:
                rf.write(zip_data)
        elif b"wordprocessingml" in zip_data:
            print(f"Success: docx extracted with success!")
            name = f"restored_{i}.docx"
            with open(os.path.join(outpath, "docx", name), 'wb') as rf:
                rf.write(zip_data)
        else:
            print(f"Success: zip extracted with success!")
            name = f"restored_{i}.zip" #the name of the file
            with open(os.path.join(outpath, "zip", name), 'wb') as rf: #opening the file in write binary mode
                rf.write(zip_data)  #writing the file
        
        g.seek(original_pos) #return the pointer to the original position for not fucking up the program
        return True #return true if the file was restored successfully

    g.seek(original_pos) #return to the original position even if everything's gone wrong
    return False #return false if the file was not restored successfully.