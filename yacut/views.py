# yacut/views.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from . import db
from .models import URLMap
from .forms import LinkForm, FileUploadForm
from .utils import get_unique_short_id, upload_files_to_disk
from .config import Config

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = LinkForm()
    message = None
    error_message = None
    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom = form.custom_id.data.strip() if form.custom_id.data else None

        if custom:
            if custom.lower() == 'files':
                error_message = 'Предложенный вариант короткой ссылки уже существует.'
                return render_template('index.html', form=form, error_message=error_message)
            if URLMap.query.filter_by(short=custom).first() is not None:
                error_message = 'Предложенный вариант короткой ссылки уже существует.'
                return render_template('index.html', form=form, error_message=error_message)
            short = custom
        else:
            short = get_unique_short_id()

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        short_url = request.host_url + short
        message = f'Ваша короткая ссылка: <a href="{short_url}">{short_url}</a>'
        return render_template('index.html', form=form, message=message)

    return render_template('index.html', form=form)

@main.route('/files', methods=['GET', 'POST'])
def file_upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not files or all(not f.filename for f in files):
            flash('Не выбраны файлы', 'danger')
            return render_template('file_upload.html', form=form)

        upload_data = []
        for f in files:
            if f.filename:
                upload_data.append((f, f.filename))

        if not upload_data:
            flash('Файлы не прикреплены', 'danger')
            return render_template('file_upload.html', form=form)

        try:
            result = upload_files_to_disk(upload_data, Config.DISK_TOKEN)
        except Exception as e:
            current_app.logger.error(f'Ошибка загрузки на Яндекс.Диск: {e}')
            flash('Ошибка при загрузке файлов. Попробуйте позже.', 'danger')
            return render_template('file_upload.html', form=form)

        file_links = []
        for filename, download_url in result:
            short = get_unique_short_id()
            url_map = URLMap(original=download_url, short=short)
            db.session.add(url_map)
            file_links.append((filename, request.host_url + short))

        db.session.commit()
        flash('Файлы успешно загружены!', 'success')
        return render_template('file_upload.html', form=form, file_links=file_links)

    return render_template('file_upload.html', form=form)

@main.route('/<short>')
def redirect_short(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)
