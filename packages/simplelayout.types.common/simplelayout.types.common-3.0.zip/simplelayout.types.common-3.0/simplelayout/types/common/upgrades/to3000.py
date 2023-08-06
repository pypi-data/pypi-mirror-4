from ftw.upgrade import UpgradeStep


class UseDefaultTypes(UpgradeStep):
    """simplelaylout.types.common goes back to plone default views for File 
    and Link.
    """
    def __call__(self):
        self.setup_install_profile(
            'profile-simplelayout.types.common.upgrades:3000')
