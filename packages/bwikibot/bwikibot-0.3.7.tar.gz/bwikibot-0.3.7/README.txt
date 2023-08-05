===========
B Wiki Bot
===========
There was a wiki bot, so I decided to create also b wiki bot.

After installation run command bwikibot, and you should see something like this:

| write             - Read text from stdio and save to page with name passed in param
| cybwiki_stop_spam - Block spammers and delete their creations on cybwiki
| endpoint          - Change endpoing but don't change cookies (for wiki families)
| throttle          - Set or get delay between queries
| read              - Print page which's name passed in param to stdout
| autocomplete      - Print list of page names which starts from passed prefix
| check_uploads     - Check and mark new files for licensing issues,
|                       and send messages to uploaders.
| logout            - Delete session file
| login             - Login to site with domain passed in param
| translate         - Automate translation of wikitext from one language to another
|                       -f from_lang (for example 'en')
|                       -t to lang (for example 'uk')

That is list of subcommands which is supported by current version of robot.
