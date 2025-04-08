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
    """Visualizza tutti i grafici generati per la playlist."""
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return "ID della playlist mancante", 400
    
    tracks = get_tracks_from_playlist(playlist_id)
    if not tracks:
        return "Nessun brano trovato", 404

    # Genera i grafici
    grafico_temporale = generare_grafico_temporale(tracks).to_html(full_html=False)
    grafico_durata = generare_grafico_durata(tracks).to_html(full_html=False)
    grafico_popolarita = generare_grafico_popolarita(tracks).to_html(full_html=False)
    grafico_generi = generare_grafico_generi(tracks).to_html(full_html=False)
    grafico_evoluzione_popolarita = generare_evoluzione_popolarita(tracks).to_html(full_html=False)

    return render_template('grafici.html', 
                           grafico_temporale=grafico_temporale,
                           grafico_durata=grafico_durata,
                           grafico_popolarita=grafico_popolarita,
                           grafico_generi=grafico_generi,
                           grafico_evoluzione_popolarita=grafico_evoluzione_popolarita)
