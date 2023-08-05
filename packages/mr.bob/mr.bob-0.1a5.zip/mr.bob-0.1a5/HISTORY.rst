Changelog
=========
    

0.1a5 (2012-12-12)
------------------

- #26: Variables were not correctly parsed from config files


0.1a4 (2012-12-11)
------------------

- Fix MANIFEST.in so that template examples are also included with distribution
  [Domen Kožar]

- Add -q/--quiet option to suppress output which isn't strictly necessary
  [Sasha Hart]

- Suppress the interactive-mode welcome banner if there are no questions to ask
  [Sasha Hart]

- Don't raise KeyError: 'questions_order' if [questions] is missing in an ini
  [Sasha Hart]


0.1a3 (2012-11-30)
------------------

- #13: Read user config from ~/.mrbob (as stated in docs and inline comments).
  [Andreas Kaiser]


0.1a2 (2012-11-29)
------------------

- #12: Fix unicode errors when using non-ASCII in questions or defaults
  [Domen Kožar]

- Ask questions in same order they were
  defined in template configuration file
  [Domen Kožar]


0.1a1 (2012-10-19)
------------------

- Initial release.
  [Domen Kožar, Tom Lazar]
