from abc import ABC, abstractmethod

class BeneficiaryLoader(ABC):

    @abstractmethod
    def load_beneficiaries_to_db(self, beneficiaries):
        pass
