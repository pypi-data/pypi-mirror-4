from django.test import TestCase

from django.core.urlresolvers import reverse
from contacts.models import Company, Person

class ContactsTest(TestCase):
	fixtures = ['contacts.json',]
	urls = 'contacts.testurls'
	
	def setUp(self):
		self.company_miys = Company.objects.get(pk=1)
		self.person_mb = Person.objects.get(pk=1)
		email = self.company_miys.email_address.create()
		email.email_address = 'info@monkeyinyoursoul.com'
		email.location = 'work'
		email.save()
	
	def testEmailAddressThoughCompany(self):
		email = self.company_miys.email_address.get()
		self.failUnlessEqual(email.email_address, 'info@monkeyinyoursoul.com')
	
	def testViewCompanyList(self):
		response = self.client.get(reverse('contacts_company_list'))
		self.failUnlessEqual(response.status_code, 200)
	
	def testViewCompanyDetail(self):
		response = self.client.get(self.company_miys.get_absolute_url())
		self.failUnlessEqual(response.status_code, 200)
	
	def testViewPersonList(self):
		response = self.client.get(reverse('contacts_person_list'))
		self.failUnlessEqual(response.status_code, 200)
	
	def testViewPersonDetail(self):
		response = self.client.get(self.person_mb.get_absolute_url())
		self.failUnlessEqual(response.status_code, 200)
