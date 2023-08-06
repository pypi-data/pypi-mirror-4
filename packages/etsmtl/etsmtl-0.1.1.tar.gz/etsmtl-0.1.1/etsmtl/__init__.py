#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
import urlparse
import logging
import platform
import simplejson as json
import datetime
import time
import types
import textwrap
from xml.dom import minidom as dom


try:
    import requests
except ImportError:
    pass

try:
    # Require version 0.8.8, but don't want to depend on distutils
    version = requests.__version__
    major, minor, patch = [int(i) for i in version.split('.')]
except Exception:
    # Probably some new-fangled version, so it should support verify
    pass
else:
    if (major, minor, patch) < (0, 8, 8):
        print >>sys.stderr, 'Warning: the ETSMTLlibrary requires that your Python "requests" library has a version no older than 0.8.8, but your "requests" library has version %s. ETSMTL will fall back to an alternate HTTP library, so everything should work, though we recommend upgrading your "requests" library.  (HINT: running "pip install -U requests" should upgrade your requests library to the latest version.)' % (
            version, )


logger = logging.getLogger('etsmtl')

# Configuration variables

username = None
password = None
api_url = None
api_action_base = 'http://etsmtl.ca/'
api_version = None
verify_ssl_certs = True


class ETSError(Exception):

    def __init__(self, message=None, http_body=None, http_status=None, json_body=None):
        super(ETSError, self).__init__(message)
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body


class AuthenticationError(ETSError):
    pass


class APIConnectionError(ETSError):
    pass


