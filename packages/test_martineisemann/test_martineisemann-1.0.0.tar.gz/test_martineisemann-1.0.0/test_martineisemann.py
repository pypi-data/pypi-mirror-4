"""Dies ist ein simples Testmodul 2readsplitfile.py."
Es macht nichts sinnvolles."""
def readsplitfile(file):
    """Dieser Kommentar beschreibt die Funktion readsplitfile."""
    print('Reading file.')
    try:
        daten = open(file)
	
        for zeile in daten:
            try:
                (rolle, aussage) = zeile.split(':')
                print(rolle, end='')
                print(' sagte: ', end='')
                print(aussage, end='')
            except:
                pass
    except:
        print('Datei nicht auffindbar.')
