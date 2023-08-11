from django.test import TestCase
from django.urls import reverse

from shops.models import Offer
from shops.services.compare import (
    _adding_missing_properties,
    compare_list_check,
    splitting_into_groups_by_category,
    _get_a_complete_list_of_property_names,
    _generating_a_comparison_dictionary,
    _comparison_of_product_properties,
    comparison_lists_and_properties,
)


class CompareTestCase(TestCase):
    """Тестирование страницы сравнения"""

    fixtures = {
        "fixtures/010_auth_group.json",
        "fixtures/011_users.json",
        "fixtures/015_shops_banner.json",
        "fixtures/020_catalog_categories.json",
        "fixtures/025_products.json",
        "fixtures/026_tags.json",
        "fixtures/027_product_image.json",
        "fixtures/030_property.json",
        "fixtures/035_productproperty.json",
        "fixtures/040_shops.json",
        "fixtures/045_offers.json",
    }

    def test_compare_list_check_success(self):
        """Тест переполнения списка сравнения. / Удаления и добавления id."""
        with self.settings(MAX_COMP_LIST_LEN=3):
            session = self.client.session
            for number_i in [1, 2, 2, 4, 5, 6, 5]:
                compare_list_check(session, number_i)
            expected_result = ["1", "4"]
            result = session.get("comp_list")
            self.assertEqual(result, expected_result)

    def test_splitting_into_groups_by_category_success(self):
        """Тест разбивки списка сравнения на категории"""
        comp_list = [1, 3, 4, 5, 17]
        result1, result2 = splitting_into_groups_by_category(comp_list)
        expected_result1 = {"ноутбуки": [1, 3, 5, 4], "бытовая техника": [17]}
        expected_result2 = [("ноутбуки", 4), ("бытовая техника", 1)]

        self.assertEqual(result1, expected_result1)
        self.assertEqual(result2, expected_result2)

    def test_get_a_complete_list_of_property_names_success(self):
        """Проверка генерации списка всех встречающихся свойств продуктов"""
        comp_list = [1, 3, 4, 5, 17]
        result = _get_a_complete_list_of_property_names(comp_list)
        expected_result = [
            "Вес",
            "Гарантия от производителя",
            "Страна-производитель",
            "Цвет, заявленный производителем",
        ]
        self.assertEqual(result, expected_result)

    def test_generating_a_comparison_dictionary_success(self):
        """Проверка генерации списка словарей для сравнения"""
        comp_list = [1, 3]
        offer_pk = Offer.objects.filter(id=comp_list[0]).select_related("product")
        property_list = Offer.objects.filter(id=offer_pk[0].id).values_list(
            "product__property__name", "product__productproperty__value"
        )
        property_dict = {}
        for name_i, value_i in property_list:
            property_dict[name_i] = [value_i, False]
        result = _generating_a_comparison_dictionary(comp_list)
        expected_result = {
            "name": offer_pk[0].product.name,
            "price": offer_pk[0].price,
            "preview": offer_pk[0].product.preview,
            "id": offer_pk[0].id,
            "category": offer_pk[0].product.category.name,
            "property": property_dict,
        }
        self.assertEqual(result[0], expected_result)
        self.assertEqual(len(result), len(comp_list))

    def test_adding_missing_properties_success(self):
        """Дополнение не достающих свойств ели таковые отсутствуют"""
        test_list = [
            {"property": {"Вес": ["5кг", False]}},
            {"property": {"Высота": ["5кг", False]}},
            {"property": {"Ширина": ["5кг", False]}},
        ]
        test_list_property = ["Вес", "Высота", "Ширина"]
        expected_result = [
            {
                "property": {
                    "Вес": ["5кг", False],
                    "Высота": ["-", False],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Высота": ["5кг", False],
                    "Вес": ["-", False],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Ширина": ["5кг", False],
                    "Вес": ["-", False],
                    "Высота": ["-", False],
                }
            },
        ]
        result = _adding_missing_properties(test_list_property, test_list)
        self.assertEqual(result, expected_result)

    def test_comparison_of_product_properties_success(self):
        """Проверка поиска одинаковых свойств"""
        test_list = [
            {
                "property": {
                    "Вес": ["5кг", False],
                    "Высота": ["7 м", False],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Высота": ["7 м", False],
                    "Вес": ["-", False],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Ширина": ["5кг", False],
                    "Вес": ["-", False],
                    "Высота": ["7 м", False],
                }
            },
        ]
        test_list_property = ["Вес", "Высота", "Ширина"]
        result = _comparison_of_product_properties(test_list, test_list_property)
        expected_result = [
            {
                "property": {
                    "Вес": ["5кг", False],
                    "Высота": ["7 м", True],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Высота": ["7 м", True],
                    "Вес": ["-", False],
                    "Ширина": ["-", False],
                }
            },
            {
                "property": {
                    "Ширина": ["5кг", False],
                    "Вес": ["-", False],
                    "Высота": ["7 м", True],
                }
            },
        ]
        self.assertEqual(result, expected_result)

    def test_get_comparison_lists_and_properties_success(self):
        """Проверка генерации финального списка сравнения и списка всех свойств."""
        comp_list = [1, 3]
        result_1, result_2 = comparison_lists_and_properties(comp_list)
        expected_result_2 = _get_a_complete_list_of_property_names(comp_list)
        self.assertEqual(len(result_1), len(comp_list))
        self.assertEqual(len(result_2), len(expected_result_2))

    def test_compare_page_view_success(self):
        """Проверка отображения страницы при количестве меньше 2-х выбранных предложений"""
        response = self.client.get(reverse("comparison"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Не достаточно данных для сравнения.")
