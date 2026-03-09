import os
import tqdm
from signatures import SIGNATURES
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from zipcarve import carve_zip
from mp4carve import carve_mp4
from txtcarve import carve_txt


OVERLAP = 1024 #this is necessary because we need to search for the signature in the previous 1024 bytes
LIMIT_SECURITY = 400*1024*1024 #limiting the search to 400MB because i don't wanna to have a disaster


def default_carve(isopath, outpath, buffer_size):
    for format in SIGNATURES:
        os.makedirs(os.path.join(outpath, format), exist_ok=True)

    with open(isopath, 'rb') as f:
        try:
            totalsize = os.path.getsize(isopath)
        except PermissionError:
            print("Error: You need to run as sudo to access the pendrive directly.")
            return
        except OSError as e:
            print(f"Error reading the device: {e}")
            return
        progress = tqdm.tqdm(total=totalsize, unit='B', unit_scale=True)
        flag = 0
        i = 0
        while flag==0: #yeah this is different but it works and i was used to C , not python :D
            actual_position = f.tell()
            data = f.read(buffer_size)
            if not data:
                print("Nothing more to read")
                flag=1
            for format_name, details in SIGNATURES.items(): 
                # here i am just initializing some useful variables
                position_header = -1
                search_pointer = 0
                while True:
                    if format_name == "mp4":
                        target_signatures = [b'ftyp'] #why does mp4 have a so fucking different signature?
                    else:
                        target_signatures = details['headers']
                    
                    # Finding the earliest occurrence of any possible header
                    position_header = -1
                    best_header = None
                    for sig in target_signatures:
                        pos = data.find(sig, search_pointer)
                        if pos != -1 and (position_header == -1 or pos < position_header):
                            position_header = pos
                            best_header = sig
                    
                    if position_header == -1:
                        print(f"No more {format_name} in buffer") #if no more headers are found, break and go to next format
                        break

                    if format_name == "mp4":
                        abs_start = actual_position + position_header - 4 #the headers of mp4 files are 4 bytes before ftyp
                    else:
                        abs_start = actual_position + position_header

                    #Here we will begin the extraction process for files
                    if format_name == "mp4":
                        if carve_mp4(i, outpath, abs_start, f):
                            i = i+1
                        search_pointer = position_header + 4
                        
                    elif format_name in ["zip", "docx", "xlsx"]:
                        if carve_zip(i, outpath, abs_start, f):
                            i = i+1
                        search_pointer = position_header + 4
                    #elif format_name == "txt":
                     #   txt_len = carve_txt(i, outpath, abs_start, f)
                      #  if txt_len > 0:
                       #     i = i+1
                        #    search_pointer = position_header + txt_len
                        #else:
                        #    search_pointer = position_header + 4
                    else:
                        # Support for multiple footers
                        position_footer = -1
                        best_footer_len = 0
                        for foot_sig in details['footers']:
                            pos = data.find(foot_sig, position_header + len(best_header))
                            if pos != -1 and (position_footer == -1 or pos < position_footer):
                                position_footer = pos
                                best_footer_len = len(foot_sig)
                        
                        if position_footer != -1: #if footer is found
                            restored_raw_file = data[position_header : position_footer + best_footer_len]
                            
                            name = f"restored_{i}.{details['extension']}"
                            with open(os.path.join(outpath, format_name, name), 'wb') as rf:
                                rf.write(restored_raw_file)
                            print(f"Success: {format_name}_{i} extracted with success!")
                            
                            i = i+1 #counting the number of extracted files
                            search_pointer = position_footer + best_footer_len #updating the search pointer for the next file
                        else:
                            #if footer is not found, fuck off and go to the next header
                            search_pointer = position_header + len(best_header)

            progress.update(len(data))