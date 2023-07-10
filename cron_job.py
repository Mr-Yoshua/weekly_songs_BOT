
# job que despues de un mes cambia las prioridades de las canciones
def change_priority_job(db_manager):
    low_priority_songs = db_manager.get_song_by_priority("low")
    for song in low_priority_songs:
        song["priority"] = "high"
        db_manager.update_song(song)
    print("Se han cambiado las prioridades de las canciones")
