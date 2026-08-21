from flask import Blueprint, render_template, redirect, flash, abort

from .constants import MSG_ALREADY_EXISTS
from .forms import LinkForm, FileUploadForm
from .models import URLMap
from .utils import upload_files_to_disk

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original = form.original_link.data
    custom = form.custom_id.data

    if custom:
        if custom.lower() == 'files' or URLMap.get_by_short(custom):
            flash(MSG_ALREADY_EXISTS)
            return render_template('index.html', form=form)
        short = custom
    else:
        short = URLMap.generate_unique_short()

    url_map = URLMap.create(original=original, short=short)
    short_url = url_map.get_short_url()
    flash(f'Ваша ссылка готова: <a href="{short_url}">{short_url}</a>')
    return render_template('index.html', form=form)


@main.route('/files', methods=['GET', 'POST'])
def file_upload():
    form = FileUploadForm()
    if not form.validate_on_submit():
        return render_template('file_upload.html', form=form)

    files = form.files.data
    try:
        download_urls = upload_files_to_disk(
            [(file, file.filename) for file in files]
        )
    except Exception as exc:
        flash(f'Ошибка при загрузке файлов: {exc}')
        return render_template('file_upload.html', form=form)

    file_links = []
    for filename, download_url in download_urls:
        short = URLMap.generate_unique_short()
        url_map = URLMap.create(original=download_url, short=short)
        file_links.append((filename, url_map.get_short_url()))

    return render_template(
        'file_upload.html', form=form, file_links=file_links)


@main.route('/<short>', endpoint='redirect_short')
def redirect_short(short):
    url_map = URLMap.get_by_short(short)
    if not url_map:
        abort(404)
    return redirect(url_map.original)