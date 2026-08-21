from flask import (
    Blueprint, render_template, request, flash, redirect, abort, current_app
)
from .models import URLMap
from .forms import LinkForm, FileUploadForm
from .utils import get_unique_short_id, is_valid_short_id, upload_files_to_disk
from .constants import SHORT_MAX_LENGTH, MSG_ALREADY_EXISTS
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
            if (custom.lower() == 'files'
                    or URLMap.get_by_short(custom)
                    or not is_valid_short_id(custom)
                    or len(custom) > SHORT_MAX_LENGTH):
                error_message = MSG_ALREADY_EXISTS
                return render_template(
                    'index.html', form=form, error_message=error_message
                )
            short = custom
        else:
            short = get_unique_short_id()

        URLMap.create(original=original, short=short)
        short_url = request.host_url + short
        message = (
            f'Ваша короткая ссылка: <a href="{short_url}">{short_url}</a>')
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

        upload_data = [(f, f.filename) for f in files if f.filename]
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
            URLMap.create(original=download_url, short=short)
            file_links.append((filename, request.host_url + short))

        flash('Файлы успешно загружены!', 'success')
        return render_template(
            'file_upload.html', form=form, file_links=file_links
        )

    return render_template('file_upload.html', form=form)


@main.route('/<short>')
def redirect_short(short):
    url_map = URLMap.get_by_short(short)
    if not url_map:
        abort(404)
    return redirect(url_map.original)