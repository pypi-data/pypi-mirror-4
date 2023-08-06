from zope.interface import implements
from zope import schema
from z3c.form.interfaces import NO_VALUE

from five import grok

from plone.dexterity.content import Container
from plone.supermodel import model
from plone.dexterity.schema import DexteritySchemaPolicy

from collective.contact.core import _
from collective.contact.core.browser.contactable import Contactable
from collective.contact.widget.interfaces import IContactContent


class IPosition(model.Schema, IContactContent):
    """Interface for Position content type"""

    position_type = schema.Choice(
        title=_("Type"),
        vocabulary="PositionTypes",
        )

    def get_organization():
        """Returns the organization to which the position is linked"""

    def get_full_title(self):
        """Returns the full title of the position
        It is constituted by the name of the position and
        the name of its organization in brackets
        """


class PositionContactableAdapter(Contactable):
    """Contactable adapter for Position content type"""

    grok.context(IPosition)

    @property
    def position(self):
        return self.context

    @property
    def organizations(self):
        organization = self.context.get_organization()
        return organization.get_organizations_chain()


class Position(Container):
    """Position content type"""

    implements(IPosition)
    use_parent_address = NO_VALUE
    parent_address = NO_VALUE

    def get_organization(self):
        """Returns the organization to which the position is linked"""
        return self.getParentNode()

    def get_full_title(self):
        """Returns the full title of the position
        It is constituted by the name of the position and
        the name of its organization in brackets
        """
        organization = self.get_organization().Title()
        return "%s (%s)" % (self.Title(), organization)


class PositionSchemaPolicy(grok.GlobalUtility,
                           DexteritySchemaPolicy):
    """Schema policy for Position content type"""

    grok.name("schema_policy_position")

    def bases(self, schemaName, tree):
        return (IPosition,)
