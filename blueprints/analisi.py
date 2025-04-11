from flask import Blueprint, render_template, request
from services.grafici import get_tracks_from_playlist, generare_grafico_temporale, generare_grafico_durata, generare_grafico_popolarita, generare_grafico_generi, generare_evoluzione_popolarita

analisi_bp = Blueprint('analisi_bp', __name__)

@analisi_bp.route('/brani_playlist', methods=['GET'])
def brani_playlist():
    """Visualizza la lista dei brani della playlist."""
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return "ID della playlist mancante", 400

    tracks = get_tracks_from_playlist(playlist_id)
    if not tracks:
        return "Nessun brano trovato", 404

    return render_template('brani_playlist.html', tracks=tracks, playlist_id=playlist_id)


@analisi_bp.route('/grafici', methods=['GET'])
def grafici():
    """Visualizza il grafico richiesto per la playlist."""
    playlist_id = request.args.get('playlist_id')
    graph_type = request.args.get('graph_type')  # Ottieni il tipo di grafico dalla richiesta
    
    if not playlist_id:
        return "ID della playlist mancante", 400

    tracks = get_tracks_from_playlist(playlist_id)
    if not tracks:
        return "Nessun brano trovato", 404

    # Determina quale grafico generare in base al tipo selezionato
    if graph_type == "grafico_temporale":
        graph = generare_grafico_temporale(tracks).to_html(full_html=False)
    elif graph_type == "grafico_durata":
        graph = generare_grafico_durata(tracks).to_html(full_html=False)
    elif graph_type == "grafico_popolarita":
        graph = generare_grafico_popolarita(tracks).to_html(full_html=False)
    elif graph_type == "grafico_generi":
        graph = generare_grafico_generi(tracks).to_html(full_html=False)
    elif graph_type == "grafico_evoluzione_popolarita":
        graph = generare_evoluzione_popolarita(tracks).to_html(full_html=False)
    else:
        return "Tipo di grafico non valido", 400

    # Restituisci solo il grafico, non l'intera pagina
    return {'graph': graph}
