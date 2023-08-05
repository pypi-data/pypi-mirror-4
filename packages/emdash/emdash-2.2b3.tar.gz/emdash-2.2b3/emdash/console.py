import glob
import optparse
import os
import re
import sys
import time

# emdash imports
import emdash.config
import emdash.handlers


class DownloadConfig(emdash.config.Config):
    applicationname = "EMDashDownload"
    def add_options(self, parser):
        parser.add_argument("--recurse", type=int, help="Recursion level", default=-1)
        parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files (default is to skip)", default=False)
        parser.add_argument("--rename", action="store_true", help="Rename files to the BDO name (e.g. bdo.201202020000.dm3)", default=False)
        parser.add_argument("--nogzip", action="store_true", help="Do not decompress files", default=False)
        parser.add_argument('names', metavar='names', nargs='+', help='Record names')
        # # parser.add_argument("--sidecar", "-s", action="store_true", help="Include file with EMEN2 metadata in JSON format")
        # # parser.add_option("--rename", "-r", action="store_true", help="If a file already exists, save with format 'rename.originalfilename'", default=False)
        # # parser.add_option("--bdorename", "-b", action="store_true", help="Rename to 'bdo.YYYYMMDDXXXXX.extension'")
        # # parser.add_option("--gzip", action="store_true", dest="compress", help="Decompress gzip'd files. Requires gzip in path (default)", default=True)
        # # parser.add_option("--nogzip", action="store_false", dest="compress", help="Do not decompress gzip'd files.")


def download():
    # Parse arguments
    ns = emdash.config.setconfig(DownloadConfig)
    names = vars(ns).get('names', [])
    # Login
    emdash.config.login()

    for name in names:
        dbt = emdash.handlers.get_handler(emdash.config.get("handler"))
        dbt.download_find(
            recurse=emdash.config.get('recurse'), 
            rename=emdash.config.get('rename'), 
            overwrite=emdash.config.get('overwrite')
            )


def upload():
    return
    
    
# if __name__ == "__main__":
#     download()
