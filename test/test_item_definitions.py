from textwrap import dedent

from .base import OCRTestCases


class ItemDefinitionTestCases(OCRTestCases):

    def test_reading_large_item_descriptions_with_no_errors(self):
        shako_readings = self.ocr.read(self._img_to_np("test/test_data/item_definition/shako.png"), width_ths=3.5)

        self.assert_readings_match_expected(
            shako_readings,
            dedent("""\
                Harlequin Crest
                Shako
                Defense: 105
                Durability: 11 of 12
                Required Strength: 50
                Required Level: 62
                +2 to All Skills
                +2 to All Attributes
                +120 to Life (Based On Character Level)
                +126 to Mana (Based Oon Character Level)
                Damage Reduced by 10%
                74% Better Chance of Getting Magic Items
                Socketed (1)
            """)
        )

        tal_rasha_lidless_eye_readings = self.ocr.read(self._img_to_np("test/test_data/item_definition/tal_rashas_lidless_eye.png"), width_ths=3.5)
        self.assert_readings_match_expected(
            tal_rasha_lidless_eye_readings,
            dedent("""\
                Inventory
                Sell Value: 35000
                Tal Rasha's Lidless Eye
                Swirling Crystal
                One-Hand Damage: 18 to 42
                Staff Class - Normal Attack Speed
                Durability: 48 of 30
                (Sorceress Only)
                Required Level: 65
                20% Faster Cast Rate
                +1 to Cold Mastery (Sorceress Only)
                +1 to Lightning Mastery (Sorceress Only)
                +2 to Fire Mastery (Sorceress Only)
                +10 to Energy
                +57 to Life
                +77 to Mana
                -15% to Enemy Fire Resistance
                +1 to Sorceress Skill Levels
                Replenish Life +10
                65% Better Chance of Getting Magic items
                Tal Rasha's Wrappings
                Tal Rasha's Horadric Crest
                Tal Rasha's Guardianship
                Tal Rasha's Lidless Eye
                Tal Rasha's Adiudication
                Tal Rasha's Fine-Spun Cloth
            """)
        )

    def test_reading_item_definitions_with_low_scaling(self):
        # check definitions but this time with much lower scaling
        assert False