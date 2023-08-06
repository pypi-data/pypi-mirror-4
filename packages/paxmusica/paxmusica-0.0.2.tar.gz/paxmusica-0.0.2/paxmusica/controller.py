#!/usr/bin/env python
# coding: utf-8

import os
from flask import Flask, request, render_template, redirect, session, g, url_for

import model
from os.path import join
import sqlite3

import config


app = Flask('paxmusica')
app.secret_key = "testtesttesttest"
app.propagate_errors = True


@app.before_request
def connect_to_db():
    g.con = sqlite3.connect(model.db_location)
    g.cur = g.con.cursor()

@app.after_request
def close_db(response):
    g.con.commit()
    g.con.close()
    return response


@app.route('/update/')
def update_playlist():
    return render_template('update.html', basedirs=model.get_basedirs())

@app.route('/do_update/', methods=['POST'])
def do_update():
    if request.form.get('folder'):
        basedir = model.Basedir("", request.form.get('folder'))
        basedir.add()
        model.update_song_library()
    elif request.form.get('basedir'):
        basedir = model.get_basedir_by_id(request.form.get('basedir'))
        basedir.delete()
        model.update_song_library()
    else:
        model.update_song_library()
    return redirect(url_for('update_playlist'))


@app.route('/migrate/')
def migrate():
    model.migrate()
    return "Migrated!"

@app.route('/')
def index():
    artists = model.get_all_artists()
    return render_template("index.html", artists=artists)

@app.route('/<artist>/')
def albums(artist):
    return render_template("albums.html",
                                        albums=model.get_albums_by_artist(artist),
                                        artist=artist)

@app.route('/<artist>/<album>/')
def songs(artist, album):
    return render_template("songs.html",
                                        songs=model.get_songs_by_artist_and_album(artist, album),
                                        artist=artist,
                                        album=album)


@app.route("/playlist/")
def playlist():
    return render_template("/playlist.html",
                            first_entry=model.get_first_playlist_entry(),
                            remaining_entries=model.get_remaining_playlist_entries(),
                            )

@app.route("/add/", methods=['POST'])
def add():
    song = model.get_song_by_id(int(request.form.get("chosen")))
    song.insert_into_playlist()
    return redirect(request.referrer)

@app.route('/device-test/')
def test():
    return request.user_agent.platform
