from plone.app.layout.analytics.view import AnalyticsViewlet as Base

class AnalyticsViewlet(Base):

    def render(self):
        snippet = super(AnalyticsViewlet, self).render()
        return '<div id="plone-analytics">%s</div>' % snippet
