from ..loader import BeneficiaryLoader

class CGRTEPlusLoader(BeneficiaryLoader):
    def load_beneficiaries_to_db(self, beneficiaries):
        super().load_beneficiaries_to_db()

        families = []
        # For each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
        for beneficiary in beneficiaries:
            # For each beneficiary row construct a family object
            family = new_family(beneficiary)
            load_family_to_db(family)
            families.append(family)
        return families