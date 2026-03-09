import os
import sys
import tqdm
from signatures import SIGNATURES
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from defaultcarve import default_carve

OVERLAP = 1024 #this is necessary because we need to search for the signature in the previous 1024 bytes
LIMIT_SECURITY = 400*1024*1024 #limiting the search to 400MB because i don't wanna to have a disaster
console = Console()


ASCII_ART = """
 [bold red]██╗      █████╗ ██╗    ██╗██╗     ██╗███████╗████████╗[/bold red]
 [bold white]██║     ██╔══██╗██║    ██║██║     ██║██╔════╝╚══██╔══╝[/bold white]
 [bold red]██║     ███████║██║ █╗ ██║██║     ██║█████╗     ██║   [/bold red]
 [bold white]██║     ██╔══██║██║███╗██║██║     ██║██╔══╝     ██║   [/bold white]
 [bold red]███████╗██║  ██║╚███╔███╔╝███████╗██║███████╗   ██║   [/bold red]
 [bold white]╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═╝╚══════╝   ╚═╝   [/bold white]
           [italic cyan]Digital Forensics File Carver[/italic cyan]
           [italic blue]By Nicolas Pauferro[/italic blue]
           [italic purple]Supported files: jpg, png, pdf, gif, zip, mp4 and docx[/italic purple]
           [italic white]txt, mp3, rar cooming soon...[/italic white]

"""

def print_welcome():
    console.print(Panel(ASCII_ART, subtitle="Version - 2.0", border_style="blue"))


def main():
    print_welcome()
    if len(sys.argv) < 3:
        console.print("Usage: python3 lawliet.py \"isopath\" \"outpath\" -b \"buffer_size (in MB)\"")
        console.print("Buffer size parameter is optional")
        console.print("Default buffer size is 8MB")
        sys.exit()
    
    if len(sys.argv) == 5 and sys.argv[3] == "-b": #Yeah i know it's not the best way but it works
        buffer_size = int(sys.argv[4])*1024*1024
    else:
        buffer_size = 8*1024*1024
    default_carve(sys.argv[1], sys.argv[2], buffer_size)
    console.print("Carving process finished")
    sys.exit()

if __name__ == "__main__":
    main()