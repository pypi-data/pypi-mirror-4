#
# Regular cron jobs for the baruwa package
#
# runs every 3 mins to update mailq stats
*/3 * * * * Debian-exim paster update-queue-stats /etc/baruwa/production.ini >/dev/null 2>&1
0 * * * * baruwa paster update-sa-rules /etc/baruwa/production.ini >/dev/null 2>&1
0 * * * * baruwa paster update-delta-index --index messages --realtime /etc/baruwa/production.ini >/dev/null 2>&1
0 0 * * * baruwa paster send-quarantine-reports /etc/baruwa/production.ini >/dev/null 2>&1
0 1 * * * baruwa paster prunedb /etc/baruwa/production.ini >/dev/null 2>&1
9 1 * * * baruwa paster update-delta-index --index archive /etc/baruwa/production.ini
0 2 * * * baruwa paster prunequarantine /etc/baruwa/production.ini >/dev/null 2>&1
0 6 1 * * baruwa paster send-pdf-reports /etc/baruwa/production.ini >/dev/null 2>&1
