# Zotero Sync

`Back up your data when using this script. I have not lost any, but I can't make any guarantees.`

A simple module for updating zotflies directories. You can use this to delete redundant files or upload newly added files from the filesystem. It works by looking at every reference you have on zotero.org (you don't need to have files uploaded to make this work) and then compares the paths of those attachements to the ones in you zotfile directory. If there are any on your zotfile directory that aren't in your zotfile cloud, you can choose to "trash" or "upload" them.

## Installation

```zsh
pip install zotero_sync
```

## Usage

Go and create a new api key at https://www.zotero.org/settings/keys. Take note of the api key and also take note of the line that says "Your userID for use in API calls is ***"

Create a `.zoterosync` file in your home directory:

``` json
# ~/.zoterosync

ZOTFILE_DIR='***'
USER_ID = '***'
API_KEY = '***'
```

For information on script usage.

```zsh
zotero_sync --help
```

