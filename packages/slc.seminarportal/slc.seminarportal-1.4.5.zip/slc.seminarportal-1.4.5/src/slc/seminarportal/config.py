# -*- coding: utf-8 -*-

"""Common configuration constants
"""

PROJECTNAME = 'slc.seminarportal'

PACKAGE_DEPENDENCIES = []
PRODUCT_DEPENDENCIES = ['Relations', 'ATReferenceBrowserWidget']
DEPENDENCIES = PRODUCT_DEPENDENCIES + PACKAGE_DEPENDENCIES

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'SPSpeechVenueFolder': 'slc.seminarportal: Add SPSpeechVenueFolder',
    'SPSpeakersFolder': 'slc.seminarportal: Add SPSpeakersFolder',
    'SPSpeech': 'slc.seminarportal: Add Speech',
    'SPSpeechVenue': 'slc.seminarportal: Add Speech Venue',
    'SPSpeaker': 'slc.seminarportal: Add Speaker',
    'SPSeminar': 'slc.seminarportal: Add Seminar',
}

ALLOWABLE_TEXT_TYPES = (
    'text/plain',
    'text/structured',
    'text/html',
    'application/msword',
    'text/x-rst'
)

ADDITIONAL_CATALOG_INDEXES = [('getSortableName', 'FieldIndex')]

product_globals = globals()

# Test data
names = (
('Bauer', 'Walter'),
('Blümich', 'Bernhard'),
('Breitmeier', 'Eberhard'),
('Dietrich', 'Wolfgang'),
('Eckert', 'Hellmut,'),
('de Graaf', 'A.A.'),
('Günther', 'Harald'),
('Haupt', 'Erhard T.K'),
('Hütterman', 'J.'),
('Loidl', 'Alois'),
('Oschkinat', 'Hartmut'),
('Steinhoff', 'Heinz-Jürgen'),
('Стоичков', 'Христо'),
('Ulrich', 'Anne S.'),
('Kotłowski', 'Tadeusz'),
)


titles = [
"Maecenas metus dui, porta sed.",
"Morbi eget mi. Ut hendrerit.",
"Phasellus porta, mauris ut mollis.",
"Donec tempus, urna porta mollis.",
"Duis dui nibh, blandit ut;.",
"Nulla facilisi. Nam nibh. Integer.",
"Mauris sodales. Donec ultrices. Cras.",
"Pellentesque lacus mi; malesuada a.", ]

short_desc = """
Vivamus ac dolor. Sed eros est, interdum eu, scelerisque non, tempus et; metus.
"""

desc = """
Vivamus ac dolor. Sed eros est, interdum eu, scelerisque non, tempus et; metus. Morbi venenatis eros a enim. Cras consequat! Curabitur feugiat, felis eget iaculis bibendum, neque libero cursus dolor; eu vulputate tellus neque eu nisi. Mauris justo. In facilisis enim vel odio? Etiam ante leo, consequat eu, rutrum non, cursus ac, augue. Nullam nec odio in erat pretium vehicula. Vestibulum neque. Mauris dignissim enim eu augue. Aenean massa.
"""

conclusions = """
Aenean id velit at orci aliquam convallis. Curabitur ullamcorper risus vitae erat! Ut justo. Donec in nibh ac sapien pharetra laoreet. Duis ut odio. Vestibulum tincidunt risus nec mauris. Sed sodales libero quis lectus porta tincidunt? Cras quis risus non augue dictum rhoncus! Phasellus eget neque. Nulla eget lacus. Mauris sagittis orci at lorem. Proin a risus vehicula urna hendrerit ullamcorper! Duis eget justo. Integer blandit risus quis ligula! Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In ac enim? Donec nec nulla. Vestibulum faucibus erat interdum ligula? Duis at tortor.

Curabitur egestas orci non mi? Phasellus id tortor sed diam molestie imperdiet. Proin ante metus, fringilla volutpat, vehicula in, adipiscing eget, nisi. Ut iaculis sodales neque? Proin metus libero, dictum fringilla, consequat in, dapibus sed, tortor. Pellentesque ante. Aenean felis. Donec venenatis. Duis nec mi ac enim euismod fermentum. Aliquam cursus, nunc nec lobortis placerat, nunc augue mollis orci, eget hendrerit sem augue et neque.
"""
