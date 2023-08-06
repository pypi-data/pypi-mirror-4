from ftw.upgrade import UpgradeStep


class RemoveIcon(UpgradeStep):

    def __call__(self):

        self.setup_install_profile(
            'profile-simplelayout.types.flowplayerblock.upgrades:1002')
