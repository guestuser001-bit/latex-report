from pylatex import Section


def add_conclusion(doc):
    with doc.create(Section('Conclusion')):
        doc.append('Summarize the main findings here.')
