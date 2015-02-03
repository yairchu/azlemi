from modeltranslation.translator import translator, TranslationOptions
from vote.models import Vote

class VoteTranslationOptions(TranslationOptions):
    fields = ('vt_title', 'vt_description',)

translator.register(Vote, VoteTranslationOptions)
