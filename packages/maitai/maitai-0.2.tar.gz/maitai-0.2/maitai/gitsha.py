import os.path


class GitSHAMiddleware(object):
    """
    This middleware adds an environ key for the HEAD git SHA1 on repos that it
    is told to watch.
    """
    def get_sha1(self, path):
        git_path = os.path.join(path, '.git')
        with open(os.path.join(git_path, 'HEAD')) as head:
            s = head.read()
            assert s.startswith('ref')
            ref_path = s[5:].strip()
            with open(os.path.join(git_path, ref_path)) as ref:
                s = ref.read()
        return s.strip()

    def __init__(self, app, *watch_paths):
        self.app = app
        self.shas = {}
        for path in watch_paths:
            repo = os.path.basename(path.rstrip('/'))
            try:
                sha = self.get_sha1(path)
            except (IOError, OSError, AssertionError) as e:
                sha = str(e)
            self.shas['git-sha1.%s' % repo] = sha

    def __call__(self, environ, start_response):
        environ.update(self.shas)
        return self.app(environ, start_response)
