data="""2011-03-16 13:35:28
  File: "STATUS.ok"
  Size: 30              Blocks: 128        IO Block: 131072 regular file
Device: eh/14d  Inode: 151003844   Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2011-03-16 13:30:27.000000000
Modify: 2011-03-16 13:30:27.000000000
Change: 2011-03-16 13:30:27.000000000

  File: "eg01-flat.vmdk"
  Size: 8589934592      Blocks: 16611328   IO Block: 131072 regular file
Device: eh/14d  Inode: 142615236   Links: 1
Access: (0600/-rw-------)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2011-03-16 13:22:27.000000000
Modify: 2011-03-16 13:22:27.000000000
Change: 2011-03-16 13:30:19.000000000

  File: "eg01.vmdk"
  Size: 521             Blocks: 128        IO Block: 131072 regular file
Device: eh/14d  Inode: 146809540   Links: 1
Access: (0600/-rw-------)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2011-03-16 13:30:19.000000000
Modify: 2011-03-16 13:30:20.000000000
Change: 2011-03-16 13:30:20.000000000

  File: "eg01.vmx"
  Size: 2336            Blocks: 128        IO Block: 131072 regular file
Device: eh/14d  Inode: 138420932   Links: 1
Access: (0755/-rwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2011-03-16 13:22:21.000000000
Modify: 2011-03-16 13:22:21.000000000
Change: 2011-03-16 13:22:21.000000000
"""

import re

class self:
    
    stat_filename_re=re.compile('^\s*File:\s*"(?P<filename>.+)"\s*$')
    stat_change_re=re.compile('^\s*Change:\s*(?P<change>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}).*\s*$')
    
date=filename=modify=change=None
for line in data.split('\n'):
    if not date:
        date=line
        print date
        continue
    
    # print line
    
    match=self.stat_filename_re.match(line)
    if match:
        filename=match.group('filename')

    match=self.stat_change_re.match(line)
    if match:
        change=match.group('change')
        print filename, change
    
    