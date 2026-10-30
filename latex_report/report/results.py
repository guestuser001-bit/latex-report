from pylatex import Section, Figure, NoEscape


def add_results(doc, figure_path):
    with doc.create(Section("Results")):
        doc.append("Total sales are compared across twelve stores in the figure below.")
        with doc.create(Figure(position="htbp")) as fig:
            fig.add_image(str(figure_path), width=NoEscape(r"\textwidth"))
            fig.add_caption("Total sales by store.")
            fig.append(NoEscape(r"\label{fig:store-sales}"))
        doc.append(NoEscape(r"Figure~\ref{fig:store-sales} compares total sales by store."))
