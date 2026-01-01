import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from pyPlotShotMarker import generate_plots

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'output'
MAX_CONTENT_LENGTH = 100 * 1024  # 100 KB
MAX_FILE_SIZE = 100 * 1024  # 100 KB
ALLOWED_EXTENSIONS = {'.csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error from Flask's MAX_CONTENT_LENGTH"""
    flash(f'File too large. Maximum size is {MAX_FILE_SIZE // 1024} KB.')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Validate file upload
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file.')
        return redirect(url_for('index'))

    # Check file size by reading content
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        flash(f'File too large. Maximum size is {MAX_FILE_SIZE // 1024} KB.')
        return redirect(url_for('index'))

    if file_size == 0:
        flash('File is empty.')
        return redirect(url_for('index'))

    # Validate CSV content by checking first line
    try:
        first_line = file.stream.readline().decode('utf-8')
        file.seek(0)  # Reset to beginning

        # Check if it looks like a CSV (has commas)
        if ',' not in first_line:
            flash('Invalid CSV format. File must contain comma-separated values.')
            return redirect(url_for('index'))

    except UnicodeDecodeError:
        flash('Invalid file encoding. Please ensure the file is a text CSV.')
        return redirect(url_for('index'))

    # Get form parameters
    try:
        distance = int(request.form.get('distance', 600))
        x_offset = int(request.form.get('x_offset', 0))
        y_offset = int(request.form.get('y_offset', 0))
    except ValueError:
        flash('Invalid parameter values')
        return redirect(url_for('index'))

    # Validate distance
    if distance not in [300, 500, 600, 700, 800, 900]:
        flash('Invalid distance. Must be one of: 300, 500, 600, 700, 800, 900')
        return redirect(url_for('index'))

    # Generate unique prefix using timestamp and UUID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    prefix = f"{timestamp}_{unique_id}"

    # Save uploaded file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{prefix}_{filename}")
    file.save(upload_path)

    try:
        # Generate plots
        left_plot, middle_plot, right_plot = generate_plots(
            csv_path=upload_path,
            prefix=prefix,
            distance=distance,
            x=x_offset,
            y=y_offset
        )

        # Clean up uploaded CSV
        os.remove(upload_path)

        # Check if at least one plot was generated
        if not any([left_plot, middle_plot, right_plot]):
            flash('No valid shooting data found in the CSV file.')
            return redirect(url_for('index'))

        # Render results page (only pass non-None plots)
        return render_template(
            'results.html',
            left_plot=left_plot,
            middle_plot=middle_plot,
            right_plot=right_plot,
            distance=distance
        )

    except ValueError as e:
        # Clean up uploaded file on error
        if os.path.exists(upload_path):
            os.remove(upload_path)
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

    except Exception as e:
        # Clean up uploaded file on error
        if os.path.exists(upload_path):
            os.remove(upload_path)
        flash(f'An unexpected error occurred: {str(e)}')
        return redirect(url_for('index'))


@app.route('/output/<path:filename>')
def serve_plot(filename):
    """Serve plot images from the output directory"""
    return send_file(os.path.join('output', filename), mimetype='image/png')


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8099))
    app.run(host='0.0.0.0', port=port, debug=False)
