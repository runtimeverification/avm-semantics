from unittest import TestCase

from kavm_pyk.teal_to_k import create_definition


class CreateDefinitionTest(TestCase):
    def test_module_name(self):
        # Given
        contract_json = {}

        # When
        definition = create_definition(contract_json)

        # Then
        self.assertEqual(len(definition.modules), 1)
        self.assertEqual(definition.modules[0].name, 'TEST_MODULE')
