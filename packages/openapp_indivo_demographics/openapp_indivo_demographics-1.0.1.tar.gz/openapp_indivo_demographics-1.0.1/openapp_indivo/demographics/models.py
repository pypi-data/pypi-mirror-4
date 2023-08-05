
# I want to map the indivo messages back into models. This makes it
# easier to programme with. The indivo design starts with models and
# then converts to a messaging api.

import json
import logging
import xml.etree.ElementTree as ET

from django.db import models
from django.db.models.manager import Manager

from middleware import get_request
from utils import get_indivo_client, _sessionkey

logger = logging.getLogger(__name__)

class DemographicsManager(Manager):
    def get(self, *args, **kwargs):
        """
            This is a very limited version of the Manager.get(). It only retrieves
            a single record.
        """
        # only two options supported record_id= or carenet_id=
        record_id = kwargs.get('record_id')
        carenet_id = kwargs.get('carenet_id')
        assert record_id or carenet_id

        request = get_request()

        sessionkey = _sessionkey(record_id, carenet_id)
        session = request.session.get(sessionkey)
        client = get_indivo_client(request, with_session_token=False, token=session['access_token'])

        # I am using JSON to get the data from the server. I could also use XML. 
        # The content of the GET document is totally different from the content of the PUT document.
        # Therefore there is no possibility of streamlineing the PUT and the GET stages.

        if record_id:
            resp, content = client.read_demographics(record_id=record_id, body={"response_format": "application/json"})
            if resp['status'] != '200':
                raise Exception("Error fetching demographics from record: %s"% record_id)
        else:
            resp, content = client.read_demographics_carenet(carenet_id=carenet_id, body={"response_format": "application/json"})
            if resp['status'] != '200':
                raise Exception("Error fetching demographics from carenet: %s"% carenet_id)

        data = json.loads(content)[0]
        o = self.model()
        o.carenet_id = carenet_id
        o.record_id = record_id
        if record_id:
            o._is_record = True
            o._is_carenet = False
        else:
            o._is_record = False
            o._is_carenet = True
        for k,v in data.items():
            if k != '__documentid__':
                setattr(o,k,v)
        return o

class Demographics(models.Model):
    """
        This is a mapping of the Indivo Demographics object. It is in
        a different "space" from the core model and it is not actually
        attached to the database.
    """
    record_id = models.CharField(max_length=200, null=True, blank=True)
    carenet_id = models.CharField(max_length=200, null=True, blank=True)

    name_prefix = models.CharField(max_length=200, null=True, blank=True)
    name_given = models.CharField(max_length=200, null=True, blank=True)
    name_middle = models.CharField(max_length=200, null=True, blank=True)
    name_family = models.CharField(max_length=200, null=True, blank=True)
    name_suffix = models.CharField(max_length=200, null=True, blank=True)

    ethnicity = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    bday = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True,
            choices=[('female', 'female'), ('male', 'male')])
    race = models.CharField(max_length=200, null=True, blank=True)

    adr_street = models.CharField(max_length=200, null=True, blank=True)
    adr_city = models.CharField(max_length=200, null=True, blank=True)
    adr_postalcode = models.CharField(max_length=200, null=True, blank=True)
    adr_region = models.CharField(max_length=200, null=True, blank=True)
    adr_country = models.CharField(max_length=200, null=True, blank=True)
    tel_1_type = models.CharField(max_length=200, null=True, blank=True,
            choices= [('h', 'Home'), ('w', 'Work'), ('c', 'Mobile')])
    tel_1_number = models.CharField(max_length=200, null=True, blank=True)
    tel_1_preferred_p = models.NullBooleanField(null=True, blank=True)
    tel_2_type = models.CharField(max_length=200, null=True, blank=True,
            choices= [('h', 'Home'), ('w', 'Work'), ('c', 'Mobile')])
    tel_2_number = models.CharField(max_length=200, null=True, blank=True)
    tel_2_preferred_p = models.NullBooleanField(null=True, blank=True)

    def __unicode__(self):
        return "%s %s %s %s %s (%s)" % (self.name_prefix, self.name_given,
            self.name_middle, self.name_family, self.name_suffix, self.bday)

    def save(self):
        carenet_id = self.carenet_id
        record_id = self.record_id
        assert record_id != None
        # Problem - XML format required
        d = self.to_xml()
        sessionkey = _sessionkey(record_id, carenet_id)
        request = get_request()
        session = request.session.get(sessionkey)
        client = get_indivo_client(request, with_session_token=False, token=session['access_token'])

        if record_id:
            resp, content = client.set_demographics(record_id=record_id, body=d)
            if resp['status'] != '200':
                logger.error("Error %s updating demographics from record (%s): %s\n%s"% (resp['status'], record_id, content, d.replace("><", ">\n<")))
                raise Exception("Error %s updating demographics from record (%s): %s"% (resp['status'], record_id, content))

    objects = DemographicsManager()

    def to_xml(self):
        doc = ET.Element('Demographics', attrib={'xmlns':"http://indivo.org/vocab/xml/documents#"})
        ET.SubElement(doc, 'dateOfBirth').text = self.bday and str(self.bday) or ""
        ET.SubElement(doc, 'gender').text = self.gender and str(self.gender) or ""
        ET.SubElement(doc, 'email').text = self.email and str(self.email) or ""
        ET.SubElement(doc, 'ethnicity').text = self.ethnicity and str(self.ethnicity) or ""
        ET.SubElement(doc, 'preferredLanguage').text = self.preferred_language and str(self.preferred_language) or ""
        ET.SubElement(doc, 'race').text = self.race and str(self.race) or ""
        name = ET.SubElement(doc, 'Name')
        ET.SubElement(name, 'familyName').text = self.name_family and str(self.name_family) or ""
        ET.SubElement(name, 'givenName').text = self.name_given and str(self.name_given) or ""
        ET.SubElement(name, 'middleName').text = self.name_middle and str(self.name_middle) or ""
        ET.SubElement(name, 'prefix').text = self.name_prefix and str(self.name_prefix) or ""
        ET.SubElement(name, 'suffix').text = self.name_suffix and str(self.name_suffix) or ""
        if self.tel_1_number:
            phone = ET.SubElement(doc, 'Telephone')
            ET.SubElement(phone, 'type').text = self.tel_1_type and str(self.tel_1_type) or ""
            ET.SubElement(phone, 'number').text = self.tel_1_number and str(self.tel_1_number) or ""
            ET.SubElement(phone, 'preferred').text = self.tel_1_preferred_p != None and (self.tel_1_preferred_p and 'true' or 'false') or ""
        if self.tel_2_number:
            phone = ET.SubElement(doc, 'Telephone')
            ET.SubElement(phone, 'type').text = self.tel_2_type and str(self.tel_2_type) or ""
            ET.SubElement(phone, 'number').text = self.tel_2_number and str(self.tel_2_number) or ""
            ET.SubElement(phone, 'preferred').text = self.tel_2_preferred_p != None and (self.tel_2_preferred_p and 'true' or 'false') or ""
        address = ET.SubElement(doc, 'Address')
        ET.SubElement(address, 'country').text = self.adr_country and str(self.adr_country) or ""
        ET.SubElement(address, 'city').text = self.adr_city and str(self.adr_city) or ""
        ET.SubElement(address, 'postalCode').text = self.adr_postalcode and str(self.adr_postalcode) or ""
        ET.SubElement(address, 'region').text = self.adr_region and str(self.adr_region) or ""
        ET.SubElement(address, 'street').text = self.adr_street and str(self.adr_street) or ""

        return ET.tostring(doc, encoding='utf8')
