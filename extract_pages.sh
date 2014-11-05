#!/bin/bash
#
# vim: tw=0

echo "USE freeon_wiki; SELECT page.page_title, text.old_text FROM text INNER JOIN revision ON revision.rev_text_id = text.old_id INNER JOIN page ON page.page_id = revision.rev_page WHERE (revision.rev_id = page.page_latest && page.page_namespace = 0)" | mysql -u wikiuser -p > pages.txt
