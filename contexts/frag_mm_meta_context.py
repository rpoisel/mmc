class CFragMMMetaContext(object):
    cmd_frag_mm_meta = 'build/frag_mm_meta'

    @staticmethod
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    def __init__(self):
        # load DLL file
        pass

    def run_frag_mm_meta(self, pArgs):
        # TODO change to library (shared object) call
        lProcess = subprocess.Popen([CCollateContext.cmd_frag_mm_meta] +
                pArgs, stdout=subprocess.PIPE)
        return (lProcess.wait(), lProcess.stdout.read())
