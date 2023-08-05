import unittest
import json
import MiiCardConsumers

class WrapperClassesTests(unittest.TestCase):
    def setUp(self):
        self.jsonBody = '{"CardImageUrl":"https:\/\/my.miicard.com\/img\/test.png","EmailAddresses":[{"Verified":true,"Address":"test@example.com","DisplayName":"testEmail","IsPrimary":true},{"Verified":false,"Address":"test2@example.com","DisplayName":"test2Email","IsPrimary":false}],"FirstName":"Test","HasPublicProfile":true,"Identities":null,"IdentityAssured":true,"LastName":"User","LastVerified":"\/Date(1345812103)\/","MiddleName":"Middle","PhoneNumbers":[{"Verified":true,"CountryCode":"44","DisplayName":"Default","IsMobile":true,"IsPrimary":true,"NationalNumber":"7800123456"},{"Verified":false,"CountryCode":"44","DisplayName":"Default","IsMobile":false,"IsPrimary":false,"NationalNumber":"7800123457"}],"PostalAddresses":[{"House":"Addr1 House1","Line1":"Addr1 Line1","Line2":"Addr1 Line2","City":"Addr1 City","Region":"Addr1 Region","Code":"Addr1 Code","Country":"Addr1 Country","IsPrimary":true,"Verified":true},{"House":"Addr2 House1","Line1":"Addr2 Line1","Line2":"Addr2 Line2","City":"Addr2 City","Region":"Addr2 Region","Code":"Addr2 Code","Country":"Addr2 Country","IsPrimary":false,"Verified":false}],"PreviousFirstName":"PrevFirst","PreviousLastName":"PrevLast","PreviousMiddleName":"PrevMiddle","ProfileShortUrl":"http:\/\/miicard.me\/123456","ProfileUrl":"https:\/\/my.miicard.com\/card\/test","PublicProfile":{"CardImageUrl":"https:\/\/my.miicard.com\/img\/test.png","FirstName":"Test","HasPublicProfile":true,"IdentityAssured":true,"LastName":"User","LastVerified":"\/Date(1345812103)\/","MiddleName":"Middle","PreviousFirstName":"PrevFirst","PreviousLastName":"PrevLast","PreviousMiddleName":"PrevMiddle","ProfileShortUrl":"http:\/\/miicard.me\/123456","ProfileUrl":"https:\/\/my.miicard.com\/card\/test","PublicProfile":null,"Salutation":"Ms","Username":"testUser"},"Salutation":"Ms","Username":"testUser","WebProperties":[{"Verified":true,"DisplayName":"example.com","Identifier":"example.com","Type":0},{"Verified":false,"DisplayName":"2.example.com","Identifier":"http:\/\/www.2.example.com","Type":1}]}'
        self.jsonResponseBody = '{"ErrorCode":0,"Status":0,"ErrorMessage":"A test error message","Data":true}'

    def test_can_deserialise_user_profile(self):
        o = MiiCardConsumers.MiiUserProfile.FromDict(json.loads(self.jsonBody))

        self.assertBasics(o)

        # Email addresses
        email1 = o.email_addresses[0]
        self.assertTrue(email1.verified)
        self.assertEqual("test@example.com", email1.address)
        self.assertEqual("testEmail", email1.display_name)
        self.assertTrue(email1.is_primary)

        email2 = o.email_addresses[1]
        self.assertFalse(email2.verified)
        self.assertEqual("test2@example.com", email2.address)
        self.assertEqual("test2Email", email2.display_name)
        self.assertFalse(email2.is_primary)

        # Phone numbers
        phone1 = o.phone_numbers[0]
        self.assertTrue(phone1.verified)
        self.assertEqual("44", phone1.country_code)
        self.assertEqual("Default", phone1.display_name)
        self.assertTrue(phone1.is_mobile)
        self.assertTrue(phone1.is_primary)
        self.assertEqual("7800123456", phone1.national_number)

        phone2 = o.phone_numbers[1]
        self.assertFalse(phone2.verified)
        self.assertEqual("44", phone2.country_code)
        self.assertEqual("Default", phone2.display_name)
        self.assertFalse(phone2.is_mobile)
        self.assertFalse(phone2.is_primary)
        self.assertEqual("7800123457", phone2.national_number)

        # Web properties
        prop1 = o.web_properties[0]
        self.assertTrue(prop1.verified)
        self.assertEqual("example.com", prop1.display_name)
        self.assertEqual("example.com", prop1.identifier)
        self.assertEqual(MiiCardConsumers.WebPropertyType.DOMAIN, prop1.type)

        prop2 = o.web_properties[1]
        self.assertFalse(prop2.verified)
        self.assertEqual("2.example.com", prop2.display_name)
        self.assertEqual("http://www.2.example.com", prop2.identifier)
        self.assertEqual(MiiCardConsumers.WebPropertyType.WEBSITE, prop2.type) 

        # Postal addresses
        addr1 = o.postal_addresses[0]
        self.assertEqual("Addr1 House1", addr1.house)
        self.assertEqual("Addr1 Line1", addr1.line1)
        self.assertEqual("Addr1 Line2", addr1.line2)
        self.assertEqual("Addr1 City", addr1.city)
        self.assertEqual("Addr1 Region", addr1.region)
        self.assertEqual("Addr1 Code", addr1.code)
        self.assertEqual("Addr1 Country", addr1.country)
        self.assertTrue(addr1.is_primary)
        self.assertTrue(addr1.verified)

        addr2 = o.postal_addresses[1]
        self.assertEqual("Addr2 House1", addr2.house)
        self.assertEqual("Addr2 Line1", addr2.line1)
        self.assertEqual("Addr2 Line2", addr2.line2)
        self.assertEqual("Addr2 City", addr2.city)
        self.assertEqual("Addr2 Region", addr2.region)
        self.assertEqual("Addr2 Code", addr2.code)
        self.assertEqual("Addr2 Country", addr2.country)
        self.assertFalse(addr2.is_primary)
        self.assertFalse(addr2.verified)

        self.assertTrue(o.has_public_profile)
        
        pp = o.public_profile
        self.assertBasics(pp)
        self.assertEqual("testUser", pp.username)
    
    def assertBasics(self, obj):
        self.assertIsNotNone(obj)
        
        self.assertEqual("https://my.miicard.com/img/test.png", obj.card_image_url)
        self.assertEqual("Test", obj.first_name)
        self.assertEqual("Middle", obj.middle_name)
        self.assertEqual("User", obj.last_name)
        
        self.assertEqual("PrevFirst", obj.previous_first_name)
        self.assertEqual("PrevMiddle", obj.previous_middle_name)
        self.assertEqual("PrevLast", obj.previous_last_name)

        self.assertTrue(obj.identity_assured)
        self.assertEqual("/Date(1345812103)/", obj.last_verified)

        self.assertTrue(obj.has_public_profile)
        self.assertEqual("http://miicard.me/123456", obj.profile_short_url)
        self.assertEqual("https://my.miicard.com/card/test", obj.profile_url)
        self.assertEqual("Ms", obj.salutation)
        self.assertEqual("testUser", obj.username)

    def test_can_deserialise_boolean(self):
        o = MiiCardConsumers.MiiApiResponse.FromDict(json.loads(self.jsonResponseBody), None)

        self.assertEqual(MiiCardConsumers.MiiApiCallStatus.SUCCESS, o.status)
        self.assertEqual(MiiCardConsumers.MiiApiErrorCode.SUCCESS, o.error_code)
        self.assertEqual("A test error message", o.error_message)
        self.assertTrue(o.data)

        pass

    def test_wrapper_throws_on_null_consumer_key(self):
        self.failUnlessRaises(ValueError, MiiCardConsumers.MiiCardOAuthClaimsService, None, "ConsumerSecret", "AccessToken", "AccessTokenSecret")
        self.failUnlessRaises(ValueError, MiiCardConsumers.MiiCardOAuthClaimsService, "ConsumerKey", None, "AccessToken", "AccessTokenSecret")
        self.failUnlessRaises(ValueError, MiiCardConsumers.MiiCardOAuthClaimsService, "ConsumerKey", "ConsumerSecret", None, "AccessTokenSecret")
        self.failUnlessRaises(ValueError, MiiCardConsumers.MiiCardOAuthClaimsService, "ConsumerKey", "ConsumerSecret", "AccessToken", None)

# Run if command-line
if __name__ == '__main__':
    unittest.main()