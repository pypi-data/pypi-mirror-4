from Products.CMFCore.utils import getToolByName


def create_speech(parent, title, desc, start_date, end_date):
    speech_id = parent.generateUniqueId('SPSpeech')
    if not hasattr(parent, 'speech_id'):
        parent.invokeFactory(
            'SPSpeech',
            speech_id,
            title=title,
            description=desc,
            startDate=start_date,
            endDate=end_date)
        s = getattr(parent, speech_id)
        s._renameAfterCreation(check_auto_id=True)
        wftool = getToolByName(parent, 'portal_workflow', None)
        if wftool is not None:
            wftool.doActionFor(s, 'publish')

        return s


def create_speaker(parent, surname, firstname):
    speaker_id = parent.generateUniqueId('SPSpeaker')
    if not hasattr(parent, 'speaker_id'):
        parent.invokeFactory(
            'SPSpeaker',
            speaker_id,)
        s = getattr(parent, speaker_id)
        s._renameAfterCreation(check_auto_id=True)
        s.setLastName(surname)
        s.setFirstName(firstname)
        wftool = getToolByName(parent, 'portal_workflow', None)
        if wftool is not None:
            wftool.doActionFor(s, 'publish')

        return s
