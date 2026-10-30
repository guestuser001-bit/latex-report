from pylatex import Section


def add_introduction(doc):
    with doc.create(Section('Introduction')):
        doc.append('This report investigates the performance of a vacuum system.')
