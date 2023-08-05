from os import path as osp
from authbwc_ta.config.settings import Default

class Dev(Default):
    def init(self):
        Default.init(self)

        #######################################################################
        # USERS: DEFAULT ADMIN
        #######################################################################
        self.components.auth.admin.username = 'rsyring'
        self.components.auth.admin.password = 'pass'
        self.components.auth.admin.email = 'randy.syring@lev12.com'
        self.apply_dev_settings(self.components.auth.admin.email)

        self.db.url = 'sqlite:///%s' % osp.join(self.dirs.data, 'application.db')

        # db connection
        self.db.url = 'postgresql://postgres:postgres@rcsserver/test'
