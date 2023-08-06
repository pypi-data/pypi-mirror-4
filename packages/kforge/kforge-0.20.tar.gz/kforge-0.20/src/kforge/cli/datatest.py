#import os
#import shutil
#import tempfile
#
#import kforge.cli.data
#
#class TestInstallData(object):
#    
#    def setup_class(self):
#        self.base_path = tempfile.mkdtemp()
#        self.installer = kforge.cli.data.InstallData(self.base_path)
#        try:
#            self.installer.execute()
#        except:
#            shutil.rmtree(self.base_path)
#            raise
#
#    def teardown_class(self):
#        shutil.rmtree(self.base_path)
#
#    def test_conf(self):
#        kforgeconf = os.path.join(self.base_path, 'kforge.conf.new')
#        assert os.path.exists(kforgeconf)
#
#    def test_templates(self):
#        dest = os.path.join(self.base_path, 'templates')
#        dest2 = os.path.join(self.base_path, 'templates', 'kui', 'master.html')
#        assert os.path.exists(dest)
#        assert os.path.exists(dest2)
#
#    def test_media(self):
#        dest = os.path.join(self.base_path, 'www', 'media', 'css')
#        assert os.path.exists(dest)
#
#    def test_htdocs(self):
#        dest = os.path.join(self.base_path, 'www', 'project', 'index.html')
#        print os.listdir(os.path.join(self.base_path, 'www'))
#        assert os.path.exists(dest)
#
#
#if __name__ == '__main__':
#    import optparse
#    usage  = \
#'''usage: %prog <base-directory>'
#'''
#    parser = OptionParser(usage)
#    options, args = parser.parse_args()
#    if len(args) != 1:
#        parser.print_help(0)
#        sys.exit(1)
#    installer = InstallData(args[0])
#    installer.execute()
