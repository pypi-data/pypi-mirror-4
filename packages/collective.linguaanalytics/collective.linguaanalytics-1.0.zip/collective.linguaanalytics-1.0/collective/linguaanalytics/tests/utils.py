class FakeSettings(object):
    def __init__(self):
        self.activated = True
        self.mapping = ['http://nohost/plone|UA-xxxxxx-x']


class FakeMember(object):
    def __init__(self):
        self.roles = ['Member']

    def has_role(self, role):
        return role in self.roles


class FakeAnalyticsTool(object):
    def __init__(self):
        self.tracking_excluded_roles = []


class FakeMembershipTool(object):
    def __init__(self):
        self.authenticated_member = FakeMember()

    def getAuthenticatedMember(self):
        return self.authenticated_member


class FakeContext(object):
    def __init__(self):
        self.portal_analytics = FakeAnalyticsTool()
        self.portal_membership = FakeMembershipTool()
