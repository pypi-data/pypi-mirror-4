from Products.kupu.python.spellcheck import SpellChecker

old_check = SpellChecker.check
def check(self, text):
	text = '\n'.join(['^%s' % l for l in text.splitlines()])
	return old_check(self, text)
SpellChecker.check = check