from ftw.upgrade import UpgradeStep


class UseNewCollectiveFlowplayer311(UpgradeStep):
    """
    """

    def __call__(self):

        self.setup_install_profile(
            'profile-collective.flowplayer:base')

        self.setup_install_profile(
            'profile-simplelayout.types.flowplayer.upgrades:1000')
