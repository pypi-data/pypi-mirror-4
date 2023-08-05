from flask import Flask
from .renderer import render_page
from .watcher import find_readme, read_file


def serve(directory='.', readme_file='README', port=None):
    """Starts a server to render the readme from the specified directory."""

    # Get the README filename
    filename = find_readme(directory, readme_file)
    if not filename:
        raise ValueError('No %s file found at %s' % ('README' if readme_file == 'README' else repr(readme_file), repr(directory)))

    # Flask application
    app = Flask('grip')
    app.config.from_pyfile('config.py')
    app.config.from_pyfile('local_config.py', silent=True)

    # Set overridden config values
    if port is not None:
        app.config['PORT'] = port

    # Views
    @app.route('/')
    def index():
        return render_page(read_file(filename), filename)

    # Run local server
    app.run(app.config['HOST'], app.config['PORT'], debug=app.config['DEBUG'], use_reloader=app.config.get('DEBUG_GRIP', False))
