# Zotero Sync

<p style="color:red">Back up your data when using this script. I have not lost any, but I can't make any guarantees.</p>

A simple module for updating zotflies directories.

You can use this to delete redundant files or upload newly added files from the filesystem.

## Installation

```zsh
pip install zotero_sync
```

## Usage

Create a `.zoterosync` file:

``` json
//~/.zoterosync
ZOTFILE_DIR='***'
USER_ID = '***'
API_KEY = '***'
```

For information on script usage.

```zsh
zotero_sync --help
```

