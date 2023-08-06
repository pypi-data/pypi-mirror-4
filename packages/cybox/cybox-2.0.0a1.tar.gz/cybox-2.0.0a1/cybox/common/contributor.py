import cybox.bindings.cybox_common as common_binding
from cybox.common.daterange import DateRange


class Contributor(object):
    def __init__(self):
        pass

    @classmethod
    def object_from_dict(cls, contributor_attributes):
        """Create the Contributor object representation from an input dictionary"""
        contributor_type = common_binding.ContributorType()
        for contributor_key, contributor_value in contributor_attributes.items():
            if contributor_key == 'role': contributor_type.set_Role(contributor_value)
            if contributor_key == 'name': contributor_type.set_Name(contributor_value)
            if contributor_key == 'email': contributor_type.set_Email(contributor_value)
            if contributor_key == 'phone': contributor_type.set_Phone(contributor_value)
            if contributor_key == 'organization': contributor_type.set_Organization(contributor_value)
            if contributor_key == 'date':
                date_dict = contributor_value
                date = DateRange.object_from_dict(date_dict)
                if date.hasContent_(): contributor_type.set_Date(date)
            if contributor_key == 'contribution_location': contributor_type.set_Contribution_Location(contributor_value)
        return contributor_type

    @classmethod
    def dict_from_object(cls, element):
        """Parse and return a dictionary for a Contributor object"""
        pass
