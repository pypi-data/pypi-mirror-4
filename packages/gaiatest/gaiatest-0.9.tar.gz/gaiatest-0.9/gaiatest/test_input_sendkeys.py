from gaiatest import GaiaTestCase
import time


class TestSomething(GaiaTestCase):

    def test_input_sendkeys(self):

        self.apps.launch('Contacts')
        time.sleep(5)
        with open('contacts.txt', 'w') as f:
            f.write(self.marionette.page_source.encode('ascii', 'replace'))

        # click new message
        create_new_message = self.marionette.find_element('id', 'add-contact-button')
        self.marionette.tap(create_new_message)

        time.sleep(2)
        contact_field = self.marionette.find_element('id', 'org')

        print "element displayed: " + str(contact_field.is_displayed())
        print "element location: " + str(contact_field.location)
        print "element size: " + str(contact_field.size)

        # type phone number
        contact_field.send_keys("la la la la")