class APIRequestor(object):

    responses = {}

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.need_authentication = True

    @classmethod
    def build_cache_key(cls, action, params):
        return '%s-%s' % (action, cls.encode(params))

    @classmethod
    def reset_cache(cls, key=None):
        if key is None:
            cls.responses = {}
        elif key in cls.responses:
            del cls[key]

    @classmethod
    def _set_value(cls, obj, node):
        if hasattr(node.firstChild, 'nodeValue'):
            value = node.firstChild.nodeValue
            if value is not None:
                if node.nodeName.startswith('date'):
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                else:
                    value = cls._utf8(value).strip()

                setattr(obj, node.nodeName, value)

    @classmethod
    def _utf8(cls, value):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        else:
            return value

    @classmethod
    def encode_dict(cls, stk, key, dictvalue):
        n = {}
        for k, v in dictvalue.iteritems():
            k = cls._utf8(k)
            v = cls._utf8(v)
            n["%s[%s]" % (key, k)] = v
        stk.extend(cls._encode_inner(n))

    @classmethod
    def encode_list(cls, stk, key, listvalue):
        for v in listvalue:
            v = cls._utf8(v)
            stk.append(("%s[]" % (key), v))

    @classmethod
    def encode_datetime(cls, stk, key, dttime):
        utc_timestamp = int(time.mktime(dttime.timetuple()))
        stk.append((key, utc_timestamp))

    @classmethod
    def encode_none(cls, stk, k, v):
        pass  # do not include None-valued params in request

    @classmethod
    def _encode_inner(cls, d):
        """
        We want post vars of form:
        {'foo': 'bar', 'nested': {'a': 'b', 'c': 'd'}}
        to become:
        foo=bar&nested[a]=b&nested[c]=d
        """
        # special case value encoding
        ENCODERS = {
            list: cls.encode_list,
            dict: cls.encode_dict,
            datetime.datetime: cls.encode_datetime,
            types.NoneType: cls.encode_none,
        }

        stk = []
        for key, value in d.iteritems():
            key = cls._utf8(key)
            try:
                encoder = ENCODERS[value.__class__]
                encoder(stk, key, value)
            except KeyError:
                # don't need special encoding
                value = cls._utf8(value)
                stk.append((key, value))
        return stk

    @classmethod
    def encode(cls, d):
        """
        Internal: encode a string for url representation
        """
        return urllib.urlencode(cls._encode_inner(d))

    @classmethod
    def action_url(cls, action=''):
        return '%s%s' % (api_action_base, action)

    @classmethod
    def build_url(cls, url, params):
        base_query = urlparse.urlparse(url).query
        if base_query:
            return '%s&%s' % (url, cls.encode(params))
        else:
            return '%s?%s' % (url, cls.encode(params))

    def request(self, action=None, url=None, params={}):

        if action is None:
            action = self.action
            if action is None:
                raise ETSError('No action provided.')

        key = self.build_cache_key(action, params)

        if key in self.responses:
            return self.responses[key]

        rbody, rcode, effective_username, effective_password = self.request_raw(action, url, params)

        resp = self.interpret_response(rbody, rcode, action)

        self.responses[key] = (resp, effective_username, effective_password)

        return self.responses[key]

    def request_raw(self, action=None, url=None, params={}):
        """
        Mechanism for issuing an API call
        """

        if self.need_authentication:
            effective_username, effective_password = self.username or username, self.password or password
            if effective_username is None or effective_password is None:
                raise AuthenticationError(
                    'No credentials provided.')

            params['codeAccesUniversel'] = effective_username
            params['motPasse'] = effective_password
        else:
            effective_username, effective_password = None, None

        if url is None:
            url = api_url
            if url is None:
                raise ETSError('No API url provided.')

        ua = {
            'lang': 'python',
            'publisher': 'etsmtl',
        }
        for attr, func in [['lang_version', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception, e:
                val = "!! %s" % e
            ua[attr] = val

        data = self.generate_data(action, params)

        headers = {
            'X-ETSMTL-Client-User-Agent': json.dumps(ua),
            'SOAPAction': self.action_url(action),
            'Content-Type': 'text/xml',
            'Content-Length': len(data)
        }
        if api_version is not None:
            headers['ETSMTL-Version'] = api_version

        logger.info('API request to %s sent (request body) : %s' % (url, data))
        rbody, rcode = self.do_request(url, headers, data)
        logger.info('API request to %s returned (response code, response body) of (%d, %r)' % (url, rcode, rbody))
        return rbody, rcode, effective_username, effective_password

    def do_request(self, abs_url, headers, data):

        kwargs = {}
        if verify_ssl_certs:
            kwargs['verify'] = os.path.join(os.path.dirname(__file__), 'data/ca-certificates.crt')
        else:
            kwargs['verify'] = False

        try:
            try:
                result = requests.post(abs_url, headers=headers, data=data, timeout=80, **kwargs)
            except TypeError, e:
                raise TypeError(
                    'Warning: It looks like your installed version of the "requests" library is not compatible with ETSMTL\'s usage thereof. (HINT: The most likely cause is that your "requests" library is out of date. You can fix that by running "pip install -U requests".) The underlying error was: %s' % (e, ))

            # This causes the content to actually be read, which could cause
            # e.g. a socket timeout. TODO: The other fetch methods probably
            # are succeptible to the same and should be updated.
            content = result.content
            status_code = result.status_code
        except Exception, e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self.handle_requests_error(e)
        return content, status_code

    @classmethod
    def _generate_header(cls, action):
        return '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><%s xmlns="%s">' % (action, api_action_base)

    @classmethod
    def _generate_footer(cls, action):
        return '</%s></soap:Body></soap:Envelope>' % action

    @classmethod
    def generate_data(cls, action, params):
        content = cls._generate_header(action)

        for key, value in params.items():
            content += '<%s>%s</%s>' % (key, value, key)

        content += cls._generate_footer(action)

        return content

    @classmethod
    def _get_xml(cls, data):
        return dom.parseString(data)

    def interpret_response(self, rbody, rcode, action):
        raise NotImplementedError()  # must be redefined in child requestors

    def handle_requests_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with ETSMTL."
            err = "%s: %s" % (type(e).__name__, e.message)
        else:
            msg = "Unexpected error communicating with ETSMTL.  It looks like there's probably a configuration issue locally."
            err = "A %s was raised" % (type(e).__name__, )
            if e.message:
                err += " with error message %s" % (e.message, )
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: " + err + ")"
        raise APIConnectionError(msg)


class EvaluationRequestor(APIRequestor):
    action = 'listeElementsEvaluation'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        result = results[0]

        evaluation = Evaluation()

        error = result.getElementsByTagName('erreur')

        if hasattr(error[0].firstChild, 'nodeValue'):
            return evaluation

        for node in result.childNodes:
            if node.nodeName in ('liste'):
                elements = node.getElementsByTagName('ElementEvaluation')
                for evaluationNode in elements:
                    element = EvaluationElement()
                    for p_node in evaluationNode.childNodes:
                        self._set_value(element, p_node)
                    evaluation.elements.append(element)
            else:
                self._set_value(evaluation, node)

        return evaluation


class Evaluation(object):

    """
    An Evaluation object is defined by these fields
            <noteACeJour>string</noteACeJour>
            <scoreFinalSur100>string</scoreFinalSur100>
            <moyenneClasse>string</moyenneClasse>
            <ecartTypeClasse>string</ecartTypeClasse>
            <medianeClasse>string</medianeClasse>
            <rangCentileClasse>string</rangCentileClasse>
            <noteACeJourElementsIndividuels>string</noteACeJourElementsIndividuels>
            <noteSur100PourElementsIndividuels>string</noteSur100PourElementsIndividuels>
    """
    requestor_class = EvaluationRequestor

    def __init__(self):
        self.elements = []
        self.noteACeJour = ''
        self.scoreFinalSur100 = ''
        self.moyenneClasse = ''
        self.ecartTypeClasse = ''
        self.medianeClasse = ''
        self.rangCentileClasse = ''
        self.noteACeJourElementsIndividuels = ''
        self.noteSur100PourElementsIndividuels = ''

    def __repr__(self):
        if len(self.noteACeJour) > 0:
            return 'Evaluation(%s/100)' % (self.scoreFinalSur100)
        return 'Evaluation()'


class EvaluationElement(object):

    """
    An EvaluationElement is defined by these fields
            <coursGroupe>string</coursGroupe>
            <nom>string</nom>
            <equipe>string</equipe>
            <dateCible>string</dateCible>
            <note>string</note>
            <corrigeSur>string</corrigeSur>
            <ponderation>string</ponderation>
            <moyenne>string</moyenne>
            <ecartType>string</ecartType>
            <mediane>string</mediane>
            <rangCentile>string</rangCentile>
            <publie>string</publie>
            <messageDuProf>string</messageDuProf>
            <ignoreDuCalcul>string</ignoreDuCalcul>
    """

    def __init__(self):
        self.coursGroupe = ''
        self.nom = ''
        self.equipe = ''
        self.dateCible = None
        self.note = ''
        self.corrigeSur = ''
        self.ponderation = ''
        self.moyenne = ''
        self.ecartType = ''
        self.mediane = ''
        self.rangCentile = ''
        self.publie = ''
        self.messageDuProf = ''
        self.ignoreDuCalcul = ''

    def __repr__(self):
        return 'EvaluationElement(%s, %s/%s)' % (self.nom, self.note, self.corrigeSur)


class CoursRequestor(APIRequestor):
    action = 'listeCours'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        xml_cours = results[0].getElementsByTagName('Cours')

        cours_list = []

        for xml_c in xml_cours:
            cours = Cours()

            for node in xml_c.childNodes:
                self._set_value(cours, node)

            cours_list.append(cours)

        return cours_list


class Cours(object):

    """
    A Cours object is defined by these fields
            <sigle>string</sigle>
            <groupe>string</groupe>
            <session>string</session>
            <programmeEtudes>string</programmeEtudes>
            <cote>string</cote>
            <nbCredits>int</nbCredits>
            <titreCours>string</titreCours>
    """
    requestor_class = CoursRequestor
    evaluation_requestor_class = EvaluationRequestor

    def __init__(self):
        self.sigle = ''
        self.groupe = ''
        self.session = ''
        self.programmeEtudes = ''
        self.nbCredits = ''
        self.titreCours = ''

    def __repr__(self):
        return 'Cours(%s, %s, %s)' % (self.sigle, self.session, self.groupe)

    def _get_evaluation(self):
        if hasattr(self, '_evaluation'):
            return getattr(self, '_evaluation')

        evaluation, effective_username, effective_password = self.evaluation_requestor_class().request(
            params={'pSigle': self.sigle, 'pGroupe': self.groupe, 'pSession': self.session})

        setattr(self, '_evaluation', evaluation)

        return self._get_evaluation()

    evaluation = property(_get_evaluation)


class SessionsRequestor(APIRequestor):
    action = 'listeSessions'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        xml_sessions = results[0].getElementsByTagName('Trimestre')

        sessions = []

        for xml_session in xml_sessions:
            session = Session()

            for node in xml_session.childNodes:
                self._set_value(session, node)

            sessions.append(session)

        return sessions


class Session(object):

    """
    A session object is defined by these fields
            <abrege>string</abrege>
            <auLong>string</auLong>
            <dateDebut>date</dateDebut>
            <dateFin>date</dateFin>
            <dateFinCours>date</dateFinCours>
            <dateDebutChemiNot>date</dateDebutChemiNot>
            <dateFinChemiNot>date</dateFinChemiNot>
            <dateDebutAnnulationAvecRemboursement>date</dateDebutAnnulationAvecRemboursement>
            <dateFinAnnulationAvecRemboursement>date</dateFinAnnulationAvecRemboursement>
            <dateFinAnnulationAvecRemboursementNouveauxEtudiants>date</dateFinAnnulationAvecRemboursementNouveauxEtudiants>
            <dateDebutAnnulationSansRemboursementNouveauxEtudiants>date</dateDebutAnnulationSansRemboursementNouveauxEtudiants>
            <dateFinAnnulationSansRemboursementNouveauxEtudiants>date</dateFinAnnulationSansRemboursementNouveauxEtudiants>
            <dateLimitePourAnnulerASEQ>date</dateLimitePourAnnulerASEQ>
    """
    requestor_class = SessionsRequestor
    cours_requestor_class = CoursRequestor

    def __init__(self):
        self.abrege = ''
        self.auLong = ''
        self.dateDebut = None
        self.dateFin = None
        self.dateFinCours = None
        self.dateDebutChemiNot = None
        self.dateFinChemiNot = None
        self.dateDebutAnnulationAvecRemboursement = None
        self.dateFinAnnulationAvecRemboursement = None
        self.dateDebutAnnulationSansRemboursementNouveauxEtudiants = None
        self.dateFinAnnulationSansRemboursementNouveauxEtudiants = None
        self.dateLimitePourAnnulerASEQ = None

    def __repr__(self):
        return 'Session(%s)' % self.abrege

    def _get_cours(self):
        if hasattr(self, '_cours'):
            return getattr(self, '_cours')

        cours, effective_username, effective_password = self.cours_requestor_class().request()

        setattr(self, '_cours', filter(lambda x: x.session in (self.abrege), cours))

        return self._get_cours()

    cours = property(_get_cours)


class ProgrammeRequestor(APIRequestor):
    action = 'listeProgrammes'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        xml_programs = results[0].getElementsByTagName('Programme')

        programs = []

        for xml_program in xml_programs:
            program = Programme()

            for node in xml_program.childNodes:
                self._set_value(program, node)

            programs.append(program)

        return programs


class Programme(object):

    """
    A Programme object is defined by these fields
            <code>string</code>
            <libelle>string</libelle>
            <profil>string</profil>
            <statut>string</statut>
            <sessionDebut>string</sessionDebut>
            <sessionFin>string</sessionFin>
            <moyenne>string</moyenne>
            <nbEquivalences>string</nbEquivalences>
            <nbCrsReussis>string</nbCrsReussis>
            <nbCrsEchoues>string</nbCrsEchoues>
            <nbCreditsInscrits>string</nbCreditsInscrits>
            <nbCreditsCompletes>string</nbCreditsCompletes>
            <nbCreditsPotentiels>string</nbCreditsPotentiels>
            <nbCreditsRecherche>string</nbCreditsRecherche>
    """
    requestor_class = ProgrammeRequestor

    def __init__(self):
        self.code = ''
        self.libelle = ''
        self.profil = ''
        self.statut = ''
        self.sessionDebut = ''
        self.sessionFin = ''
        self.moyenne = ''
        self.nbEquivalences = ''
        self.nbCrsReussis = ''
        self.nbCrsEchoues = ''
        self.nbCreditsInscrits = ''
        self.nbCreditsCompletes = ''
        self.nbCreditsPotentiels = ''
        self.nbCreditsRecherche = ''

    def __repr__(self):
        return 'Programme(%s, %s, %s)' % (self.libelle, self.statut, self.nbCreditsPotentiels)


class EtudiantRequestor(APIRequestor):
    action = 'infoEtudiant'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        etudiant = Etudiant()

        for node in results[0].childNodes:
            self._set_value(etudiant, node)

        return etudiant


class Etudiant(object):

    """
    An Etudiant object is defined by these fields
        <nom>string</nom>
        <prenom>string</prenom>
        <codePerm>string</codePerm>
        <soldeTotal>string</soldeTotal>

    """

    def __init__(self):
        self.nom = ''
        self.prenom = ''
        self.codePerm = ''
        self.soldeTotal = ''

    def __repr__(self):
        return 'Etudiant(%s, %s, %s, %s)' % (self.prenom, self.nom, self.codePerm, self.soldeTotal)


class HoraireSearchRequestor(APIRequestor):
    action = 'lireHoraire'

    def __init__(self, *args, **kwargs):
        super(HoraireSearchRequestor, self).__init__(*args, **kwargs)
        self.need_authentication = False

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        xml_cours = results[0].getElementsByTagName('coursHoraire')

        cours_list = []

        for xml_c in xml_cours:
            cours = CoursHoraire()

            for node in xml_c.childNodes:
                self._set_value(cours, node)

            cours_list.append(cours)

        return cours_list


class HoraireRequestor(APIRequestor):
    action = 'listeHoraireEtProf'

    def interpret_response(self, rbody, rcode, action):
        if rcode is not 200:
            raise ETSError('Bad request')

        xml = self._get_xml(rbody)
        results = xml.getElementsByTagName('%sResult' % action)

        if len(results) is 0:
            raise ETSError('No results were returned')

        xml_cours = results[0].getElementsByTagName('HoraireActivite')

        cours_list = []

        for xml_c in xml_cours:
            cours = CoursHoraire()

            for node in xml_c.childNodes:
                self._set_value(cours, node)

            cours_list.append(cours)

        return cours_list


class CoursHoraire(object):

    """
    A CoursHoraire object is defined by these fields
            <sigle>string</sigle>
            <groupe>string</groupe>
            <jour>string</jour>
            <journee>string</journee>
            <codeActivite>string</codeActivite>
            <nomActivite>string</nomActivite>
            <activitePrincipale>string</activitePrincipale>
            <heureDebut>string</heureDebut>
            <heureFin>string</heureFin>
            <local>string</local>
            <titreCours>string</titreCours>
    """

    requestor_class = HoraireSearchRequestor

    def __init__(self):
        self.sigle = ''
        self.groupe = ''
        self.jour = ''
        self.journee = ''
        self.codeActivite = ''
        self.nomActivite = ''
        self.activitePrincipale = ''
        self.heureDebut = ''
        self.heureFin = ''
        self.local = ''
        self.titreCours = ''

    def __repr__(self):
        return 'CoursHoraire(%s, %s, %s, %s, %s, %s, %s)' % (self.sigle, self.titreCours, self.groupe, self.journee, self.heureDebut, self.heureFin, self.nomActivite)
