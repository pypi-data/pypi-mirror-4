import unittest
import requests
from StringIO import StringIO
from dukaan import xmlutil, utility, Validator
from mock import patch, Mock, MagicMock
from xml.etree.ElementTree import ElementTree, XML, fromstring, Element
from requests import ConnectionError

class XmlUtilTestCases(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	# ======== Unit Tests ========
	def test_bad_tag_ordering_fails(self):
		xml_string = """<?xml version='1.0' encoding='utf-8'?>
		<Something>
			<zebra>
				<charlie>foo</charlie>
			</zebra>
			<alpha>bar</alpha>
		</Something>
		"""

		e = xmlutil.get_root_element(xmlutil.get_subtree_from_xml_string(xml_string))
		self.assertRaises(xmlutil.TagOrderingException, xmlutil.check_tags_alpha_ordered, e)

	def test_good_tag_ordering_succeeds(self):
		xml_string = """<?xml version='1.0' encoding='utf-8'?>
		<Something>
			<alpha>bar</alpha>
			<zebra>
				<bravo>foo</bravo>
				<charlie>foo</charlie>
			</zebra>
		</Something>
		"""

		try:
			e = xmlutil.get_root_element(xmlutil.get_subtree_from_xml_string(xml_string))
			xmlutil.check_tags_alpha_ordered(e)
		except xmlutil.TagOrderingException:
			self.fail("check_tags_alpha_ordered method unexpectedly failed")

class DukaanTestCases(unittest.TestCase):
	def setUp(self):
		self.config = {
			'command': None,
			'manifest_path': None,
			'env': 'test',
			'resource_provider_namespace': 'contoso',
			'subscription_id': utility.random_subscription(),
			'cloud_service_name': utility.random_cloud_service(),
			'resource_type': 'my_resource',
			'resource_name': 'my_resource',
			'promo_code': 'my_promo_code',
			'plan': 'free'
		}

	def tearDown(self):
		pass

	# ======== Unit Tests ========
	def test_parse_manifest_with_no_https(self):
		xml_string = """<?xml version='1.0' encoding='utf-8'?>
		<Something>
			<zebra>
				<charlie>foo</charlie>
			</zebra>
			<alpha>bar</alpha>
		</Something>
		"""
		my_mock = MagicMock()
		with patch('__builtin__.open', my_mock):
			manager = my_mock.return_value.__enter__.return_value
			manager.read.return_value = xml_string
			errors, warnings, manifest_config = xmlutil.parse_manifest("foo")

			assert len(errors) == 2

		# open_name = '%s.open' % __name__
		# with patch(open_name, create=True) as mock_open:
		# 	mock_open.return_value = MagicMock(spec=file)



		# with patch.object(xmlutil, 'parse_manifest') as mock_method:
		# 	bad_manifest = {
		# 		'test':
		# 		{
		# 			'base': "http://foo.com",
		# 			'sso': "http://foo.com/sso"
		# 		},
		# 		'prod':
		# 		{
		# 			'base': "http://prod.foo.com",
		# 			'sso': "http://prod.foo.com"
		# 		},
		# 		'output_keys':[]
		# 	}
		# 	mock_method.return_value = ([],[],bad_manifest)
		# 	validator = Validator(self.config)
		# 	validator.manifest()