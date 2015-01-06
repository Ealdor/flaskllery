from flask import render_template, flash, redirect, url_for, send_file, abort, Response, jsonify
from flask.ext.user import login_required, current_user
from app.models import Album, Directory, Photo
from app.gallery.forms import NewAlbumForm, EditAlbumForm, AddDirectoryForm
from app import db
from PIL import Image
from . import blueprint
import StringIO

@blueprint.route('/')
@blueprint.route('/index')
@blueprint.route('/index/<int:page>')
@login_required
def index(page=1):
	'''
	Show gallery main page: album list
	'''
	albums = Album.query.paginate(page, 6, False)
	return render_template('index.html', albums=albums)

@blueprint.route('/album/new', methods=['GET', 'POST'])
@login_required
def new_album():
	'''
	New album
	'''
	form = NewAlbumForm()
	if form.validate_on_submit():
		album = Album(title=form.title.data, description=form.description.data, author=current_user)
		db.session.add(album)
		db.session.commit()
		flash('New album \'' + album.title + '\' added')
		return redirect(url_for('.index'))
	return render_template('new_album.html', form=form)

@blueprint.route('/album/view/<int:id>')
@login_required
def album(id):
	'''
	View album
	'''
	album = Album.query.get(id)
	return render_template('album.html', album=album)

@blueprint.route('/album/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_album(id):
	'''
	Edit album
	'''
	form = EditAlbumForm(prefix='form1')
	directory_form = AddDirectoryForm(prefix='form2')
	album = Album.query.get(id)
	if form.validate_on_submit() and form.submit.data:
		album.title = form.title.data
		album.description = form.description.data
		db.session.add(album)
		db.session.commit()
		flash('Album \'' + album.title + '\' edited')
		return redirect(url_for('.album', id=album.id))
	if directory_form.validate_on_submit() and directory_form.submit.data:
		directory = Directory(album=album, path=directory_form.path.data)
		db.session.add(directory)
		db.session.commit()
		flash('\'' + directory.path + '\' directory added to \'' + album.title + '\'')
		return redirect(url_for('.edit_album', id=album.id))

	form.title.data = album.title
	form.description.data = album.description
	return render_template('edit_album.html', album=album, form=form, directory_form = directory_form)

@blueprint.route('/album/delete/<int:id>')
@login_required
def delete_album(id):
	'''
	Delete album
	'''
	album = Album.query.get(id)
	db.session.delete(album)
	db.session.commit()
	flash('\'' + album.title + '\' album deleted')
	return redirect(url_for('.index'))

@blueprint.route('/album/refresh/<int:id>')
@login_required
def refresh_album(id):
	'''
	Refresh album: check all directories tracked by album for new photos & changes
	'''
	album = Album.query.get(id)
	album.refresh()
	flash('\'' + album.title + '\' album refreshed')
	return redirect(url_for('.album', id=album.id))

@blueprint.route('/directory/refresh/<int:id>')
@login_required
def refresh_directory(id):
	'''
	Refresh directory: check directory for new photos & changes
	'''
	directory = Directory.query.get(id)
	directory.refresh()
	flash('Directory \'' + directory.path + '\' refreshed')
	return redirect(url_for('.edit_album', id=directory.album_id))

@blueprint.route('/directory/delete/<int:id>')
@login_required
def delete_directory(id):
	'''
	Delete directory
	'''
	directory = Directory.query.get(id)
	album = directory.album
	db.session.delete(directory)
	db.session.commit()
	flash('\'' + directory.path + '\' directory deleted from \'' + album.title + '\'')
	return redirect(url_for('.edit_album', id=album.id))

@blueprint.route('/photo/raw/<int:id>')
def photo_file(id):
	'''
	Return raw photo file
	'''
	photo = Photo.query.get(id)
	return send_file(photo.path)

@blueprint.route('/photo/thumb/<int:id>/<int:width>x<int:height>')
@login_required
def photo(id, width, height):
	'''
	Return photo thumbnail of given dimension
	'''
	photo = Photo.query.get(id)
	return photo.thumb(width,height)

@blueprint.route('/json/photo/<int:id>')
@login_required
def json_photo(id):
	'''
	Returns photo info in json format
	'''
	photo = Photo.query.get(id)
	return jsonify(photo.json())
