# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.apogee.interfaces.utility import IApogee, IApogeeLayout

from OFS.SimpleItem import SimpleItem

# Imports
#import json
#import ldap
#import sqlite3
from sqlite3 import dbapi2 as sqlite
from DateTime import DateTime

import tables

# SQL Alchemy
from sqlalchemy import create_engine, and_, or_, distinct
from sqlalchemy.sql import func, text
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.pool import NullPool


def form_adapter(context):
    """Form Adapter"""
    return getUtility(IApogee)


class Apogee(SimpleItem):
    """Apogee Utility"""
    implements(IApogee)
    classProvides(
        IApogeeLayout,
        )
    security = ClassSecurityInfo()

    # Parametres généraux
    url_connexion = FieldProperty(IApogeeLayout['url_connexion'])
    cod_anu = FieldProperty(IApogeeLayout['cod_anu'])
    uel = FieldProperty(IApogeeLayout['uel'])
    type_base = FieldProperty(IApogeeLayout['type_base'])
    sessionApogee = None
    Session = sessionmaker()
    #ScopedSession = None

    #debug = []

    def getSession(self):
        #print "----------- getSession -----------"
        #print self.sessionApogee
        try:
            self.Session().get_bind()
            #print self.Session()
        except:
            #print "except Session"
            self.sessionApogee = None
        if (not self.sessionApogee) or (self.sessionApogee != self.type_base):
            #print "initialiser session"
            try:
                self.Session().close()
            except:
                pass
            if self.type_base == "sqlite":
                engine = create_engine(self.url_connexion, module=sqlite, echo=False, poolclass=NullPool)
            if self.type_base == "apogee":
                engine = create_engine(self.url_connexion, echo=False, poolclass=NullPool)
            #print "ouverture connexion"
            self.Session.configure(bind=engine)
            self.sessionApogee = self.type_base
        return self.Session()

    # Parametres spécifiques
    def getAttribut(self, attribut):
        return self.__getattribute__(attribut)

    def getGroupesEtudiant(self, COD_ETU):
        session = self.getSession()
        if self.type_base == "apogee":
            GPE = aliased(tables.Groupe)
            GPO = aliased(tables.GpeObj)
            IAG = aliased(tables.IndAffecteGpe)
            IND = aliased(tables.Individu)
            recherche = session.query(IAG.COD_GPE, GPE.LIB_GPE, GPE.COD_EXT_GPE, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).outerjoin(GPE, IAG.COD_GPE == GPE.COD_GPE).outerjoin(GPO, GPE.COD_GPE == GPO.COD_GPE).outerjoin(IND, IAG.COD_IND == IND.COD_IND).filter(and_(IAG.COD_ANU == int(self.cod_anu), GPE.LIB_GPE <> None, IND.COD_ETU == COD_ETU)).group_by(IAG.COD_GPE, GPE.LIB_GPE, GPE.COD_EXT_GPE, GPE.COD_EXT_GPE, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).order_by(GPE.LIB_GPE)
            return recherche.all()
        if self.type_base == "sqlite":
            listeGroupe = []
            ELP = aliased(tables.ElementPedagogiSQLITE)
            ICE = aliased(tables.IndContratElpSQLITE)
            ERE = aliased(tables.ETPRegroupeELPSQLITE)
            rechercheGroupe = [groupe[0] for groupe in session.query(ICE.COD_ELP).filter(and_(ICE.SESAME_ETU == COD_ETU, ICE.TYPE_ELP == 'groupe')).all()]
            if not rechercheGroupe:
                return []
            recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.COD_GPE).filter(ELP.COD_ELP.in_(rechercheGroupe)).all()
            for groupe in recherche:
                recherche = session.query(ERE.TYP_ELP, ERE.COD_ELP_PERE).filter(ERE.COD_ELP_FILS == groupe[0])
                for ligne in recherche.all():
                    if ligne[0] == "VET":
                        COD_ELP = ligne[1]
                        COD_ETP, COD_VRS_VET = ligne[1].split("-")
                    else:
                        COD_ELP = COD_ETP = COD_VRS_VET = ligne[1]
                    groupe = list(groupe)
                    groupe.extend([ligne[0], COD_ELP, COD_ETP, COD_VRS_VET])
                    listeGroupe.append(groupe)
            return listeGroupe

    def getTousEtudiantsGroupes(self):
        GPE = aliased(tables.Groupe)
        GPO = aliased(tables.GpeObj)
        IAG = aliased(tables.IndAffecteGpe)
        IND = aliased(tables.Individu)
        session = self.getSession()
        recherche = session.query(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).outerjoin(GPE, IAG.COD_GPE==GPE.COD_GPE).outerjoin(GPO, GPE.COD_GPE==GPO.COD_GPE).outerjoin(IND, IAG.COD_IND==IND.COD_IND).filter(and_(IAG.COD_ANU==int(self.cod_anu), GPE.LIB_GPE <> None)).group_by(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET)
        #session.close()
        return recherche.all()

    def getInfosEtape(self, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        if self.type_base == "apogee":
            V = aliased(tables.VersionEtape)
            IAE = aliased(tables.InsAdmEtp)
            recherche = session.query(V.LIB_WEB_VET, func.concat(V.COD_ETP + "-", V.COD_VRS_VET), func.count(distinct(IAE.COD_IND)).label("nb_etu")).outerjoin(IAE, and_(IAE.COD_ETP == V.COD_ETP, IAE.COD_VRS_VET == V.COD_VRS_VET, IAE.COD_ANU == int(self.cod_anu))).filter(and_(V.COD_ETP == COD_ETP, V.COD_VRS_VET == int(COD_VRS_VET))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET)
            #session.close()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu")).filter(ELP.COD_ELP == "%s-%s" % (COD_ETP, str(COD_VRS_VET)))
        return recherche.first()

    def getInfosELP(self, COD_ELP):
        session = self.getSession()
        if self.type_base == "apogee":
            ELP = aliased(tables.ElementPedagogi)
            ICE = aliased(tables.IndContratElp)
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ICE, and_(ICE.COD_ELP == ELP.COD_ELP, ICE.COD_ANU == int(self.cod_anu))).filter(ELP.COD_ELP == COD_ELP).group_by(ELP.LIB_ELP, ELP.COD_ELP)
            #session.close()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu")).filter(ELP.COD_ELP == COD_ELP)
        return recherche.first()

    def getInfosGPE(self, COD_GPE):
        session = self.getSession()
        if self.type_base == "apogee":
            GPE = aliased(tables.Groupe)
            IAG = aliased(tables.IndAffecteGpe)
            recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu"), GPE.COD_EXT_GPE).outerjoin(IAG, and_(IAG.COD_GPE == GPE.COD_GPE, IAG.COD_ANU == int(self.cod_anu))).filter(GPE.COD_GPE == int(COD_GPE)).group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE)
            #session.close()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.COD_GPE).filter(ELP.COD_ELP == COD_GPE)
        return recherche.first()

    def getInscriptionPedago(self, COD_ETU, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        if self.type_base == "apogee":
            ICE = aliased(tables.IndContratElp)
            IND = aliased(tables.Individu)
            ELP = aliased(tables.ElementPedagogi)
            recherche = session.query(ICE.COD_ELP, ELP.LIB_ELP).outerjoin(IND, ICE.COD_IND == IND.COD_IND).outerjoin(ELP, ICE.COD_ELP == ELP.COD_ELP).filter(and_(ICE.COD_ANU == int(self.cod_anu), ICE.COD_ETP == COD_ETP, ICE.COD_VRS_VET == int(COD_VRS_VET), IND.COD_ETU == int(COD_ETU)))
        if self.type_base == "sqlite":
            ICE = aliased(tables.IndContratElpSQLITE)
            ELP = aliased(tables.ElementPedagogiSQLITE)
            listeIDUE = [idue[0] for idue in session.query(ICE.COD_ELP).filter(and_(ICE.SESAME_ETU == COD_ETU, ICE.COD_ELP_PERE == '%s-%s' % (COD_ETP, COD_VRS_VET))).all()]
            if not listeIDUE:
                return []
            recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP).filter(ELP.COD_ELP.in_(listeIDUE))
        return recherche.all()

    def getToutesInscriptionPedago(self):
        ICE = aliased(tables.IndContratElp)
        IND = aliased(tables.Individu)
        ELP = aliased(tables.ElementPedagogi)
        session = self.getSession()
        recherche = session.query(IND.COD_ETU, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, ICE.COD_ELP, ICE.COD_ETP, ICE.COD_VRS_VET).outerjoin(ICE, ICE.COD_IND == IND.COD_IND).outerjoin(ELP, ICE.COD_ELP == ELP.COD_ELP).filter(ICE.COD_ANU == int(self.cod_anu)).order_by(IND.LIB_NOM_PAT_IND)
        #recherche = session.query(IND.COD_ETU, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, ICE.COD_ELP).outerjoin(ICE, ICE.COD_IND == IND.COD_IND).outerjoin(ELP, ICE.COD_ELP == ELP.COD_ELP).filter(ICE.COD_ANU == int(self.cod_anu)).order_by(IND.LIB_NOM_PAT_IND)
        #session.close()
        return recherche.all()

    def getUeEtape(self, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        if self.type_base == "apogee":
            requete = text("""SELECT ere.cod_elp_fils, elp.lib_elp
                              FROM elp_regroupe_elp ere, element_pedagogi elp
                              WHERE elp.cod_elp = ere.cod_elp_fils
                              START WITH ere.cod_lse in
                                 (SELECT LSE.COD_LSE
                                 FROM LISTE_ELP LSE, VET_REGROUPE_LSE VRL
                                 WHERE vrl.cod_etp = '%s'
                                    AND vrl.cod_vrs_vet = %s
                                    AND lse.cod_lse = vrl.cod_lse
                                    AND vrl.dat_frm_rel_lse_vet is null
                                    AND lse.eta_lse != 'F'
                                 )
                                 AND ere.cod_elp_pere is null
                                 AND ere.eta_elp_fils != 'F'
                                 AND ere.tem_sus_elp_fils = 'N'
                              CONNECT BY PRIOR ere.cod_elp_fils = ere.cod_elp_pere
                                 AND ere.eta_elp_fils != 'F'
                                 AND ere.tem_sus_elp_fils = 'N'
                                 AND NVL (ere.eta_elp_pere, 'O') != 'F'
                                 AND NVL (ere.tem_sus_elp_pere, 'N') = 'N'
                                 AND ere.eta_lse != 'F'
                                 AND ere.date_fermeture_lien is null
                          """ % (str(COD_ETP), int(COD_VRS_VET)))
            recherche = session.execute(requete)
            return recherche.fetchall()
        if self.type_base == "sqlite":
            ERE = aliased(tables.ETPRegroupeELPSQLITE)
            ELP = aliased(tables.ElementPedagogiSQLITE)
            listeIDUE = [idue[0] for idue in session.query(ERE.COD_ELP_FILS).filter(and_(ERE.COD_ELP_PERE == "%s-%s" % (COD_ETP, COD_VRS_VET), ERE.TYP_ELP == 'VET')).all()]
            if not listeIDUE:
                return []
            recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP).filter(ELP.COD_ELP.in_(listeIDUE))
            return recherche.all()

    def getCodAnu(self):
        return self.cod_anu

    def getURLApogee(self):
        return self.url_connexion

    def getVersionEtape(self, COD_ETP, COD_VRS_VET):
        session = self.getSession()
        if self.type_base == "apogee":
            VET = aliased(tables.VersionEtape)
            etape = session.query(VET.LIB_WEB_VET).filter(and_(VET.COD_ETP == COD_ETP, VET.COD_VRS_VET == COD_VRS_VET)).first()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            etape = session.query(ELP.LIB_ELP).filter(ELP.COD_ELP == '%s-%s' % (COD_ETP, str(COD_VRS_VET))).first()
        return etape

    security.declarePrivate('convertirDate')

    def convertirDate(self, d, us=False):
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m-%d")

    def rechercherEtape(self, listeRecherche):
        listeCond = []
        session = self.getSession()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot)))
                listeCond.append(ELP.TYP_ELP == "etape")
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
        if self.type_base == "apogee":
            V = aliased(tables.VersionEtape)
            VV = aliased(tables.VdiFractionnerVet)
            IAE = aliased(tables.InsAdmEtp)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(V.COD_ETP).like(mot), func.upper(V.LIB_WEB_VET).like(mot)))
            recherche = session.query(V.LIB_WEB_VET, func.concat(V.COD_ETP + "-", V.COD_VRS_VET), VV.DAA_FIN_RCT_VET, func.max(VV.DAA_FIN_VAL_VET), func.count(distinct(IAE.COD_IND)).label("nb_etu")).outerjoin(VV, and_(VV.COD_ETP==V.COD_ETP, VV.COD_VRS_VET==V.COD_VRS_VET)).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).filter(and_(VV.DAA_FIN_RCT_VET >= int(self.cod_anu), VV.DAA_FIN_VAL_VET >= int(self.cod_anu), and_(*listeCond))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET, VV.DAA_FIN_RCT_VET).having(func.count(distinct(IAE.COD_IND)) > 0).order_by(V.LIB_WEB_VET)
        return recherche.all()

    def rechercherToutesEtapes(self):
        V = aliased(tables.VersionEtape)
        VV = aliased(tables.VdiFractionnerVet)
        IAE = aliased(tables.InsAdmEtp)
        session = self.getSession()
        recherche = session.query(V.COD_ETP, V.COD_VRS_VET, V.LIB_WEB_VET, func.count(distinct(IAE.COD_IND))).outerjoin(VV, and_(VV.COD_ETP==V.COD_ETP, VV.COD_VRS_VET==V.COD_VRS_VET)).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.COD_ANU==int(self.cod_anu))).filter(and_(VV.DAA_FIN_RCT_VET >= int(self.cod_anu), VV.DAA_FIN_VAL_VET >= int(self.cod_anu))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET).having(func.count(distinct(IAE.COD_IND)) > 0).order_by(V.LIB_WEB_VET)
        return recherche.all()

    def rechercherELP(self, listeRecherche, uel):
        listeCond = []
        session = self.getSession()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot)))
            if uel:
                listeCond.append(ELP.TYP_ELP == "uel")
            else:
                listeCond.append(ELP.TYP_ELP == "ue")
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
        if self.type_base == "apogee":
            ELP = aliased(tables.ElementPedagogi)
            ERE = aliased(tables.ElpRegroupeElp)
            ICE = aliased(tables.IndContratElp)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot)))
            if uel:
                listeCond.append(ERE.COD_LSE.like(self.uel + '%'))
            else:
                listeCond.append(~ERE.COD_LSE.like(self.uel + '%'))
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, ERE.COD_ELP_FILS==ELP.COD_ELP).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(self.cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', and_(*listeCond))).group_by(ELP.LIB_ELP, ELP.COD_ELP).having(func.count(distinct(ICE.COD_IND)) > 0).order_by(ELP.LIB_ELP)
        return recherche.all()

    def rechercherToutesELPs(self, uel=None):
        ELP = aliased(tables.ElementPedagogi)
        ERE = aliased(tables.ElpRegroupeElp)
        ICE = aliased(tables.IndContratElp)
        if uel:
            condition = ERE.COD_LSE.like(self.uel + '%')
        else:
            condition = ~ERE.COD_LSE.like(self.uel + '%')
        session = self.getSession()
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, ERE.COD_ELP_FILS==ELP.COD_ELP).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(self.cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', condition)).group_by(ELP.LIB_ELP, ELP.COD_ELP).having(func.count(distinct(ICE.COD_IND)) > 0).order_by(ELP.LIB_ELP)
        return recherche.all()

    def rechercherGPE(self, listeRecherche):
        listeCond = []
        session = self.getSession()
        if self.type_base == "sqlite":
            ELP = aliased(tables.ElementPedagogiSQLITE)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot)))
                listeCond.append(ELP.TYP_ELP == "groupe")
            recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.COD_GPE, ELP.ETU_ELP.label("nb_etu")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
        if self.type_base == "apogee":
            GPE = aliased(tables.Groupe)
            IAG = aliased(tables.IndAffecteGpe)
            for element in listeRecherche:
                mot = self.supprimerAccent(element).upper()
                listeCond.append(or_(func.upper(GPE.COD_EXT_GPE).like(mot), func.upper(GPE.LIB_GPE).like(mot)))
            recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu")).outerjoin(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(self.cod_anu))).filter(and_(GPE.LIB_GPE <> 'None', and_(*listeCond))).group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE).having(func.count(distinct(IAG.COD_IND)) > 0).order_by(GPE.LIB_GPE)
        return recherche.all()

    def rechercherTousGPEs(self):
        GPE = aliased(tables.Groupe)
        IAG = aliased(tables.IndAffecteGpe)
        session = self.getSession()
        recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu")).outerjoin(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(self.cod_anu))).filter(GPE.LIB_GPE <> 'None').group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE).having(func.count(distinct(IAG.COD_IND)) > 0).order_by(GPE.LIB_GPE)
        return recherche.all()

    def rechercherEtudiants(self, code, type):
        # à modifier uel
        session = self.getSession()
        if self.type_base == "apogee":
            IND = aliased(tables.Individu)
            if type == "etape":
                COD_ETP, COD_VRS_VET = code.split("-")
                IAE = aliased(tables.InsAdmEtp)
                recherche = session.query(IAE.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU, IND.DATE_NAI_IND, IND.LIB_NOM_USU_IND).outerjoin(IND, IND.COD_IND == IAE.COD_IND).filter(and_(IAE.COD_ETP == COD_ETP, IAE.COD_VRS_VET == COD_VRS_VET, IAE.COD_ANU == int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
            if type in ["ue", "uel"]:
                COD_ELP = code
                ICE = aliased(tables.IndContratElp)
                recherche = session.query(ICE.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU, IND.DATE_NAI_IND, IND.LIB_NOM_USU_IND).outerjoin(IND, IND.COD_IND == ICE.COD_IND).filter(and_(ICE.COD_ELP == COD_ELP, ICE.COD_ANU == int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
            if type == "groupe":
                COD_GPE = code
                IAG = aliased(tables.IndAffecteGpe)
                recherche = session.query(IAG.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU, IND.DATE_NAI_IND, IND.LIB_NOM_USU_IND).outerjoin(IND, IND.COD_IND == IAG.COD_IND).filter(and_(IAG.COD_GPE == COD_GPE, IAG.COD_ANU == int(self.cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
        if self.type_base == "sqlite":
            IND = aliased(tables.IndividuSQLITE)
            ICE = aliased(tables.IndContratElpSQLITE)
            sesame = session.query(distinct(ICE.SESAME_ETU)).filter(ICE.COD_ELP == str(code)).order_by(ICE.SESAME_ETU)
            listeSesame = [x[0] for x in sesame.all()]
            taille = len(listeSesame)
            if taille > 500:
                liste = []
                deb = 0
                while deb < taille:
                    fin = deb + 499
                    if fin > taille:
                        fin = taille
                    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU.in_(listeSesame[deb:fin])).order_by(IND.LIB_NOM_PAT_IND)
                    liste.extend(recherche.all())
                    deb = deb + 500
                return liste
            recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU.in_(listeSesame)).order_by(IND.LIB_NOM_PAT_IND)
        return recherche.all()

    def getIndividuLITE(self, sesame):
        session = self.getSession()
        IND = aliased(tables.IndividuSQLITE)
        recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU == sesame)
        return recherche.all()

    # getIndividus renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour la liste des sesames (logins) en entree
    def getIndividus(self, listeSesames):
        session = self.getSession()
        IND = aliased(tables.IndividuSQLITE)
        taille = len(listeSesames)
        if taille > 500:
            liste = []
            deb = 0
            while deb < taille:
                fin = deb + 499
                if fin > taille:
                    fin = taille
                recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU.in_(listeSesames[deb:fin])).order_by(IND.LIB_NOM_PAT_IND)
                liste.extend(recherche.all())
                deb = deb + 500
            return liste
        else:
            recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU.in_(listeSesames)).order_by(IND.LIB_NOM_PAT_IND)
            return recherche.all()

    def supprimerAccent(self, ligne):
        """ supprime les accents du texte source """
        accents = {'a': ['à', 'ã', 'á', 'â'],
                   'e': ['é', 'è', 'ê', 'ë'],
                   'c': ['ç'],
                   'i': ['î', 'ï'],
                   'u': ['ù', 'ü', 'û'],
                   'o': ['ô', 'ö']}
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                ligne = ligne.replace(accented_char, char)
        return ligne
