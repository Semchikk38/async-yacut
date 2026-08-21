from http import HTTPStatus

from flask import Blueprint, render_template, redirect, flash, abort

from .constants import ALREADY_EXISTS, REDIRECT_ENDPOINT
from .forms import LinkForm, FileUploadForm
from .models import URLMap
from .utils import upload_files_to_disk
from .errors import ShortAlreadyExists

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original = form.original_link.data
    short = form.custom_id.data or None   # пустая строка → None

    try:
        url_map = URLMap.create(original=original, short=short)
    except ShortAlreadyExists:
        flash(ALREADY_EXISTS)
        return render_template('index.html', form=form)
    except ValueError as exc:
        flash(str(exc))
        return render_template('index.html', form=form)

    return render_template('index.html', form=form,
                           short_url=url_map.get_short_url())


@main.route('/files', methods=['GET', 'POST'])
def file_upload():
    form = FileUploadForm()
    if not form.validate_on_submit():
        return render_template('file_upload.html', form=form)

    files = form.files.data
    try:
        public_urls = upload_files_to_disk(
            [(file, file.filename) for file in files]
        )
    except Exception as exc:
        flash(f'Ошибка при загрузке файлов: {exc}')
        return render_template('file_upload.html', form=form)

    try:
        file_links = [
            (file.filename, URLMap.create(original=public_url,
                                          short=None,
                                          commit=(idx == len(files) - 1)
                                          ).get_short_url())
            for idx, (file, public_url) in enumerate(zip(files, public_urls))
        ]
    except ValueError as exc:
        flash(str(exc))
        return render_template('file_upload.html', form=form)

    return render_template('file_upload.html', form=form,
                           file_links=file_links)


@main.route('/<short>', endpoint=REDIRECT_ENDPOINT)
def redirect_short(short):
    url_map = URLMap.get(short)
    if not url_map:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)
