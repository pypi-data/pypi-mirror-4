from cStringIO import StringIO
from giotto.programs import GiottoProgram
from giotto.views import GiottoView, renders
from giotto.utils import super_accept_to_mimetype
import os

class FileView(GiottoView):
    @renders('*/*')
    def html(self, result):
        _, ext = os.path.splitext(result.name)
        mimetype = super_accept_to_mimetype(ext)
        if not mimetype:
            import magic # done here to avoid import error in GAE
            mimetype = magic.from_buffer(result.read(1024), mime=True)
            result.seek(0)
        
        return {'body': result, 'mimetype': mimetype}

    @renders('text/x-cmd')
    def cmd(self, result):
        return {'body': result.read(), 'mimetype': ''}

def StaticServe(base_path):
    """
    Meta program for serving any file based on the path
    """
    def get_file(path):
        return open(base_path + path, 'r')

    class StaticServe(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return StaticServe()

def SingleStaticServe(file_path):
    """
    Meta program for serving a single file. Useful for favicon.ico
    """
    def get_file():
        return open(file_path, 'r')

    class SingleStaticServe(GiottoProgram):
        controllers = ('http-get', )
        model = [get_file, StringIO("Mock file content")]
        view = FileView

    return SingleStaticServe()