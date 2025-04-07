import flet as ft
import pygame
import os
import asyncio
import random
from mutagen.mp3 import MP3

class Song:
    def __init__(self, filename):
        self.filename = filename
        self.title = os.path.splitext(filename)[0]
        self.duration = self.get_duration()

    def get_duration(self):
        audio = MP3(os.path.join("Playlist#1", self.filename))
        return audio.info.length

async def main(page: ft.Page):
    #Configuracion de ventana
    page.window.width = 400
    page.window.height = 450
    page.title = "Mi reproductor MP3"
    page.bgcolor = ft.colors.PURPLE_300
    page.padding = 20

    titulo = ft.Text("WELCOME BACK", size=30, color=ft.colors.WHITE)
    pygame.mixer.init()
    
    # Se carga la carpeta de musica(playlsit XD)
    playlist = [Song(f) for f in os.listdir("Playlist#1") if f.endswith(".mp3")]
    current_song_index = 0
    shuffled = False
    original_playlist = playlist.copy()
    
    def load_song():
        pygame.mixer.music.load(os.path.join("Playlist#1", playlist[current_song_index].filename))
    
    #boton de play
    def play_next_song(e=None):
        nonlocal current_song_index
        current_song_index = (current_song_index + 1) % len(playlist)
        load_song()
        pygame.mixer.music.play()
        update_song_info()
        play_button.icon = ft.icons.PAUSE
        page.update()

    #boton de pausa
    def pause_song():
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            play_button.icon = ft.icons.PLAY_ARROW
        else:
            if pygame.mixer.music.get_pos() == -1:
                load_song()
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            play_button.icon = ft.icons.PAUSE
        page.update()
    
    #bontes para cambio de rola
    def change_song(delta):
        nonlocal current_song_index
        current_song_index = (current_song_index + delta) % len(playlist)
        load_song()
        pygame.mixer.music.play()
        update_song_info()
        play_button.icon = ft.icons.PAUSE
        page.update()

    #Randomizar playlist
    def shuffle_playlist():
        nonlocal playlist, shuffled, current_song_index
        if not shuffled:
            current_song = playlist[current_song_index]
            temp_playlist = playlist.copy()
            temp_playlist.pop(current_song_index)
            random.shuffle(temp_playlist)
            playlist = [current_song] + temp_playlist
            current_song_index = 0
            shuffled = True
            shuffle_button.icon = ft.icons.SHUFFLE_ON
        else:
            playlist = original_playlist.copy()
            current_song = playlist[current_song_index]
            current_song_index = original_playlist.index(current_song)
            shuffled = False
            shuffle_button.icon = ft.icons.SHUFFLE
        update_playlist_display()
        page.update()

    def format_time(secs):
        mins, secs = divmod(int(secs), 60)
        return f"{mins:02d}:{secs:02d}"
    
    #Mostrar cambios de cancion
    def update_song_info():
        song = playlist[current_song_index]
        song_info.value = f"Now Playing: {song.title}"
        duration_label.value = format_time(song.duration)
        progress_bar.value = 0.0
        current_time_text.value = "00:00"
        update_playlist_display()
        page.update()
    

    def update_playlist_display():
        playlist_items.controls.clear()
        for i, song in enumerate(playlist):
            playlist_items.controls.append(
                ft.ListTile(
                    title=ft.Text(song.title, 
                                color=ft.colors.WHITE if i == current_song_index else ft.colors.WHITE60,
                                weight=ft.FontWeight.BOLD if i == current_song_index else ft.FontWeight.NORMAL),
                    on_click=lambda e, idx=i: play_selected_song(idx),
                )
            )
        page.update()
    
    #Reproducir rola seleccionada
    def play_selected_song(index):
        nonlocal current_song_index
        current_song_index = index
        load_song()
        pygame.mixer.music.play()
        update_song_info()
        play_button.icon = ft.icons.PAUSE
        page.update()

    async def update_progress():
        while True:
            if pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos() / 1000
                progress_bar.value = current_time / playlist[current_song_index].duration
                current_time_text.value = format_time(current_time)
                
                if current_time >= playlist[current_song_index].duration - 0.5:
                    play_next_song()
                
                page.update()
            await asyncio.sleep(1)

    #Componentes de la pantalla
    song_info = ft.Text(size=15, color=ft.colors.WHITE)
    current_time_text = ft.Text(value="00:00", color=ft.colors.WHITE60)
    duration_label = ft.Text(value="00:00", color=ft.colors.WHITE60)
    progress_bar = ft.ProgressBar(value=0.0, width=300, color="white", bgcolor="#141B41")
    
    play_button = ft.IconButton(
        icon=ft.icons.PLAY_ARROW,
        on_click=lambda _: pause_song(),
        icon_color=ft.colors.WHITE
    )
    
    prev_button = ft.IconButton(
        icon=ft.icons.SKIP_PREVIOUS,
        on_click=lambda _: change_song(-1),
        icon_color=ft.colors.WHITE
    )
    
    next_button = ft.IconButton(
        icon=ft.icons.SKIP_NEXT,
        on_click=lambda _: change_song(1),
        icon_color=ft.colors.WHITE
    )
    
    shuffle_button = ft.IconButton(
        icon=ft.icons.SHUFFLE,
        on_click=lambda _: shuffle_playlist(),
        icon_color=ft.colors.WHITE
    )

    playlist_items = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        height=150,
        spacing=5
    )

    # Diseño 
    controls_row = ft.Row(
        [prev_button, play_button, next_button, shuffle_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    progress_row = ft.Row(
        [current_time_text, progress_bar, duration_label],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )
    
    main_column = ft.Column(
        [
            titulo, 
            song_info, 
            progress_row, 
            controls_row,
            ft.Divider(color=ft.colors.WHITE30),
            ft.Text("Playlist", size=16, color=ft.colors.WHITE),
            playlist_items
        ],
        spacing=10,
        expand=True
    )

    page.add(main_column)

    # Configuracion de un evento para cuando termine la canción
    pygame.mixer.music.set_endevent(pygame.USEREVENT)

    # Iniciar reproduccion
    if playlist:
        load_song()
        update_song_info()
        page.update()
        await update_progress()
    else:
        song_info.value = "No hay canciones en la playlist"
        page.update()

ft.app(target=main)