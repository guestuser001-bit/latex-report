from pylatex import Section, Math


def add_theory(doc):
    with doc.create(Section('Theory')):
        doc.append('The ideal gas law is given by:')
        doc.append(Math(data=[r'PV = nRT']))
